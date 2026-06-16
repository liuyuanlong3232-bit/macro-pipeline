#!/usr/bin/env python3
"""
周报公共工具函数
统一管理 load/fetch_fedwatch/yahoo_quote_direct，避免各周报文件重复实现
"""
import time, random, sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import requests

DATA_DIR = Path.home() / "hermes-macro-data"
TODAY = datetime.now().strftime("%Y-%m-%d")


# ═══════ 数据加载 ═══════

def load_csv(name):
    """加载CSV数据，优先TODAY目录，回退到最近7天，最后回退到SQLite"""
    # 1. 优先今日CSV
    p = DATA_DIR / "csv" / TODAY / f"{name}.csv"
    if p.exists():
        return pd.read_csv(p)
    # 2. 回退到最近7天
    csv_root = DATA_DIR / "csv"
    if csv_root.exists():
        base = datetime.strptime(TODAY, "%Y-%m-%d")
        for i in range(1, 8):
            d = (base - timedelta(days=i)).strftime("%Y-%m-%d")
            p2 = csv_root / d / f"{name}.csv"
            if p2.exists():
                return pd.read_csv(p2)
    # 3. 最终回退到SQLite
    db_path = DATA_DIR / "hermes.db"
    if db_path.exists():
        try:
            db = sqlite3.connect(str(db_path))
            df = pd.read_sql(f'SELECT * FROM "{name}"', db)
            db.close()
            return df
        except Exception:
            pass
    return pd.DataFrame()


def load_week(name, days=7):
    """加载最近N天的CSV数据，合并为一个DataFrame"""
    base = datetime.strptime(TODAY, "%Y-%m-%d")
    frames = []
    for i in range(days):
        d = (base - timedelta(days=i)).strftime("%Y-%m-%d")
        p = DATA_DIR / "csv" / d / f"{name}.csv"
        if p.exists():
            frames.append(pd.read_csv(p))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


# ═══════ FedWatch ═══════

def fetch_fedwatch():
    """从oddpool.com API获取FedWatch FOMC利率概率
    返回: {"hold": "85.0", "cut_25": "15.0", "hike_25": "0.0"} 或 None
    """
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    base = "https://www.oddpool.com/api/events/history"
    now = datetime.now()
    # FOMC通常在月中，尝试当月和下月
    for m_offset in range(0, 2):
        m = now.month + m_offset
        y = now.year + (m - 1) // 12
        m = (m - 1) % 12 + 1
        for day in [17, 16, 18, 15, 19, 14, 20]:
            event_id = f"fomc-{y}-{m:02d}-{day:02d}"
            try:
                # 获取 hold 概率
                r = requests.get(f"{base}/no_change", params={"event_id": event_id, "hours": 1},
                                 headers=headers, timeout=10)
                if r.status_code != 200:
                    continue
                data = r.json()
                if not (data.get("kalshi") or data.get("polymarket")):
                    continue
                hold = cut_25 = hike_25 = None
                # 解析 hold
                for venue in ["kalshi", "polymarket"]:
                    items = data.get(venue, [])
                    if items:
                        p = items[-1].get("probabilities", {})
                        hold_val = p.get("no_change")
                        if hold_val is not None:
                            hold = f"{hold_val * 100:.1f}"
                        break
                # 解析 cut_25bps
                r2 = requests.get(f"{base}/cut_25bps", params={"event_id": event_id, "hours": 1},
                                  headers=headers, timeout=10)
                if r2.status_code == 200:
                    d2 = r2.json()
                    for venue in ["kalshi", "polymarket"]:
                        items = d2.get(venue, [])
                        if items:
                            p = items[-1].get("probabilities", {})
                            cut_val = p.get("cut_25bps")
                            if cut_val is not None:
                                cut_25 = f"{cut_val * 100:.1f}"
                            break
                # 解析 hike_25bps
                r3 = requests.get(f"{base}/hike_25bps", params={"event_id": event_id, "hours": 1},
                                  headers=headers, timeout=10)
                if r3.status_code == 200:
                    d3 = r3.json()
                    for venue in ["kalshi", "polymarket"]:
                        items = d3.get(venue, [])
                        if items:
                            p = items[-1].get("probabilities", {})
                            hike_val = p.get("hike_25bps")
                            if hike_val is not None:
                                hike_25 = f"{hike_val * 100:.1f}"
                            break
                # 概率校验：三者之和不应超过105%
                vals = [float(v) for v in [hold, cut_25, hike_25] if v is not None]
                if vals and sum(vals) > 105:
                    print(f"[FedWatch] 概率之和异常: {sum(vals):.1f}%, 数据丢弃")
                    return None
                return {"hold": hold, "cut_25": cut_25, "hike_25": hike_25}
            except Exception:
                continue
    return None


# ═══════ Yahoo 直连 ═══════

def yahoo_quote_direct(symbol, retries=3):
    """Yahoo Finance 直连API — CSV数据过期时的fallback
    返回: (price, prev_close, date) 或 (None, None, None)
    """
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {"range": "5d", "interval": "1d"}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=15)
            if r.status_code == 200:
                data = r.json()
                result = data["chart"]["result"][0]
                meta = result.get("meta", {})
                price = meta.get("regularMarketPrice")
                prev = meta.get("chartPreviousClose")
                return price, prev, TODAY
            elif r.status_code == 429:
                time.sleep((2 ** attempt) + random.random() * 2)
            else:
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        except Exception:
            time.sleep(2 ** attempt)
    return None, None, None
