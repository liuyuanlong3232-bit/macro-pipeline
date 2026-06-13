"""Check USDA and alt sources for ag Gulf stocks & SA carryover"""
import requests, json

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# Try USDA AMS - Gulf export barge / rail reports
urls = [
    ("USDA AMS - Grain Inspection Summary", 
     "https://www.ams.usda.gov/mnreports/lsddhgr.pdf"),
    ("USDA AMS - Gulf Grain Barge", 
     "https://www.ams.usda.gov/mnreports/gx_gr112.txt"),
    ("USDA AMS - Grain Truck Advisory", 
     "https://www.ams.usda.gov/mnreports/gx_gr210.txt"),
    ("USDA AMS - Weekly Export Grain Inspections",
     "https://www.ams.usda.gov/mnreports/wa_gr101.txt"),
    ("USDA AMS - Milling Wheat Bids at Gulf",
     "https://www.ams.usda.gov/mnreports/gx_gr110.txt"),
    ("USDA AMS - Soybean Bids at Gulf",
     "https://www.ams.usda.gov/mnreports/gx_gr115.txt"),
    ("USDA FAS - Export Sales Announcements",
     "https://apps.fas.usda.gov/export-sales/"),
    ("USDA FAS - Grain World Markets and Trade",
     "https://apps.fas.usda.gov/psdonline/circulars/grain.pdf"),
    ("USDA FAS - Oilseeds World Markets and Trade",
     "https://apps.fas.usda.gov/psdonline/circulars/oilseeds.pdf"),
    ("USDA ERS Data - Feed Grains Yearbook Tables",
     "https://www.ers.usda.gov/data-products/feed-grains-database/"),
    ("USDA WASDE main page",
     "https://www.usda.gov/oce/commodity/wasde"),
]

for name, url in urls:
    print(f"\n--- {name} ---")
    print(f"  {url}")
    try:
        r = requests.get(url, timeout=15, headers=UA, allow_redirects=True)
        print(f"  Status: {r.status_code}, Length: {len(r.content)}")
        if r.status_code == 200 and len(r.content) < 5000 and 'text' in r.headers.get('Content-Type', ''):
            print(f"  Content:\n{r.text[:800]}")
        elif r.status_code == 200:
            print(f"  Content-Type: {r.headers.get('Content-Type', '?')}")
    except Exception as e:
        print(f"  Error: {e}")
