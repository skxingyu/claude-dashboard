# Finance Monitor

A local financial dashboard for monitoring US stocks and market indices, built with Python + Flask.

## Features

- Real-time market index tracking (NASDAQ, S&P 500)
- Custom watchlist for individual stocks
- Automated news scraping with keyword filtering
- Institutional news detection
- Price and volume alert system
- Light-themed responsive UI

## Quick Start

```bash
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Project Structure

```
finance-monitor/
├── app.py                  # Flask entry point
├── config.py               # Watchlist, alerts, intervals
├── requirements.txt        # Dependencies
├── collectors/
│   ├── stock_api.py        # Eastmoney API for stock/index data
│   └── news_scraper.py     # Sina, Eastmoney, CNBC, Seeking Alpha
├── analyzers/
│   └── analyzer.py         # Price/volume alerts, sentiment analysis
├── scheduler/
│   └── scheduler.py        # APScheduler for periodic data collection
├── templates/
│   └── dashboard.html      # Dashboard UI
└── data/                   # JSON cache (gitignored)
```

## Tech Stack

- Python 3.10+
- Flask
- BeautifulSoup4
- APScheduler
- requests / lxml

## License

MIT
