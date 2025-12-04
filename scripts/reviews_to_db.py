import os
import pandas as pd
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, Date, MetaData, ForeignKey
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert
from dotenv import load_dotenv

class ReviewDBHandler:
    """
    Handles insertion of banks and cleaned review data into PostgreSQL.
    It reads raw reviews for structure and bank data, and theme reviews for processed columns.
    """

    def __init__(self, database_url: str, raw_csv: str, themes_csv: str):
        """
        Initialize with PostgreSQL database URL and paths to both CSV files.
        """
        self.engine = create_engine(database_url)
        self.metadata = MetaData()
        self.raw_csv = raw_csv
        self.themes_csv = themes_csv

        # Define tables
        self.banks_table = Table(
            "banks", self.metadata,
            Column("bank_id", Integer, primary_key=True, autoincrement=True),
            Column("bank_name", String, nullable=False, unique=True),
            Column("app_name", String)
        )

        # Reviews table based on the suggested columns
        self.reviews_table = Table(
            "reviews", self.metadata,
            Column("review_id", Integer, primary_key=True),  # review_id from raw CSV is primary key
            Column("bank_id", Integer, ForeignKey("banks.bank_id")),
            Column("review_text", String),
            Column("rating", Integer),
            Column("review_date", Date),
            Column("sentiment_label", String),
            Column("sentiment_score", Float),
            Column("source", String),
        )

        # Create tables if they don't exist
        self.metadata.create_all(self.engine)
        print("Database connection established and tables ensured.")

    def insert_banks(self) -> None:
        """
        Insert unique banks (bank_name and bank_code as app_name) 
        from the raw reviews CSV into the banks table.
        """
        try:
            raw_df = pd.read_csv(self.raw_csv)
            
            # Extract unique bank names and their codes (app_name)
            # Ensure only the necessary columns are selected
            banks_df = raw_df[['bank_name', 'bank_code']].drop_duplicates().copy() 
            
            # Rename 'bank_code' to 'app_name' to match the schema
            banks_records = banks_df.rename(columns={"bank_code": "app_name"}).to_dict(orient="records")
            
        except FileNotFoundError:
            print(f"Error: Raw reviews CSV file not found at {self.raw_csv}")
            return

        with self.engine.connect() as conn:
            for record in banks_records:
                try:
                    stmt = insert(self.banks_table).values(record).on_conflict_do_nothing(
                        index_elements=['bank_name']
                    )
                    conn.execute(stmt)
                except SQLAlchemyError as e:
                    print(f"Error inserting bank {record.get('bank_name')}: {e}")
            
            # Commit the transaction to persist changes
            conn.commit() 
            
            print(f"Inserted/checked {len(banks_records)} banks.")

    def insert_reviews(self) -> None:
        """
        Reads data from two CSVs, merges them, maps the bank IDs, and inserts the final records.
        Includes robustness checks for data mismatch (case/spacing).
        """
        try:
            # Load raw data (primary source for structure: ID, text, date, source)
            raw_df = pd.read_csv(self.raw_csv)
            # Load processed data (source for sentiment/themes)
            themes_df = pd.read_csv(self.themes_csv)
            
            # Prepare dates and rename columns for merging
            raw_df['review_date'] = pd.to_datetime(raw_df['review_date']).dt.date
            raw_df = raw_df.rename(columns={'review_text': 'review'})
            
        except FileNotFoundError as e:
            print(f"Error: Missing CSV file during review insertion: {e}")
            return
        
        # --- 1. MERGE DATA ---
        # Join the two dataframes on common identifying columns (review text and rating)
        merged_df = pd.merge(
            raw_df, 
            themes_df[['review', 'rating', 'sentiment_label', 'sentiment_score']],
            on=['review', 'rating'], 
            how='inner' # Use 'inner' to only keep reviews that exist in BOTH files
        )
        
        with self.engine.connect() as conn:
            # 2. MAP BANK ID and NORMALIZE
            try:
                bank_id_map = pd.read_sql(self.banks_table.select(), conn).set_index("bank_name")["bank_id"].to_dict()
                
                merged_df['bank_name_norm'] = merged_df['bank_name'].astype(str).str.strip().str.lower()
                
                normalized_map = {name.strip().lower(): id for name, id in bank_id_map.items()}
                
                merged_df['bank_id'] = merged_df['bank_name_norm'].map(normalized_map)
                
                merged_df.dropna(subset=['bank_id'], inplace=True)
                merged_df['bank_id'] = merged_df['bank_id'].astype(int) 
            
            except Exception as e:
                print(f"Error mapping bank IDs: {e}. Check for column names in the raw CSV.")
                return

            # 3. PREPARE RECORDS: Select only the final target columns
            # Ensure column names match the Reviews Table schema
            review_records = merged_df[[
                 "bank_id", "review", "rating", "review_date", "sentiment_label",
                "sentiment_score", "source"
            ]].rename(columns={
                "review": "review_text" # Rename back to review_text for the DB insert
            }).to_dict(orient="records")

            # 4. INSERT
            if not review_records:
                print("No valid reviews to insert after merging, mapping, and filtering. Check data consistency between CSVs.")
                return

            try:
                # EFFICIENT BATCH INSERT
                conn.execute(self.reviews_table.insert(), review_records)
                
                # Commit the transaction
                conn.commit()
                
                print(f"Successfully inserted {len(review_records)} reviews.")
            except SQLAlchemyError as e:
                print(f"Error performing batch insert for reviews: {e}")

if __name__ == "__main__":
    # Load Environment Variables
    load_dotenv()
    
    # Get the necessary variables
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Update CSV paths to match your two files
    RAW_CSV = "data/raw/reviews_raw.csv"
    THEMES_CSV = "data/processed/reviews_with_themes.csv"
    
    # Validation Check
    if not DATABASE_URL:
        print("ERROR: DATABASE_URL not found in environment variables. Please check your .env file.")
    else:
        # Execution
        try:
            print("--- Starting Database Insertion Process ---")
            print(f"Using database URL: {DATABASE_URL.split('@')[-1]}") 
            print(f"Reading RAW data from: {RAW_CSV}")
            print(f"Reading PROCESSED data from: {THEMES_CSV}")
            
            # Initialize the handler with both CSV paths
            inserter = ReviewDBHandler(DATABASE_URL, RAW_CSV, THEMES_CSV)
            
            # Insert banks (must happen first to generate bank_ids)
            print("\nInserting Banks...")
            inserter.insert_banks()
            
            # Insert reviews (relies on bank_ids from the previous step)
            print("\nInserting Reviews...")
            inserter.insert_reviews()
            
            print("\n--- Database Insertion Complete! ---")
            
        except Exception as e:
            print(f"\nAn unexpected error occurred during execution: {e}")