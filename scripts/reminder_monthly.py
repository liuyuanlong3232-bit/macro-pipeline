#!/usr/bin/env python3
"""每月15日里程碑检查"""
from pathlib import Path
from datetime import datetime, date

today = date.today()

reminders = []
if today >= date(2026, 7, 13):
    reminders.append("🔔 市场规律库已到启动日(2026-07-13)，可以开始了！")
    reminders.append("  操作：打开 knowledge/待补清单.md 查看详细说明")
if today >= date(2026, 6, 22):
    reminders.append("🔔 交易日志已到启动日(2026-06-22)")
    reminders.append("  操作：每日记录判断（品种+方向+理由），存到日志文件")

summary = f"📌 月度里程碑检查 ({today.isoformat()})\n" + "\n".join(reminders) if reminders else f"📌 月度检查 ({today.isoformat()}) 暂无到期项目"

reminder_file = Path.home() / "hermes-pipeline" / "shared" / "reminders" / f"monthly_{today.isoformat()}.txt"
reminder_file.parent.mkdir(parents=True, exist_ok=True)
reminder_file.write_text(summary, "utf-8")
print(f"[reminder] {summary}")
