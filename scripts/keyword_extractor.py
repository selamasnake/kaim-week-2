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