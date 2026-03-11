import logging
logging.basicConfig(level=logging.INFO)
from scraper.extractor import LinkedInExtractor

with open('debug/search_Adya_AI.html', 'r', encoding='utf-8') as f:
    html = f.read()

ex = LinkedInExtractor(html)
posts = ex.extract_posts()
print(f'Extracted {len(posts)} posts')
if posts:
    print('First post:', posts[0])
