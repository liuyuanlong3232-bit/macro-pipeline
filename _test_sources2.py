#!/usr/bin/env python3
"""Test all 4 data sources - round 2 with alternates."""
import requests, json, sys, re

PROXY = {"http":"http://127.0.0.1:10808","https":"http://127.0.0.1:10808"}

# === 1. Baker Hughes - already works, now examine the content ===
print("=== 1. Baker Hughes - Content Analysis ===")
try:
    r = requests.get("https://rigcount.bakerhughes.com/intl-rig-count",
                     timeout=15, proxies=PROXY)
    print(f"Status: {r.status_code}, Len: {len(r.text)}")
    # Look for table structure
    text = r.text
    
    # Search for "North America" or "US" or "Canada" totals
    for kw in ["North America", "International", "U.S.", "Canada", "Total", "rig count"]:
        idx = text.lower().find(kw.lower())
        if idx >= 0:
            print(f"  Found '{kw}' at pos {idx}: ...{text[max(0,idx-50):idx+150]}...")
    
    # Try to parse table with Scrapling
    from scrapling import Fetcher
    f = Fetcher()
    # Check what tables exist
    tables = re.findall(r'<table[^>]*>', text)
    print(f"  Tables found: {len(tables)}")
    for i, t in enumerate(tables[:5]):
        print(f"    Table {i}: {t}")
    
    # Look for numbers that look like rig counts
    nums = re.findall(r'(\d{2,3})[,\s]*', text)
    print(f"  Potential rig numbers: {nums[:30]}")
    
except Exception as e:
    print(f"  ❌ Error: {e}")

# === 2. NOAA - try alternate URLs ===
print("\n=== 2. NOAA - Alternate URLs ===")
alt_urls = [
    "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/regional_monitoring/us_precip.shtml",
    "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/weekly_precip.shtml",
    "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/regional_monitoring/precip.shtml",
    "https://www.cpc.ncep.noaa.gov/products/predictions/threats/threats.shtml",
]
for url in alt_urls:
    try:
        r = requests.get(url, timeout=15, proxies=PROXY,
                         headers={"User-Agent": "Mozilla/5.0"})
        print(f"  URL: {url}")
        print(f"    Status: {r.status_code}, Len: {len(r.text)}")
        if r.status_code == 200:
            print(f"    First 200: {r.text[:200]}")
    except Exception as e:
        print(f"    ❌ Error: {e}")

# === 3. USDA ===
print("\n=== 3. USDA Crop Progress ===")
usda_urls = [
    "https://www.nass.usda.gov/Publications/State_Crop_Progress_and_Condition/",
    "https://downloads.usda.library.cornell.edu/usda-esmis/files/8336h188j",
]
for url in usda_urls:
    try:
        r = requests.get(url, timeout=15, proxies=PROXY,
                         headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        print(f"  URL: {url}")
        print(f"    Status: {r.status_code}, Len: {len(r.text)}")
        if r.status_code == 200:
            print(f"    First 300: {r.text[:300]}")
    except Exception as e:
        print(f"    ❌ Error: {e}")

# === 4. BDI - try alternatives ===
print("\n=== 4. BDI - Alternate symbols ===")
bdi_urls = [
    "https://query1.finance.yahoo.com/v8/finance/chart/BDI",
    "https://query1.finance.yahoo.com/v8/finance/chart/%5EBDI",
    "https://query1.finance.yahoo.com/v8/finance/chart/BDIY",
    "https://query1.finance.yahoo.com/v8/finance/chart/%5EBALD",
]
for url in bdi_urls:
    try:
        r = requests.get(url, timeout=15, proxies=PROXY,
                         headers={"User-Agent": "Mozilla/5.0"})
        print(f"  URL: {url}")
        print(f"    Status: {r.status_code}, Len: {len(r.text)}")
        if r.status_code == 200:
            data = r.json()
            err = data.get("chart", {}).get("error")
            if err:
                print(f"    Error from API: {err.get('description')}")
            else:
                result = data.get("chart", {}).get("result", [])
                if result:
                    meta = result[0].get("meta", {})
                    print(f"    Regular market price: {meta.get('regularMarketPrice')}")
                    print(f"    Previous close: {meta.get('previousClose')}")
                    indicators = result[0].get("indicators", {})
                    quote = indicators.get("quote", [{}])[0]
                    closes = quote.get("close", [])
                    valid_closes = [c for c in closes if c is not None]
                    print(f"    Latest close: {valid_closes[-1] if valid_closes else 'N/A'}")
    except Exception as e:
        print(f"    ❌ Error: {e}")
