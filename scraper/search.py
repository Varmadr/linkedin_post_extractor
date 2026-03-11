import time
import urllib.parse
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

class LinkedInSearcher:
    def __init__(self, driver):
        self.driver = driver

    def search_posts(self, keyword, scroll_pause_time=2, max_scrolls=10):
        """
        Navigates to the content search page for the given keyword,
        sorted by latest posts.
        """
        encoded_keyword = urllib.parse.quote(keyword)
        # Some newer LinkedIn layouts fail with deep query params. Trying the standard broader search layout.
        url = f"https://www.linkedin.com/search/results/all/?keywords={encoded_keyword}"
        
        logger.info(f"Navigating to search page for keyword: '{keyword}'")
        self.driver.get(url)
        
        # Wait until the search results container loads
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".search-results-container"))
            )
            logger.info("Search results page loaded.")
        except TimeoutException:
            logger.warning("Timeout waiting for search results container. The page might be empty or DOM changed.")
        
        self._scroll_down(scroll_pause_time, max_scrolls)
        # Save raw HTML to debug directory to check LinkedIn's response DOM
        import os
        debug_path = os.path.join("debug", f"search_{keyword.replace(' ', '_')}.html")
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(self.driver.page_source)
        logger.info(f"Saved raw page source to {debug_path}")
        
        # Return the page source for extraction
        return self.driver.page_source

    def _scroll_down(self, scroll_pause_time, max_scrolls):
        """Scroll down smoothly to load dynamic content."""
        logger.info(f"Scrolling down {max_scrolls} times to load posts...")
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        for i in range(max_scrolls):
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Wait to load page
            time.sleep(scroll_pause_time)
            
            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                # Try clicking "Show more results" if it exists
                try:
                    show_more_btn = self.driver.find_element(By.XPATH, "//button[contains(@class, 'artdeco-button') and contains(span, 'Show more')]")
                    self.driver.execute_script("arguments[0].scrollIntoView();", show_more_btn)
                    time.sleep(1)
                    show_more_btn.click()
                    time.sleep(scroll_pause_time)
                except NoSuchElementException:
                    logger.info("Reached the end of the page or no 'Show more' button found.")
                    break
            last_height = new_height
        logger.info("Finished scrolling.")
