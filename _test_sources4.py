#!/usr/bin/env python3
"""Round 3 - find alternative sources for NOAA and BDI, explore Baker/USDA in depth."""
import requests, json, sys, re
from bs4 import BeautifulSoup

PROXY = {"http":"http://127.0.0.1:10808","https":"http://127.0.0.1:10808"}
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# === 1. Baker Hughes - parse with BeautifulSoup ===
print("=== 1. Baker Hughes - Parse tables ===")
try:
    r = requests.get("https://rigcount.bakerhughes.com/intl-rig-count", timeout=15, proxies=PROXY)
    soup = BeautifulSoup(r.text, "lxml")
    tables = soup.find_all("table", class_="nirtable")
    print(f"Tables found: {len(tables)}")
    for ti, tbl in enumerate(tables):
        print(f"\n--- Table {ti} ---")
        rows = tbl.find_all("tr")
        for ri, row in enumerate(rows[:15]):
            cells = row.find_all(["th", "td"])
            texts = [c.get_text(strip=True) for c in cells]
            print(f"  Row {ri}: {texts}")
except Exception as e:
    print(f"  ❌ Error: {e}")
    import traceback; traceback.print_exc()

# === 2. NOAA - try finding CPC drought/precip pages ===
print("\n=== 2. NOAA - Find precip pages ===")
noaa_urls = [
    "https://www.cpc.ncep.noaa.gov/products/Drought/",
    "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/regional_monitoring/palmer_drought/wpda.shtml",
    "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/cdus/prcp_temp_tables/",
    "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/regional_monitoring/",
]
for url in noaa_urls:
    try:
        r = requests.get(url, timeout=15, proxies=PROXY, headers=UA)
        print(f"  URL: {url} -> Status: {r.status_code}, Len: {len(r.text)}")
        if r.status_code == 200:
            # Find links with "precip" in them
            soup = BeautifulSoup(r.text, "lxml")
            links = [a.get("href") for a in soup.find_all("a") if a.get("href") and "precip" in a.get("href", "").lower()]
            print(f"    Precip links: {links[:10]}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n--- Try drought.gov for US agriculture precip info ---")
try:
    r = requests.get("https://www.drought.gov/", timeout=15, proxies=PROXY, headers=UA)
    print(f"  Status: {r.status_code}, Len: {len(r.text)}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# === 3. USDA - Parse NASS page for crop progress links ===
print("\n=== 3. USDA - Parse NASS page ===")
try:
    r = requests.get("https://www.nass.usda.gov/Publications/State_Crop_Progress_and_Condition/",
                     timeout=15, proxies=PROXY, headers=UA)
    soup = BeautifulSoup(r.text, "lxml")
    links = soup.find_all("a")
    # Find links with "crop" or "progress" or "condition"
    relevant = []
    for a in links:
        href = a.get("href", "")
        txt = a.get_text(strip=True)
        if any(x in href.lower() for x in ["crop", "progress", "weekly", "report"]):
            relevant.append((txt, href))
        if any(x in txt.lower() for x in ["crop", "corn", "soybean", "wheat", "progress"]):
            relevant.append((txt, href))
    print(f"  Relevant links: {len(relevant)}")
    for txt, href in relevant[:20]:
        print(f"    {txt[:60]:60s} -> {href}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# === 4. BDI - try finding Baltic Dry Index on Yahoo alternatives ===
print("\n=== 4. BDI - Alternative sources ===")
# Try searching Yahoo for "Baltic Dry"
try:
    r = requests.get("https://query1.finance.yahoo.com/v1/finance/search?q=baltic+dry",
                     timeout=15, proxies=PROXY, headers=UA)
    print(f"Yahoo search 'baltic dry': Status {r.status_code}")
    data = r.json()
    for q in data.get("quotes", []):
        print(f"  {q.get('symbol', '?')}: {q.get('shortname', '?')}")
    for q in data.get("news", []):
        pass
except Exception as e:
    print(f"  ❌ Error: {e}")

# Try investing.com or other free source
# BDI is published by the Baltic Exchange, try finding a simple source
print("\n--- Try alternative BDI data sources ---")
bdi_sources = [
    "https://www.balticexchange.com/en/index.html",
    "https://tradingeconomics.com/commodity/bdi",
]
for url in bdi_sources:
    try:
        r = requests.get(url, timeout=15, proxies=PROXY, headers=UA)
        print(f"  {url} -> Status: {r.status_code}, Len: {len(r.text)}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
