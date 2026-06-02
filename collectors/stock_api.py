import json
import os
import time
from datetime import datetime

import requests

import config

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def get_index_weekly_data(secid):
    """Fetch weekly kline data for an index."""
    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        "secid": secid,
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
        "klt": "101",  # daily
        "fqt": "1",
        "end": "20500101",
        "lmt": "5",  # last 5 days
    }

    # Use browser-like headers to avoid blocking
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://quote.eastmoney.com/",
    }

    try:
        r = requests.get(url, headers=headers, params=params, timeout=15)
        data = r.json()
        if data.get("data") and data["data"].get("klines"):
            klines = data["data"]["klines"]
            weekly_data = []
            for k in klines:
                parts = k.split(",")
                weekly_data.append({
                    "date": parts[0],
                    "open": float(parts[1]),
                    "close": float(parts[2]),
                    "high": float(parts[3]),
                    "low": float(parts[4]),
                    "change_pct": float(parts[8]) if parts[8] and parts[8] != "-" else 0,
                })

            # Calculate weekly summary
            if len(weekly_data) >= 2:
                first_close = weekly_data[0]["close"]
                last_close = weekly_data[-1]["close"]
                weekly_change = ((last_close - first_close) / first_close) * 100
                weekly_high = max(d["high"] for d in weekly_data)
                weekly_low = min(d["low"] for d in weekly_data)
                weekly_amplitude = ((weekly_high - weekly_low) / first_close) * 100

                return {
                    "klines": weekly_data,
                    "weekly_change": round(weekly_change, 2),
                    "weekly_high": weekly_high,
                    "weekly_low": weekly_low,
                    "weekly_amplitude": round(weekly_amplitude, 2),
                    "first_close": first_close,
                    "last_close": last_close,
                }
    except Exception as e:
        print(f"[ERROR] Failed to fetch weekly data for {secid}: {e}")

    return None


def get_index_data():
    """Fetch market index data from Eastmoney."""
    results = []
    secids = []
    name_map = {}
    for name, symbol in config.INDICES.items():
        if symbol == "^IXIC":
            secid = "100.NDX"
        elif symbol == "^GSPC":
            secid = "100.SPX"
        else:
            secid = f"100.{symbol}"
        secids.append(secid)
        name_map[secid] = name

    url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
    params = {
        "fltt": "2",
        "invt": "2",
        "fields": "f2,f3,f4,f5,f6,f7,f10,f12,f14,f15,f16,f17,f18",
        "secids": ",".join(secids),
    }

    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=10)
        data = r.json()
        if data.get("data") and data["data"].get("diff"):
            for i, item in enumerate(data["data"]["diff"]):
                secid = f"100.{item.get('f12', '')}"
                price = item.get("f2", 0)
                change_pct = item.get("f3", 0)
                change_amt = item.get("f4", 0)
                volume = item.get("f5", 0)
                amount = item.get("f6", 0)
                amplitude = item.get("f7", 0)
                volume_ratio = item.get("f10", 0)
                high = item.get("f15", 0)
                low = item.get("f16", 0)
                open_price = item.get("f17", 0)
                prev_close = item.get("f18", 0)

                if price and price != "-":
                    # Add delay between weekly data requests to avoid rate limiting
                    if i > 0:
                        time.sleep(1)
                    
                    # Fetch weekly data for this index
                    weekly = get_index_weekly_data(secid)

                    results.append({
                        "name": name_map.get(secid, item.get("f14", "")),
                        "symbol": item.get("f12", ""),
                        "price": float(price),
                        "change_pct": float(change_pct) if change_pct and change_pct != "-" else 0,
                        "change_amt": float(change_amt) if change_amt and change_amt != "-" else 0,
                        "open": float(open_price) if open_price and open_price != "-" else 0,
                        "high": float(high) if high and high != "-" else 0,
                        "low": float(low) if low and low != "-" else 0,
                        "prev_close": float(prev_close) if prev_close and prev_close != "-" else 0,
                        "volume": int(volume) if volume and volume != "-" else 0,
                        "amount": float(amount) if amount and amount != "-" else 0,
                        "amplitude": float(amplitude) if amplitude and amplitude != "-" else 0,
                        "volume_ratio": float(volume_ratio) if volume_ratio and volume_ratio != "-" else 0,
                        "weekly": weekly,
                        "time": datetime.now().isoformat(),
                    })
    except Exception as e:
        print(f"[ERROR] Failed to fetch indices: {e}")

    return results


def get_stock_data():
    """Fetch watchlist stock data from Eastmoney."""
    results = []

    symbol_map = {}
    secids = []
    for symbol in config.WATCHLIST:
        secid = f"105.{symbol}"
        secids.append(secid)
        symbol_map[secid] = symbol

    url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
    params = {
        "fltt": "2",
        "invt": "2",
        "fields": "f2,f3,f4,f5,f6,f7,f10,f12,f14,f15,f16,f17,f18",
        "secids": ",".join(secids),
    }

    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=10)
        data = r.json()
        if data.get("data") and data["data"].get("diff"):
            for item in data["data"]["diff"]:
                code = item.get("f12", "")
                price = item.get("f2", 0)
                change_pct = item.get("f3", 0)
                change_amt = item.get("f4", 0)
                volume = item.get("f5", 0)
                amount = item.get("f6", 0)
                amplitude = item.get("f7", 0)
                volume_ratio = item.get("f10", 0)
                high = item.get("f15", 0)
                low = item.get("f16", 0)
                open_price = item.get("f17", 0)
                prev_close = item.get("f18", 0)

                if price and price != "-":
                    results.append({
                        "symbol": code,
                        "name": str(item.get("f14", code)),
                        "price": float(price),
                        "change_pct": float(change_pct) if change_pct and change_pct != "-" else 0,
                        "change_amt": float(change_amt) if change_amt and change_amt != "-" else 0,
                        "open": float(open_price) if open_price and open_price != "-" else 0,
                        "high": float(high) if high and high != "-" else 0,
                        "low": float(low) if low and low != "-" else 0,
                        "prev_close": float(prev_close) if prev_close and prev_close != "-" else 0,
                        "volume": int(volume) if volume and volume != "-" else 0,
                        "amount": float(amount) if amount and amount != "-" else 0,
                        "amplitude": float(amplitude) if amplitude and amplitude != "-" else 0,
                        "volume_ratio": float(volume_ratio) if volume_ratio and volume_ratio != "-" else 0,
                        "time": datetime.now().isoformat(),
                    })
    except Exception as e:
        print(f"[ERROR] Failed to fetch stocks: {e}")

    return results


def fetch_and_save():
    """Fetch all stock data and save to JSON."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching stock data...")
    indices = get_index_data()
    stocks = get_stock_data()

    data = {
        "indices": indices,
        "stocks": stocks,
        "updated": datetime.now().isoformat(),
    }

    filepath = os.path.join(config.DATA_DIR, "stocks.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"  -> Saved {len(indices)} indices, {len(stocks)} stocks")
    return data


def load_stock_data():
    """Load cached stock data from JSON."""
    filepath = os.path.join(config.DATA_DIR, "stocks.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"indices": [], "stocks": [], "updated": "N/A"}


if __name__ == "__main__":
    fetch_and_save()
