#!/usr/bin/env python3
"""发送报告到邮箱，带图表"""
import os, sys, smtplib, ssl, base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.header import Header
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv("/root/hermes-pipeline/.env")

CHART_DIR = Path.home() / "hermes-macro-data" / "charts"

def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def send_report(filepath, chart_type=""):
    """发送Markdown报告到邮箱，含图表"""
    if not os.path.exists(filepath):
        print(f"❌ 报告不存在: {filepath}")
        return False

    from_addr = os.getenv("EMAIL_USER")
    to_addr = os.getenv("EMAIL_TO")
    password = os.getenv("EMAIL_PASS")
    smtp_host = os.getenv("EMAIL_HOST", "smtp.qq.com")
    smtp_port = int(os.getenv("EMAIL_PORT", 465))

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.strip().split("\n")
    title = "研究报告"
    for line in lines:
        if line.startswith("# "):
            title = line.replace("# ", "").strip()
            break

    date_str = datetime.now().strftime("%Y-%m-%d")
    subject = f"{title} | {date_str}"

    msg = MIMEMultipart("alternative")
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Subject"] = Header(subject, "utf-8")

    # === 生成HTML版本（含图表） ===
    html_parts = []
    html_parts.append(f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"></head><body style="font-family: 'Microsoft YaHei', sans-serif; color: #333; max-width: 800px; margin: 0 auto; padding: 20px;">
<div style="background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">""")

    # 图表区域
    chart_section = ""
    if chart_type == "macro" or chart_type == "":
        # 宏观周报有FRED走势图
        fred_chart = CHART_DIR / "fred_trends.png"
        if fred_chart.exists():
            b64 = img_to_base64(fred_chart)
            chart_section += f'<img src="data:image/png;base64,{b64}" style="width:100%;max-width:700px;border-radius:4px;margin:10px 0;"><br>'
            html_parts.append(f"""<div style="margin: 15px 0;"><h3 style="color:#2C3E50;border-left:4px solid #3498DB;padding-left:10px;">📊 美国关键宏观指标走势</h3>{chart_section}</div>""")

    if chart_type in ("metals", "energy", "") or chart_type == "":
        # COT图表
        for name, title_text in [("cot_net", "COT投机净持仓排行榜"), ("cot_index", "COT Index一览"), ("cot_long_short", "COT多空对比")]:
            p = CHART_DIR / f"{name}.png"
            if p.exists():
                b64 = img_to_base64(p)
                html_parts.append(f"""<div style="margin: 15px 0;"><h3 style="color:#2C3E50;border-left:4px solid #E67E22;padding-left:10px;">📊 {title_text}</h3><img src="data:image/png;base64,{b64}" style="width:100%;max-width:700px;border-radius:4px;margin:10px 0;"></div>""")

    # Markdown内容转HTML
    html_body = ""
    in_table = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# "):
            continue  # 标题已在邮件主题中
        elif stripped.startswith("## "):
            html_body += f'<h3 style="color:#2C3E50;margin-top:25px;border-bottom:1px solid #eee;padding-bottom:8px;">{stripped[3:]}</h3>\n'
        elif stripped.startswith("### "):
            html_body += f'<h4 style="color:#E67E22;margin-top:20px;">{stripped[4:]}</h4>\n'
        elif stripped.startswith("| "):
            if not in_table:
                in_table = True
                html_body += '<table style="border-collapse:collapse;width:100%;margin:12px 0;font-size:13px;">\n'
            # 检测表头分隔行
            if all(c in stripped for c in ["-"]):
                continue
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            tag = "th"
            row_html = "<tr>" + "".join(f'<{tag} style="border:1px solid #ddd;padding:8px;background:#f8f9fa;text-align:center;">{c}</{tag}>' for c in cells) + "</tr>\n"
            html_body += row_html
        else:
            if in_table:
                html_body += "</table>\n"
                in_table = False
            if stripped:
                html_body += f'<p style="line-height:1.6;">{stripped}</p>\n'

    if in_table:
        html_body += "</table>\n"

    html_parts.append(f'<div style="margin-top:20px;">{html_body}</div>')
    html_parts.append('</div></body></html>')

    html_full = "\n".join(html_parts)

    # 纯文本版（备用）
    text_part = MIMEText(f"请查看HTML版本报告\n{filepath}", "plain", "utf-8")
    msg.attach(text_part)

    # HTML版（含图）
    html_part = MIMEText(html_full, "html", "utf-8")
    msg.attach(html_part)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
            server.login(from_addr, password)
            server.sendmail(from_addr, [to_addr], msg.as_string())
        print(f"✅ 已发送: {subject} (含{len(html_parts)-3}张图)")
        return True
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        return False

def send_alert(subject, message):
    """发送纯文本预警"""
    from_addr = os.getenv("EMAIL_USER")
    to_addr = os.getenv("EMAIL_TO")
    password = os.getenv("EMAIL_PASS")
    smtp_host = os.getenv("EMAIL_HOST", "smtp.qq.com")
    smtp_port = int(os.getenv("EMAIL_PORT", 465))

    msg = MIMEText(message, "plain", "utf-8")
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Subject"] = Header(f"⚠️ {subject}", "utf-8")

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
            server.login(from_addr, password)
            server.sendmail(from_addr, [to_addr], msg.as_string())
        print(f"✅ 预警已发送: {subject}")
        return True
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ct = sys.argv[2] if len(sys.argv) > 2 else ""
        send_report(sys.argv[1], ct)
    else:
        print("用法: python3 send_email.py <报告路径> [chart_type]")
