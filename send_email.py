#!/usr/bin/env python3
"""发送报告到邮箱，带图表"""
import os, sys, smtplib, ssl, base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.header import Header
from datetime import datetime
from pathlib import Path

# 公共工具函数
sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared.utils import load_env, DATA_DIR

load_env()

CHART_DIR = DATA_DIR / "charts"

def _email_block_reason():
    """Return the runtime safety flag that blocks email sending, if any."""
    if os.getenv("HERMES_NO_EMAIL") == "1":
        return "HERMES_NO_EMAIL=1"
    if os.getenv("SAFE_MODE") == "1":
        return "SAFE_MODE=1"
    return None

def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def send_report(filepath, chart_type=""):
    """发送Markdown报告到邮箱，含图表"""
    block_reason = _email_block_reason()
    if block_reason:
        print(f"Email send blocked by runtime safety flag: {block_reason}")
        return False

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

    # 图表区域 - 按报告类型，不配图就不渲图
    chart_section = ""
    if chart_type == "macro":
        fred_chart = CHART_DIR / "fred_trends.png"
        if fred_chart.exists():
            b64 = img_to_base64(fred_chart)
            html_parts.append(f"""<div style="margin:15px 0;"><h3 style="color:#2C3E50;border-left:4px solid #3498DB;padding-left:10px;">美国关键宏观指标走势（近3年）</h3><img src="data:image/png;base64,{b64}" style="width:100%;max-width:700px;border-radius:4px;margin:10px 0;"></div>""")

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

    # Markdown内容转HTML - 表格转HTML <table>，其他保持精简
    html_body = ""
    table_rows = []  # 暂存表格行
    in_table = False

    def flush_table():
        nonlocal in_table, table_rows
        if not table_rows:
            return ""
        html = '<table style="border-collapse:collapse;width:100%;margin:10px 0;font-size:12px;">\n'
        for is_header, cells in table_rows:
            tag = "th" if is_header else "td"
            bg = "#f8f9fa" if is_header else "#fff"
            fw = "bold" if is_header else "normal"
            row = "<tr>"
            for c in cells:
                row += f'<{tag} style="border:1px solid #ddd;padding:6px 8px;background:{bg};font-weight:{fw};text-align:center;">{c}</{tag}>'
            row += f"</tr>\n"
            html += row
        html += "</table>\n"
        table_rows = []
        in_table = False
        return html

    # ── helper: detect markdown table separator row ──────────
    def _is_sep(s: str) -> bool:
        return "|" in s and not s.replace("|", "").replace("-", "").replace(":", "").strip()

    for i, line in enumerate(lines):
        stripped = line.strip()

        # 标题行（跳过#标题，已在邮件主题）
        if stripped.startswith("# ") and not stripped.startswith("## "):
            continue

        # 检测表格行：包含|且不纯粹是分隔符
        if _is_sep(stripped):
            continue

        if "|" in stripped:
            cells_raw = [c.strip() for c in stripped.split("|")]
            real_cells = [c for c in cells_raw if c.strip()]
            if len(real_cells) >= 2:
                # 如果行首尾有|，去掉首尾的空单元格
                cells = cells_raw[:]
                if stripped.startswith("|") and stripped.endswith("|"):
                    cells = cells[1:-1]
                cells = [c.strip() for c in cells if c.strip()]
                if len(cells) < 2:
                    continue
                # 判断是否是表头行（上一行是分隔行 or 当前行包含---）
                is_header = False
                if i > 0:
                    prev = lines[i - 1].strip()
                    if _is_sep(prev):
                        is_header = False
                    elif i > 1 and _is_sep(lines[i - 2].strip()):
                        is_header = True
                    else:
                        # 第一张表格：第一行后通常跟着分隔行
                        if not in_table and i + 1 < len(lines) and _is_sep(lines[i + 1].strip()):
                            is_header = True
                        else:
                            is_header = False
                else:
                    is_header = True

                table_rows.append((is_header, cells))
                in_table = True
                continue

        # 非表格行：先flush暂存的表格
        if in_table:
            html_body += flush_table()

        # 其他行类型
        if stripped.startswith("## "):
            text = stripped[3:].strip()
            html_body += f'<h3 style="color:#2C3E50;margin-top:22px;border-bottom:1px solid #eee;padding-bottom:6px;font-size:15px;">{text}</h3>\n'
        elif stripped.startswith("### "):
            html_body += f'<h4 style="color:#E67E22;margin-top:18px;font-size:13px;">{stripped[4:]}</h4>\n'
        elif stripped.startswith("**") and stripped.endswith("**"):
            html_body += f'<p style="font-weight:bold;margin-top:12px;color:#2C3E50;font-size:13px;">{stripped.strip("*")}</p>\n'
        elif stripped.startswith("- ") or stripped.startswith("* "):
            html_body += f'<p style="margin:3px 0;color:#444;padding-left:15px;font-size:12px;">{stripped[2:]}</p>\n'
        elif stripped.startswith("> "):
            html_body += f'<p style="margin:5px 0;color:#888;font-style:italic;padding-left:10px;border-left:3px solid #ddd;font-size:12px;">{stripped[2:]}</p>\n'
        elif stripped == "---":
            html_body += '<hr style="border:none;border-top:1px solid #eee;margin:15px 0;">\n'
        elif stripped == "":
            html_body += '<br>\n'
        elif stripped.startswith("```"):
            # 跳过代码块
            continue
        else:
            # 普通段落
            html_body += f'<p style="line-height:1.6;color:#333;font-size:13px;margin:5px 0;">{stripped}</p>\n'

    # 最后的表格
    if in_table:
        html_body += flush_table()

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
    block_reason = _email_block_reason()
    if block_reason:
        print(f"Email alert blocked by runtime safety flag: {block_reason}")
        return False

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
        if not send_report(sys.argv[1], ct):
            sys.exit(1)
    else:
        print("用法: python3 send_email.py <报告路径> [chart_type]")
