#!/usr/bin/env python3
"""Parse USDA crop progress PDF for corn & soybean condition."""
import requests, io, pdfplumber, re

PROXY = {"http":"http://127.0.0.1:10808","https":"http://127.0.0.1:10808"}
UA = {"User-Agent": "Mozilla/5.0"}

# First get the TXT version
txt_url = "https://esmis.nal.usda.gov/sites/default/release-files/795933/prog2326.txt"
r = requests.get(txt_url, timeout=30, headers=UA, proxies=PROXY)
print(f"TXT Status: {r.status_code}, Len: {len(r.text)}")
if r.status_code == 200:
    print("=== TXT Content (first 4000 chars) ===")
    print(r.text[:4000])
    print("\n...")
    # Look for condition data
    text = r.text
    for kw in ["Corn", "Soybean", "Condition", "Good", "Excellent", "Very poor", "Poor", "Fair"]:
        for m in re.finditer(kw, text):
            start = max(0, m.start()-20)
            end = min(len(text), m.end()+200)
            ctx = text[start:end]
            print(f"\n  '{kw}': {ctx}")
            break

# Now try PDF parsing
print("\n=== PDF Parsing ===")
pdf_url = "https://esmis.nal.usda.gov/sites/default/release-files/795933/prog2326.pdf"
r2 = requests.get(pdf_url, timeout=30, headers=UA, proxies=PROXY)
print(f"PDF Status: {r2.status_code}, Len: {len(r2.content)}")
if r2.status_code == 200:
    with pdfplumber.open(io.BytesIO(r2.content)) as pdf:
        print(f"Pages: {len(pdf.pages)}")
        for pi in range(min(8, len(pdf.pages))):
            text = pdf.pages[pi].extract_text() or ""
            print(f"\n--- Page {pi} ---")
            print(text[:2000])
