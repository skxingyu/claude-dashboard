import config


def check_price_alerts(stocks):
    """Check if any stock has price change exceeding threshold."""
    alerts = []
    threshold = config.ALERT_THRESHOLD["price_change_pct"]

    for stock in stocks:
        change_pct = abs(stock.get("change_pct", 0))
        if change_pct >= threshold:
            direction = "上涨" if stock["change_pct"] > 0 else "下跌"
            alerts.append({
                "type": "price",
                "symbol": stock["symbol"],
                "name": stock.get("name", stock["symbol"]),
                "message": f"{stock['name']} {direction} {change_pct:.2f}%",
                "value": stock["change_pct"],
                "level": "warning" if change_pct < 5 else "danger",
            })

    return alerts


def check_volume_alerts(stocks):
    """Check for abnormal volume spikes."""
    alerts = []
    threshold = config.ALERT_THRESHOLD["volume_ratio"]

    for stock in stocks:
        volume = stock.get("volume", 0)
        if volume > 0:
            avg_volume = stock.get("avg_volume", volume)
            if avg_volume > 0:
                ratio = volume / avg_volume
                if ratio >= threshold:
                    alerts.append({
                        "type": "volume",
                        "symbol": stock["symbol"],
                        "name": stock.get("name", stock["symbol"]),
                        "message": f"{stock['name']} 成交量异常放大 {ratio:.1f}倍",
                        "value": ratio,
                        "level": "warning",
                    })

    return alerts


def analyze_news_sentiment(news_list):
    """Enhanced keyword-based sentiment analysis for financial news."""
    positive_keywords = [
        # Chinese
        "利好", "上涨", "增长", "突破", "创新高", "盈利", "超预期",
        "大涨", "反弹", "回升", "看多", "买入", "增持", "乐观",
        "强劲", "复苏", "繁荣", "牛市", "红利", "收益",
        # English
        "bullish", "surge", "rally", "gain", "rise", "up",
        "buy", "outperform", "beat", "strong", "growth",
        "record high", "all-time high", "optimistic",
    ]

    negative_keywords = [
        # Chinese
        "利空", "下跌", "暴跌", "亏损", "裁员", "下调", "风险",
        "大跌", "崩盘", "熊市", "衰退", "危机", "抛售", "减持",
        "看空", "卖出", "悲观", "疲软", "萎缩", "通胀",
        # English
        "bearish", "crash", "plunge", "drop", "fall", "down",
        "sell", "underperform", "miss", "weak", "decline",
        "recession", "crisis", "inflation", "risk",
    ]

    results = []
    for news in news_list:
        title = news.get("title", "")
        sentiment = "neutral"

        title_lower = title.lower()

        if any(kw in title_lower for kw in positive_keywords):
            sentiment = "positive"
        elif any(kw in title_lower for kw in negative_keywords):
            sentiment = "negative"

        results.append({**news, "sentiment": sentiment})

    return results


def run_analysis(stock_data, news_data):
    """Run all analyzers and return results."""
    stocks = stock_data.get("stocks", [])

    alerts = []
    alerts.extend(check_price_alerts(stocks))
    alerts.extend(check_volume_alerts(stocks))

    analyzed_news = analyze_news_sentiment(news_data)

    return {
        "alerts": alerts,
        "analyzed_news": analyzed_news,
    }
