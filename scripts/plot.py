import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set a clean visual style for all plots
sns.set(style='whitegrid')
plt.figure(figsize=(12, 5))



class ReviewDataVisualizer:
    """
    A class to visualize Google Play Store review data per banking app.

    Attributes:
        filepath (str): Path to the processed reviews CSV file.
        df (DataFrame): Loaded review data.
    """
    def __init__(self, filepath='../data/processed/reviews_processed.csv'):
        """
        Initialize the visualizer with a CSV filepath and load the data.
        """
        self.filepath = filepath
        self.df = None
        self.load_data()  # Load the data when class is instantiated

    def load_data(self):
        """
        Load the processed review CSV and preprocess it for plotting:
        """
        self.df = pd.read_csv(self.filepath)
        self.df['date'] = pd.to_datetime(self.df['date'])
        if 'text_length' not in self.df.columns:
            self.df['text_length'] = self.df['review'].str.len()

    def plot_rating_distribution(self):
        """Plot the distribution of ratings (1-5 stars) for each bank."""

        sns.countplot(data=self.df, x='rating', hue='bank', palette='Set2')
        plt.title('Rating Distribution by Bank')
        plt.xlabel('Rating')
        plt.ylabel('Number of Reviews')
        plt.legend(title='Bank')
        plt.tight_layout()
        plt.show()

    def plot_review_counts_over_time(self):
        """Plot a time series of review counts per bank with a 7-day rolling average."""

        time_series = self.df.groupby(['date', 'bank']).size().unstack(fill_value=0)
        time_series.rolling(window=7).mean().plot()
        plt.title('7-Day Rolling Average of Reviews Over Time')
        plt.xlabel('Date')
        plt.ylabel('Number of Reviews')
        plt.legend(title='Bank')
        plt.tight_layout()
        plt.show()

    
class AppDataVisualizer:
    """
    Visualizer for Google Play app metadata such as score, ratings, reviews, installs.

    """
    def __init__(self, filepath='../data/raw/app_info.csv'):
        """
        Args:
            filepath (str): Path to app_info.csv
        """
        self.filepath = filepath
        self.df = pd.read_csv(self.filepath)
        # Convert installs to numeric
        if 'installs' in self.df.columns:
            self.df['installs_numeric'] = self.df['installs'].str.replace('[,+]', '', regex=True).astype(int)

    def plot_app_scores(self):
        """Plot app scores vs. average scores."""
        sns.barplot(data=self.df, x='title', y='score', hue='title', palette='pastel', legend=False)
        plt.title('Google Play App Scores')
        plt.ylabel('Average Score')
        plt.xlabel('App')
        plt.xticks(rotation=15)
        plt.ylim(0, 5)
        plt.tight_layout()
        plt.show()


    def plot_num_ratings(self):
        """Plot number of ratings for each banking app"""
        plt.figure(figsize=(8,5))
        sns.barplot(data=self.df, x='title', y='ratings', hue='title', palette='coolwarm', legend=False)
        plt.title('Number of Ratings per App')
        plt.ylabel('Number of Ratings')
        plt.xlabel('App')
        plt.xticks(rotation=15)
        plt.tight_layout()
        plt.show()


    def plot_num_reviews(self):
        """Plot number of reviews for each banking app"""
        plt.figure(figsize=(8,5))
        sns.barplot(data=self.df, x='title', y='reviews', hue='title', palette='Set2', legend=False)
        plt.title('Number of Reviews per App')
        plt.ylabel('Number of Reviews')
        plt.xlabel('App')
        plt.xticks(rotation=15)
        plt.tight_layout()
        plt.show()


    def plot_num_installs(self):
        """Plot number of installs for each banking app"""
        plt.figure(figsize=(8,5))
        sns.barplot(data=self.df, x='title', y='installs_numeric', hue='title', palette='viridis', legend=False)
        plt.title('Number of Installs per App')
        plt.ylabel('Installs')
        plt.xlabel('App')
        plt.xticks(rotation=15)
        plt.tight_layout()
        plt.show()


class SentimentPlotter:
    """Plot sentiment analysis results in various formats."""

    def plot_sentiment_counts(self, df, label_col="sentiment_label", title=None):
        """Plot counts of sentiment labels."""
        counts = df[label_col].value_counts()
        sns.barplot(x=counts.index, y=counts.values)
        plt.title(title or "Sentiment Label Counts")
        plt.ylabel("Count")
        plt.show()

    def plot_sentiment_by_bank(self, agg_df, method_name):     
        banks = agg_df['bank'].unique()
        n = len(banks)
        # fig, axes = plt.subplots(n, 1, figsize=(4, 4 * n), sharey=True)
        fig, axes = plt.subplots(1, n, figsize=(5*n, 4), sharey=True)
        for i, bank in enumerate(banks):
            ax = axes[i] if n > 1 else axes
            subset = agg_df[agg_df['bank'] == bank]
            sns.lineplot(x='rating', y='sentiment_score', data=subset, marker='o', ax=ax)
            ax.set_title(f"{method_name} Mean Sentiment by Rating - {bank}")
            ax.set_ylabel("Mean Sentiment Score")
            ax.set_xlabel("Rating")

        plt.tight_layout()
        plt.show()


    def plot_comparison(self, dfs, labels, label_col="sentiment_label"):
        """Compare sentiment distributions across multiple sentiment datasets."""
        n = len(dfs)
        fig, axes = plt.subplots(1, n, figsize=(5*n, 4), sharey=True)
        for i, (df, label) in enumerate(zip(dfs, labels)):
            counts = df[label_col].value_counts()
            sns.barplot(x=counts.index, y=counts.values, ax=axes[i])
            axes[i].set_title(label)
            axes[i].set_ylabel("Count" if i == 0 else "")
        plt.tight_layout()
        plt.show()

# Example usage for notebook or script
if __name__ == "__main__":
    # Review visualizations
    review_visualizer = ReviewDataVisualizer()

    # App metadata visualizations from CSV
    app_visualizer = AppDataVisualizer()

    #Sentiment plots for reviews
    sentiment_plotter = SentimentPlotter()
