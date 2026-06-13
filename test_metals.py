#!/usr/bin/env python3
"""Test script to verify metals_weekly.py output structure"""
import sys
sys.path.insert(0, r"C:\Users\Administrator\hermes-macro-pipeline")

# Patch load to return empty data so we test the report structure
import metals_weekly as mw
original_load = mw.load
def fake_load(name):
    import pandas as pd
    return pd.DataFrame()
mw.load = fake_load

output = mw.report()
expected_sections = [
    "## 一、本周贵金属市场总结",
    "## 二、价格走势分析",
    "## 三、宏观驱动环境分析",
    "## 四、CFTC COT资金持仓分析",
    "## 五、产业&需求基本面简析",
    "## 六、地缘&跨资产联动影响",
    "## 七、供需强弱评分",
    "## 八、未来30天重点观察方向+潜在风险提示",
]

tail_texts = [
    "数据来源：Alpha Vantage、Yahoo Finance、CFTC、美联储、彭博宏观数据",
    "免责声明：本文仅为贵金属宏观、资金、产业数据周度复盘",
    "AI生成标注：本文AI辅助整理，全部核心数据人工核验校准。",
]

all_ok = True
for s in expected_sections:
    if s in output:
        print(f"✓ Found section: {s}")
    else:
        print(f"✗ MISSING section: {s}")
        all_ok = False

for t in tail_texts:
    if t in output:
        print(f"✓ Found tail text: {t[:40]}...")
    else:
        print(f"✗ MISSING tail text: {t[:40]}...")
        all_ok = False

# Check section order
lines = output.split("\n")
section_lines = [l for l in lines if l.startswith("## ")]
print("\n--- Section order ---")
for i, l in enumerate(section_lines):
    print(f"  {i+1}. {l}")

print(f"\n{'✓ ALL CHECKS PASSED' if all_ok else '✗ SOME CHECKS FAILED'}")
