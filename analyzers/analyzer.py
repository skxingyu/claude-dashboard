import config


def check_price_alerts(stocks):
    """Check if any stock has price change exceeding threshold."""
    alerts = []
    threshold = config.ALERT_THRESHOLD["price_change_pct"]

    for stock in stocks:
        change_pct = abs(stock.get("change_pct", 0))
        if change_pct >= threshold:
            direction = "上涨" if stock["change_pct"] > 0 else "下跌"
            alerts.append(
                {
                    "type": "price",
                    "symbol": stock["symbol"],
                    "name": stock.get("name", stock["symbol"]),
                    "message": f"{stock['name']} {direction} {change_pct:.2f}%",
                    "value": stock["change_pct"],
                    "level": "warning" if change_pct < 5 else "danger",
                }
            )

    return alerts


def check_volume_alerts(stocks):
    """Check for abnormal volume spikes using API-provided volume_ratio."""
    alerts = []
    threshold = config.ALERT_THRESHOLD["volume_ratio"]

    for stock in stocks:
        ratio = stock.get("volume_ratio", 0)
        if ratio >= threshold:
            alerts.append(
                {
                    "type": "volume",
                    "symbol": stock["symbol"],
                    "name": stock.get("name", stock["symbol"]),
                    "message": f"{stock['name']} 成交量异常放大 {ratio:.1f}倍",
                    "value": ratio,
                    "level": "warning",
                }
            )

    return alerts


def analyze_volatility(indices):
    """Analyze index volatility based on weekly kline data.

    Rules:
    - Single day change > 3%: "异常波动" alert
    - Single day change > 2%: attention notice
    - 3+ consecutive days with change > 1.3%: attention notice
    """
    alerts = []

    for idx in indices:
        name = idx.get("name", "")
        weekly = idx.get("weekly")
        if not weekly or not weekly.get("klines"):
            continue

        klines = weekly["klines"]

        # Check each day's change
        for k in klines:
            pct = abs(k.get("change_pct", 0))
            date = k.get("date", "")
            direction = "上涨" if k["change_pct"] > 0 else "下跌"

            if pct > 3:
                alerts.append({
                    "level": "danger",
                    "index": name,
                    "date": date,
                    "message": f"⚠️ {name} 异常波动：{direction} {pct:.2f}%",
                    "type": "abnormal",
                    "value": k["change_pct"],
                })
            elif pct > 2:
                alerts.append({
                    "level": "warning",
                    "index": name,
                    "date": date,
                    "message": f"{name} 大幅波动：{direction} {pct:.2f}%",
                    "type": "attention",
                    "value": k["change_pct"],
                })

        # Check 3+ consecutive days > 1.3%
        if len(klines) >= 3:
            for i in range(len(klines) - 2):
                window = klines[i:i + 3]
                if all(abs(k.get("change_pct", 0)) > 1.3 for k in window):
                    avg_pct = sum(k["change_pct"] for k in window) / 3
                    direction = "上涨" if avg_pct > 0 else "下跌"
                    dates = f"{window[0]['date']}~{window[-1]['date']}"
                    alerts.append({
                        "level": "warning",
                        "index": name,
                        "date": dates,
                        "message": f"{name} 连续3日剧烈波动（{dates}），平均{direction} {abs(avg_pct):.2f}%",
                        "type": "consecutive",
                        "value": avg_pct,
                    })
                    break  # Only report once per index

    return alerts


def analyze_market_sentiment(indices, analyzed_news):
    """Rule-based market sentiment analysis combining index trends and news.

    Returns structured analysis with bullish/bearish factors and outlook.
    """
    bullish_factors = []
    bearish_factors = []

    # --- Index Trend Analysis ---
    up_count = 0
    down_count = 0
    weekly_up = 0
    weekly_down = 0

    for idx in indices:
        name = idx.get("name", "")
        change_pct = idx.get("change_pct", 0)
        weekly = idx.get("weekly")

        # Daily trend
        if change_pct > 0.5:
            up_count += 1
        elif change_pct < -0.5:
            down_count += 1

        # Weekly trend
        if weekly:
            wc = weekly.get("weekly_change", 0)
            if wc > 1:
                weekly_up += 1
            elif wc < -1:
                weekly_down += 1

    idx_count = len(indices) or 1

    # Aggregate daily signals
    if up_count >= 2:
        bullish_factors.append(f"多数指数今日上涨（{up_count}/{idx_count}），市场整体偏强")
    if down_count >= 2:
        bearish_factors.append(f"多数指数今日下跌（{down_count}/{idx_count}），市场承压")
    if up_count >= 2 and weekly_up >= 2:
        bullish_factors.append("日线与周线共振上涨，短期动能强劲")
    if down_count >= 2 and weekly_down >= 2:
        bearish_factors.append("日线与周线共振下跌，短期下行风险加大")

    # Large single-day moves
    for idx in indices:
        pct = abs(idx.get("change_pct", 0))
        name = idx.get("name", "")
        if pct > 3:
            if idx["change_pct"] > 0:
                bullish_factors.append(f"{name} 单日大涨 {pct:.2f}%，市场情绪亢奋")
            else:
                bearish_factors.append(f"{name} 单日大跌 {pct:.2f}%，市场恐慌情绪蔓延")
        elif pct > 2:
            if idx["change_pct"] > 0:
                bullish_factors.append(f"{name} 涨幅 {pct:.2f}%，买方力量较强")
            else:
                bearish_factors.append(f"{name} 跌幅 {pct:.2f}%，卖方压力明显")

    # --- News Sentiment Analysis ---
    pos_count = sum(1 for n in analyzed_news if n.get("sentiment") == "positive")
    neg_count = sum(1 for n in analyzed_news if n.get("sentiment") == "negative")
    inst_news = [n for n in analyzed_news if n.get("is_institutional")]
    inst_pos = sum(1 for n in inst_news if n.get("sentiment") == "positive")
    inst_neg = sum(1 for n in inst_news if n.get("sentiment") == "negative")

    total = len(analyzed_news) or 1

    if pos_count > neg_count * 1.5:
        bullish_factors.append(f"新闻面偏多：利好 {pos_count} 条 vs 利空 {neg_count} 条")
    elif neg_count > pos_count * 1.5:
        bearish_factors.append(f"新闻面偏空：利空 {neg_count} 条 vs 利好 {pos_count} 条")
    elif pos_count > 0 and neg_count > 0:
        bullish_factors.append(f"新闻面多空交织：利好 {pos_count} 条 / 利空 {neg_count} 条")
        bearish_factors.append(f"新闻面多空交织：利好 {pos_count} 条 / 利空 {neg_count} 条")

    # Institutional signals
    if inst_pos > inst_neg:
        bullish_factors.append(f"机构观点偏乐观（看多 {inst_pos} / 看空 {inst_neg}）")
    elif inst_neg > inst_pos:
        bearish_factors.append(f"机构观点偏谨慎（看空 {inst_neg} / 看多 {inst_pos}）")

    # Extract key institutional headlines
    for n in inst_news[:5]:
        title = n.get("title", "")
        if n.get("sentiment") == "positive":
            bullish_factors.append(f"[机构] {title[:60]}")
        elif n.get("sentiment") == "negative":
            bearish_factors.append(f"[机构] {title[:60]}")

    # --- Determine Overall Trend ---
    bull_score = len(bullish_factors)
    bear_score = len(bearish_factors)

    if bull_score > bear_score + 1:
        trend = "bullish"
    elif bear_score > bull_score + 1:
        trend = "bearish"
    else:
        trend = "mixed"

    # --- Short-term Outlook (1-3 days) ---
    short_factors = []
    for idx in indices:
        name = idx.get("name", "")
        pct = idx.get("change_pct", 0)
        if abs(pct) > 2:
            short_factors.append(f"{name} {'反弹' if pct > 0 else '调整'} {abs(pct):.2f}%")

    if pos_count > neg_count:
        short_factors.append("当日新闻情绪偏正面")
    elif neg_count > pos_count:
        short_factors.append("当日新闻情绪偏负面")

    if trend == "bullish":
        short_outlook = "短期偏乐观，关注能否延续上涨动能"
    elif trend == "bearish":
        short_outlook = "短期偏谨慎，注意下行风险和支撑位"
    else:
        short_outlook = "短期方向不明，建议观望等待明确信号"

    # --- Long-term Outlook ---
    long_factors = []
    if weekly_up >= 2:
        long_factors.append("多数指数周线收涨，中期趋势向好")
    elif weekly_down >= 2:
        long_factors.append("多数指数周线收跌，中期承压")
    else:
        long_factors.append("指数周线分化，中期方向待确认")

    if inst_pos > inst_neg:
        long_factors.append("机构中长期观点偏积极")
    elif inst_neg > inst_pos:
        long_factors.append("机构中长期观点偏保守")

    if trend == "bullish":
        long_outlook = "中长期偏乐观，但需关注宏观政策变化"
    elif trend == "bearish":
        long_outlook = "中长期偏悲观，建议控制仓位、关注避险资产"
    else:
        long_outlook = "中长期前景不确定，建议分散配置、等待趋势明朗"

    return {
        "trend": trend,
        "bullish_factors": bullish_factors if bullish_factors else ["暂无明显利好信号"],
        "bearish_factors": bearish_factors if bearish_factors else ["暂无明显利空信号"],
        "short_term": {
            "outlook": short_outlook,
            "factors": short_factors if short_factors else ["市场波动较小"],
        },
        "long_term": {
            "outlook": long_outlook,
            "factors": long_factors,
        },
        "stats": {
            "positive_news": pos_count,
            "negative_news": neg_count,
            "neutral_news": total - pos_count - neg_count,
            "institutional_news": len(inst_news),
        },
    }


def analyze_news_sentiment(news_list):
    """Enhanced keyword-based sentiment analysis for financial news."""
    positive_keywords = [
        "利好", "上涨", "增长", "突破", "创新高", "盈利", "超预期",
        "大涨", "反弹", "回升", "看多", "买入", "增持", "乐观",
        "强劲", "复苏", "繁荣", "牛市", "红利", "收益",
        "bullish", "surge", "rally", "gain", "rise", "up", "buy",
        "outperform", "beat", "strong", "growth", "record high",
        "all-time high", "optimistic",
    ]

    negative_keywords = [
        "利空", "下跌", "暴跌", "亏损", "裁员", "下调", "风险",
        "大跌", "崩盘", "熊市", "衰退", "危机", "抛售", "减持",
        "看空", "卖出", "悲观", "疲软", "萎缩", "通胀",
        "bearish", "crash", "plunge", "drop", "fall", "down", "sell",
        "underperform", "miss", "weak", "decline", "recession",
        "crisis", "inflation", "risk",
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
    indices = stock_data.get("indices", [])

    alerts = []
    alerts.extend(check_price_alerts(stocks))
    alerts.extend(check_volume_alerts(stocks))

    # Volatility analysis on indices
    volatility_alerts = analyze_volatility(indices)

    analyzed_news = analyze_news_sentiment(news_data)

    # Market sentiment analysis
    market_sentiment = analyze_market_sentiment(indices, analyzed_news)

    return {
        "alerts": alerts,
        "analyzed_news": analyzed_news,
        "volatility_alerts": volatility_alerts,
        "market_sentiment": market_sentiment,
    }
