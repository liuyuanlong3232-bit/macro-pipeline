#!/usr/bin/env python3
"""统一报告生成+发送入口"""
import sys, subprocess
from pathlib import Path
from datetime import datetime

TODAY = datetime.now().strftime("%Y-%m-%d")
PIPELINE = Path("/root/hermes-pipeline")

SCRIPTS = {
    "macro": {
        "script": "macro_weekly.py",
        "outfile": f"macro_weekly_{TODAY}.md",
        "chart_type": "macro",
        "need_charts": True
    },
    "energy": {
        "script": "energy_weekly.py",
        "outfile": f"energy_weekly_{TODAY}.md",
        "chart_type": "energy",
        "need_charts": True
    },
    "agri": {
        "script": "agri_weekly.py",
        "outfile": f"agri_global_{TODAY}.md",
        "chart_type": "",
        "need_charts": False
    },
    "agri_cn": {
        "script": "",
        "outfile": f"agri_china_{TODAY}.md",
        "chart_type": "",
        "need_charts": False
    },
    "metals": {
        "script": "metals_weekly.py",
        "outfile": f"metals_weekly_{TODAY}.md",
        "chart_type": "metals",
        "need_charts": True
    },
    "allocation": {
        "script": "",
        "outfile": f"allocation_{TODAY}.md",
        "chart_type": "",
        "need_charts": False
    },
}

def run(name):
    cfg = SCRIPTS.get(name)
    if not cfg:
        print(f"❌ 未知报告类型: {name}")
        return False

    # 1. 生成图表（如果需要）
    if cfg["need_charts"]:
        subprocess.run(["python3", "charts.py"], cwd=PIPELINE)
        print("  📊 图表已生成")

    # 2. 生成报告
    if cfg["script"]:
        r = subprocess.run(["python3", cfg["script"]], cwd=PIPELINE,
                         capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  ❌ 报告生成失败: {r.stderr}")
            return False
        print(f"  ✅ 报告已生成: {cfg['outfile']}")
    else:
        print(f"  ⏭️ 无需生成脚本，直接发送已有报告")

    # 3. 发送邮件
    report_path = Path("/root/hermes-macro-data/reports") / cfg["outfile"]
    if not report_path.exists():
        print(f"  ❌ 报告文件不存在: {report_path}")
        return False

    from send_email import send_report
    return send_report(str(report_path), cfg["chart_type"])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 run_report.py <macro|energy|agri|agri_cn|metals|allocation>")
        sys.exit(1)
    ok = run(sys.argv[1])
    sys.exit(0 if ok else 1)
