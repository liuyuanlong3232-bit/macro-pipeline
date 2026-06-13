"""Debug Baker Hughes verbose"""
import subprocess

cmd = ["curl", "-v", "-s", "https://rigcount.bakerhughes.com/",
       "-H", "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
       "--max-time", "15", "-o", "/tmp/bh.html", "-w", "%{http_code}"]
r = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
print("RC:", r.returncode)
print("Stderr:", r.stderr[:500])

import os
if os.path.exists("/tmp/bh.html"):
    sz = os.path.getsize("/tmp/bh.html")
    print("File size:", sz)
    if sz > 0:
        with open("/tmp/bh.html") as f:
            html = f.read(200)
        print("Content:", html[:200])
else:
    print("No file created")
