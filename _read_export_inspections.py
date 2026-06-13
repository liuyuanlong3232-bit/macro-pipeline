"""Read USDA Weekly Export Grain Inspections (wa_gr101.txt)"""
import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
url = "https://www.ams.usda.gov/mnreports/wa_gr101.txt"
r = requests.get(url, timeout=15, headers=UA)
print(f"Status: {r.status_code}")
print(f"Length: {len(r.content)}")
print("=" * 60)
# Print first 4000 characters to understand structure
print(r.text[:4000])
print("=" * 60)
print("...(see remaining below)...")
print(r.text[4000:6000])
