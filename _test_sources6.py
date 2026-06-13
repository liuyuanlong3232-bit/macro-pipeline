#!/usr/bin/env python3
"""Round 5 - Finalize data source access methods."""
import requests, json, sys, re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

PROXY = {"http":"http://127.0.0.1:10808","https":"http://127.0.0.1:10808"}
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# === 1. Baker Hughes - Check main page for live rig count ===
print("=== 1. Baker Hughes - Check main/home page ===")
try:
    r = requests.get("https://rigcount.bakerhughes.com/", timeout=15, proxies=PROXY)
    soup = BeautifulSoup(r.text, "lxml")
    # Look for any numbers or rig counts on the page
    text = soup.get_text()
    # Find parts mentioning rig count numbers
    for kw in ["U.S.", "Canada", "Total", "rig", "count", "North America"]:
        idx = text.lower().find(kw.lower())
        if idx >= 0:
            print(f"  '{kw}' context: ...{text[max(0,idx-30):idx+80]}...")
    
    # Look for the current rig count numbers
    # Check for numbers near keywords
    import re
    for kw in ["U.S.", "Canada", "North America", "total", "rig count"]:
        parts = re.split(r'(?<=' + kw + r')\s*[=:]\s*', text, flags=re.I)
        if len(parts) > 1:
            print(f"  After '{kw}': {parts[1][:100]}")
    
    # Try to find the actual rig count display
    tables = soup.find_all("table")
    print(f"\n  Tables: {len(tables)}")
    for ti, tbl in enumerate(tables):
        txt = tbl.get_text(strip=True)
        if any(x in txt.lower() for x in ["rig", "count", "total", "u.s.", "canada"]):
            print(f"  Table {ti} relevant text: {txt[:200]}")
    
    # Check for script data
    scripts = soup.find_all("script")
    for s in scripts:
        if s.string and ("rig" in s.string.lower() or "count" in s.string.lower() or "data" in s.string.lower()):
            print(f"  Script data: {s.string[:200]}")
            
except Exception as e:
    print(f"  ❌ Error: {e}")

# === 2. NOAA - try drought.gov/usda joint site ===
print("\n=== 2. NOAA - Check drought.gov for ag region precip ===")
try:
    r = requests.get("https://www.drought.gov/", timeout=15, proxies=PROXY, headers=UA)
    print(f"  Status: {r.status_code}, Len: {len(r.text)}")
    soup = BeautifulSoup(r.text, "lxml")
    # Find any data/precip related content
    text = soup.get_text()
    for kw in ["precip", "drought", "moisture", "condition", "agriculture"]:
        matches = [m.start() for m in re.finditer(kw, text, re.I)]
        if matches:
            print(f"  '{kw}' found {len(matches)} times")
except Exception as e:
    print(f"  ❌ Error: {e}")

# === 3. USDA - Parse the latest crop progress PDF URL ===
print("\n=== 3. USDA - Get crop progress data from PDF ===")
# The latest crop progress PDF from Cornell
pdf_url = "https://downloads.usda.library.cornell.edu/usda-esmis/files/8336h188j"
try:
    r = requests.get(pdf_url, timeout=15, proxies=PROXY, headers=UA)
    print(f"  Status: {r.status_code}, Content-Type: {r.headers.get('Content-Type')}")
    if r.status_code == 200:
        print(f"  Content length: {len(r.content)}")
        # Try extracting text from PDF
        try:
            import io
            import PyPDF2
            pdf_file = io.BytesIO(r.content)
            reader = PyPDF2.PdfReader(pdf_file)
            print(f"  Pages: {len(reader.pages)}")
            for pi in range(min(3, len(reader.pages))):
                page_text = reader.pages[pi].extract_text()
                print(f"  Page {pi}: {page_text[:500]}")
        except ImportError:
            # Try pdfminer
            pass
    # Also try direct PDF URL
    print("\n--- Try specific PDF ---")
    pdf_url2 = "https://downloads.usda.library.cornell.edu/usda-esmis/files/8336h188j/795933/prog2326.pdf"
    r2 = requests.get(pdf_url2, timeout=15, proxies=PROXY, headers=UA)
    print(f"  Status: {r2.status_code}, Content-Type: {r2.headers.get('Content-Type')}")
    if r2.status_code == 200:
        print(f"  Content length: {len(r2.content)}")
        try:
            import io, PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(r2.content))
            print(f"  Pages: {len(reader.pages)}")
            for pi in range(min(5, len(reader.pages))):
                page_text = reader.pages[pi].extract_text()
                print(f"  --- Page {pi} ---")
                print(page_text[:800])
        except ImportError:
            print(f"  Text: {r2.text[:500]}")
except Exception as e:
    print(f"  ❌ Error: {e}")
    import traceback; traceback.print_exc()

# === 4. BDI - Try to extract from TradingEconomics or Investing.com ===
print("\n=== 4. BDI - Extract from TradingEconomics ===")
try:
    r = requests.get("https://tradingeconomics.com/commodity/bdi", timeout=15, proxies=PROXY, headers=UA)
    soup = BeautifulSoup(r.text, "lxml")
    # Find the overview div
    ov = soup.find("div", class_=re.compile(r"overview|data|stats", re.I))
    if ov:
        print(f"  Overview: {ov.get_text(strip=True)[:200]}")
    # Find span with bdi value
    spans = soup.find_all("span")
    for sp in spans:
        txt = sp.get_text(strip=True)
        if re.match(r'^[\d,]+\.?\d*$', txt) and len(txt) >= 3:
            # Check nearby text
            parent = sp.parent
            parent_text = parent.get_text(strip=True)
            if "baltic" in parent_text.lower() or "bdi" in parent_text.lower():
                print(f"  Found BDI value: {txt} in context: {parent_text[:200]}")
    
    # Try finding the table
    data_table = soup.find("table", class_=re.compile(r"table", re.I))
    if data_table:
        rows = data_table.find_all("tr")
        for row in rows:
            cells = row.find_all(["th", "td"])
            texts = [c.get_text(strip=True) for c in cells]
            row_text = " | ".join(texts)
            if "baltic" in row_text.lower() or "bdi" in row_text.lower() or "dry" in row_text.lower():
                print(f"  BDI row: {row_text}")
    
    # Search entire text for "Baltic"
    text = soup.get_text()
    idx = text.lower().find("baltic")
    if idx >= 0:
        print(f"  'Baltic' context: {text[max(0,idx-20):idx+150]}")
    
    # Look for BDI in the page structure
    for tag in soup.find_all(["h1", "h2", "h3", "h4"]):
        txt = tag.get_text(strip=True)
        if "baltic" in txt.lower() or "bdi" in txt.lower() or "dry" in txt.lower():
            print(f"  Heading: {txt}")
            # Get next sibling for value
            ns = tag.find_next_sibling()
            if ns:
                print(f"  Next: {ns.get_text(strip=True)[:100]}")
except Exception as e:
    print(f"  ❌ Error: {e}")
