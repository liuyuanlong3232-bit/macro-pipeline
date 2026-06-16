#!/usr/bin/env python3
"""周日自检"""
from pathlib import Path
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")

checks = [
    "天气入库: 检查是否已启动",
    "交叉验证: 天气完成后开始", 
    "市场规律库: 计划2026-07-13",
    "交易日志: 计划2026-06-22",
]

summary = "📋 知识库周检 (" + today + ")\n" + "\n".join("  ⬜ " + c for c in checks)

f = Path.home() / "hermes-pipeline" / "shared" / "reminders" / ("weekly_" + today + ".txt")
f.parent.mkdir(parents=True, exist_ok=True)
f.write_text(summary, "utf-8")
print(summary)
