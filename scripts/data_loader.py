# data_loader.py
import pandas as pd
import os

class DataLoader:
    """Generic CSV data loader for processed reviews"""

    def __init__(self, path=None):
        self.path = path
        self.df = None

    def load_csv(self, path=None):
        """Load CSV into a DataFrame"""
        file_path = path or self.path
        if not file_path:
            raise ValueError("No file path specified for loading data.")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        self.df = pd.read_csv(file_path)
        print(f"Loaded {len(self.df)} rows from {file_path}")
        return self.df

    def save_csv(self, output_path):
        """Save current DataFrame to CSV"""
        if self.df is None:
            raise ValueError("No data loaded to save.")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        self.df.to_csv(output_path, index=False)
        print(f"Saved {len(self.df)} rows to {output_path}")
