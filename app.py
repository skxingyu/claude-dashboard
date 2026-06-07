import os

from flask import Flask, render_template

import config
from collectors.stock_api import load_stock_data
from collectors.news_scraper import load_news_data
from analyzers.analyzer import run_analysis
from scheduler.scheduler import start_scheduler

app = Flask(__name__)


@app.route("/")
def dashboard():
    stock_data = load_stock_data()
    news_data = load_news_data()
    analysis = run_analysis(stock_data, news_data)

    return render_template(
        "dashboard.html",
        data=stock_data,
        news=analysis["analyzed_news"],
        alerts=analysis["alerts"],
        volatility_alerts=analysis["volatility_alerts"],
        market_sentiment=analysis["market_sentiment"],
    )


@app.route("/api/stocks")
def api_stocks():
    return load_stock_data()


@app.route("/api/news")
def api_news():
    return load_news_data()


if __name__ == "__main__":
    os.makedirs(config.DATA_DIR, exist_ok=True)
    scheduler = start_scheduler()
    print(f"\n[Finance Monitor] Running at http://{config.HOST}:{config.PORT}\n")
    try:
        app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
    finally:
        scheduler.shutdown()
