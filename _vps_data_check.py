"""查EIA美湾 + Tushare DR007 + akshare"""
import os, json
from pathlib import Path
from dotenv import load_dotenv

env_path = os.environ.get("HERMES_HOME", "/root/hermes-pipeline")
load_dotenv(Path(env_path) / ".env")

eia_key = os.getenv("EIA_API_KEY")
ts_token = os.getenv("TUSHARE_TOKEN")
fred_key = os.getenv("FRED_API_KEY")

print(f"EIA: {eia_key[:6] if eia_key else 'NONE'}...")
print(f"Tushare: {ts_token[:6] if ts_token else 'NONE'}...")
print(f"FRED: {fred_key[:6] if fred_key else 'NONE'}...")

import requests

# 1. EIA美湾库存
if eia_key:
    print("\n=== EIA美湾(PADD 3)库存 ===")
    proxies = None
    try:
        requests.get("http://127.0.0.1:10808", timeout=1)
        proxies = {"http":"http://127.0.0.1:10808","https":"http://127.0.0.1:10808"}
    except:
        pass
    
    url = f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={eia_key}&frequency=weekly&data[0]=value&facets[duoarea][]=R3P&facets[product][]=EPC0&sort[0][column]=period&sort[0][direction]=desc&length=2"
    try:
        r = requests.get(url, timeout=15, proxies=proxies)
        d = r.json()
        data = d.get("response",{}).get("data",[])
        if data:
            print(f"  {data[0]['period']}: {data[0].get('value','?')} 千桶")
        else:
            print(f"  无: {json.dumps(d, ensure_ascii=False)[:200]}")
    except Exception as e:
        print(f"  请求失败: {e}")

# 2. FRED - 美湾库存/库存相关
if fred_key:
    print("\n=== FRED库存系列 ===")
    for sid in ["WCSSTUS1", "WCESTUS1", "TOTALSA", "BOGZ1FL145012005Q"]:
        url = f"https://api.stlouisfed.org/fred/series/search?api_key={fred_key}&search_text={sid}&file_type=json&limit=1"
        r = requests.get(url, timeout=10)
        print(f"  {sid}: {r.status_code}")

# 3. Tushare DR007 (Shibor 7天)
if ts_token:
    print("\n=== Tushare DR007/利率 ===")
    # shibor
    payload = {
        "api_name": "shibor",
        "token": ts_token,
        "params": {"start_date": "20260601", "end_date": "20260613"},
        "fields": "date,7_days"
    }
    r = requests.post("http://api.tushare.pro", json=payload, timeout=10)
    data = r.json()
    if data.get("code") == 0 and data.get("data",{}).get("items"):
        items = data["data"]["items"]
        print(f"  shibor 7天: {items[0]} 等{len(items)}条")
    else:
        print(f"  shibor: {json.dumps(data, ensure_ascii=False)[:200]}")
    
    # 银行间质押式回购利率 DR007
    payload2 = {
        "api_name": "repo",
        "token": ts_token,
        "params": {"start_date": "20260601", "end_date": "20260613"},
        "fields": "date,7_days"
    }
    r2 = requests.post("http://api.tushare.pro", json=payload2, timeout=10)
    print(f"  repo: {json.dumps(r2.json(), ensure_ascii=False)[:200]}")
    
    # MLF利率
    payload3 = {
        "api_name": "mlf",
        "token": ts_token,
        "params": {"start_date": "20260101", "end_date": "20260613"},
        "fields": "date,rate"
    }
    r3 = requests.post("http://api.tushare.pro", json=payload3, timeout=10)
    d3 = r3.json()
    if d3.get("code") == 0 and d3.get("data",{}).get("items"):
        print(f"  mlf: {d3['data']['items'][0]}")
    else:
        print(f"  mlf: {json.dumps(d3, ensure_ascii=False)[:200]}")
