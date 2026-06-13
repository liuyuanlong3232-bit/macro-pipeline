#!/usr/bin/env python3
"""Quick Baker Hughes test."""
import requests
PROXY = {"http":"http://127.0.0.1:10808","https":"http://127.0.0.1:10808"}
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
try:
    r = requests.get("https://rigcount.bakerhughes.com/", timeout=15, proxies=PROXY, headers=HEADERS)
    print(f"Status: {r.status_code}, Len: {len(r.text)}")
    if r.status_code == 200:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "lxml")
        tables = soup.find_all("table")
        print(f"Tables: {len(tables)}")
        for ti, table in enumerate(tables):
            rows = table.find_all("tr")
            for ri, row in enumerate(rows):
                cells = row.find_all(["th", "td"])
                texts = [c.get_text(strip=True) for c in cells]
                print(f"Row {ri}: {texts}")
except Exception as e:
    print(f"Error: {e}")
