#!/usr/bin/env python3
"""VPS上用curl拿到HTML后解析Baker Hughes钻机表"""
import sys, subprocess, re

result = subprocess.run([
    "curl", "-s", "https://rigcount.bakerhughes.com/",
    "-H", "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "-H", "Accept: text/html,application/xhtml+xml",
    "--max-time", "15"
], capture_output=True, text=True)

if result.returncode != 0 or not result.stdout:
    print("CURL_FAILED")
    sys.exit(1)

html = result.stdout

# 用BeautifulSoup解析（pip已装）
from bs4 import BeautifulSoup
soup = BeautifulSoup(html, "lxml")

tables = soup.find_all("table")
if not tables:
    print("NO_TABLE")
    sys.exit(1)

# 找北美钻机数
for table in tables:
    rows = table.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) >= 3:
            area = cells[0].get_text(strip=True)
            count = cells[2].get_text(strip=True)
            if "U.S." in area or area.upper() == "US":
                us_val = count.replace(",", "")
            elif "Canada" in area or area.upper() == "CANADA":
                ca_val = count.replace(",", "")
            elif "International" in area:
                intl_val = count.replace(",", "")
            elif "North America" in area or "Total" in area:
                na_val = count.replace(",", "")

print(f"US:{us_val}:Canada:{ca_val}:NA:{na_val}:Intl:{intl_val}")
