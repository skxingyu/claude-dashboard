# Monitor list - stocks to track
WATCHLIST = ["AAPL", "MSFT", "NVDA", "GOOGL", "META", "TSLA"]

# Market indices (Eastmoney codes: NDX=纳斯达克, SPX=标普500)
INDICES = {
    "NASDAQ": "^IXIC",
    "S&P500": "^GSPC",
}

# Alert thresholds
ALERT_THRESHOLD = {
    "price_change_pct": 3.0,    # Alert if price changes > 3%
    "volume_ratio": 2.0,        # Alert if volume > 2x average
}

# Collection intervals (seconds)
INTERVAL = {
    "stock": 300,       # Stock data: every 5 min
    "news": 1800,       # News: every 30 min
}

# News keywords filter
NEWS_KEYWORDS = [
    "AI", "人工智能", "半导体", "芯片", "GPU",
    "科技", "纳指", "标普", "美股", "特斯拉",
    "苹果", "英伟达", "谷歌", "Meta", "微软",
]

# Institutional news keywords (international investment banks, research firms)
INSTITUTIONAL_KEYWORDS = [
    # Investment Banks - English names
    "Goldman Sachs", "JPMorgan", "Morgan Stanley", "Citigroup",
    "UBS", "Barclays", "Deutsche Bank", "Bank of America", "BofA",
    "Credit Suisse", "Wells Fargo", "HSBC", "BNP Paribas", "Societe Generale",
    "Jefferies", "Evercore", "Lazard", "Moelis", "PJT Partners",
    # Asset Management
    "BlackRock", "Vanguard", "Fidelity", "PIMCO", "T. Rowe Price",
    "Bridgewater", "Renaissance Technologies", "Two Sigma", "Citadel",
    "AQR Capital", "Millennium Management", "Point72", "DE Shaw",
    # Private Equity
    "Blackstone", "KKR", "Apollo", "Carlyle", "Warburg Pincus",
    "TPG", "Silver Lake", "Vista Equity", "Thoma Bravo",
    # Rating Agencies
    "S&P Global", "Moody's", "Fitch Ratings",
    # Central Banks
    "Federal Reserve", "Fed", "ECB", "Bank of Japan", "BOJ",
    "Bank of England", "BOE", "People's Bank of China", "PBOC",
    # Research & Analytics
    "Bloomberg", "Reuters", "Morningstar", "CFRA", "Argus Research",
    "Zacks", "Seeking Alpha", "The Motley Fool",
]

# Flask config
HOST = "127.0.0.1"
PORT = 5000
DEBUG = True

# Data storage path
DATA_DIR = "data"
