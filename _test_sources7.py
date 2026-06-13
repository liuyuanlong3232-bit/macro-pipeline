#!/usr/bin/env python3
"""Round 6 - Get final working data for each source."""
import requests, json, sys, re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

PROXY = {"http":"http://127.0.0.1:10808","https":"http://127.0.0.1:10808"}
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# === 1. Baker Hughes - Parse the homepage table ===
print("=== 1. Baker Hughes - Homepage table data ===")
try:
    r = requests.get("https://rigcount.bakerhughes.com/", timeout=15, proxies=PROXY)
    soup = BeautifulSoup(r.text, "lxml")
    table = soup.find("table")
    if table:
        rows = table.find_all("tr")
        print(f"Rows: {len(rows)}")
        for ri, row in enumerate(rows):
            cells = row.find_all(["th", "td"])
            texts = [c.get_text(strip=True) for c in cells]
            print(f"  Row {ri}: {texts}")
            
            # Try to parse data rows
            if ri > 0 and len(cells) >= 6:
                area = texts[0]
                count = texts[2]
                chg = texts[3]
                date = texts[1]
                print(f"    -> Area: {area}, Count: {count}, Date: {date}, Change: {chg}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# === 2. NOAA - Check if drought.gov has an API ===
print("\n=== 2. NOAA - Try drought.gov API or simpler text page ===")
noaa_attempts = [
    "https://www.drought.gov/api/current.json?area=US",
    "https://droughtmonitor.unl.edu/data/json/DMArea_json.aspx?area=US",
    "https://www.cpc.ncep.noaa.gov/products/Soilmst_Monitoring/US/Soilmst/Soilmst.shtml",
    "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/cdus/prcp_temp_tables/daily/PRCP_US_daily.html",
]
for url in noaa_attempts:
    try:
        r = requests.get(url, timeout=15, proxies=PROXY, headers=UA)
        print(f"  {url} -> Status: {r.status_code}, Len: {len(r.text)}")
        if r.status_code == 200:
            print(f"    First 300: {r.text[:300]}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

# === 3. USDA - Try the crop progress PDF from different URL ===
print("\n=== 3. USDA - Try PDF from NASS directly ===")
usda_urls = [
    "https://www.nass.usda.gov/Publications/State_Crop_Progress_and_Condition/",
    "https://www.nass.usda.gov/Publications/Calendar/report_by_date.php?report_id=17011",
    "https://usda.library.cornell.edu/concern/publications/8336h188j?locale=en",
]
for url in usda_urls:
    try:
        r = requests.get(url, timeout=15, proxies=PROXY, headers=UA)
        print(f"  {url} -> Status: {r.status_code}")
        if r.status_code == 200:
            # Find PDF links
            soup = BeautifulSoup(r.text, "lxml")
            pdf_links = []
            for a in soup.find_all("a"):
                href = a.get("href", "")
                if href.endswith(".pdf"):
                    full_url = href if href.startswith("http") else f"https://www.nass.usda.gov{href}" if href.startswith("/") else href
                    pdf_links.append((a.get_text(strip=True), full_url))
            for txt, url in pdf_links[:5]:
                print(f"    PDF: {txt[:50]:50s} -> {url}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

# Try NASS direct PDF
print("\n--- Try NASS direct crop progress results ---")
try:
    # The crop progress report is released weekly on Mondays
    # Try the most recent Monday
    r = requests.get("https://www.nass.usda.gov/Charts_and_Maps/Crop_Progress_&_Condition/", 
                     timeout=15, proxies=PROXY, headers=UA)
    print(f"  Status: {r.status_code}, Len: {len(r.text)}")
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "lxml")
        # Look for content
        text = soup.get_text()
        for kw in ["corn", "soybean", "good", "excellent", "condition", "progress"]:
            idx = text.lower().find(kw.lower())
            if idx >= 0:
                print(f"  '{(kw+':').ljust(12)} {text[max(0,idx-30):idx+100]}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Try the USDA JSON/API 
print("\n--- Try USDA quick stats API ---")
try:
    r = requests.get("https://quickstats.nass.usda.gov/api/api_GET/?key=DEMO&format=JSON&commodity_desc=CORN&statisticcat_desc=PROGRESS&freq_desc=WEEKLY&year__LE=2026",
                     timeout=15, proxies=PROXY, headers=UA)
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"  Keys: {list(data.keys())}")
        if "data" in data:
            print(f"  Data count: {len(data['data'])}")
            for d in data["data"][:3]:
                print(f"    {json.dumps(d, indent=2)[:200]}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# === 4. BDI - Try to get from various sources ===
print("\n=== 4. BDI - Try Baltic Exchange or other free sources ===")
bdi_urls = [
    "https://www.balticexchange.com/en/index.html",
    "https://markets.ft.com/data/indices/tearsheet/summary?s=BDI:IND",
    "https://www.marketwatch.com/investing/index/bdi",
    "https://www.investing.com/indices/baltic-dry-historical-data",
]
for url in bdi_urls:
    try:
        r = requests.get(url, timeout=15, proxies=PROXY, headers=UA)
        print(f"  {url} -> Status: {r.status_code}, Len: {len(r.text)}")
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "lxml")
            text = soup.get_text()[:500]
            print(f"    Text: {text[:200]}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

# Try a simpler BDI API
print("\n--- Try API-based BDI sources ---")
api_urls = [
    "https://api.bitget.com/api/v2/market/tickers?symbol=BDIUSDT",
    "https://financialmodelingprep.com/api/v3/profile/BDI?apikey=test",
]
for url in api_urls:
    try:
        r = requests.get(url, timeout=10, proxies=PROXY)
        print(f"  {url} -> Status: {r.status_code}, Len: {len(r.text)}")
    except:
        print(f"  ❌ Error: {url}")

# Try to get BDI from cnyes.com or macrodatas
print("\n--- Try alternative BDI sources ---")
alt_bdi = [
    "https://www.macromicro.me/collections/18/bdi-shipping",
    "https://cdn.quik.app/feeds/1.0/indices/BDI",
]
for url in alt_bdi:
    try:
        r = requests.get(url, timeout=15, proxies=PROXY, headers=UA)
        print(f"  {url} -> Status: {r.status_code}, Len: {len(r.text)}")
        if r.status_code == 200:
            print(f"    Content: {r.text[:300]}")
    except Exception as e:
        print(f"    ❌ Error: {e}")
