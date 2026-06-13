"""测试Baker Hughes"""
import sys
sys.path.insert(0, "/root/hermes-pipeline")
from data_scrapers import fetch_baker_hughes
bh = fetch_baker_hughes()
if bh:
    us = bh.get("us_count")
    ca = bh.get("canada_count")
    total = bh.get("na_total")
    dt = bh.get("date")
    print("US: " + str(us) + " Canada: " + str(ca) + " Total: " + str(total) + " (" + str(dt) + ")")
else:
    print("FAILED")
