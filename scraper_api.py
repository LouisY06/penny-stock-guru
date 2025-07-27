from flask import Flask, jsonify
from scraper import get_top_hyped_tickers  # you write this function

app = Flask(__name__)

@app.route("/api/hype")
def hype():
    return jsonify(get_top_hyped_tickers())

if __name__ == "__main__":
    app.run(port=5000)