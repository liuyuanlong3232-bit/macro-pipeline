#!/usr/bin/env python3
"""Try Baker Hughes with Scrapling Fetcher."""
from scrapling import Fetcher

fetcher = Fetcher()
# Configure with proxy
fetcher.configure(proxy="http://127.0.0.1:10808")

# Try fetching
resp = fetcher.fetch("https://rigcount.bakerhughes.com/")
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
