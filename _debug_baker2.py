#!/usr/bin/env python3
"""Debug Baker Hughes - try different endpoints and headers."""
import requests
from bs4 import BeautifulSoup

PROXY = {"http":"http://127.0.0.1:10808","https":"http://127.0.0.1:10808"}

# Try with more browser-like headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Referer": "https://rigcount.bakerhughes.com/",
}

# First try the main page with longer timeout
for url in ["https://rigcount.bakerhughes.com/", "https://rigcount.bakerhughes.com/intl-rig-count"]:
    try:
        s = requests.Session()
        r = s.get(url, timeout=30, proxies=PROXY, headers=HEADERS)
        print(f"\nURL: {url}")
        print(f"Status: {r.status_code}, Len: {len(r.text)}")
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "lxml")
            tables = soup.find_all("table")
            print(f"Tables: {len(tables)}")
            for ti, table in enumerate(tables):
                rows = table.find_all("tr")
                for ri, row in enumerate(rows):
                    cells = row.find_all(["th", "td"])
                    texts = [c.get_text(strip=True) for c in cells]
                    print(f"  Row {ri}: {texts}")
        else:
            print(f"First 300 chars: {r.text[:300]}")
    except Exception as e:
        print(f"Error: {e}")
