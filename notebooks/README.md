#### Notebooks Overview

This folder contains Jupyter notebooks used for scraping, cleaning, and exploring banking app review data from the Google Play Store.

##### Usage

1. `review_preprocessing.ipynb` 
Use this notebook to run the full workflow for collecting and preparing review data.
It allows to:
- Run the Play Store scraper
- Clean and preprocess the raw reviews
- Save the processed dataset for analysis

2. `review_visualizations.ipynb`
Provides exploratory visualizations for both Google Play app metadata and raw review data before any sentiment or thematic analysis.
Includes:
- Visualizations of app-level metadata (ratings counts, reviews count, score, installs)
- Rating distribution plots for each bank
- Used for early exploration and understanding baseline patterns in the raw dataset.

3. `sentiment_analysis.ipynb`
Applies sentiment analysis to the processed review data using a Transformer model.
Includes steps to:

- Load the cleaned dataset
- Generate sentiment labels and confidence scores
- Explore sentiment distribution across banks and rating categories
- Export the sentiment-enriched dataset

4. `thematic_analysis.ipynb`
Focuses on keyword extraction, topic modeling, and rule-based theme assignment.
Enables you to:
- Run TF-IDF keyword extraction
- Perform LDA topic modeling
- Assign rule-based themes