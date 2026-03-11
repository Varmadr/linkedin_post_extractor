import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LinkedInAuthenticator:
    def __init__(self, headless=False):
        self.headless = headless
        self.driver = self._setup_driver()

    def _setup_driver(self):
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
        
        # Anti-detection measures
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("window-size=1920,1080")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Execute CDP commands to mask automation
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
            """
        })
        return driver

    def login(self):
        email = os.getenv("LINKEDIN_EMAIL")
        password = os.getenv("LINKEDIN_PASSWORD")

        if not email or not password:
            raise ValueError("LinkedIn credentials not found. Please check your .env file.")

        logger.info("Navigating to LinkedIn login page...")
        self.driver.get("https://www.linkedin.com/login")
        time.sleep(3)

        try:
            # Enter email - LinkedIn sometimes uses 'username' or 'session_key'
            try:
                email_field = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.ID, "username"))
                )
            except:
                email_field = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.ID, "session_key"))
                )
            email_field.send_keys(email)
            time.sleep(1)

            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(password)
            time.sleep(1)

            # Click Login
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            logger.info("Submitted login form. Waiting for successful login...")
            
            # Wait for global navigation bar indicating successful login
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, "global-nav"))
            )
            logger.info("Successfully logged into LinkedIn.")
            return self.driver

        except Exception as e:
            logger.error(f"Login failed. Please check your credentials or if a CAPTCHA appeared. Error: {e}")
            self.driver.save_screenshot("login_error.png")
            raise e

    def close(self):
        if self.driver:
            self.driver.quit()
