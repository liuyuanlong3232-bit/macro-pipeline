"""Quick test for updated energy_weekly.py"""
import sys
sys.path.insert(0, 'C:/Users/Administrator/hermes-macro-pipeline')
from energy_weekly import fetch_eia_energy, fmt_chg

eia = fetch_eia_energy()
print('=== EIA Data Fetched ===')
print(f'Crude Stocks: {eia.get("crude_stocks","N/A"):,.0f} (period: {eia.get("crude_stocks_period","N/A")})')
print(f'Crude Stocks Change: {fmt_chg(eia.get("crude_stocks_chg"))}')
print(f'SPR: {eia.get("spr_stocks","N/A"):,.0f}')
print(f'Cushing: {eia.get("cushing_stocks","N/A"):,.0f}')
print(f'Production: {eia.get("production","N/A"):,.0f} kb/d ({eia.get("production_period","N/A")})')
print(f'Refinery Utilization: {eia.get("refinery_util","N/A")}%')
print(f'NG Storage: {eia.get("ng_storage","N/A"):,.0f} BCF')
print()
print(f'All keys: {sorted(eia.keys())}')
print(f'Data count: {len(eia)}')
