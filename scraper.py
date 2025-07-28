from dotenv import load_dotenv
import os
import praw
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import yfinance as yf
import time

load_dotenv()
analyzer = SentimentIntensityAnalyzer()

# Extend VADER sentiment with stock-related keywords/emojis
analyzer.lexicon.update({
    "🚀": 3.0,
    "moon": 2.5,
    "💎": 2.0,
    "💰": 2.5,
    "🔥": 2.0,
    "bag": -2.0,       # as in "bagholder"
    "insane": 2.0,
    "momentum": 1.5,
    "mooning": 3.0,
    "squeeze": 2.0,
    "running": 1.5,
    "exploding": 2.5
})

# Function to extract tickers from a given text
def extract_tickers(text):
    pattern = r'\$[A-Z]{2,5}\b'
    matches = re.findall(pattern, text)

    extracted = []

    for match in matches:
        if match.startswith('$'):
            match = match[1:]
        extracted.append(match)

    return extracted

# Function to load valid ticker symbols from a Nasdaq file
def load_ticker_list(file_path):
    ticker_set = set()

    with open(file_path, "r") as file:
        next(file)  # skip header

        for line in file:
            parts = line.strip().split("|")

            if len(parts) > 0:
                symbol = parts[0].strip().upper()

                if symbol:
                    ticker_set.add(symbol)

    return ticker_set

# Load valid tickers once at the start
valid_tickers = load_ticker_list("./files/nasdaqlisted.txt")

# Main function that scrapes Reddit and returns hyped tickers
def get_top_hyped_tickers(limit=10):
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT")
    )

    subreddit = reddit.subreddit("pennystocks")
    ticker_scores = {}

    for post in subreddit.hot(limit=10):
        time.sleep(1)

        title_tickers = extract_tickers(post.title)

        for ticker in title_tickers:
            if ticker in valid_tickers:
                if ticker not in ticker_scores:
                    ticker_scores[ticker] = {"mentions": 1, "hype": 0.0}
                else:
                    ticker_scores[ticker]["mentions"] += 1

        post.comments.replace_more(limit=0)
        all_comments = post.comments.list()

        for comment in all_comments:
            text = comment.body
            tickers = extract_tickers(text)

            if not tickers:
                continue

            score = analyzer.polarity_scores(text)["compound"]

            for ticker in tickers:
                if ticker in valid_tickers:
                    if ticker not in ticker_scores:
                        ticker_scores[ticker] = {"mentions": 1, "hype": score}
                    else:
                        ticker_scores[ticker]["mentions"] += 1
                        ticker_scores[ticker]["hype"] += score

    sorted_tickers = sorted(ticker_scores.items(), key=lambda item: item[1]["mentions"],reverse=True)

    result = []

    for ticker, data in sorted_tickers[:limit]:
        stock = yf.Ticker(ticker)
        current_price = stock.info["currentPrice"]

        history = stock.history(period="1mo")

        week_ago_price = history['Close'].iloc[-6]
        month_ago_price = history['Close'].iloc[0]

        change_1w = ((current_price - week_ago_price) / week_ago_price) * 100
        change_1mo = ((current_price - month_ago_price) / month_ago_price) * 100

        if change_1mo > 5:
            trend = "Up"
        elif change_1mo < -5:
            trend = "Down"
        else:
            trend = "Flat"

        result.append({
            "ticker": ticker,
            "mentions": data["mentions"],
            "hype_score": round(data["hype"], 3),
            "current_price": current_price,
            "change_1w": round(change_1w, 2),
            "change_1mo": round(change_1mo, 2),
            "trend": trend
        })

    return result

if __name__ == "__main__":
    results = get_top_hyped_tickers(limit=10)
    for stock in results:
        print(f"\nTicker: {stock['ticker']}")
        print(f"Mentions: {stock['mentions']}")
        print(f"Hype Score: {stock['hype_score']}")
        print(f"Price: ${stock['current_price']:.2f}")
        print(f"1 Week Change: {stock['change_1w']}%")
        print(f"1 Month Change: {stock['change_1mo']}%")
        print(f"Trend: {stock['trend']}")
        print("-" * 40)