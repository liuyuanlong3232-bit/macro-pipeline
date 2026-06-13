#!/usr/bin/env python3
"""Get USDA crop progress TXT."""
import requests

PROXY = {"http":"http://127.0.0.1:10808","https":"http://127.0.0.1:10808"}
UA = {"User-Agent": "Mozilla/5.0"}

url = "https://www.nass.usda.gov/sites/default/release-files/795933/prog2326.txt"
r = requests.get(url, timeout=30, headers=UA, proxies=PROXY)
print(f"Status: {r.status_code}, Len: {len(r.text)}")
if r.status_code == 200:
    print(r.text[:3000])
else:
    print(r.text[:500])
