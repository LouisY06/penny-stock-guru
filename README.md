# Penny Stock Recommender

With the increase in popularity of penny stocks recently, I've recognized that Reddit is a good place to start your research, analagous to using Wikapedia to learn more about a topic. This program will analyze Reddit posts and comments and assign a sentiment score to the top 10 most mentioned tickers on the subreddit r/pennystocks. I have tested this theory of only relying on sentiment score, and I have earned over $400 with a $700 initial investment.  Please do not trust this program blindly and do your own research as this is just a project to learn more about NLP libraries and various APIs. This project is a good start to introduce various high risk high potential stocks to the user, but more research should be done before investing.

## Features
- Scrapes Reddit for stock mentions and sentiment
- Calculates hype scores based on mention frequency
- Retrieves real-time stock data using Yahoo Finance
- Tracks price changes and trends
- CLI interface for quick stock analysis

## Installation
```bash
# Clone repository
git clone https://github.com/yourusername/penny-stock-guru.git
cd penny-stock-guru

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Add your Reddit API credentials to .env

Disclaimer
This tool is for educational purposes only. Always do your own research before making investment decisions. Trading penny stocks involves substantial risk of loss. 