# scraper.py
import os
import time
import pandas as pd
from google_play_scraper import reviews, Sort, app
from config import APP_IDS, BANK_NAMES, DATA_PATHS, SCRAPING_CONFIG
from datetime import datetime
from tqdm import tqdm

class PlayStoreScraper:
    """Scraper for Google Play Store reviews"""

    def __init__(self):
        self.app_ids = APP_IDS
        self.bank_names = BANK_NAMES
        self.reviews_per_bank = SCRAPING_CONFIG['reviews_per_bank']
        self.lang = SCRAPING_CONFIG['lang']
        self.country = SCRAPING_CONFIG['country']
        self.max_retries = SCRAPING_CONFIG['max_retries']

    def get_app_info(self, app_id):
        try:
            info = app(app_id, lang=self.lang, country=self.country)
            return {
                'app_id': app_id,
                'title': info.get('title', 'N/A'),
                'score': info.get('score', 0),
                'ratings': info.get('ratings', 0),
                'reviews': info.get('reviews', 0),
                'installs': info.get('installs', 'N/A')
            }
        except Exception as e:
            print(f"Error getting app info for {app_id}: {e}")
            return None

    def scrape_reviews(self, app_id, bank_code):
        """Scrape reviews for a specific app"""
        for attempt in range(self.max_retries):
            try:
                result, _ = reviews(
                    app_id,
                    lang=self.lang,
                    country=self.country,
                    sort=Sort.NEWEST,
                    count=self.reviews_per_bank,
                    filter_score_with=None
                )
                return result
            except Exception as e:
                print(f"Attempt {attempt+1} failed for {bank_code}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(5)
                else:
                    return []
                
    def process_reviews(self, raw_reviews, bank_code):
        """Convert raw reviews into clean dicts."""
        processed = []
        for review in raw_reviews:
            processed.append({
                'review_id': review.get('reviewId', ''),
                'review_text': review.get('content', ''),
                'rating': review.get('score', 0),
                'review_date': review.get('at', datetime.now()),
                'user_name': review.get('userName', 'Anonymous'),
                'thumbs_up': review.get('thumbsUpCount', 0),
                'reply_content': review.get('replyContent', None),
                'bank_code': bank_code,
                'bank_name': self.bank_names[bank_code],
                'app_id': review.get('reviewCreatedVersion', 'N/A'),
                'source': 'Google Play'
            })
        return processed

    def scrape_all_banks(self):
        """
        1. Iterates through all configured banks
        2. Fetches app metadata
        3. Scrapes reviews for each bank
        4. Combines all data into a single DataFrame
        5. Saves the raw data to CSV
        """
        all_reviews = []
        app_info_list = []

        print("=" * 60)
        print("Starting Google Play Store Review Scraper")
        print("=" * 60)

        # --- Phase 1: Fetch App Info ---
        print("\n[1/2] Fetching app information...")
        for bank_code, app_id in self.app_ids.items():
            print(f"\nBank Code: {bank_code} | Bank Name: {self.bank_names[bank_code]}")
            print(f"App ID: {app_id}")

            info = self.get_app_info(app_id)
            if info:
                info['bank_code'] = bank_code
                info['bank_name'] = self.bank_names[bank_code]
                app_info_list.append(info)
                print(f"Current Rating: {info['score']} | Total Ratings: {info['ratings']} | Total Reviews: {info['reviews']}")

        # Save the gathered app info to a CSV file
        if app_info_list:
            app_info_df = pd.DataFrame(app_info_list)
            os.makedirs(DATA_PATHS['raw'], exist_ok=True)
            app_info_df.to_csv(f"{DATA_PATHS['raw']}/app_info.csv", index=False)
            print(f"\nApp information saved to {DATA_PATHS['raw']}/app_info.csv")

        # --- Phase 2: Scrape Reviews ---
        print("\n[2/2] Scraping reviews...")
        for bank_code, app_id in tqdm(self.app_ids.items(), desc="Banks"):
            reviews_data = self.scrape_reviews(app_id, bank_code)
            if reviews_data:
                processed = self.process_reviews(reviews_data, bank_code)
                # Ensure bank_code column exists in processed reviews for stats
                for r in processed:
                    r['bank_code'] = bank_code
                all_reviews.extend(processed)
                print(f"Collected {len(processed)} reviews for {self.bank_names[bank_code]}")
            else:
                print(f"WARNING: No reviews collected for {self.bank_names[bank_code]}")

            time.sleep(2)

        # --- Phase 3: Save Data ---
        if all_reviews:
            df = pd.DataFrame(all_reviews)

            # Save raw data to CSV
            os.makedirs(DATA_PATHS['raw'], exist_ok=True)
            df.to_csv(DATA_PATHS['raw_reviews'], index=False)

            print("\n" + "=" * 60)
            print("Scraping Complete!")
            print("=" * 60)
            print(f"\nTotal reviews collected: {len(df)}")

            # Print stats per bank
            print("\nReviews per bank:")
            for bank_code in self.bank_names.keys():
                count = len(df[df['bank_code'] == bank_code])
                print(f"  {self.bank_names[bank_code]}: {count}")

            print(f"\nData saved to: {DATA_PATHS['raw_reviews']}")
        else:
            print("\nERROR: No reviews were collected!")
            return pd.DataFrame()

    
def main():
    scraper = PlayStoreScraper()
    df = scraper.scrape_all_banks()
    print(f"Total reviews collected: {len(df)}")
    return df

if __name__ == "__main__":
    main()