#!/usr/bin/env python3
"""Round 7 - Final attempt to get USDA PDF and BDI data."""
import requests, json, sys, re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

PROXY = {"http":"http://127.0.0.1:10808","https":"http://127.0.0.1:10808"}
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# === 3. USDA - Try to download and parse the crop progress PDF ===
print("=== 3. USDA - Download crop progress PDF ===")
# From the Cornell page, the latest PDF URL is:
# https://www.nass.usda.gov/sites/default/release-files/795933/prog2326.pdf
pdf_url = "https://www.nass.usda.gov/sites/default/release-files/795933/prog2326.pdf"
try:
    r = requests.get(pdf_url, timeout=30, headers=UA, proxies=PROXY)
    print(f"  Status: {r.status_code}, Content-Type: {r.headers.get('Content-Type')}")
    if r.status_code == 200:
        print(f"  Length: {len(r.content)} bytes")
        import io, pdfplumber
        with pdfplumber.open(io.BytesIO(r.content)) as pdf:
            print(f"  Pages: {len(pdf.pages)}")
            for pi in range(min(6, len(pdf.pages))):
                page = pdf.pages[pi]
                text = page.extract_text() or ""
                print(f"\n  --- Page {pi} ---")
                print(f"  {text[:1200]}")
        except Exception as e:
        print(f"  ❌ Error: {e}")

# === 4. BDI - Try to parse from Investing.com ===
print("\n=== 4. BDI - Parse from Investing.com ===")
try:
    r = requests.get("https://www.investing.com/indices/baltic-dry", 
                     timeout=30, headers={
                         **UA,
                         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                         "Accept-Language": "en-US,en;q=0.5",
                     }, proxies=PROXY)
    print(f"  Status: {r.status_code}, Len: {len(r.text)}")
    soup = BeautifulSoup(r.text, "lxml")
    # Find price data
    text = soup.get_text()
    # Look for BDI value
    for m in re.finditer(r'[\d,]+\.?\d*', text):
        val = m.group()
        start = max(0, m.start()-50)
        end = min(len(text), m.end()+50)
        ctx = text[start:end]
        if "baltic" in ctx.lower() or "bdi" in ctx.lower() or "dry" in ctx.lower():
            print(f"  Found: {val} in context: {ctx}")
    
    # Try specific investing.com data attributes
    # Look for the instrument data 
    for tag in soup.find_all(["span", "div", "data", "meta"]):
        cls = tag.get("class", [])
        id_attr = tag.get("id", "")
        if any(x in str(cls).lower() for x in ["price", "last", "value", "bid", "ask"]):
            print(f"  {cls}: {tag.get_text(strip=True)[:50]}")
    
    # Try to find the current price from JSON-LD
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            print(f"  JSON-LD: {json.dumps(data, indent=2)[:300]}")
        except:
            pass
except Exception as e:
    print(f"  ❌ Error: {e}")

# Try FT.com for BDI
print("\n--- Try FT.com for BDI ---")
try:
    r = requests.get("https://markets.ft.com/data/indices/tearsheet/summary?s=BDI:IND",
                     timeout=30, headers=UA, proxies=PROXY)
    print(f"  Status: {r.status_code}, Len: {len(r.text)}")
    soup = BeautifulSoup(r.text, "lxml")
    text = soup.get_text()
    for m in re.finditer(r'[\d,]+\.?\d*', text):
        val = m.group()
        if len(val) >= 3:
            start = max(0, m.start()-30)
            end = min(len(text), m.end()+30)
            ctx = text[start:end]
            if "baltic" in ctx.lower() or "bdi" in ctx.lower():
                print(f"  Found: {val} in context: {ctx}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# === Try getting NOAA precip data from a simpler source ===
print("\n=== NOAA - Try drought.gov data API ===")
try:
    # Try the drought monitor JSON API
    r = requests.get("https://droughtmonitor.unl.edu/Ajax.aspx/GetDMData",
                     timeout=15, headers={"Content-Type": "application/json"},
                     json={"area":"US","type":"C","statisticsType":"1"},
                     proxies=PROXY)
    print(f"  Status: {r.status_code}, Len: {len(r.text)}")
    print(f"  {r.text[:500]}")
except Exception as e:
    print(f"  ❌ Error: {e}")
