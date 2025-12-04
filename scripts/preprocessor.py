import os
import re
import pandas as pd
import numpy as np
from datetime import datetime
from config import DATA_PATHS
from IPython.display import display
from langdetect import detect, DetectorFactory
import spacy
import re


class ReviewPreprocessor:
    """Notebook-friendly preprocessor for scraped reviews"""

    def __init__(self, input_path=None, output_path=None):
        self.input_path = input_path or DATA_PATHS['raw_reviews']
        self.output_path = output_path or DATA_PATHS['processed_reviews']
        self.df = None
        self.stats = {}

    def load_data(self, input_path=None):
        """Load CSV into DataFrame"""

        self.input_path = input_path or self.input_path
        print(f"Loading raw data from {self.input_path}...")
        try:
            self.df = pd.read_csv(self.input_path)
            print(f"Loaded {len(self.df)} reviews.")
            self.stats['original_count'] = len(self.df)
        except FileNotFoundError:
            print(f"ERROR: File not found: {self.input_path}")
            return None
        except Exception as e:
            print(f"ERROR loading data: {e}")
            return None
        return self.df

    def show_missing(self):
        """Display columns with missing values"""


        missing = self.df.isna().sum()
        missing = missing[missing > 0]
        if len(missing) == 0:
            print("No missing values!")
        else:
            print("Columns with missing values:")
            display(missing)
        return missing

    def remove_duplicates(self):
        """Remove duplicate reviews"""

        before = len(self.df)
        self.df = self.df.drop_duplicates(subset=['review_text', 'bank_name'])
        removed = before - len(self.df)
        print(f"Removed {removed} duplicate reviews.")
        return self.df

    def handle_missing_data(self):
        """Drop critical missing data and fill optional columns"""

        before = len(self.df)
        critical_cols = ['review_text', 'rating', 'bank_name']
        self.df = self.df.dropna(subset=critical_cols)
        removed = before - len(self.df)
        print(f"Removed {removed} rows with missing critical data.")
        # Fill optional columns
        self.df['user_name'] = self.df['user_name'].fillna('Anonymous')
        self.df['thumbs_up'] = self.df['thumbs_up'].fillna(0)
        self.df['reply_content'] = self.df['reply_content'].fillna('')
        self.df['source'] = self.df['source'].fillna('Google Play')
        self.stats['rows_removed_missing'] = removed
        return self.df

    def normalize_dates(self):
        """Normalize review_date to YYYY-MM-DD"""

        try:
            self.df['review_date'] = pd.to_datetime(self.df['review_date']).dt.date
        except Exception as e:
            print(f"Could not normalize dates: {e}")

    def clean_text(self):
        """Clean review text and remove empty reviews"""

        def clean_review(text):
            if pd.isna(text) or text == '':
                return ''
            text = str(text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text

        self.df['review_text'] = self.df['review_text'].apply(clean_review)
        before = len(self.df)
        self.df = self.df[self.df['review_text'].str.len() > 0]
        removed = before - len(self.df)
        if removed > 0:
            print(f"Removed {removed} empty reviews.")
        self.df['text_length'] = self.df['review_text'].str.len()
        self.stats['empty_reviews_removed'] = removed
        return self.df

    def validate_ratings(self):
        """Keep only ratings between 1 and 5"""


        invalid = self.df[(self.df['rating'] < 1) | (self.df['rating'] > 5)]
        if len(invalid) > 0:
            print(f"Removed {len(invalid)} invalid ratings.")
            self.df = self.df[(self.df['rating'] >= 1) & (self.df['rating'] <= 5)]
        else:
            print("All ratings are valid (1-5).")
        self.stats['invalid_ratings_removed'] = len(invalid)
        return self.df

    def prepare_final_output(self):
        """Reorder, rename, and clean final output for saving"""
        

        # Select only the columns we want
        cols = ['review_text', 'rating', 'review_date', 'bank_code', 'source']
        cols = [c for c in cols if c in self.df.columns]
        self.df = self.df[cols]

        # Rename columns to final names
        rename_map = {
            'review_text': 'review',
            'review_date': 'date',
            'bank_code': 'bank'
        }
        self.df = self.df.rename(columns=rename_map)

        # Optional: sort by bank and date
        if 'bank' in self.df.columns and 'date' in self.df.columns:
            self.df = self.df.sort_values(['bank', 'date'], ascending=[True, False])

        # Reset index
        self.df = self.df.reset_index(drop=True)

        print(f"Final dataset contains {len(self.df)} reviews.")
        self.stats['final_count'] = len(self.df)
        return self.df


    def save_clean_data(self, output_path=None):
        """Save processed DataFrame to CSV"""
        if self.df is None:
            print("Data not loaded yet.")
            return
        self.output_path = output_path or self.output_path
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        self.df.to_csv(self.output_path, index=False)
        print(f"Cleaned data saved to {self.output_path} ({len(self.df)} rows)")

    def generate_report(self):
        """Display preprocessing statistics"""
        print("\n" + "="*50)
        print("PREPROCESSING REPORT")
        print("="*50)
        print(f"Original records: {self.stats.get('original_count', 0)}")
        print(f"Rows removed (missing critical): {self.stats.get('rows_removed_missing', 0)}")
        print(f"Empty reviews removed: {self.stats.get('empty_reviews_removed', 0)}")
        print(f"Invalid ratings removed: {self.stats.get('invalid_ratings_removed', 0)}")
        print(f"Final records: {self.stats.get('final_count', 0)}")
        if self.df is not None:
            print("\nReviews per bank:")
            display(self.df['bank'].value_counts())
            print("\nRating distribution:")
            display(self.df['rating'].value_counts().sort_index(ascending=False))
            print(f"\nDate range: {self.df['date'].min()} to {self.df['date'].max()}")

    def process(self, input_path=None, output_path=None):
        """Run full preprocessing pipeline"""
        if self.load_data(input_path) is None:
            return None
        self.remove_duplicates()
        self.handle_missing_data()
        self.normalize_dates()
        self.clean_text()
        self.validate_ratings()
        self.prepare_final_output()
        self.save_clean_data(output_path)
        print("Preprocessing complete!")
        self.generate_report()
        return self.df

class TextPreprocessor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def is_english(self, text):
        """Check if the text is English"""
        try:
            return detect(text) == "en"
        except:
            return False

    def filter_non_english(self, df, text_col="review"):
        """Remove rows where the review is not in English"""
        mask = df[text_col].apply(self.is_english)
        return df[mask].reset_index(drop=True)

    def clean_text(self, text):
        """Lowercase, remove punctuation, extra spaces"""
        text = text.lower()
        text = re.sub(r"[^\w\s]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def lemmatize(self, text):
        """Return lemmatized text without stopwords"""
        doc = self.nlp(text)
        tokens = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]
        return " ".join(tokens)

    def extract_nouns(self, text):
        """Return a list of nouns in the text"""
        doc = self.nlp(text)
        return [token.text for token in doc if token.pos_ == "NOUN"]