#!/usr/bin/env python3
"""Round 4 - explore specific pages for each source."""
import requests, json, sys, re
from bs4 import BeautifulSoup

PROXY = {"http":"http://127.0.0.1:10808","https":"http://127.0.0.1:10808"}
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# === 1. Baker Hughes - North America Rig Count ===
print("=== 1. Baker Hughes - North America Rig Count ===")
try:
    r = requests.get("https://rigcount.bakerhughes.com/na-rig-count", timeout=15, proxies=PROXY)
    soup = BeautifulSoup(r.text, "lxml")
    tables = soup.find_all("table")
    print(f"Tables found: {len(tables)}")
    for ti, tbl in enumerate(tables):
        print(f"\n--- Table {ti} ---")
        rows = tbl.find_all("tr")
        for ri, row in enumerate(rows[:20]):
            cells = row.find_all(["th", "td"])
            texts = [c.get_text(strip=True) for c in cells]
            print(f"  Row {ri}: {texts}")
except Exception as e:
    print(f"  ❌ Error: {e}")
    import traceback; traceback.print_exc()

# === 2. NOAA - try CPC precip tables page ===
print("\n=== 2. NOAA - CPC Precip Tables ===")
try:
    r = requests.get("https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/cdus/prcp_temp_tables/",
                     timeout=15, proxies=PROXY, headers=UA)
    soup = BeautifulSoup(r.text, "lxml")
    links = soup.find_all("a")
    print(f"Links found: {len(links)}")
    for a in links:
        href = a.get("href", "")
        txt = a.get_text(strip=True)
        if href and not href.startswith("#"):
            print(f"  {txt:40s} -> {href}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# === 3. USDA - Find actual crop progress report ===
print("\n=== 3. USDA - Find crop progress reports ===")
try:
    r = requests.get("https://www.nass.usda.gov/Publications/Calendar/reports_by_date.php",
                     timeout=15, proxies=PROXY, headers=UA)
    soup = BeautifulSoup(r.text, "lxml")
    links = soup.find_all("a")
    crop_links = []
    for a in links:
        href = a.get("href", "")
        txt = a.get_text(strip=True)
        if "crop" in txt.lower() or "progress" in txt.lower() or "Crop" in href:
            crop_links.append((txt, href))
    print(f"Crop-related links: {len(crop_links)}")
    for txt, href in crop_links[:30]:
        print(f"  {txt[:60]:60s} -> {href}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Try the USDA library API for crop progress
print("\n--- Try USDA library API ---")
try:
    r = requests.get("https://usda.library.cornell.edu/concern/publications/8336h188j?locale=en",
                     timeout=15, proxies=PROXY, headers=UA)
    print(f"Status: {r.status_code}, Len: {len(r.text)}")
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "lxml")
        links = soup.find_all("a")
        for a in links:
            href = a.get("href", "")
            txt = a.get_text(strip=True)
            if any(x in href.lower() for x in [".pdf", ".csv", ".xls"]):
                print(f"  {txt[:50]:50s} -> {href}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# === 4. BDI - Try to parse TradingEconomics ===
print("\n=== 4. BDI - TradingEconomics parse ===")
try:
    r = requests.get("https://tradingeconomics.com/commodity/bdi", timeout=15, proxies=PROXY, headers=UA)
    soup = BeautifulSoup(r.text, "lxml")
    # Look for price data
    price_el = soup.find("span", class_=re.compile(r"price|value|last"))
    if price_el:
        print(f"Price element: {price_el.get_text(strip=True)}")
    # Look for tables or divs with data
    for cls in ["table", "data", "value", "price", "current"]:
        els = soup.find_all(class_=re.compile(cls, re.I))
        if els:
            for el in els[:5]:
                text = el.get_text(strip=True)[:100]
                print(f"  {cls}: {text}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Try investing.com for BDI
print("\n--- Try investing.com for BDI ---")
try:
    r = requests.get("https://www.investing.com/indices/baltic-dry", timeout=15, proxies=PROXY, headers={
        **UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    })
    print(f"Status: {r.status_code}, Len: {len(r.text)}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Try to find BDI from a JSON API
print("\n--- Try market index APIs for BDI ---")
bdi_apis = [
    "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=BDI&apikey=demo",
    "https://financialmodelingprep.com/api/v3/quote/BDI?apikey=demo",
]
for url in bdi_apis:
    try:
        r = requests.get(url, timeout=15, proxies=PROXY)
        print(f"  {url[:60]:60s} -> Status: {r.status_code}")
        print(f"    {r.text[:200]}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
