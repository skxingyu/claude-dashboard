import json
import os
from datetime import datetime

import requests
from bs4 import BeautifulSoup

import config


def is_institutional_news(title):
    """Check if news is from or about major international institutions."""
    return any(kw in title for kw in config.INSTITUTIONAL_KEYWORDS)


def scrape_sina_finance():
    """Scrape US stock news from Sina Finance."""
    url = "https://finance.sina.com.cn/stock/usstock/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    news_list = []

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")

        links = soup.select("a[href]")
        for link in links:
            title = link.get_text(strip=True)
            href = link.get("href", "")

            if not title or len(title) < 8:
                continue
            if "stock" not in href and "finance" not in href:
                continue

            # Check if it matches general keywords or institutional keywords
            if any(kw in title for kw in config.NEWS_KEYWORDS) or is_institutional_news(title):
                news_list.append({
                    "title": title,
                    "url": href,
                    "source": "新浪财经",
                    "is_institutional": is_institutional_news(title),
                    "time": datetime.now().isoformat(),
                })

    except Exception as e:
        print(f"[ERROR] Failed to scrape Sina Finance: {e}")

    return news_list[:30]


def scrape_eastmoney():
    """Scrape news from Eastmoney US stock section."""
    url = "https://stock.eastmoney.com/us.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    news_list = []

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")

        items = soup.select("a[href]")
        for item in items:
            title = item.get_text(strip=True)
            href = item.get("href", "")

            if not title or len(title) < 8:
                continue

            # Check if it matches general keywords or institutional keywords
            if any(kw in title for kw in config.NEWS_KEYWORDS) or is_institutional_news(title):
                news_list.append({
                    "title": title,
                    "url": href,
                    "source": "东方财富",
                    "is_institutional": is_institutional_news(title),
                    "time": datetime.now().isoformat(),
                })

    except Exception as e:
        print(f"[ERROR] Failed to scrape Eastmoney: {e}")

    return news_list[:30]


def scrape_cnbc():
    """Scrape institutional news from CNBC."""
    url = "https://www.cnbc.com/markets/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    news_list = []

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")

        links = soup.select("a[href]")
        for link in links:
            title = link.get_text(strip=True)
            href = link.get("href", "")

            if not title or len(title) < 20:
                continue

            # Make sure it's a CNBC link
            if not href.startswith("https://www.cnbc.com"):
                continue

            # Check if it's institutional news
            if is_institutional_news(title):
                news_list.append({
                    "title": title,
                    "url": href,
                    "source": "CNBC",
                    "is_institutional": True,
                    "time": datetime.now().isoformat(),
                })

    except Exception as e:
        print(f"[ERROR] Failed to scrape CNBC: {e}")

    return news_list[:20]


def scrape_seeking_alpha():
    """Scrape institutional research from Seeking Alpha."""
    url = "https://seekingalpha.com/market-news"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    news_list = []

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")

        links = soup.select("a[href]")
        for link in links:
            title = link.get_text(strip=True)
            href = link.get("href", "")

            if not title or len(title) < 20:
                continue

            # Make sure it's a Seeking Alpha link
            if not href.startswith("/news/") and not href.startswith("https://seekingalpha.com/news/"):
                continue

            # Check if it's institutional news
            if is_institutional_news(title):
                # Fix relative URLs
                if href.startswith("/"):
                    href = "https://seekingalpha.com" + href
                
                news_list.append({
                    "title": title,
                    "url": href,
                    "source": "Seeking Alpha",
                    "is_institutional": True,
                    "time": datetime.now().isoformat(),
                })

    except Exception as e:
        print(f"[ERROR] Failed to scrape Seeking Alpha: {e}")

    return news_list[:20]


def fetch_and_save():
    """Fetch news from all sources and save."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching news...")

    all_news = []
    all_news.extend(scrape_sina_finance())
    all_news.extend(scrape_eastmoney())
    all_news.extend(scrape_cnbc())
    all_news.extend(scrape_seeking_alpha())

    seen = set()
    unique_news = []
    for item in all_news:
        if item["title"] not in seen:
            seen.add(item["title"])
            unique_news.append(item)

    # Sort: institutional news first, then by time
    unique_news.sort(key=lambda x: (not x.get("is_institutional", False), x["time"]), reverse=False)

    filepath = os.path.join(config.DATA_DIR, "news.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(unique_news, f, ensure_ascii=False, indent=2)

    institutional_count = sum(1 for n in unique_news if n.get("is_institutional"))
    print(f"  -> Saved {len(unique_news)} news items ({institutional_count} institutional)")
    return unique_news


def load_news_data():
    """Load cached news data."""
    filepath = os.path.join(config.DATA_DIR, "news.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


if __name__ == "__main__":
    fetch_and_save()
