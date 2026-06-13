"""Check USDA and other agricultural data sources for Gulf grain stocks and South America carryover"""
import requests, json

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# ============================================================
# 1. USDA FAS Export Sales API (gives export commitments by destination)
# ============================================================
print("=" * 60)
print("1. USDA FAS Export Sales API")
print("=" * 60)
try:
    # USDA FAS API requires no key for some endpoints
    url = "https://apps.fas.usda.gov/export-sales/api/v1/commodity/ALL"
    r = requests.get(url, timeout=20, headers=UA)
    print(f"  FAS Commodity List: {r.status_code}")
    if r.status_code == 200:
        print(f"  Response: {r.text[:500]}")
    else:
        print(f"  {r.text[:200]}")
except Exception as e:
    print(f"  Error: {e}")

# ============================================================
# 2. USDA FAS Grain Inspections for Export - weekly data
#    Barge / Gulf port inspections
# ============================================================
print("\n" + "=" * 60)
print("2. USDA AMS Grain Inspections")
print("=" * 60)
try:
    # USDA AMS market news reports - Gulf grain export inspections
    # This is the official weekly report for grain inspections at export facilities
    url = "https://www.ams.usda.gov/mnreports/gx_gr224.txt"
    r = requests.get(url, timeout=20, headers=UA)
    print(f"  Gulf Grain Inspections TXT: {r.status_code}")
    if r.status_code == 200:
        print(f"  Content (first 1000 chars):\n{r.text[:1000]}")
    else:
        print(f"  {r.text[:200]}")
except Exception as e:
    print(f"  Error: {e}")

# ============================================================
# 3. USDA AMS - weekly grain transportation report
#    Includes barge grain movements to Gulf
# ============================================================
print("\n" + "=" * 60)
print("3. USDA Grain Transportation Report")
print("=" * 60)
try:
    url = "https://www.ams.usda.gov/mnreports/gx_gr116.txt"
    r = requests.get(url, timeout=20, headers=UA)
    print(f"  Grain Transp Report: {r.status_code}")
    if r.status_code == 200:
        print(f"  Content (first 1000 chars):\n{r.text[:1000]}")
    else:
        print(f"  {r.text[:200]}")
except Exception as e:
    print(f"  Error: {e}")

# ============================================================
# 4. USDA WASDE summary (World Agricultural Supply & Demand)
#    This has Brazil/Argentina carryover stocks
# ============================================================
print("\n" + "=" * 60)
print("4. USDA WASDE Report")
print("=" * 60)
try:
    # USDA ERS data API for WASDOE data
    url = "https://www.usda.gov/sites/default/files/documents/WASDE-Latest.pdf"
    r = requests.head(url, timeout=20, headers=UA)
    print(f"  WASDE PDF: {r.status_code}")
except Exception as e:
    print(f"  Error: {e}")

# ============================================================
# 5. Try USDA Quick Stats API for grain stocks
# ============================================================
print("\n" + "=" * 60)
print("5. USDA NASS Quick Stats API")
print("=" * 60)
try:
    # USDA Quick Stats API - needs params
    url = "https://quickstats.nass.usda.gov/api/api_GET/"
    params = {
        "key": "DEMO_KEY",  # public key
        "commodity_desc": "CORN",
        "statisticcat_desc": "STOCKS",
        "agg_level_desc": "STATE",
        "format": "JSON",
        "year__GE": 2025,
    }
    r = requests.get(url, params=params, timeout=20, headers=UA)
    print(f"  NASS Quick Stats: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"  Data keys: {list(data.keys())}")
        print(f"  First item: {json.dumps(data.get('data', [{}])[0], indent=2)[:300]}")
    else:
        print(f"  {r.text[:500]}")
except Exception as e:
    print(f"  Error: {e}")

# ============================================================
# 6. CONAB (Brazil) crop report - try to access
# ============================================================
print("\n" + "=" * 60)
print("6. CONAB Brazil Crop Reports")
print("=" * 60)
try:
    url = "https://www.conab.gov.br/info-agro/safras/graos/boletim-da-safra-de-graos"
    r = requests.get(url, timeout=20, headers=UA)
    print(f"  CONAB page: {r.status_code}")
except Exception as e:
    print(f"  Error: {e}")
