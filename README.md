# kaim-week-2

This project collects and processes Google Play Store reviews from major Ethiopian banking apps. It includes automated scraping, data cleaning, and preparation workflows to support downstream analysis such as sentiment analysis, trend tracking, or app performance monitoring.

Key activities include:
  * Scraping reviews from Google Play Store.
  * Cleaning and preprocessing the scraped review data.
  * Normalizing and structuring fields such as text, dates, ratings, and user information.
  * Exporting both raw and processed datasets for further analysis.

### File Structure
The project is organized as follows:

* data/: Stores raw and processed review datasets.
* notebooks/: Contains Jupyter notebooks for scraping, cleaning, and exploring the reviews.
* scripts/: Python scripts for scraping and preprocessing (scraper, config loader, cleaner).
* requirements.txt: Contains the necessary dependencies to run the project.

### Tools, Frameworks, and Libraries Used

#### Tools:
  * Jupyter Notebooks: Used for interactive analysis and visualization.
  * Git: Version control for managing changes.
  * Python: Primary programming language for data processing and analysis.

#### Frameworks & Libraries:
  * google-play-scraper – For programmatic Play Store review extraction.
  * Pandas – For all data transformations, cleaning, and exporting CSVs.
  * NumPy – For numerical and structural operations.
  * TQDM – For progress tracking during scraping.
  * python-dotenv – For loading environment variables.
  
### User Guide: How to Run the Project

1. Clone the repository and navigate to the project
    ```
    https://github.com/selamasnake/kaim-week-2.git
    cd kaim-week-1
    ```
Make sure a virtual environment is activated then,
2. Install dependencies : Install the required Python libraries by using the requirements.txt
    ```
    pip install -r requirements.txt
    ```
3. Run the notebooks
   Run the notebooks Navigate to the `notebooks` directory, `review_preprocessing.ipynb` → scrape reviews, clean them, and save both raw and processed datasets.
Visual outputs are generated to help inspect the data.

5. Running Python Scripts
    Navigate to the scripts directory,
    Run the scraper  `python scraper.py`, this collects reviews and saves them to `data/raw/reviews_raw.csv`.
    Run `python preprocessor.py` This cleans the raw dataset and saves the final processed version to `data/processed/reviews_processed.csv`.