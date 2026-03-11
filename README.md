# LinkedIn Post Extractor

An automated system to extract LinkedIn posts mentioning specific keywords within the last 6 months.

## Prerequisites
- Python 3.9+
- Google Chrome installed

## Setup Instructions

1. **Clone or navigate to the project directory**
   ```bash
   cd linkedin_post_extractor
   ```

2. **Create a virtual environment (Recommended)**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   Make a copy of `.env.example` named `.env` and fill in your LinkedIn credentials:
   ```bash
   cp .env.example .env
   ```
   Edit `.env`:
   ```env
   LINKEDIN_EMAIL=your_email@example.com
   LINKEDIN_PASSWORD=your_password
   ```

## Usage

### 1. Run the Scraper
To start the scraping process for keywords "Adya AI" and "Shayak Mazumder":
```bash
python main.py
```
*Note: This will open a Chrome browser (Selenium), log into your account, and perform searches to extract posts from the last 6 months. The data will be saved to SQLite and CSV formats in the `data/` directory.*

### 2. View the Dashboard
Once the scraping is complete, launch the Streamlit dashboard to view and filter the results:
```bash
streamlit run app.py
```

## Limitations of LinkedIn Scraping
- **Anti-Bot Mechanisms:** LinkedIn has strict anti-scraping measures. Too many requests in a short period might lead to an account restriction or CAPTCHA triggers.
- **Dynamic DOM Elements:** LinkedIn frequently changes its HTML classes and DOM structure, which may break the scraper. The scraper uses robust XPath and CSS selectors where possible, but updates might be required.
- **Rate Limits:** We use randomized sleep delays to mimic human behavior, but large volume scraping on a single account may result in temporary bans.

## Ethical Usage Note
This tool is intended for personal research, analytics, and educational use only. Automated continuous scraping without API access is against LinkedIn's Terms of Service. Please respect user privacy, rate limits, and use this tool responsibly.
