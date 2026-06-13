"""测试发送报告"""
from pathlib import Path
from send_email import send_report

reports = sorted(Path("/root/hermes-macro-data/reports").glob("metals_weekly_*.md"))
if reports:
    print(f"发送测试: {reports[-1]}")
    send_report(str(reports[-1]), "metals")
else:
    print("无报告")
