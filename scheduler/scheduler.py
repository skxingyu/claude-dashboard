from apscheduler.schedulers.background import BackgroundScheduler

import config
from collectors.stock_api import fetch_and_save as fetch_stocks
from collectors.news_scraper import fetch_and_save as fetch_news


def create_scheduler():
    """Create and configure the background scheduler."""
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        func=fetch_stocks,
        trigger="interval",
        seconds=config.INTERVAL["stock"],
        id="stock_fetcher",
        name="Stock Data Fetcher",
        replace_existing=True,
    )

    scheduler.add_job(
        func=fetch_news,
        trigger="interval",
        seconds=config.INTERVAL["news"],
        id="news_scraper",
        name="News Scraper",
        replace_existing=True,
    )

    return scheduler


def start_scheduler():
    """Start the scheduler and run initial data fetch."""
    scheduler = create_scheduler()
    scheduler.start()
    print("[Scheduler] Started")

    fetch_stocks()
    fetch_news()

    return scheduler