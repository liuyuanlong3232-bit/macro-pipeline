"""Debug Baker Hughes"""
import sys, subprocess, re
sys.path.insert(0, "/root/hermes-pipeline")

cmd = ["curl", "-s", "https://rigcount.bakerhughes.com/",
       "-H", "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
       "--max-time", "15"]
r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
print("RC:", r.returncode)
print("Len:", len(r.stdout))

if r.stdout:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r.stdout, "lxml")
    tables = soup.find_all("table")
    print("Tables:", len(tables))
    if tables:
        rows = tables[0].find_all("tr")
        for row in rows[:10]:
            cells = row.find_all(["td","th"])
            texts = [c.get_text(strip=True) for c in cells]
            print("Row:", " | ".join(texts[:6]))
