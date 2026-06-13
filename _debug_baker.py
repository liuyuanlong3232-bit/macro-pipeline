#!/usr/bin/env python3
"""Debug Baker Hughes parser."""
import requests
from bs4 import BeautifulSoup

PROXY = {"http":"http://127.0.0.1:10808","https":"http://127.0.0.1:10808"}
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

r = requests.get("https://rigcount.bakerhughes.com/", timeout=20, proxies=PROXY, headers=UA)
print(f"Status: {r.status_code}")
soup = BeautifulSoup(r.text, "lxml")

# Find all tables
tables = soup.find_all("table")
print(f"Tables: {len(tables)}")

for ti, table in enumerate(tables):
    print(f"\n=== Table {ti} ===")
    rows = table.find_all("tr")
    for ri, row in enumerate(rows):
        cells = row.find_all(["th", "td"])
        texts = [c.get_text(strip=True) for c in cells]
        print(f"  Row {ri}: {texts}")
        print(f"  Cell count: {len(cells)}")
        for ci, cell in enumerate(cells):
            print(f"    Cell {ci}: '{cell.get_text(strip=True)}' tag={cell.name}")
