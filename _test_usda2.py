#!/usr/bin/env python3
"""Try to get USDA crop progress data from NASS website."""
import requests, io, re
from bs4 import BeautifulSoup

PROXY = {"http":"http://127.0.0.1:10808","https":"http://127.0.0.1:10808"}
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# Try the calendar landing page for crop progress
print("=== Try NASS calendar landing page ===")
url = "https://www.nass.usda.gov/Publications/Calendar/calendar-landing.php?source=n&year=26&month=06&day=08&report_id=17011"
try:
    r = requests.get(url, timeout=15, headers=UA, proxies=PROXY)
    print(f"Status: {r.status_code}, Len: {len(r.text)}")
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "lxml")
        links = soup.find_all("a")
        for a in links:
            href = a.get("href", "")
            txt = a.get_text(strip=True)
            if href and ("pdf" in href.lower() or "csv" in href.lower() or "xls" in href.lower()):
                print(f"  {txt[:50]:50s} -> {href}")
        # Also look for content divs
        text = soup.get_text()
        for kw in ["corn", "soybean", "good", "excellent", "condition"]:
            idx = text.lower().find(kw)
            if idx >= 0:
                print(f"  '{kw}' at {idx}: {text[max(0,idx-40):idx+100]}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Try the charts and maps page for crop condition
print("\n=== Try NASS Charts & Maps for crop condition ===")
url2 = "https://www.nass.usda.gov/Charts_and_Maps/Crop_Progress_&_Condition/"
try:
    r = requests.get(url2, timeout=15, headers=UA, proxies=PROXY)
    print(f"Status: {r.status_code}, Len: {len(r.text)}")
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "lxml")
        # Find all elements with crop data
        text = soup.get_text()
        # Look for tables or data
        tables = soup.find_all("table")
        print(f"Tables: {len(tables)}")
        for ti, tbl in enumerate(tables[:3]):
            rows = tbl.find_all("tr")
            for row in rows:
                cells = row.find_all(["th", "td"])
                texts = [c.get_text(strip=True) for c in cells]
                print(f"  Table {ti}: {texts}")
        
        # Look for specific data patterns
        for kw in ["corn", "soybean", "good", "excellent", "very poor", "poor", "fair"]:
            for m in re.finditer(r'[\d]+', text):
                idx = m.start()
                ctx = text[max(0,idx-30):idx+30]
                if kw in ctx.lower():
                    print(f"  '{kw}' near {m.group()}: {ctx}")
                    
except Exception as e:
    print(f"  ❌ Error: {e}")

# Try the Crop Progress reports list
print("\n=== Try Crop Progress reports page ===")
url3 = "https://usda.library.cornell.edu/concern/publications/8336h188j?locale=en"
try:
    r = requests.get(url3, timeout=15, headers=UA, proxies=PROXY)
    print(f"Status: {r.status_code}, Len: {len(r.text)}")
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "lxml")
        text = soup.get_text()
        # Extract sections with crop progress data
        # The page has links to each weekly report
        for a in soup.find_all("a"):
            href = a.get("href", "")
            txt = a.get_text(strip=True)
            if "prog23" in href or "prog22" in href:
                print(f"  {txt:40s} -> {href}")
                # Try this PDF
                if href.startswith("/"):
                    full_url = "https://www.nass.usda.gov" + href
                elif href.startswith("http"):
                    full_url = href
                else:
                    full_url = "https://www.nass.usda.gov/" + href
                print(f"    Full URL: {full_url}")
except Exception as e:
    print(f"  ❌ Error: {e}")
