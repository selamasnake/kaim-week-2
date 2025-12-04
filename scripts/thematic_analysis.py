import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.corpora.dictionary import Dictionary
from gensim.models.ldamodel import LdaModel
import spacy
import re

class DataLoader:
    """Generic CSV data loader for processed reviews"""

    def __init__(self, path=None):
        self.path = path
        self.df = None

    def load_csv(self, path=None):
        """Load CSV into a DataFrame"""
        file_path = path or self.path
        if not file_path:
            raise ValueError("No file path specified for loading data.")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        self.df = pd.read_csv(file_path)
        print(f"Loaded {len(self.df)} rows from {file_path}")
        return self.df

    def save_csv(self, output_path):
        """Save current DataFrame to CSV"""
        if self.df is None:
            raise ValueError("No data loaded to save.")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        self.df.to_csv(output_path, index=False)
        print(f"Saved {len(self.df)} rows to {output_path}")


class TextPreprocessor:
    """
    Clean the reviews by lowercase, remove punctuation, normalize spaces and lemmatize
    """
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

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
    
class KeywordExtractor:
    """Extract top keywords per bank using TF-IDF."""

    def __init__(self, max_features=200, ngram_range=(1,2)):
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=ngram_range,
            max_features=max_features
        )

    def extract(self, df, text_col="processed_text"):
        keywords_per_bank = {}
        for bank in df["bank"].unique():
            bank_df = df[df["bank"] == bank]
            if len(bank_df) < 3:
                keywords_per_bank[bank] = []
                continue
            tfidf_matrix = self.vectorizer.fit_transform(bank_df[text_col])
            feature_names = self.vectorizer.get_feature_names_out()
            mean_scores = tfidf_matrix.mean(axis=0).A1
            top_indices = mean_scores.argsort()[::-1][:15]
            keywords = [(feature_names[i], mean_scores[i]) for i in top_indices]
            keywords_per_bank[bank] = keywords
        return keywords_per_bank

class TopicModeler:
    """
    Perform LDA topic modeling on preprocessed text and extract themes.
    """
    def __init__(self, num_topics=5, num_words=10, passes=15, random_state=42):
        self.num_topics = num_topics
        self.num_words = num_words
        self.passes = passes
        self.random_state = random_state
        self.lda_model = None
        self.dictionary = None
        self.corpus = None
        self.topics = None

    def fit(self, df, text_col='lemmatized_text'):
        """
        Fit the LDA model on the given DataFrame column.
        """
        # Tokenize
        df['tokens'] = df[text_col].str.split()

        # Create dictionary and corpus
        self.dictionary = Dictionary(df['tokens'])
        self.corpus = [self.dictionary.doc2bow(tokens) for tokens in df['tokens']]

        # Train LDA model
        self.lda_model = LdaModel(
            corpus=self.corpus,
            id2word=self.dictionary,
            num_topics=self.num_topics,
            passes=self.passes,
            random_state=self.random_state
        )

        # Extract topics as lists of words
        self.topics = {}
        for i in range(self.num_topics):
            self.topics[i] = [word for word, _ in self.lda_model.show_topic(i, topn=self.num_words)]

        return self

    def get_topics(self):
        """Return dictionary of topics"""
        return self.topics

    def assign_dominant_topic(self, df, text_col='lemmatized_text'):
        """
        Assign the dominant topic for each document based on highest topic probability.
        Adds a column 'dominant_topic' to the DataFrame.
        """
        if self.lda_model is None or self.corpus is None:
            raise ValueError("You must fit the model first!")

        dominant_topics = []
        for doc_bow in self.corpus:
            topic_probs = self.lda_model.get_document_topics(doc_bow)
            dominant_topic = max(topic_probs, key=lambda x: x[1])[0] if topic_probs else None
            dominant_topics.append(dominant_topic)

        df['dominant_topic'] = dominant_topics
        return df

class ThemeExtractor:
    """Rule-based keyword theming."""

    THEMES = {
        "Account Access Issues": [
            "login", "logout", "pin", "password", "otp",
            "fingerprint", "authentication", "session", "access"
        ],
        "Transaction Performance": [
            "transaction", "payment", "transfer", "bill", "delay", "money", "lag"
            "recharge", "airtime", "balance", "deduct", "deposit", "withdraw", "failed"
        ],
        "User Interface & Experience": [
            "ui", "design", "interface", "easy", "user", "friendly", "good", "convenient"
            "experience", "smooth", "simple", "layout", "beautiful", "wow", "amazing"

        ],
        "Customer Support": [
            "support", "help", "service", "customer care", "assist", "assistance", "contact"
        ],
        "Bugs & Crashes": [
            "error", "crash", "lag", "bug", "fail", "failed", "issue", "bad"
            "problem", "stuck", "glitch", "freeze", "slow", "not",
        ],
    }

    def assign_theme(self, text):
        text = str(text).lower()
        assigned = []

        for theme, keywords in self.THEMES.items():
            if any(re.search(rf"\b{k}\b", text) for k in keywords):
                assigned.append(theme)

        return assigned if assigned else ["Other"]

    def apply(self, df, text_col="review"):
        df["identified_theme"] = df[text_col].apply(self.assign_theme)
        return df


if __name__ == "__main__":
    import os

    # -------- 1. LOAD DATA --------
    input_path = "../data/processed/reviews_processed.csv"  
    output_path = "../data/processed/reviews_with_themes.csv"

    loader = DataLoader(path=input_path)
    df = loader.load_csv()

    # -------- 2. PREPROCESS TEXT --------
    print("\n[1/5] Preprocessing text...")
    preprocessor = TextPreprocessor()

    df["clean_text"] = df["review"].apply(preprocessor.clean_text)
    df["lemmatized_text"] = df["clean_text"].apply(preprocessor.lemmatize)

    # -------- 3. KEYWORD EXTRACTION--------
    print("\n[2/5] Extracting keywords per bank using TF-IDF...")
    keyword_extractor = KeywordExtractor(max_features=200)

    keywords_per_bank = keyword_extractor.extract(df, text_col="lemmatized_text")

    print("\nTop keywords per bank:")
    for bank, words in keywords_per_bank.items():
        print(f"\n{bank}:")
        for word, score in words:
            print(f"  {word} ({score:.3f})")

    # -------- 4. LDA TOPIC MODELING --------
    print("\n[3/5] Running LDA topic modeling...")
    topic_modeler = TopicModeler(num_topics=5, num_words=10)

    topic_modeler.fit(df, text_col="lemmatized_text")
    df = topic_modeler.assign_dominant_topic(df)

    print("\nIdentified LDA topics:")
    for topic_id, words in topic_modeler.get_topics().items():
        print(f"  Topic {topic_id}: {', '.join(words)}")

    # -------- 5. RULE-BASED THEME ASSIGNMENT --------
    print("\n[4/5] Assigning rule-based themes...")
    theme_extractor = ThemeExtractor()

    df = theme_extractor.apply(df, text_col="review")

    # Convert list → string for clean CSV
    df["identified_theme"] = df["identified_theme"].apply(lambda t: "; ".join(t))

    # -------- 6. SAVE OUTPUT --------
    print("\n[5/5] Saving final dataset...")

    loader.df = df 
    loader.save_csv(output_path)

    print("\nPipeline completed successfully!")
    print("Saved thematic analysis to:", output_path)
