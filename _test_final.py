#!/usr/bin/env python3
"""Round 7 - Final attempt to get USDA PDF and BDI data."""
import requests, json, sys, re, io
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pdfplumber

PROXY = {"http":"http://127.0.0.1:10808","https":"http://127.0.0.1:10808"}
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# === 3. USDA - Download and parse crop progress PDF ===
print("=== 3. USDA - Download crop progress PDF ===")
pdf_url = "https://www.nass.usda.gov/sites/default/release-files/795933/prog2326.pdf"
try:
    r = requests.get(pdf_url, timeout=30, headers=UA, proxies=PROXY)
    print(f"  Status: {r.status_code}, Content-Type: {r.headers.get('Content-Type')}")
    if r.status_code == 200:
        print(f"  Length: {len(r.content)} bytes")
        with pdfplumber.open(io.BytesIO(r.content)) as pdf:
            print(f"  Pages: {len(pdf.pages)}")
            for pi in range(min(6, len(pdf.pages))):
                page = pdf.pages[pi]
                text = page.extract_text() or ""
                print(f"\n  --- Page {pi} ---")
                print(f"  {text[:1200]}")
    else:
        print(f"  Response: {r.text[:300]}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# === 4. BDI - Parse from Investing.com ===
print("\n=== 4. BDI - Parse from Investing.com ===")
try:
    r = requests.get("https://www.investing.com/indices/baltic-dry",
                     timeout=30, headers={
                         **UA,
                         "Accept-Language": "en-US,en;q=0.5",
                     }, proxies=PROXY)
    print(f"  Status: {r.status_code}, Len: {len(r.text)}")
    soup = BeautifulSoup(r.text, "lxml")
    text = soup.get_text()
    # Search for "Baltic Dry" and nearby numbers
    for m in re.finditer(r'([\d,]+\.?\d*)', text):
        val = m.group()
        start = max(0, m.start()-80)
        end = min(len(text), m.end()+80)
        ctx = text[start:end]
        if "baltic" in ctx.lower() or "bdi" in ctx.lower():
            print(f"  Found: {val} -> ...{ctx}...")
    
    # Try data attributes
    for tag in soup.find_all(attrs={"data-test": True}):
        print(f"  data-test: {tag.get('data-test')} = {tag.get_text(strip=True)[:50]}")
    
    # Try JSON-LD
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            print(f"  JSON-LD: {json.dumps(data, indent=2)[:500]}")
        except:
            pass
except Exception as e:
    print(f"  ❌ Error: {e}")
