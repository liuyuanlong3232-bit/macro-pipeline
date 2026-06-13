#!/usr/bin/env python3
"""Try USDA PDF with referer header."""
import requests, io, pdfplumber

PROXY = {"http":"http://127.0.0.1:10808","https":"http://127.0.0.1:10808"}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://usda.library.cornell.edu/concern/publications/8336h188j?locale=en",
    "Accept": "application/pdf,application/octet-stream,*/*",
}

pdf_url = "https://www.nass.usda.gov/sites/default/release-files/795933/prog2326.pdf"
r = requests.get(pdf_url, timeout=30, headers=HEADERS, proxies=PROXY)
print(f"Status: {r.status_code}, Type: {r.headers.get('Content-Type')}")
if r.status_code == 200:
    with pdfplumber.open(io.BytesIO(r.content)) as pdf:
        print(f"Pages: {len(pdf.pages)}")
        for pi in range(min(4, len(pdf.pages))):
            text = pdf.pages[pi].extract_text() or ""
            print(f"\n--- Page {pi} ---")
            print(text[:2000])
else:
    print(f"Response: {r.text[:300]}")
