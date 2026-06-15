#!/usr/bin/env python3
"""
天气历史数据采集 + 每日更新
遵循 Open-Meteo 官方规则：
  - 免费API: 10,000次/天, 5,000次/时, 600次/分
  - 历史模型: ERA5 (0.25°, 1940至今)
  - 归因: CC-BY 4.0 (数据来自 Open-Meteo)
  - 端点: https://archive-api.open-meteo.com/v1/archive
"""
import requests, sqlite3, time
from pathlib import Path
from datetime import datetime, timedelta

# ===== 官方参数 =====
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
MODEL = "era5"  # 官方推荐长期气候研究用ERA5
DAILY_VARS = "temperature_2m_mean,precipitation_sum"  # 日温度和降水

# ===== 六大核心产区 =====
REGIONS = [
    ("US_IL", 40.0, -89.0, "美国中西部IL大豆玉米带"),
    ("US_IA", 42.0, -93.0, "美国中西部IA大豆玉米带"),
    ("BR_MT", -13.0, -55.0, "巴西马托格罗索大豆带"),
    ("BR_PR", -24.0, -51.0, "巴西帕拉纳大豆带"),
    ("AR_BA", -33.0, -62.0, "阿根廷布宜诺斯艾利斯大​​豆带"),
    ("US_KS", 38.5, -98.0, "美国堪萨斯冬小麦带"),
]

DB = Path.home() / "hermes-macro-data" / "hermes.db"

def init_table():
    conn = sqlite3.connect(str(DB))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS agri_weather (
            region TEXT,
            date TEXT,
            temp_mean_c REAL,
            precip_mm REAL,
            source TEXT,
            fetched_at TEXT,
            PRIMARY KEY (region, date)
        )
    """)
    conn.commit()
    conn.close()
    print("[init] agri_weather 表已就绪")

def fetch_region(code, lat, lon, name, start="2011-01-01", end=None):
    """单产区拉取：一次请求拉整个时间段"""
    if end is None:
        end = datetime.now().strftime("%Y-%m-%d")

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "daily": DAILY_VARS,
        "timezone": "Asia/Shanghai",
        "models": MODEL,
    }

    print(f"[fetch] {code} ({name}) lat={lat} lon={lon} ...")
    try:
        r = requests.get(ARCHIVE_URL, params=params, timeout=120)
        if r.status_code == 200:
            data = r.json()
            days = data.get("daily", {}).get("time", [])
            temps = data.get("daily", {}).get("temperature_2m_mean", [])
            precips = data.get("daily", {}).get("precipitation_sum", [])
            print(f"  ✅ {code}: {len(days)}天数据")
            return list(zip(days, temps, precips))
        elif r.status_code == 429:
            print(f"  ⚠️ {code}: 限流429，等待60秒...")
            time.sleep(60)
            return fetch_region(code, lat, lon, name, start, end)
        else:
            print(f"  ❌ {code}: HTTP {r.status_code} {r.text[:200]}")
            return []
    except Exception as e:
        print(f"  ❌ {code}: {e}")
        return []

def save_region(code, rows):
    if not rows:
        return 0
    conn = sqlite3.connect(str(DB))
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    cnt = 0
    for day, temp, precip in rows:
        conn.execute("""
            INSERT OR REPLACE INTO agri_weather (region, date, temp_mean_c, precip_mm, source, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (code, day, temp, precip, f"Open-Meteo/{MODEL} (CC-BY 4.0)", now))
        cnt += 1
    conn.commit()
    conn.close()
    print(f"  💾 {code}: {cnt}条写入")
    return cnt

def incremental_update():
    """每日增量：只拉昨天到今天"""
    yesterday = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    total = 0
    for code, lat, lon, name in REGIONS:
        rows = fetch_region(code, lat, lon, name, start=yesterday)
        total += save_region(code, rows)
        time.sleep(1)  # 温和间隔，不超过600次/分
    return total

def full_historical():
    """全量历史采集：每个产区一次请求拉15年"""
    init_table()
    total = 0
    for i, (code, lat, lon, name) in enumerate(REGIONS):
        rows = fetch_region(code, lat, lon, name)
        total += save_region(code, rows)
        if i < len(REGIONS) - 1:
            time.sleep(2)  # 温和间隔
    return total

if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    
    if mode == "full":
        print("🌍 全量历史采集（每个产区独立请求，遵守官方限额）")
        total = full_historical()
        print(f"\n📦 总计: {total}条天气记录已入库")
    elif mode == "daily":
        print("📡 每日增量更新")
        total = incremental_update()
        print(f"\n📦 新增: {total}条")
    else:
        print("用法: python3 fetch_weather.py [full|daily]")
