#!/usr/bin/env python3
"""Try Baker Hughes with Scrapling adaptive mode."""
from scrapling import Fetcher

fetcher = Fetcher()
# Try adaptive mode - Scrapling has built-in stealth
resp = fetcher.fetch("https://rigcount.bakerhughes.com/", adaptive=True)
print(f"Status: {resp.status}")
if resp.status == 200:
    print(f"Len: {len(resp.text)}")
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(resp.text, "lxml")
    tables = soup.find_all("table")
    print(f"Tables: {len(tables)}")
    for ti, table in enumerate(tables):
        rows = table.find_all("tr")
        for ri, row in enumerate(rows):
            cells = row.find_all(["th", "td"])
            texts = [c.get_text(strip=True) for c in cells]
            print(f"  Row {ri}: {texts}")
else:
    print(f"Body: {resp.text[:300]}")
