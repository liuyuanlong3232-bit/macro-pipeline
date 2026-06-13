#!/usr/bin/env python3
"""Deep dive into working data sources."""
import requests, json, sys, re
from scrapling import Fetcher

PROXY = {"http":"http://127.0.0.1:10808","https":"http://127.0.0.1:10808"}

# === 1. Baker Hughes - Parse the table using Scrapling ===
print("=== 1. Baker Hughes - Parsing with Scrapling ===")
try:
    f = Fetcher()
    r = f.fetch("https://rigcount.bakerhughes.com/intl-rig-count", proxy=PROXY)
    print(f"Status: {r.status}, Len: {len(r.text)}")
    
    # Find the tables
    tables = r.css("table.nirtable")
    print(f"Tables found: {len(tables)}")
    
    for ti, tbl in enumerate(tables):
        print(f"\n--- Table {ti} ---")
        rows = tbl.css("tr")
        print(f"  Rows: {len(rows)}")
        for ri, row in enumerate(rows[:10]):
            cells = row.css("th, td")
            cell_texts = [c.text.strip() for c in cells]
            print(f"  Row {ri}: {cell_texts}")
    
except Exception as e:
    print(f"  ❌ Error: {e}")

# === 2. NOAA - Try different URLs ===
print("\n=== 2. NOAA - More URL attempts ===")
noaa_urls = [
    "https://www.cpc.ncep.noaa.gov/",
    "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/precip.shtml",
    "https://www.cpc.ncep.noaa.gov/products/precip/realtime/retro.shtml",
    "https://www.weather.gov/",
    "https://www.drought.gov/states/us",
]
for url in noaa_urls:
    try:
        r = requests.get(url, timeout=15, proxies=PROXY,
                         headers={"User-Agent": "Mozilla/5.0"})
        print(f"  URL: {url} -> Status: {r.status_code}, Len: {len(r.text)}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

# === 4. BDI - Check what BDI returns ===
print("\n=== 4. BDI - Deep check on Yahoo Finance ===")
try:
    r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/BDI",
                     timeout=15, proxies=PROXY,
                     headers={"User-Agent": "Mozilla/5.0"})
    print(f"Status: {r.status_code}")
    data = r.json()
    print(f"Raw JSON: {json.dumps(data, indent=2)[:1000]}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Try BDI as a futures or index from Yahoo
print("\n--- Trying Yahoo search for BDI ---")
try:
    r = requests.get("https://query1.finance.yahoo.com/v1/finance/search?q=baltic+exchange+BDI",
                     timeout=15, proxies=PROXY,
                     headers={"User-Agent": "Mozilla/5.0"})
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        quotes = data.get("quotes", [])
        for q in quotes[:10]:
            print(f"  {q.get('symbol')} - {q.get('shortname')}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Also try different format for BDI
print("\n--- Try BDI with different Yahoo API endpoints ---")
for endpoint in [
    "https://query2.finance.yahoo.com/v8/finance/chart/BDI",
    "https://query1.finance.yahoo.com/v8/finance/chart/BDI?range=1mo&interval=1d",
]:
    try:
        r = requests.get(endpoint, timeout=15, proxies=PROXY,
                         headers={"User-Agent": "Mozilla/5.0"})
        print(f"  Endpoint: {endpoint}")
        print(f"  Status: {r.status_code}, Len: {len(r.text)}")
        if r.status_code == 200:
            print(f"  Body: {r.text[:500]}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
