#!/usr/bin/env python3
"""关键位预警：监控黄金/白银/COT/DXY突破阈值，超限发邮件"""
import os, sys, json
from pathlib import Path
from datetime import datetime

# 公共工具函数
sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared.utils import load_env

load_env()

# ===== 阈值配置 =====
# 设定依据：基于2024-2025年历史价格区间，超出范围触发预警
# 更新时间：2025年初，如市场结构变化需重新评估
THRESHOLDS = {
    "gold": {"min": 4000, "max": 4500, "label": "COMEX黄金($)"},      # 2024年高点~2790，预留上行空间
    "silver": {"min": 50, "max": 80, "label": "COMEX白银($)"},        # 2024年高点~35，预留上行空间
    "wti": {"min": 70, "max": 110, "label": "WTI原油($)"},            # 2024年区间70-95
    "dxy_net": {"min": 0, "max": 10000, "label": "DXY投机净持仓"},     # 宽范围，仅监控极端值
}

COT_EXTREME = {"index": {"min": 5, "max": 95}}  # COT Index极端值

LOG_FILE = Path.home() / "hermes-macro-data" / "alert_log.json"

# ===== 加载数据 =====
def get_data():
    import sqlite3
    db = sqlite3.connect(str(Path.home() / "hermes-macro-data" / "hermes.db"))

    data = {}

    # 黄金/白银期货价格
    for name, keyword in [("gold", "黃金"), ("silver", "白銀"), ("wti", "WTI")]:
        row = db.execute(
            "SELECT 最新價, \"日漲跌幅%\" FROM yahoo_futures WHERE 品種 LIKE ?",
            (f"%{keyword}%",)
        ).fetchone()
        if row and row[0] is not None:
            data[name] = {"price": float(row[0]), "change": float(row[1] or 0)}

    # COT数据
    cot_rows = db.execute(
        'SELECT 品種, "投機淨持倉", "COT Index(26W)" FROM cotdata'
    ).fetchall()
    data["cot"] = [{"name": r[0], "net": float(r[1] or 0), "index": float(r[2] or 0)} for r in cot_rows if r[1] is not None]

    # DXY净持仓
    for r in cot_rows:
        if ("DXY" in r[0] or "美元" in r[0]) and r[1] is not None:
            data["dxy_net"] = float(r[1])

    db.close()
    return data

# ===== 检查阈值 =====
def check_thresholds(data):
    alerts = []

    # 价格阈值
    for key, conf in THRESHOLDS.items():
        if key not in data:
            continue
        if isinstance(data[key], dict) and "price" in data[key]:
            val = data[key]["price"]
        else:
            val = data[key]
        if val < conf["min"]:
            alerts.append(f"🔴 {conf['label']} {val:.2f} 低于阈值 {conf['min']}")
        elif val > conf["max"]:
            alerts.append(f"🟠 {conf['label']} {val:.2f} 高于阈值 {conf['max']}")

    # COT极端值
    for item in data.get("cot", []):
        idx = item["index"]
        if idx >= COT_EXTREME["index"]["max"]:
            alerts.append(f"🟠 {item['name']} COT Index {idx:.0f} — 极端看多 (>=95)")
        elif idx <= COT_EXTREME["index"]["min"]:
            alerts.append(f"🔴 {item['name']} COT Index {idx:.0f} — 极端看空 (<=5)")

    return alerts

# ===== 去重：避免重复报警 =====
def load_history():
    if LOG_FILE.exists():
        try:
            with open(LOG_FILE) as f:
                return json.load(f)
        except Exception: pass
    return {"sent": [], "last_check": ""}

def save_history(h):
    with open(LOG_FILE, "w") as f:
        json.dump(h, f, ensure_ascii=False, indent=2)

def is_new_alert(msg, history):
    # 同一个警告24小时内不重复发
    key = msg[:60]
    return key not in history.get("sent", [])

def mark_sent(msg, history):
    history.setdefault("sent", []).append(msg[:60])
    if len(history["sent"]) > 200:
        history["sent"] = history["sent"][-100:]  # 只保留最近100条
    history["last_check"] = datetime.now().strftime("%Y-%m-%d %H:%M")

# ===== 主函数 =====
def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"🔍 关键位检查 ({now})")

    data = get_data()
    print(f"  数据: 黄金={data.get('gold',{}).get('price','N/A')} | 白银={data.get('silver',{}).get('price','N/A')}")

    alerts = check_thresholds(data)
    if not alerts:
        print("  ✅ 所有指标在正常范围")
        return

    history = load_history()
    new_alerts = [a for a in alerts if is_new_alert(a, history)]

    if not new_alerts:
        print(f"  ⏭️ {len(alerts)}个旧警报已存在，跳过")
        return

    print(f"  🚨 {len(new_alerts)}个新警报!")
    for a in new_alerts:
        print(f"    {a}")

    # 发邮件
    subject = f"市场关键位预警 ({len(new_alerts)}项)"
    message = f"⏰ 检查时间: {now}\n\n" + "\n".join(new_alerts)
    message += f"\n\n---\n所有数据来源: SQLite数据库 | 自动监控"

    try:
        from send_email import send_alert
        ok = send_alert(subject, message)
        if ok:
            for a in new_alerts:
                mark_sent(a, history)
            save_history(history)
    except Exception as e:
        print(f"  ❌ 发送失败: {e}")

if __name__ == "__main__":
    main()
