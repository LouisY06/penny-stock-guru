from dotenv import load_dotenv
import os
import praw
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import yfinance as yf
import time
import pandas as pd

load_dotenv()
analyzer = SentimentIntensityAnalyzer()
#rockets mean the commenter believes that it's going to rise soon
analyzer.lexicon["🚀"] = 3.0
analyzer.lexicon["moon"] = 2.5
analyzer.lexicon["💎"] = 2.0
analyzer.lexicon["💰"] = 2.5
analyzer.lexicon["🔥"] = 2.0
analyzer.lexicon["bag"] = -2.0  # as in "bagholder"
analyzer.lexicon["insane"] = 2.0
analyzer.lexicon["momentum"] = 1.5
analyzer.lexicon["mooning"] = 3.0
analyzer.lexicon["squeeze"] = 2.0
analyzer.lexicon["running"] = 1.5
analyzer.lexicon["exploding"] = 2.5

# Extract tickers from a given string of text
def extract_tickers(text):
    pattern = r'\$[A-Z]{2,5}\b'
    matches = re.findall(pattern, text)

    cleaned_tickers = []

    for match in matches:
        if match.startswith('$'):
            match = match[1:]

        cleaned_tickers.append(match)

    return cleaned_tickers

# Load the list of valid tickers from the Nasdaq file
def load_ticker_list(file_path):
    ticker_set = set()

    with open(file_path, "r") as file:
        next(file)  # Skip header line

        for line in file:
            parts = line.strip().split("|")

            if len(parts) > 0:
                symbol = parts[0].upper()

                if symbol != "":
                    ticker_set.add(symbol)

    return ticker_set

# Load the valid tickers only once
valid_tickers = load_ticker_list("./files/nasdaqlisted.txt")

# Set up PRAW (Reddit API)
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

# Select subreddit and prepare ticker count dictionary
subreddit = reddit.subreddit("pennystocks")

ticker_scores = {}
ticker_counts = {}

for post in subreddit.hot(limit=10):
    time.sleep(2)
    title = post.title
    tickers_in_title = extract_tickers(title)

    for ticker in tickers_in_title:
        if ticker in valid_tickers:
            if ticker not in ticker_scores:
                ticker_scores[ticker] = {"mentions": 1, "hype": 0.0}
            else:
                ticker_scores[ticker]["mentions"] += 1

    # Load all comments
    post.comments.replace_more(limit=0)
    all_comments = post.comments.list()

    for comment in all_comments:
        text = comment.body
        tickers_in_comment = extract_tickers(text)

        if len(tickers_in_comment) > 0:
            sentiment = analyzer.polarity_scores(text)
            compound_score = sentiment["compound"]

            for ticker in tickers_in_comment:
                if ticker in valid_tickers:
                    if ticker not in ticker_scores:
                        ticker_scores[ticker] = {"mentions": 1, "hype": compound_score}
                    else:
                        ticker_scores[ticker]["mentions"] += 1
                        ticker_scores[ticker]["hype"] += compound_score
            #just for debugging, making sure vader was working properly

            #print("Comment:")
            #print(text)
            #print("Hype Score:", round(compound_score, 3))
            #print("Tickers Found:", tickers_in_comment)
            #print("-" * 60)

    for ticker in tickers_in_comment:
        if ticker in valid_tickers:
            if ticker not in ticker_scores:
                ticker_scores[ticker] = {"mentions": 1, "hype": compound_score}
            else:
                ticker_scores[ticker]["mentions"] += 1
                ticker_scores[ticker]["hype"] += compound_score

        if len(tickers_in_comment) > 0:
            sentiment = analyzer.polarity_scores(text)
            compound_score = sentiment["compound"]

            for ticker in tickers_in_comment:
                if ticker in valid_tickers:
                    if ticker not in ticker_scores:
                        ticker_scores[ticker] = {"mentions": 1, "hype": compound_score}
                    else:
                        ticker_scores[ticker]["mentions"] += 1
                        ticker_scores[ticker]["hype"] += compound_score

# Display the ticker counts, sorted by frequency
print("Ticker Sentiment Summary:")
print("-" * 40)
sorted_ticker = sorted(ticker_scores.items(), key=lambda x: x[1]["mentions"], reverse=True)
rows = []
i = 0
for ticker, data in sorted_ticker:
    if i == 10:
        break

    mentions = data["mentions"]
    hype = round(data["hype"], 3)

    try:
        tkr = yf.Ticker(ticker)
        current_price = tkr.info.get("currentPrice", None)

        hist = tkr.history(period="1mo")
        if len(hist) >= 6:
            week_ago_price = hist['Close'].iloc[-6]  # 5 trading days ago
            month_ago_price = hist['Close'].iloc[0]

            week_change = ((current_price - week_ago_price) / week_ago_price) * 100
            month_change = ((current_price - month_ago_price) / month_ago_price) * 100

            # determine trend
            if month_change > 5:
                trend = "Up"
            elif month_change < -5:
                trend = "Down"
            else:
                trend = "Flat"

            print(f"{ticker}: {mentions} mentions | Hype Score: {hype} | Current: {current_price}")
            print(f"  - 1W change: {week_change:.2f}% | 1M change: {month_change:.2f}% | Trend: {trend}")
            print("-" * 60)

        else:
            print(f"{ticker}: {mentions} mentions | Hype Score: {hype} | Not enough historical data.")
            print("-" * 60)

    except Exception as e:
        print(f"{ticker}: Error fetching data — {e}")
        print("-" * 60)

    i += 1