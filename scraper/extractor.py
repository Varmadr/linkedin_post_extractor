from bs4 import BeautifulSoup
import re
import logging

logger = logging.getLogger(__name__)

class LinkedInExtractor:
    def __init__(self, html_source):
        self.soup = BeautifulSoup(html_source, 'html.parser')

    def extract_posts(self):
        """
        Parses the DOM and extracts LinkedIn posts.
        Returns a list of dictionaries with author, date, text, and URL.
        """
        posts_data = []
        
        # LinkedIn uses several classes for a post. The most recent DOM uses data-view-name="feed-full-update"
        post_elements = self.soup.find_all('div', {'data-view-name': 'feed-full-update'})
        
        if not post_elements:
            # Fallback to older known classes or attributes just in case
            post_elements = self.soup.find_all('div', {'data-urn': re.compile(r'urn:li:activity')})
        if not post_elements:
            post_elements = self.soup.find_all('div', {'data-id': re.compile(r'urn:li:activity')})
        if not post_elements:
            post_elements = self.soup.find_all('div', class_=re.compile(r'feed-shared-update-v2|occludable-update'))
            
        logger.info(f"Found {len(post_elements)} potential post elements on the page.")
        
        for post in post_elements:
            # 1. Post URL (Activity URN)
            activity_urn = post.get('data-urn', '') or post.get('data-id', '')
            post_url = "Unknown URL"
            
            # Look for a structural link that points to a specific post update
            if not activity_urn or "Unknown URL" in post_url:
                urn_link = post.find('a', href=re.compile(r'/update/urn:li:'))
                if urn_link:
                    post_url = urn_link.get('href', '').split('?')[0] # Remove tracking params
                
            if post_url == "Unknown URL" and activity_urn:
                 post_url = f"https://www.linkedin.com/feed/update/{activity_urn}/"
            
            # 2. Author Name
            # New DOM uses a span with visually-hidden or specific classes, or an aria-label on the image
            author = "Unknown Author"
            actor_link = post.find('a', {'data-view-name': 'feed-actor-image'})
            if actor_link:
                img = actor_link.find('img')
                if img and img.get('alt'):
                    author = img.get('alt').replace('View company:', '').replace('View profile:', '').strip()
            
            if author == "Unknown Author":
                 author_element = post.find('span', class_=re.compile(r'update-components-actor__name|app-shared-entity__title|actor-name'))
                 if author_element:
                     hidden_span = author_element.find('span', {'aria-hidden': 'true'})
                     if hidden_span:
                         author = hidden_span.get_text(strip=True)
                     else:
                         author = author_element.get_text(strip=True)
            
            # 3. Post Date (relative time)
            post_date = "Unknown Date"
            date_element = post.find('span', class_=re.compile(r'update-components-actor__sub-description|feed-actor-sub-description'))
            if not date_element:
                # Fallback: finding text containing a bullet point followed by a time indicator like '1d •' or '6h •'
                time_patterns = post.find_all(string=re.compile(r'\d+[hdwmy]\s*•'))
                if time_patterns:
                    post_date = time_patterns[0].strip().replace('•', '').strip()
            else:
                 hidden_span = date_element.find('span', {'aria-hidden': 'true'})
                 if hidden_span:
                     post_date = hidden_span.get_text(strip=True).replace('•', '').strip()
                 else:
                     post_date = date_element.get_text(strip=True).replace('•', '').strip()
                     
            # Clean up 'Edited' tag from date
            post_date = post_date.replace('Edited', '').strip()
                     
            # 4. Post Content
            post_content = "No Text"
            
            # Use data-testid as primary, very robust selector
            expandable_box = post.find('span', {'data-testid': 'expandable-text-box'})
            if expandable_box:
                # Try to remove '... more' button if it exists
                more_btn = expandable_box.find('button')
                if more_btn:
                    more_btn.decompose()
                post_content = expandable_box.get_text(separator=' ', strip=True)
                
            if post_content == "No Text":
                 # Fallback
                 content_element = post.find('div', {'data-view-name': 'feed-commentary'})
                 if not content_element:
                      content_element = post.find('div', class_=re.compile(r'update-components-text|feed-shared-update-v2__description|break-words'))
                      
                 if content_element:
                     more_button = content_element.find('button')
                     if more_button:
                          more_button.decompose()
                          
                     post_content = content_element.get_text(separator=' ', strip=True)
                
                
            posts_data.append({
                'author': author,
                'content': post_content,
                'published_date': post_date,
                'post_url': post_url
            })
            
        logger.info(f"Successfully extracted data for {len(posts_data)} posts.")
        return posts_data
