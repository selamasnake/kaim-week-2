#### Scripts Overview

This folder contains Python scripts used for scraping banking app reviews from the Google Play Store and preparing the data for further analysis.

##### Scripts

- `config.py`: Handles project configuration. Loads environment variables, defines app IDs and bank name mappings, sets scraping parameters, and stores all file path locations for raw and processed data.

- `scraper.py`: Script used to scrape Google Play Store reviews for each bank. Fetches app metadata, collects reviews, processes basic fields (ratings, dates, usernames), and saves the combined raw dataset into the project’s data directory.

- `preprocessor.py`: Script used for cleaning and preparing the scraped review data. Removes duplicates, handles missing values, normalizes text and dates, validates ratings, and outputs a final processed dataset ready for analysis or modeling.

- `data_loader.py` : Utility module for loading and saving datasets. Ensures consistent file handling, validates paths, and manages output directories.

- `sentiment_analysis.py`: Runs sentiment analysis on user reviews using a Transformer-based model. Produces sentiment labels and scores that are appended to the dataset.

- `keyword_extractor.py`: Extracts significant keywords per bank using TF-IDF. Identifies top unigrams and bigrams that reveal common user concerns or praise.

- `topic_modeling.py`: Performs LDA topic modeling on lemmatized review text. Extracts topic word clusters and assigns a dominant topic to each review for unsupervised theme discovery.

- `theme_extraction.py`: Applies a rule-based theme classifier using curated keyword dictionaries. Assigns final high-level themes such as Account Access Issues, Transaction Performance, UI/UX, Bugs & Crashes, and Customer Support.

- `thematic_analysis.py`: Main pipeline script that combines preprocessing, keyword extraction, topic modeling, and rule-based theming to generate the final enriched dataset containing themes and topics.

- `plot.py` : Provides simple visualizations such as review and sentiment distributions to support reporting and exploration.
