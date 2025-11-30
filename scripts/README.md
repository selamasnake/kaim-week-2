#### Scripts Overview

This folder contains Python scripts used for scraping banking app reviews from the Google Play Store and preparing the data for further analysis.

##### Scripts

- `config.py`: Handles project configuration. Loads environment variables, defines app IDs and bank name mappings, sets scraping parameters, and stores all file path locations for raw and processed data.
- `scraper.py`: Script used to scrape Google Play Store reviews for each bank. Fetches app metadata, collects reviews, processes basic fields (ratings, dates, usernames), and saves the combined raw dataset into the project’s data directory.
- `preprocessor.py`: Script used for cleaning and preparing the scraped review data. Removes duplicates, handles missing values, normalizes text and dates, validates ratings, and outputs a final processed dataset ready for analysis or modeling.


