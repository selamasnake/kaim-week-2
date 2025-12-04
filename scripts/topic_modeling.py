from gensim.corpora.dictionary import Dictionary
from gensim.models.ldamodel import LdaModel
import pandas as pd

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
