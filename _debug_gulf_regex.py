"""Debug: find exact text around GULF section"""
import requests, re
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
r = requests.get('https://www.ams.usda.gov/mnreports/wa_gr101.txt', timeout=15, headers=UA)
text = r.text

# Find the GULF section in the "BY REGION AND PORT AREA" table
# The report has multiple GULF sections, we want the one with port area breakdown
idx = text.find("GULF")
if idx >= 0:
    # Print surrounding context
    start = max(0, idx - 50)
    end = min(len(text), idx + 500)
    chunk = text[start:end]
    print("=== Raw text around first GULF occurrence ===")
    print(repr(chunk))
    print()

# Also search for "BY REGION AND PORT AREA" to find the right table
idx2 = text.find("BY REGION AND PORT AREA")
if idx2 >= 0:
    chunk2 = text[idx2:idx2+1500]
    print("=== Raw text after 'BY REGION AND PORT AREA' ===")
    print(repr(chunk2[:1200]))
