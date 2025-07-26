from dotenv import load_dotenv
import os
import praw

load_dotenv()

import re

def extract_tickers(text):
    pattern = r'\$[A-Z]{2,5}\b'
    matches = re.findall(pattern, text)

    cleaned_tickers = []

    for match in matches:
        if match.startswith('$'):
            match = match[1:]
    return cleaned_tickers


reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

subreddit = reddit.subreddit("pennystocks")

for post in subreddit.hot(limit=25):
    title = post.title
    tickers = extract_tickers(title)

    if len(tickers) > 0:
        print("Title:", title)
        print("Extracted tickers:")

        for ticker in tickers:
            print("-", ticker)

        print("-" * 40)  

