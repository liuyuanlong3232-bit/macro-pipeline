"""VPS爬虫诊断"""
import sys, os
sys.path.insert(0, "/root/hermes-pipeline")
from data_scrapers import fetch_usda_crop_condition, fetch_bdi, fetch_baker_hughes

print("=== USDA ===")
try:
    usda = fetch_usda_crop_condition()
    print(f"  result: {usda}")
except Exception as e:
    print(f"  FAIL: {e}")

print("=== BDI ===")
try:
    bdi = fetch_bdi()
    print(f"  result: {bdi}")
except Exception as e:
    print(f"  FAIL: {e}")

print("=== Baker Hughes ===")
try:
    bh = fetch_baker_hughes()
    print(f"  result: {bh}")
except Exception as e:
    print(f"  FAIL: {e}")

print("=== EIA ===")
try:
    from energy_weekly import fetch_eia_energy
    eia = fetch_eia_energy()
    print(f"  result: {eia}")
except Exception as e:
    print(f"  FAIL: {e}")
