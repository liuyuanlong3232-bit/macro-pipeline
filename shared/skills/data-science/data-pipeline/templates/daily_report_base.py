#!/usr/bin/env python3
"""贵金属日报生成器 — template for daily report scripts"""
import sys, sqlite3
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, "/root/hermes-pipeline")

NOW = datetime.now()
TODAY = NOW.strftime("%Y-%m-%d")
DB = str(Path.home() / "hermes-macro-data" / "hermes.db")

def gv(series):
    """Get FRED indicator value"""
    try:
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute(f'SELECT 數值, 日期 FROM fred_indicators WHERE "系列ID" = ? ORDER BY 日期 DESC LIMIT 1', (series,))
        r = cur.fetchone()
        conn.close()
        return (str(r[0]), str(r[1])) if r else ("—", "—")
    except:
        return ("—", "—")

def yv(kw):
    """Get Yahoo Futures price (using traditional Chinese keywords)"""
    try:
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute(f'SELECT 最新價, "日漲跌幅%" FROM yahoo_futures WHERE 品種 LIKE ? ORDER BY 日期 DESC LIMIT 1', (f"%{kw}%",))
        r = cur.fetchone()
        conn.close()
        return (float(r[0]), str(r[1]) if r[1] else "0") if r and r[0] else (None, "")
    except:
        return (None, "")

def cv(kw):
    """Get COT Index (using simplified Chinese keywords)"""
    try:
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute(f'SELECT "COT Index(26W)" FROM cotdata WHERE 品種 LIKE ? LIMIT 1', (f"%{kw}%",))
        r = cur.fetchone()
        conn.close()
        return f"{float(r[0]):.0f}" if r and r[0] else "—"
    except:
        return "—"

def vix_val():
    """Get VIX from vix_data table (not yahoo_futures)"""
    try:
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute('SELECT 价格 FROM vix_data WHERE 品種 = "VIX" ORDER BY 报告日期 DESC LIMIT 1')
        r = cur.fetchone()
        conn.close()
        return str(r[0]) if r and r[0] else "—"
    except:
        return "—"

def send_mail(report_path):
    """Send report via QQ SMTP"""
    from send_email import send_report
    send_report(report_path, "macro")

# Usage: copy this template, customize the macro keys and format strings for your report type.
# See references/database-schema-mappings.md for correct table/column names.
