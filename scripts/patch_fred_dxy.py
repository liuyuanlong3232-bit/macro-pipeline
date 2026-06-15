#!/usr/bin/env python3
"""Patch 1: Add DTWEXAFEGS + DTWEXEMEGS to FRED_SERIES"""
path = "/root/hermes-pipeline/macro_pipeline.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = '"DTWEXBGS": "美元指數 (貿易加權)",'
new = '"DTWEXBGS": "美元指數 (貿易加權·廣義)",\n    "DTWEXAFEGS": "美元指數 (貿易加權·發達經濟體) — ICE DXY近似替代",\n    "DTWEXEMEGS": "美元指數 (貿易加權·新興市場)",'

if old in content:
    content = content.replace(old, new, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ DTWEXAFEGS + DTWEXEMEGS 已加入 FRED_SERIES")
else:
    print("??? 未找到目标行")
