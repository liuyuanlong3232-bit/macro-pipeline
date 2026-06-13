#!/usr/bin/env python3
"""Verify report output structure matches prompt template."""
from macro_weekly import report
output = report()
lines = output.split('\n')

print("=== SECTION HEADERS ===")
for line in lines:
    if line.startswith('## '):
        print(line)

print()
print("=== TAIL (last 5 non-empty lines) ===")
tail = [l for l in lines if l.strip()]
for l in tail[-5:]:
    print(l)

print()
print("=== STRUCTURE CHECK ===")
expected = [
    "## 一、本周全球宏观市场总结",
    "## 二、核心宏观指标价格走势",
    "## 三、海外央行+经济基本面分析",
    "## 四、跨境资金&机构宏观持仓分析",
    "## 五、中国本土宏观高频联动简析",
    "## 六、宏观流动性强弱评分",
    "## 七、未来30天重点观察方向+潜在风险提示",
]
found = [l for l in lines if l.startswith('## ')]
for i, exp in enumerate(expected):
    if i < len(found):
        status = "✓" if found[i].strip() == exp else "✗"
        print(f"  {status} Expected: {exp}")
        if found[i].strip() != exp:
            print(f"     Got:      {found[i].strip()}")
    else:
        print(f"  ✗ MISSING: {exp}")

print()
print("=== TAIL VERIFICATION ===")
required_tail = [
    "数据来源：",
    "免责声明：",
    "AI生成标注：",
]
for t in required_tail:
    if any(t in l for l in tail[-5:]):
        print(f"  ✓ Contains: {t}")
    else:
        print(f"  ✗ MISSING: {t}")

print()
total_lines = len(lines)
print(f"Total lines: {total_lines}")
print(f"Total non-empty lines: {len(tail)}")
