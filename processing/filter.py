import datetime
import re
from dateutil.relativedelta import relativedelta

def parse_linkedin_date(date_str):
    """
    Parses LinkedIn relative date strings like '2h', '1w', '3mo', '1yr'
    and returns an approximate datetime object.
    If the format is unrecognized, returns datetime.now().
    """
    now = datetime.datetime.now()
    
    # Extract number and unit
    match = re.match(r'(\d+)([a-zA-Z]+)', date_str)
    if not match:
        return now
        
    value = int(match.group(1))
    unit = match.group(2).lower()
    
    if unit in ['s', 'sec', 'secs']:
        return now - relativedelta(seconds=value)
    elif unit in ['m', 'min', 'mins']:
        return now - relativedelta(minutes=value)
    elif unit in ['h', 'hr', 'hrs']:
        return now - relativedelta(hours=value)
    elif unit in ['d', 'day', 'days']:
        return now - relativedelta(days=value)
    elif unit in ['w', 'wk', 'wks']:
        return now - relativedelta(weeks=value)
    elif unit in ['mo', 'mos', 'month', 'months']:
        return now - relativedelta(months=value)
    elif unit in ['y', 'yr', 'yrs', 'year', 'years']:
        return now - relativedelta(years=value)
        
    return now

def is_within_last_6_months(date_str):
    """
    Checks if the LinkedIn relative date string falls within the last 6 months.
    """
    post_date = parse_linkedin_date(date_str)
    six_months_ago = datetime.datetime.now() - relativedelta(months=6)
    return post_date >= six_months_ago

def filter_posts_by_date(posts):
    """
    Takes a list of post dictionaries and returns only those within 6 months.
    """
    filtered = []
    for post in posts:
        date_str = post.get('published_date', '')
        if is_within_last_6_months(date_str):
            filtered.append(post)
    return filtered
