#!/usr/bin/env python3
"""Test USDA PDF from Cornell directly."""
import requests, io, pdfplumber, re

PROXY = {"http":"http://127.0.0.1:10808","https":"http://127.0.0.1:10808"}
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# The full PDF URL from Cornell library
pdf_url = "https://downloads.usda.library.cornell.edu/usda-esmis/files/8336h188j/795933/prog2326.pdf"
print(f"Trying: {pdf_url}")
r = requests.get(pdf_url, timeout=30, headers=UA, proxies=PROXY)
print(f"Status: {r.status_code}, Type: {r.headers.get('Content-Type')}")
if r.status_code == 200:
    with pdfplumber.open(io.BytesIO(r.content)) as pdf:
        print(f"Pages: {len(pdf.pages)}")
        for pi in range(min(6, len(pdf.pages))):
            text = pdf.pages[pi].extract_text() or ""
            print(f"\n--- Page {pi} ---")
            print(text[:1500])
else:
    print(f"Response: {r.text[:300]}")
