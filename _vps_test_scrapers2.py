"""VPS爬虫测试"""
import sys; sys.path.insert(0, "/root/hermes-pipeline")
from data_scrapers import get_proxy, fetch_baker_hughes, fetch_usda_crop_condition, fetch_bdi

p = get_proxy()
print(f"Proxy: {p}")

print("=== Baker Hughes ===")
bh = fetch_baker_hughes()
if bh:
    print(f"  US: {bh['us_count']}, Canada: {bh['canada_count']}, Total: {bh['na_total']} ({bh.get('date','')})")
else:
    print("  FAILED")

print("=== USDA ===")
usda = fetch_usda_crop_condition()
if usda and usda.get("corn"):
    cc = usda["corn"]["good_excellent"]
    sc = usda["soybeans"]["good_excellent"]
    print(f"  Corn G/E: {cc}%, Soy G/E: {sc}% ({usda.get('date','')})")
else:
    print("  FAILED")

print("=== BDI ===")
bdi = fetch_bdi()
if bdi:
    print(f"  Price: {bdi['price']}, Chg: {bdi['change_pct']:.2f}%")
else:
    print("  FAILED")
