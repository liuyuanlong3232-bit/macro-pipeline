#!/usr/bin/env python3
"""Try Cornell PDF URL."""
import requests

PROXY = {"http":"http://127.0.0.1:10808","https":"http://127.0.0.1:10808"}
UA = {"User-Agent": "Mozilla/5.0"}

# Try with Cornell domain prefix
url = "https://usda.library.cornell.edu/sites/default/release-files/795933/prog2326.pdf"
r = requests.get(url, timeout=30, headers=UA, proxies=PROXY)
print(f"URL: {url}")
print(f"Status: {r.status_code}, Type: {r.headers.get('Content-Type')}, Len: {len(r.content)}")
if r.status_code == 200:
    print(f"Content (first 500): {r.content[:500]}")
else:
    print(f"Response: {r.text[:300]}")

# Also try to find the download link in the Cornell page
print("\n=== Find download links from Cornell page ===")
from bs4 import BeautifulSoup
r2 = requests.get("https://usda.library.cornell.edu/concern/publications/8336h188j?locale=en",
                  timeout=15, headers=UA, proxies=PROXY)
soup = BeautifulSoup(r2.text, "lxml")
for a in soup.find_all("a"):
    href = a.get("href", "")
    if "prog2326" in href or "prog23" in href:
        print(f"  Link: {href[:100]}")
        # Try full URL
        if href.startswith("/"):
            full = "https://usda.library.cornell.edu" + href
            print(f"  Full: {full}")
            r3 = requests.head(full, timeout=10, headers=UA, proxies=PROXY, allow_redirects=True)
            print(f"  Status: {r3.status_code}")
            print(f"  Final URL: {r3.url}")
