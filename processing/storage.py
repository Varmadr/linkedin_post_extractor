import os
import pandas as pd
import sqlite3
import logging

logger = logging.getLogger(__name__)

class DataStorage:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def save_to_csv(self, posts_data, filename="linkedin_posts.csv"):
        """Saves a list of post dictionaries to a CSV file."""
        if not posts_data:
            logger.warning(f"No data to save to {filename}")
            return
            
        filepath = os.path.join(self.data_dir, filename)
        df = pd.DataFrame(posts_data)
        
        # If file exists, append without writing header again
        if os.path.exists(filepath):
            df.to_csv(filepath, mode='a', header=False, index=False)
        else:
            df.to_csv(filepath, index=False)
            
        logger.info(f"Saved {len(posts_data)} posts to {filepath}")

    def save_to_sqlite(self, posts_data, db_name="linkedin_data.db", table_name="posts"):
        """Saves a list of post dictionaries to an SQLite database."""
        if not posts_data:
            logger.warning(f"No data to save to {db_name}")
            return
            
        db_path = os.path.join(self.data_dir, db_name)
        conn = sqlite3.connect(db_path)
        
        df = pd.DataFrame(posts_data)
        
        # We use append in case we run multiple times
        df.to_sql(table_name, conn, if_exists='append', index=False)
        conn.close()
        logger.info(f"Saved {len(posts_data)} posts to SQLite database: {db_path}, table: {table_name}")
