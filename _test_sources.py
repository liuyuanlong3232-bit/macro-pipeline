#!/usr/bin/env python3
"""Test all 4 data sources to check connectivity."""
import requests, json, sys

PROXY = {"http":"http://127.0.0.1:10808","https":"http://127.0.0.1:10808"}

def test_baker():
    print("=== 1. Baker Hughes Rig Count ===")
    try:
        r = requests.get("https://rigcount.bakerhughes.com/intl-rig-count",
                         timeout=15, proxies=PROXY)
        print(f"  Status: {r.status_code}, Len: {len(r.text)}")
        if "rig count" in r.text.lower() or "baker" in r.text.lower():
            print("  ✅ Got rig count page")
            # Find numbers
            import re
            nums = re.findall(r'[\d,]+', r.text)
            print(f"  Numbers found: {nums[:20]}")
        else:
            print(f"  First 300 chars: {r.text[:300]}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

def test_noaa():
    print("\n=== 2. NOAA US Precipitation ===")
    for url in [
        "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/regional_monitoring/us_precip.shtml",
        "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/weekly_precip.shtml"
    ]:
        try:
            r = requests.get(url, timeout=15, proxies=PROXY)
            print(f"  URL: {url}")
            print(f"  Status: {r.status_code}, Len: {len(r.text)}")
            if r.status_code == 200:
                # Check if we got actual content
                txt = r.text[:500]
                print(f"  First 500 chars: {txt}")
            break
        except Exception as e:
            print(f"  ❌ Error: {e}")

def test_usda():
    print("\n=== 3. USDA Crop Progress ===")
    urls = [
        "https://www.nass.usda.gov/Publications/State_Crop_Progress_and_Condition/",
        "https://usda.library.cornell.edu/concern/publications/8336h188j"
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=15, proxies=PROXY,
                             headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
            print(f"  URL: {url}")
            print(f"  Status: {r.status_code}, Len: {len(r.text)}")
            if r.status_code == 200:
                txt = r.text[:500]
                print(f"  First 500 chars: {txt}")
            break
        except Exception as e:
            print(f"  ❌ Error: {e}")

def test_bdi():
    print("\n=== 4. BDI from Yahoo Finance ===")
    try:
        r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/%5EBDI",
                         timeout=15, proxies=PROXY,
                         headers={"User-Agent": "Mozilla/5.0"})
        print(f"  Status: {r.status_code}, Len: {len(r.text)}")
        if r.status_code == 200:
            data = r.json()
            print(f"  JSON keys: {list(data.keys())}")
            result = data.get("chart", {}).get("result", [])
            if result:
                meta = result[0].get("meta", {})
                print(f"  Regular market price: {meta.get('regularMarketPrice')}")
                print(f"  Previous close: {meta.get('previousClose')}")
                # Get latest close
                indicators = result[0].get("indicators", {})
                quote = indicators.get("quote", [{}])[0]
                closes = quote.get("close", [])
                valid_closes = [c for c in closes if c is not None]
                if valid_closes:
                    print(f"  Latest close: {valid_closes[-1]}")
                    print(f"  ✅ Got BDI data! ({len(valid_closes)} data points)")
            else:
                print(f"  Raw: {json.dumps(data, indent=2)[:500]}")
        else:
            print(f"  Response: {r.text[:500]}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

test_baker()
test_noaa()
test_bdi()
