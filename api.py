from flask import Flask, jsonify
from scraper import get_top_hyped_tickers  
app = Flask(__name__)

@app.route("/api/hype")
def hype_route():
    data = get_top_hyped_tickers(limit=10)
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True, port=5000)