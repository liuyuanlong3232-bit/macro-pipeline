#!/usr/bin/env python3
"""
中国城市天气采集 — 和风天气 API v7
官方文档: https://dev.qweather.com/docs/api/weather/
认证方式: X-QW-Api-Key Header + 专属 API Host
免费额度: 50,000次/月 (我们用量 ~120次/月)
"""
import os, sys, requests, sqlite3
from pathlib import Path
from datetime import datetime

# ── 读取配置 ──
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.utils import load_env, DATA_DIR
load_env()
key = os.getenv("QWEATHER_KEY", "")
host = os.getenv("QWEATHER_HOST", "")

# ── 核心城市 ──
CITIES = {
    "哈尔滨": "126.63,45.75",
    "郑州": "113.65,34.76",
    "北京": "116.41,39.92",
    "济南": "117.00,36.65",
    "石家庄": "114.52,38.05",
    "呼和浩特": "111.75,40.84",
    "通辽": "122.28,43.63",
    "巴彦淖尔": "107.39,40.74",
    "呼伦贝尔": "119.77,49.21",
}

DB = str(Path.home() / "hermes-macro-data" / "hermes.db")
now = datetime.now()

# ── 建表 ──
conn = sqlite3.connect(DB)
conn.execute("""CREATE TABLE IF NOT EXISTS cn_weather (
    city TEXT, date TEXT, hour TEXT,
    temp REAL, text TEXT, humidity REAL, wind_dir TEXT, wind_scale TEXT,
    precip REAL, pressure REAL, vis REAL,
    forecast_date TEXT, forecast_text_day TEXT, forecast_temp_min REAL, forecast_temp_max REAL,
    source TEXT, fetched_at TEXT,
    PRIMARY KEY (city, date, hour)
)""")
conn.commit()

# ── 采集 ──
total = 0
for city, loc in CITIES.items():
    # 实时天气
    try:
        r = requests.get(f"https://{host}/v7/weather/now",
            params={"location": loc}, headers={"X-QW-Api-Key": key}, timeout=10)
        if r.status_code == 200:
            n = r.json()["now"]
            today_str = now.strftime("%Y-%m-%d")
            hour = "now"  # 固定hour避免obsTime变化导致重复

            conn.execute("""INSERT OR REPLACE INTO cn_weather 
                (city, date, hour, temp, text, humidity, wind_dir, wind_scale, precip, pressure, vis, source, fetched_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (city, today_str, hour,
                 float(n.get("temp", 0)), n.get("text"), float(n.get("humidity", 0)),
                 n.get("windDir"), n.get("windScale"), float(n.get("precip", 0)),
                 float(n.get("pressure", 0)), float(n.get("vis", 0)),
                 "QWeather API v7", now.strftime("%Y-%m-%d %H:%M")))
            total += 1
            print("OK {} now: {}C {} hum{}%".format(city, n.get("temp"), n.get("text"), n.get("humidity")))
    except Exception as e:
        print("FAIL {} now: {}".format(city, e))

    # 3天预报
    try:
        r2 = requests.get(f"https://{host}/v7/weather/3d",
            params={"location": loc}, headers={"X-QW-Api-Key": key}, timeout=10)
        if r2.status_code == 200:
            for day in r2.json().get("daily", []):
                conn.execute("""INSERT OR REPLACE INTO cn_weather 
                    (city, date, hour, forecast_date, forecast_text_day, forecast_temp_min, forecast_temp_max, source, fetched_at)
                    VALUES (?,?,?,?,?,?,?,?,?)""",
                    (city, day.get("fxDate"), "forecast",
                     day.get("fxDate"), day.get("textDay"),
                     float(day.get("tempMin", 0)), float(day.get("tempMax", 0)),
                     "QWeather API v7", now.strftime("%Y-%m-%d %H:%M")))
                total += 1
            print("   3d forecast: OK")
    except Exception as e:
        print("   3d forecast: FAIL {}".format(e))

conn.commit()
conn.close()
print("\nDone: {}条".format(total))
