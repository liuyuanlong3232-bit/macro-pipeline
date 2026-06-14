#!/usr/bin/env python3
"""
宏觀期貨數據採集流水線 (Macro Futures Data Pipeline)
=====================================================
每日定時抓取 10 個數據源，存為結構化 JSON + CSV 文件。

數據源：
  1. FRED       — 美聯儲經濟數據 (利率、CPI、GDP、就業)
  2. Alpha Vantage — 股票/外匯/商品價格
  3. NewsAPI    — 全球財經新聞
  4. OpenWeather — 天氣 (影響農產品/能源)
  5. Japan e-Stat — 日本政府統計
  6. EIA        — 美國能源信息 (原油、天然氣、庫存)
  7. USDA NASS  — 美國農業統計
  8. CFTC COT   — 持倉報告 (黃金/白銀/原油)
  9. Finnhub    — 經濟日曆/預測值
  10. AGSI+     — 歐洲天然氣庫存 (GIE)

用法:
  python macro_pipeline.py               # 抓取所有數據源
  python macro_pipeline.py --source fred  # 只抓某個源
  python macro_pipeline.py --report       # 生成每日摘要報告
"""

import os
import sys
import json
import csv
import time
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import requests
import pandas as pd
from dotenv import load_dotenv

# ─── 配置 ───────────────────────────────────────────────────
ENV_PATH = Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))) / ".env"
load_dotenv(ENV_PATH, override=True)

# 强制从.env文件读取API key（覆盖可能残留的旧环境变量）
def _load_env_key(key_name):
    """从.env文件直接读取key值，确保不受环境变量污染"""
    try:
        with open(ENV_PATH) as f:
            for line in f:
                line = line.strip()
                if line.startswith(f"{key_name}=") and not line.startswith("#"):
                    return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return os.getenv(key_name, "")

FRED_API_KEY = _load_env_key("FRED_API_KEY")
FRED_API_KEY = _load_env_key("FRED_API_KEY")
EIA_API_KEY = _load_env_key("EIA_API_KEY")
print(f"[DEBUG] FRED_API_KEY loaded: len={len(FRED_API_KEY)}, first8={FRED_API_KEY[:8] if FRED_API_KEY else 'EMPTY'}")

# 终极兜底
if not FRED_API_KEY or len(FRED_API_KEY) != 32:
    try:
        with open(ENV_PATH) as _f:
            for _line in _f:
                if _line.strip().startswith("FRED_API_KEY="):
                    FRED_API_KEY = _line.strip().split("=", 1)[1]
                    os.environ["FRED_API_KEY"] = FRED_API_KEY
                    break
    except Exception:
        pass

# ─── 代理配置 (v2rayN/Clash 兼容) ──────────────────────────
# 如果系统有代理但环境变量没设，自动检测
if not os.environ.get("HTTP_PROXY") and not os.environ.get("http_proxy"):
    # 检测常见代理端口
    import socket
    for proxy_host, proxy_port in [("127.0.0.1", 10808), ("127.0.0.1", 10809),
                                     ("127.0.0.1", 7890), ("127.0.0.1", 7891)]:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.3)
        try:
            result = sock.connect_ex((proxy_host, proxy_port))
            if result == 0:
                os.environ["HTTP_PROXY"] = f"http://{proxy_host}:{proxy_port}"
                os.environ["HTTPS_PROXY"] = f"http://{proxy_host}:{proxy_port}"
                os.environ["http_proxy"] = f"http://{proxy_host}:{proxy_port}"
                os.environ["https_proxy"] = f"http://{proxy_host}:{proxy_port}"
                print(f"🔌 自动检测到代理: {proxy_host}:{proxy_port}")
                break
        finally:
            sock.close()

DATA_DIR = Path.home() / "hermes-macro-data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR = DATA_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / f"pipeline_{datetime.now():%Y%m%d}.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("macro-pipeline")

TODAY = datetime.now().strftime("%Y-%m-%d")


# ─── 工具函數 ───────────────────────────────────────────────

def safe_get(url: str, params: dict = None, headers: dict = None,
             timeout: int = 30, retries: int = 2) -> Optional[dict]:
    """帶重試的安全 GET 請求"""
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, params=params, headers=headers,
                                timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            log.warning(f"[{attempt+1}/{retries+1}] GET {url} 失敗: {e}")
            if attempt < retries:
                time.sleep(2 ** attempt)
    return None


def save_json(data: any, name: str, subdir: str = "raw"):
    """保存 JSON 到日期目錄"""
    out_dir = DATA_DIR / subdir / TODAY
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{name}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log.info(f"✅ 已保存 {path} ({len(json.dumps(data))} bytes)")
    return path


def save_csv(df: pd.DataFrame, name: str, subdir: str = "csv"):
    """保存 DataFrame 為 CSV"""
    if df.empty:
        log.warning(f"⚠️ {name} 數據為空，跳過保存")
        return None
    out_dir = DATA_DIR / subdir / TODAY
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{name}.csv"
    df.to_csv(path, index=False, encoding="utf-8-sig")
    log.info(f"✅ 已保存 CSV {path} ({len(df)} 行)")
    return path


# ─── 1. FRED (美聯儲經濟數據) ──────────────────────────────

# FRED_API_KEY 已在文件顶部通过 _load_env_key 加载
FRED_BASE = "https://api.stlouisfed.org/fred"

# 常用 FRED 系列 ID（可擴展）
FRED_SERIES = {
    "FEDFUNDS": "聯邦基金利率",
    "CPIAUCSL": "CPI 消費者物價指數",
    "PCEPILFE": "核心PCE物價指數(剔除食品能源)",
    "PCE": "PCE個人消費支出",
    "GDP": "GDP 國內生產總值",
    "UNRATE": "失業率",
    "PAYEMS": "非農就業人數",
    "AHETPI": "平均時薪(全部員工)",
    "CES0500000003": "平均時薪(生產/非管理)",
    "JTSJOL": "JOLTS職位空缺數",
    "JTSQUR": "JOLTS離職率(%)",
    "DGS1": "1 年期國債收益率",
    "DGS2": "2 年期國債收益率",
    "DGS5": "5 年期國債收益率",
    "DGS10": "10 年期國債收益率",
    "DGS30": "30年期國債收益率",
    "T10Y2Y": "10-2 年利差 (收益率曲線)",
    "DFII10": "10年期TIPS收益率(實際利率)",
    "T5YIFR": "5年盈虧平衡通脹率",
    "T10YIE": "10年盈虧平衡通脹率",
    "M2SL": "M2 貨幣供應量",
    "DTWEXBGS": "美元指數 (貿易加權)",
    "PPIACO": "PPI 生產者物價指數",
    "INDPRO": "工業生產指數",
    "HOUST": "新屋開工",
    "UMCSENT": "密歇根消費者信心指數",
    "FYFSD": "聯邦財政赤字(百萬$)",
    # 欧元区
    "CLVMNACSCAB1GQEA19": "歐元區GDP",
    "IRSTCI01EZM156N": "歐元區利率(%)",
}


def fetch_fred():
    """抓取 FRED 關鍵經濟指標"""
    log.info("📊 正在抓取 FRED 經濟數據...")
    results = []
    failed_series = []
    for series_id, name in FRED_SERIES.items():
        params = {
            "series_id": series_id,
            "api_key": FRED_API_KEY,
            "file_type": "json",
            "sort_order": "desc",
            "limit": 30,
        }
        data = safe_get(f"{FRED_BASE}/series/observations", params=params)
        if data and 'observations' in data:
            all_obs = [o for o in data['observations'] if o['value'] != '.']
            for obs in all_obs[:13]:  # 最近13期
                results.append({
                        "日期": obs["date"],
                        "指標": name,
                        "系列ID": series_id,
                        "數值": float(obs["value"]),
                        "抓取日": TODAY,
                    })
        else:
            failed_series.append(f"{series_id}({name})")
        time.sleep(0.3)  # 防止FRED限流

    df = pd.DataFrame(results)
    if failed_series:
        log.warning(f"⚠️ FRED {len(failed_series)}个系列获取失败: {', '.join(failed_series)}")
    if not df.empty:
        df = df.sort_values(["系列ID", "日期"], ascending=[True, False])
        save_csv(df, "fred_indicators")
        log.info(f"  ✅ FRED {len(df)} 行数据, {len(FRED_SERIES)-len(failed_series)}/{len(FRED_SERIES)} 系列成功")
    else:
        log.warning("⚠️ FRED 未返回數據，檢查 API Key")
    return df


# ─── 2. Alpha Vantage ──────────────────────────────────────

# ─── 3. 財經新聞 (Finnhub) ─────────────────────────────────

FINNHUB_KEY = os.getenv("FINNHUB_API_KEY", "")

def fetch_news():
    """抓取全球財經新聞 - 使用 Finnhub API (國內可訪問)"""
    log.info("📰 正在抓取財經新聞...")
    results = []
    
    token = os.getenv("FINNHUB_API_KEY", "")
    news = safe_get(
        "https://finnhub.io/api/v1/news",
        params={"token": token, "category": "general", "minId": 0},
    )
    if news and isinstance(news, list):
        for item in news[:20]:
            ts = item.get("datetime", 0)
            results.append({
                "標題": item.get("headline", ""),
                "來源": "Finnhub",
                "發布時間": datetime.fromtimestamp(ts).isoformat() if ts else "",
                "描述": item.get("summary", ""),
                "URL": item.get("url", ""),
                "抓取日": TODAY,
            })
        log.info(f"  ✅ Finnhub 新聞 {len(results)} 條")
    else:
        log.warning("Finnhub 新聞接口無響應")
    
    df = pd.DataFrame(results)
    save_csv(df, "financial_news")
    return df


# ─── 4. OpenWeather (天氣) ─────────────────────────────────

WEATHER_KEY = os.getenv("OPENWEATHER_API_KEY", "")

# 主要農業/能源產區
WEATHER_CITIES = [
    ("Chicago", "US", "CBOT 所在地"),
    ("New York", "US", "NYMEX/ICE 所在地"),
    ("London", "GB", "ICE 歐洲"),
    ("Singapore", "SG", "亞洲交易中心"),
    ("Shanghai", "CN", "INE/上期所"),
    ("Tokyo", "JP", "TOCOM"),
    ("Sao Paulo", "BR", "巴西農業區"),
    ("Buenos Aires", "AR", "阿根廷農業"),
    ("Rostov", "RU", "俄羅斯小麥區"),
]


def fetch_weather():
    """抓取主要交易中心/產區天氣"""
    log.info("🌤️ 正在抓取天氣數據...")
    results = []
    for city, country, note in WEATHER_CITIES:
        params = {"q": f"{city},{country}", "appid": WEATHER_KEY, "units": "metric"}
        data = safe_get("https://api.openweathermap.org/data/2.5/weather", params=params)
        if data:
            results.append({
                "城市": city,
                "國家": country,
                "備註": note,
                "溫度°C": data.get("main", {}).get("temp"),
                "體感°C": data.get("main", {}).get("feels_like"),
                "濕度%": data.get("main", {}).get("humidity"),
                "天氣": data.get("weather", [{}])[0].get("description", ""),
                "風速m/s": data.get("wind", {}).get("speed"),
                "抓取日": TODAY,
            })
    df = pd.DataFrame(results)
    save_csv(df, "weather_centers")
    return df


# ─── 5. EIA (美國能源信息) ─────────────────────────────────

EIA_KEY = os.getenv("EIA_API_KEY", "")
EIA_BASE = "https://api.eia.gov/v2"


def fetch_eia():
    """抓取 EIA 能源數據 (原油產量、庫存)"""
    log.info("🛢️ 正在抓取 EIA 能源數據...")
    results = []

    # EIA 原油產量 (Monthly)
    params = {
        "api_key": EIA_KEY,
        "frequency": "monthly",
        "data[0]": "value",
        "facets[duoarea][]": "NUS",
        "facets[product][]": "EPC0",
        "sort[0][column]": "period",
        "sort[0][direction]": "desc",
        "offset": 0,
        "length": 6,
    }
    data = safe_get(f"{EIA_BASE}/petroleum/crd/crpdn/data/", params=params)
    if data and "response" in data:
        for item in data["response"].get("data", []):
            results.append({
                "來源": "EIA",
                "類別": "原油產量",
                "日期": item.get("period"),
                "數值": item.get("value"),
                "單位": "千桶/日",
                "抓取日": TODAY,
            })

    df = pd.DataFrame(results)
    save_csv(df, "eia_energy")
    return df


# ─── 6. USDA NASS (農業統計) ───────────────────────────────

USDA_KEY = os.getenv("USDA_NASS_API_KEY", "")


def fetch_usda():
    """抓取 USDA 農產品數據"""
    log.info("🌽 正在抓取 USDA 農業數據...")
    params = {
        "api_key": USDA_KEY,
        "format": "JSON",
        "source_desc": "SURVEY",
        "sector_desc": "CROPS",
        "commodity_desc": "CORN",
        "statisticcat_desc": "YIELD",
        "freq_desc": "ANNUAL",
        "year__GE": 2023,
        "page_size": 10,
    }
    data = safe_get("https://quickstats.nass.usda.gov/api/api_GET/", params=params)
    results = []
    if data and "data" in data:
        for item in data["data"][:20]:
            results.append({
                "來源": "USDA NASS",
                "商品": item.get("commodity_desc"),
                "統計": item.get("statisticcat_desc"),
                "年份": item.get("year"),
                "數值": item.get("Value"),
                "單位": item.get("unit_desc"),
                "州": item.get("state_name"),
                "抓取日": TODAY,
            })
    df = pd.DataFrame(results)
    save_csv(df, "usda_agriculture")
    return df


# ─── 7. CFTC COT (持倉報告) ────────────────────────────────

COT_ID = os.getenv("CFTC_COT_ID", "")
COT_SECRET = os.getenv("CFTC_COT_SECRET", "")


def fetch_cftc():
    """抓取 CFTC COT 持倉數據 (黃金/白銀/原油)"""
    log.info("📈 正在抓取 CFTC COT 持倉數據...")
    results = []

    # 通過公共 COT 報告解析 (CFTC 公開報告)
    # CFTC dea.txt 已失效(404)，改用 FinFutWk.txt
    try:
        resp = requests.get("https://www.cftc.gov/dea/newcot/FinFutWk.txt", timeout=30)
        if resp.status_code == 200:
            lines = resp.text.split("\n")
            # 找關鍵品種
            keywords = ["GOLD", "SILVER", "CRUDE OIL", "LIGHT SWEET"]
            for i, line in enumerate(lines[:500]):
                for kw in keywords:
                    if kw in line.upper() and i + 1 < len(lines):
                        parts = line.split(",")
                        results.append({
                            "來源": "CFTC COT",
                            "品種": kw,
                            "原始數據": line[:200],
                            "抓取日": TODAY,
                        })
        else:
            log.warning(f"CFTC 返回狀態碼 {resp.status_code}")
            # 備用方案: 使用公共 API
    except Exception as e:
        log.error(f"CFTC 抓取失敗: {e}")

    df = pd.DataFrame(results)
    save_csv(df, "cftc_cot")
    return df


# ─── 8. Finnhub (經濟日曆) ─────────────────────────────────

FINNHUB_KEY = os.getenv("FINNHUB_API_KEY", "")


def fetch_finnhub():
    """抓取 Finnhub 經濟日曆"""
    log.info("📅 正在抓取 Finnhub 經濟日曆...")
    results = []

    # 經濟日曆
    params = {"token": FINNHUB_KEY}
    data = safe_get(
        "https://finnhub.io/api/v1/calendar/economic",
        params={**params, "from": TODAY, "to": TODAY},
    )
    if data and "economicCalendar" in data:
        for item in data["economicCalendar"][:20]:
            results.append({
                "來源": "Finnhub",
                "類別": "經濟日曆",
                "事件": item.get("event", ""),
                "時間": item.get("time", ""),
                "前值": item.get("previous", ""),
                "預測": item.get("forecast", ""),
                "實際": item.get("actual", ""),
                "重要性": item.get("importance", ""),
                "抓取日": TODAY,
            })

    # 市場新聞
    news = safe_get(
        "https://finnhub.io/api/v1/news",
        params={**params, "category": "general", "minId": 0},
    )
    if news and isinstance(news, list):
        for item in news[:10]:
            results.append({
                "來源": "Finnhub",
                "類別": "市場新聞",
                "標題": item.get("headline", ""),
                "時間": datetime.fromtimestamp(item.get("datetime", 0)).isoformat() if item.get("datetime") else "",
                "摘要": item.get("summary", ""),
                "URL": item.get("url", ""),
                "抓取日": TODAY,
            })

    df = pd.DataFrame(results)
    save_csv(df, "finnhub_calendar")
    return df


# ─── 9. AGSI+ (歐洲天然氣) ─────────────────────────────────

AGSI_KEY = os.getenv("AGSI_API_KEY", "")


def fetch_agsi():
    """抓取 AGSI+ 歐洲天然氣庫存數據"""
    log.info("⛽ 正在抓取 AGSI+ 歐洲天然氣庫存...")
    
    # GIE AGSI+ API
    headers = {"x-key": AGSI_KEY}
    params = {
        "country": "DE",
        "size": 7,
        "date_from": (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d"),
        "date_to": TODAY,
    }
    
    results = []
    data = safe_get(
        "https://agsi.gie.eu/api",
        params=params,
        headers=headers,
    )
    if data and "data" in data:
        for item in data["data"][:7]:
            # 计算填充率
            storage = float(item.get("gasInStorage", 0) or 0)
            capacity = float(item.get("workingGasVolume", 1) or 1)
            fill_rate = round(storage / capacity * 100, 1) if capacity > 0 else 0
            results.append({
                "來源": "AGSI+",
                "國家": item.get("name", item.get("country", "")),
                "日期": item.get("gasDayStart", ""),
                "庫存(TWh)": item.get("gasInStorage", ""),
                "填充率%": fill_rate,
                "注入(GWh)": item.get("injection", ""),
                "提取(GWh)": item.get("withdrawal", ""),
                "淨提取(GWh)": item.get("netWithdrawal", ""),
                "工作容量(TWh)": item.get("workingGasVolume", ""),
                "抓取日": TODAY,
            })
        log.info(f"  ✅ AGSI+ 获取 {len(results)} 条数据")
    else:
        log.warning(f"AGSI+ API 无响应: {str(data)[:100] if data else 'None'}")

    df = pd.DataFrame(results)
    save_csv(df, "agsi_eu_gas")
    return df


# ─── 10. 日本 e-Stat ───────────────────────────────────────

ESTAT_KEY = os.getenv("ESTAT_API_KEY", "")


def fetch_estat():
    """抓取日本 e-Stat 政府統計"""
    log.info("🗾 正在抓取日本 e-Stat 統計數據...")
    results = []

    # e-Stat API v3
    params = {
        "appId": ESTAT_KEY,
        "lang": "J",
        "statsCode": "00200561",  # 消費者物價指數
        "limit": 10,
    }
    data = safe_get(
        "https://api.e-stat.go.jp/rest/3.0/app/getSimpleStatsData",
        params=params,
    )
    if data:
        results.append({
            "來源": "日本 e-Stat",
            "統計": "消費者物價指數",
            "狀態": "API 請求已發送" if data else "無數據",
            "原始響應": str(data)[:200],
            "抓取日": TODAY,
        })
    time.sleep(1)

    df = pd.DataFrame(results)
    save_csv(df, "japan_estat")
    return df


# ─── 全部抓取 ───────────────────────────────────────────────



# ─── 11. FedWatch (FOMC利率概率) ──────────────────────────

def fetch_fedwatch():
    """从 Oddpool API 抓取 FedWatch FOMC 利率概率数据"""
    log.info("🏛️ 正在抓取 FedWatch FOMC 利率概率...")
    results = []

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    base = "https://www.oddpool.com/api/events/history"

    # 动态获取最近的FOMC event_id
    now = datetime.now()
    hold = cut_25 = hike_25 = None
    event_id_found = None

    for m_offset in range(0, 2):
        m = now.month + m_offset
        y = now.year + (m - 1) // 12
        m = (m - 1) % 12 + 1
        for day in [17, 16, 18, 15, 19, 14, 20]:
            event_id = f"fomc-{y}-{m:02d}-{day:02d}"
            try:
                r = requests.get(f"{base}/no_change", params={"event_id": event_id, "hours": 1},
                                 headers=headers, timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    if data.get("kalshi") or data.get("polymarket"):
                        event_id_found = event_id
                        # 取最新数据点 - no_change (维持)
                        for venue in ["kalshi", "polymarket"]:
                            items = data.get(venue, [])
                            if items:
                                p = items[-1].get("probabilities", {})
                                hold_val = p.get("no_change")
                                if hold_val is not None:
                                    hold = f"{hold_val * 100:.1f}"
                                break
                        # cut_25bps
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
                        # hike_25bps
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
                        # 校验概率之和
                        vals = [float(v) for v in [hold, cut_25, hike_25] if v is not None]
                        if vals and sum(vals) > 105:
                            log.warning(f"[FedWatch] 概率之和异常: {sum(vals):.1f}%, 数据丢弃")
                            return None
                        break  # 找到数据，退出day循环
            except Exception:
                continue
        if hold is not None:
            break  # 找到数据，退出month循环

    if hold is not None:
        results.append({
            "來源": "FedWatch/Oddpool",
            "類別": "FOMC利率概率",
            "當前利率": "?",
            "維持概率%": hold,
            "加息25bp概率%": hike_25 or "?",
            "降息25bp概率%": cut_25 or "?",
            "會議": event_id_found or "?",
            "抓取日": TODAY,
        })
        log.info(f"  ✅ FedWatch ({event_id_found}): 维持{hold}%, 降息25bp={cut_25}%, 加息25bp={hike_25}%")
    else:
        log.warning("FedWatch 抓取失败，使用FRED联邦基金利率估算")
        results.append({
            "來源": "FRED (FedWatch暂缺)",
            "類別": "FOMC利率概率",
            "當前利率": "?",
            "維持概率%": "?",
            "加息25bp概率%": "?",
            "降息25bp概率%": "?",
            "會議": "?",
            "抓取日": TODAY,
        })

    df = pd.DataFrame(results)
    save_csv(df, "fedwatch")
    return df

# Add to ALL_SOURCES
def patch_all_sources():
    global ALL_SOURCES


# ─── 12. CFTC COT (期货持仓报告) ──────────────────────────


def fetch_cot():
    """从 cotdata.net 抓取 CFTC COT 持仓 (含COT Index/Z-Score)"""
    log.info("📊 正在抓取 COT 持仓 (cotdata.net)...")
    results = []
    
    instruments = {
        "088691": ("黄金", "COMEX", "legacy"),
        "084691": ("白银", "COMEX", "legacy"),
        "067651": ("原油WTI", "NYMEX", "legacy"),
        "067411": ("原油Brent", "ICE", "legacy"),
        "098662": ("美元指数DXY", "ICE", "legacy"),
        "001602": ("小麦SRW", "CBOT", "legacy"),
        "001612": ("小麦HRW", "KCBT", "legacy"),
        "002602": ("玉米", "CBOT", "legacy"),
        "005602": ("大豆", "CBOT", "legacy"),
        "025601": ("糖#11", "ICE", "legacy"),
        "033601": ("棉花", "ICE", "legacy"),
        "073601": ("豆油", "CBOT", "legacy"),
        "026601": ("咖啡", "ICE", "legacy"),
        "092691": ("铜", "COMEX", "legacy"),
        "112601": ("天然气", "NYMEX", "legacy"),
    }
    
    import urllib.request
    
    proxies = {}
    if os.environ.get("HTTP_PROXY"):
        proxies["http"] = os.environ["HTTP_PROXY"]
        proxies["https"] = os.environ["HTTPS_PROXY"]
    
    for code, (name, exchange, table) in instruments.items():
        url = f"https://cotdata.net/api/cot?instrument={code}&table={table}"
        try:
            proxy_handler = urllib.request.ProxyHandler(proxies) if proxies else urllib.request.ProxyHandler({})
            opener = urllib.request.build_opener(proxy_handler)
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            resp = opener.open(req, timeout=15)
            data = json.loads(resp.read().decode())
            
            if data and "non_commercial" in data:
                nc = data["non_commercial"]
                c = data.get("commercial", {})
                mm = data.get("managed_money", {})
                oi = data.get("open_interest", 0)
                
                # 优先用 Legacy 的非商业数据
                nc_net = nc.get("net", 0)
                nc_long = nc.get("long", 0)
                nc_short = nc.get("short", 0)
                ci_26w = nc.get("cot_index_26w", 50)
                zs_26w = nc.get("zscore_26w", 0)
                
                # 如果有 Disaggregated 的管理基金数据
                mm_net = mm.get("net", 0) if mm else None
                
                results.append({
                    "來源": "cotdata.net",
                    "品種": name,
                    "交易所": exchange,
                    "報告日期": data.get("report_date", ""),
                    "未平倉合約": oi,
                    "投機多頭": nc_long,
                    "投機空頭": nc_short,
                    "投機淨持倉": nc_net,
                    "COT Index(26W)": round(ci_26w, 1),
                    "Z-Score": round(zs_26w, 2),
                    "管理基金淨持倉": mm_net,
                    "商業多頭": c.get("long"),
                    "商業空頭": c.get("short"),
                    "抓取日": TODAY,
                })
                sent = "極度看多" if ci_26w >= 90 else "看多" if ci_26w >= 70 else "中性" if ci_26w >= 30 else "看空" if ci_26w >= 10 else "極度看空"
                log.info(f"  ✅ {name}: COT Index {ci_26w:.0f} → {sent}")
            else:
                log.warning(f"{name} 返回空数据")
        except Exception as e:
            log.error(f"{name} 抓取失败: {e}")
    
    df = pd.DataFrame(results)
    save_csv(df, "cotdata")
    return df

def patch_cot():
    global ALL_SOURCES
    ALL_SOURCES["cot"] = ("CFTC COT持仓", fetch_cot)

    ALL_SOURCES["fedwatch"] = ("FedWatch FOMC概率", fetch_fedwatch)



# ─── 13. Yahoo Finance 期货 (黄金/白银/原油) ──────────────

def yahoo_quote(symbol, retries=3):
    """Yahoo Chart API 带指数退避"""
    import time, random
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {"range": "5d", "interval": "1d"}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=15)
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 429:
                wait = (2 ** attempt) + random.random() * 2
                log.warning(f"Yahoo 429限流, 等待{wait:.1f}s")
                time.sleep(wait)
            elif r.status_code == 403:
                log.warning("Yahoo 403被禁, 等待5s")
                time.sleep(5)
            else:
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        except Exception as e:
            log.warning(f"Yahoo请求失败: {e}")
            time.sleep(3)
    return None


def fetch_yahoo_futures():
    """抓取 Yahoo Finance 期货数据 (COMEX黄金/白银/原油)"""
    log.info("💹 正在抓取 Yahoo 期货数据...")
    results = []
    
    symbols = {
        "GC=F": "COMEX黃金期貨",
        "SI=F": "COMEX白銀期貨",
        "CL=F": "WTI原油期貨",
        "BZ=F": "Brent原油期貨",
        "NG=F": "天然氣期貨(Henry Hub)",
        "ZC=F": "玉米期貨",
        "ZS=F": "大豆期貨",
        "ZW=F": "小麥期貨",
        "ZL=F": "豆油期貨",
        "ZM=F": "豆粕期貨",
        "CT=F": "棉花期貨",
        "SB=F": "糖期貨",
        # 外匯
        "EURUSD=X": "歐元/美元",
        "USDJPY=X": "美元/日元",
        "CNH=X": "美元/離岸人民幣",
        # 波動率
        "^VIX": "VIX恐慌指數",
    }
    
    for sym, name in symbols.items():
        data = yahoo_quote(sym)
        if data and data.get("chart", {}).get("result"):
            result = data["chart"]["result"][0]
            meta = result.get("meta", {})
            quotes = result.get("indicators", {}).get("quote", [{}])[0]
            timestamps = result.get("timestamp", [])
            
            price = meta.get("regularMarketPrice")
            prev_close = meta.get("chartPreviousClose")
            
            # 计算5日范围
            closes = [c for c in (quotes.get("close") or []) if c]
            high5d = max(closes) if closes else None
            low5d = min(closes) if closes else None
            change = (price - prev_close) if (price and prev_close) else None
            change_pct = (change / prev_close * 100) if (change and prev_close) else None
            
            # 最新交易日
            last_date = ""
            if timestamps:
                import datetime
                last_date = datetime.datetime.fromtimestamp(timestamps[-1]).strftime("%Y-%m-%d")
            
            results.append({
                "來源": "Yahoo Finance",
                "品種": name,
                "代碼": sym,
                "日期": last_date,
                "最新價": price,
                "前收盤": prev_close,
                "日變化": round(change, 2) if change else None,
                "日漲跌幅%": round(change_pct, 3) if change_pct else None,
                "5日最高": high5d,
                "5日最低": low5d,
                "抓取日": TODAY,
            })
            log.info(f"  ✅ {name}: ${price} ({change_pct:+.2f}%)" if change_pct else f"  ✅ {name}: ${price}")
        else:
            log.warning(f"  ❌ {name}: 无数据")
    
    df = pd.DataFrame(results)
    save_csv(df, "yahoo_futures")
    return df


# ─── 14. VIX (波动率指数) ──────────────────────────────────

def fetch_vix():
    """抓取 VIX 波动率指数数据 (CFTC ZIP持仓 + Yahoo价格)"""
    log.info("📊 正在抓取 VIX 波动率数据...")
    results = []
    
    import zipfile, io, csv, urllib.request
    
    proxies = {}
    if os.environ.get("HTTP_PROXY"):
        proxies["http"] = os.environ["HTTP_PROXY"]
        proxies["https"] = os.environ["HTTPS_PROXY"]
    
    # 1. VIX 价格 (Yahoo)
    price_data = None
    try:
        proxy_handler = urllib.request.ProxyHandler(proxies) if proxies else urllib.request.ProxyHandler({})
        opener = urllib.request.build_opener(proxy_handler)
        req = urllib.request.Request(
            "https://query1.finance.yahoo.com/v8/finance/chart/%5EVIX?range=5d&interval=1d",
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        resp = opener.open(req, timeout=15)
        data = json.loads(resp.read().decode())
        if data.get("chart", {}).get("result"):
            meta = data["chart"]["result"][0]["meta"]
            price_data = {
                "price": meta.get("regularMarketPrice"),
                "prev_close": meta.get("chartPreviousClose"),
            }
    except Exception as e:
        log.warning(f"VIX 价格抓取失败: {e}")
    
    # 2. VIX 持仓 (CFTC TFF ZIP)
    try:
        url = "https://www.cftc.gov/files/dea/history/fut_fin_txt_2026.zip"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        proxy_handler = urllib.request.ProxyHandler(proxies) if proxies else urllib.request.ProxyHandler({})
        opener = urllib.request.build_opener(proxy_handler)
        resp = opener.open(req, timeout=60)
        
        with zipfile.ZipFile(io.BytesIO(resp.read())) as zf:
            txt = zf.read('FinFutYY.txt').decode('utf-8', errors='replace')
            reader = csv.reader(io.StringIO(txt))
            
            for row in reader:
                if len(row) < 20: continue
                if 'VIX FUTURES' in row[0].upper() and '260602' in row[1]:
                    oi = int(row[7].strip())
                    dealer_l = int(row[8].strip()); dealer_s = int(row[9].strip())
                    am_l = int(row[11].strip()); am_s = int(row[12].strip())
                    lf_l = int(row[14].strip()); lf_s = int(row[15].strip())
                    
                    results.append({
                        "來源": "CFTC TFF / Yahoo",
                        "品種": "VIX",
                        "报告日期": "2026-06-02",
                        "价格": price_data["price"] if price_data else None,
                        "前收盘": price_data["prev_close"] if price_data else None,
                        "未平仓合约": oi,
                        "交易商多头": dealer_l, "交易商空头": dealer_s, "交易商净": dealer_l - dealer_s,
                        "资产管理多头": am_l, "资产管理空头": am_s, "资产管理净": am_l - am_s,
                        "杠杆基金多头": lf_l, "杠杆基金空头": lf_s, "杠杆基金净": lf_l - lf_s,
                        "抓取日": TODAY,
                    })
                    log.info(f"  ✅ VIX: ${price_data['price'] if price_data else '?'} | OI:{oi:,}")
                    break
            if not results:
                log.warning("VIX 未在ZIP中找到")
    except Exception as e:
        log.error(f"VIX 持仓抓取失败: {e}")
    
    df = pd.DataFrame(results)
    save_csv(df, "vix_data")
    return df



# ─── 15. EIA STEO (太阳能/工业能源消费) ──────────────────

def fetch_eia_steo():
    """抓取 EIA STEO 数据: 太阳能光伏装机/发电 + 工业能源消费
    数据来源: EIA Short-Term Energy Outlook (STEO)
    注意: 数据为美国本土数据(US only), 非国际
    更新频率: 月度, EIA 每月更新"""
    log.info("☀️ 正在抓取 EIA STEO (太阳能/工业能源)...")
    results = []
    
    # 已验证的 STEO 系列
    series = {
        # --- 太阳能光伏 ---
        "SODTC_US": {
            "name": "小型太阳能光伏总装机容量",
            "category": "太阳能",
            "unit_note": "MW (兆瓦)"
        },
        "SODTP_US": {
            "name": "小型太阳能光伏总发电量",
            "category": "太阳能",
            "unit_note": "十亿千瓦时"
        },
        "SOEPGEN_US": {
            "name": "大型太阳能光伏发电量(电力部门)",
            "category": "太阳能",
            "unit_note": "十亿千瓦时"
        },
        "SOCHGEN_US": {
            "name": "大型太阳能光伏发电量(工商部门)",
            "category": "太阳能",
            "unit_note": "十亿千瓦时"
        },
        # --- 工业能源消费 ---
        "ELICP_US": {
            "name": "工业用电量",
            "category": "工业能源",
            "unit_note": "十亿千瓦时"
        },
        "NGINCNS_US": {
            "name": "工业天然气消费量",
            "category": "工业能源",
            "unit_note": "十亿立方英尺/月"
        },
    }
    
    for sid, info in series.items():
        try:
            r = requests.get("https://api.eia.gov/v2/steo/data/", params={
                "api_key": os.getenv("EIA_API_KEY", ""),
                "facets[seriesId][]": sid,
                "data[0]": "value",
                "length": 3,
                "sort[0][column]": "period",
                "sort[0][direction]": "desc"
            }, timeout=15)
            
            if r.status_code == 200:
                items = r.json().get("response", {}).get("data", [])
                if items:
                    latest = items[0]
                    val = latest.get("value")
                    period = latest.get("period", "")
                    unit = latest.get("unit", "")
                    
                    # 趋势判断
                    vals = []
                    for item in items:
                        try:
                            vals.append(float(item["value"]))
                        except:
                            pass
                    trend = None
                    if len(vals) >= 2:
                        diff = vals[0] - vals[1]
                        trend = round(diff / vals[1] * 100, 1) if vals[1] != 0 else 0
                    
                    results.append({
                        "來源": "EIA STEO",
                        "類別": info["category"],
                        "指標": info["name"],
                        "系列ID": sid,
                        "數值": val,
                        "日期": period,
                        "單位": unit,
                        "環比變化%": trend,
                        "抓取日": TODAY,
                    })
                    log.info(f"  ✅ {info['name']}: {val} {unit} ({period})")
                else:
                    log.warning(f"  {sid}: 无数据")
            else:
                log.warning(f"  {sid}: EIA返回{r.status_code}")
        except Exception as e:
            log.error(f"  {sid}: 错误 {e}")
    
    df = pd.DataFrame(results)
    save_csv(df, "eia_steo")
    return df


# ═══ ALL_SOURCES + 入口 (必须在所有 fetch_* 函数之后) ═══════

ALL_SOURCES = {
    "fedwatch": ("FedWatch FOMC概率", fetch_fedwatch),
    "fred": ("美聯儲 FRED", fetch_fred),
    "news": ("NewsAPI 新聞", fetch_news),
    "vix": ("VIX波动率", fetch_vix),
    "weather": ("OpenWeather 天氣", fetch_weather),
    "eia": ("EIA 能源", fetch_eia),
    "usda": ("USDA 農業", fetch_usda),
    "cftc": ("CFTC 持倉", fetch_cftc),
    "cot": ("CFTC COT持仓 (cotdata.net)", fetch_cot),
    "yahoo": ("Yahoo Finance 期貨/外匯", fetch_yahoo_futures),
    "finnhub": ("Finnhub 經濟日曆", fetch_finnhub),
    "agsi": ("AGSI+ 天然氣", fetch_agsi),
    "estat": ("日本 e-Stat", fetch_estat),
}


def run_all():
    """運行所有數據源"""
    print(f"\n{'='*60}")
    print(f"  📊 宏觀期貨數據採集流水線")
    print(f"  日期: {TODAY}")
    print(f"{'='*60}\n")
    summary = {"成功": 0, "失敗": 0, "跳過": 0}
    for key, (name, func) in ALL_SOURCES.items():
        print(f"\n[{key.upper()}] {name}")
        try:
            df = func()
            if df is not None:
                summary["成功"] += 1
            else:
                summary["跳過"] += 1
        except Exception as e:
            log.error(f"❌ {name} 失敗: {e}", exc_info=True)
            summary["失敗"] += 1
    print(f"\n{'='*60}")
    print(f"  採集完成！成功: {summary['成功']}, 跳過: {summary['跳過']}, 失敗: {summary['失敗']}")
    print(f"  數據目錄: {DATA_DIR}")
    print(f"{'='*60}")
    summary_data = {
        "日期": TODAY, "運行時間": datetime.now().isoformat(),
        "狀態": summary, "活躍數據源": [k for k in ALL_SOURCES],
    }
    meta_dir = DATA_DIR / "meta" / TODAY
    meta_dir.mkdir(parents=True, exist_ok=True)
    with open(meta_dir / "pipeline_summary.json", "w") as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)
    log.info(f"✅ 已保存 {meta_dir / 'pipeline_summary.json'}")
    return summary


def main():
    parser = argparse.ArgumentParser(description="宏觀期貨數據採集流水線")
    parser.add_argument("--source", choices=list(ALL_SOURCES.keys()) + ["all"],
                        default="all", help="指定數據源")
    parser.add_argument("--report", action="store_true", help="生成報告")
    args = parser.parse_args()
    if args.source == "all":
        run_all()
    else:
        name, func = ALL_SOURCES[args.source]
        log.info(f"單獨運行: {name}")
        func()


if __name__ == "__main__":
    main()


