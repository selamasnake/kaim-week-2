from transformers import pipeline
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import nltk

nltk.download('vader_lexicon', quiet=True)

class SentimentAnalyzer:
    """Compute sentiment scores using DistilBERT SST-2, VADER, or TextBlob."""

    def __init__(self):
        self.distilbert_pipeline = None
        self.sia = SentimentIntensityAnalyzer()

    def score(self, df, text_column="review", method="vader"):
        method = method.lower()
        df = df.copy()

        if method == "distilbert":
            if self.distilbert_pipeline is None:
                print("Loading DistilBERT sentiment pipeline...")
                self.distilbert_pipeline = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english"
                )
            results = self.distilbert_pipeline(df[text_column].tolist(), truncation=True)
            df["sentiment_label"] = [r["label"].lower() for r in results]
            df["sentiment_score"] = [r["score"] for r in results]

        elif method == "vader":
            df["sentiment_score"] = df[text_column].apply(lambda x: self.sia.polarity_scores(x)["compound"])
            df["sentiment_label"] = df["sentiment_score"].apply(self._vader_label)

        elif method == "textblob":
            df["sentiment_score"] = df[text_column].apply(lambda x: TextBlob(x).sentiment.polarity)
            df["sentiment_label"] = df["sentiment_score"].apply(self._textblob_label)

        else:
            raise ValueError("method must be 'distilbert', 'vader', or 'textblob'")

        return df

    @staticmethod
    def _vader_label(score):
        if score >= 0.05:
            return "positive"
        elif score <= -0.05:
            return "negative"
        else:
            return "neutral"

    @staticmethod
    def _textblob_label(score):
        if score > 0.1:
            return "positive"
        elif score < -0.1:
            return "negative"
        else:
            return "neutral"

    @staticmethod
    def aggregate(df, by=["bank", "rating"]):
        """Return mean sentiment_score by bank and rating"""
        return df.groupby(by)["sentiment_score"].mean().reset_index()
