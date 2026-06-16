#!/usr/bin/env python3
"""提醒：天气数据入库可以开始"""
m = "🌤️ 天气数据入库提醒：Open-Meteo API就绪，现在就能开始。需要做的：1.选产区 2.建表 3.写采集脚本。完成标志：agri_weather表有数据。"
print(m)
from pathlib import Path
f = Path.home() / "hermes-pipeline" / "shared" / "reminders" / "weather_reminder.txt"
f.parent.mkdir(parents=True, exist_ok=True)
f.write_text(m, "utf-8")
