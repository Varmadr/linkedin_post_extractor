import logging
import time
from scraper.login import LinkedInAuthenticator
from scraper.search import LinkedInSearcher
from scraper.extractor import LinkedInExtractor
from processing.filter import filter_posts_by_date
from processing.storage import DataStorage

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    keywords = ["Adya AI", "Shayak Mazumder"]
    
    # Initialize authenticator (Set headless=True if you want it to run without a UI)
    logger.info("Starting LinkedIn Post Extractor...")
    authenticator = LinkedInAuthenticator(headless=False)
    
    try:
        # 1. Login
        driver = authenticator.login()
        time.sleep(2)
        
        searcher = LinkedInSearcher(driver)
        storage = DataStorage(data_dir='data')
        
        all_filtered_posts = []

        # 2. Search and Extract for each keyword
        for keyword in keywords:
            logger.info(f"=== Processing Keyword: {keyword} ===")
            
            # Search & scroll
            html_source = searcher.search_posts(keyword, scroll_pause_time=3, max_scrolls=5)
            
            # Extract
            extractor = LinkedInExtractor(html_source)
            posts = extractor.extract_posts()
            
            # Add a keyword field to the extracted posts for better tracking
            for post in posts:
                post['search_keyword'] = keyword
            
            # 3. Filter (last 6 months)
            filtered_posts = filter_posts_by_date(posts)
            logger.info(f"Posts within the last 6 months for '{keyword}': {len(filtered_posts)}")
            
            all_filtered_posts.extend(filtered_posts)
            
            # Rest a bit before the next keyword search to avoid spamming
            time.sleep(5)

        # 4. Save results
        if all_filtered_posts:
            logger.info(f"Total filtered posts across all keywords: {len(all_filtered_posts)}")
            storage.save_to_sqlite(all_filtered_posts, db_name="linkedin_data.db", table_name="posts")
            storage.save_to_csv(all_filtered_posts, filename="linkedin_posts.csv")
            logger.info("Data correctly stored. You can now run `streamlit run app.py`.")
        else:
            logger.info("No new posts matched the criteria in the specified timeframe.")

    except Exception as e:
        logger.error(f"An error occurred during execution: {e}")
    finally:
        logger.info("Closing browser and cleaning up.")
        authenticator.close()

if __name__ == "__main__":
    main()
