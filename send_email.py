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

    # 图表区域 - 按报告类型
    chart_section = ""
    if chart_type == "macro" or chart_type == "":
        fred_chart = CHART_DIR / "fred_trends.png"
        if fred_chart.exists():
            b64 = img_to_base64(fred_chart)
            html_parts.append(f"""<div style="margin:15px 0;"><h3 style="color:#2C3E50;border-left:4px solid #3498DB;padding-left:10px;">📊 美国关键宏观指标走势（15年）</h3><img src="data:image/png;base64,{b64}" style="width:100%;max-width:700px;border-radius:4px;margin:10px 0;"></div>""")

    if chart_type in ("metals",):
        for name, title_text in [
            ("gold_price", "黄金走势（15年）"),
            ("silver_price", "白银走势（15年均线）"),
            ("gold_silver_ratio", "金银比（15年）"),
            ("cot_net_history", "黄金COT投机净持仓历史"),
            ("cot_net", "COT投机净持仓排行榜"),
            ("cot_index", "COT Index一览"),
        ]:
            p = CHART_DIR / f"{name}.png"
            if p.exists():
                b64 = img_to_base64(p)
                html_parts.append(f"""<div style="margin:15px 0;"><h3 style="color:#2C3E50;border-left:4px solid #E67E22;padding-left:10px;">📊 {title_text}</h3><img src="data:image/png;base64,{b64}" style="width:100%;max-width:700px;border-radius:4px;margin:10px 0;"></div>""")

    if chart_type in ("energy",):
        for name, title_text in [("cot_net", "COT投机净持仓"), ("cot_index", "COT Index")]:
            p = CHART_DIR / f"{name}.png"
            if p.exists():
                b64 = img_to_base64(p)
                html_parts.append(f"""<div style="margin:15px 0;"><h3 style="color:#2C3E50;border-left:4px solid #27AE60;padding-left:10px;">📊 {title_text}</h3><img src="data:image/png;base64,{b64}" style="width:100%;max-width:700px;border-radius:4px;margin:10px 0;"></div>""")

    # Markdown内容转HTML - 精简版，有图就不需要完整表格了
    html_body = ""
    skip_next_n = 0
    for i, line in enumerate(lines):
        if skip_next_n > 0:
            skip_next_n -= 1
            continue
        stripped = line.strip()

        # 跳过标题（已在邮件主题）
        if stripped.startswith("# "):
            continue

        # 跳过表格分隔行
        if stripped.startswith("|---") or stripped.startswith("|:---"):
            continue

        # 跳过整行纯表格线
        if set(stripped) <= set("|-: "):
            continue

        # 标题
        if stripped.startswith("## "):
            html_body += f'<h3 style="color:#2C3E50;margin-top:22px;border-bottom:1px solid #eee;padding-bottom:6px;">{stripped[3:]}</h3>\n'
        elif stripped.startswith("### "):
            html_body += f'<h4 style="color:#E67E22;margin-top:18px;">{stripped[4:]}</h4>\n'
        elif stripped.startswith("**") and stripped.endswith("**"):
            # 加粗文本当作小标题
            html_body += f'<p style="font-weight:bold;margin-top:12px;color:#2C3E50;">{stripped.strip("*")}</p>\n'
        elif stripped.startswith("| "):
            # 表格行 → 中文冒号分隔
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            if cells:
                # 表头行和普通行不一样处理
                txt = "　　" + "　".join(cells)
                html_body += f'<p style="font-size:12px;color:#555;margin:2px 0;">{txt}</p>\n'
        elif stripped.startswith("- "):
            html_body += f'<li style="margin:3px 0;color:#444;">{stripped[2:]}</li>\n'
        elif stripped == "---":
            html_body += '<hr style="border:none;border-top:1px solid #eee;margin:15px 0;">\n'
        elif stripped == "":
            html_body += '<br>\n'
        else:
            html_body += f'<p style="line-height:1.6;color:#333;font-size:13px;">{stripped}</p>\n'

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
