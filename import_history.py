#!/usr/bin/env python3
"""导入15年历史Excel数据到SQLite数据库"""
import sys, os, sqlite3
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

SRC = Path(r"D:\commodity_research_platform\export\merged")
DB = Path.home() / "hermes-macro-data" / "hermes.db"

def import_price_data():
    """商品价格.xlsx -> hermes_price_history 表"""
    fp = SRC / "商品价格.xlsx"
    xl = pd.ExcelFile(fp)
    all_rows = []
    for sheet in xl.sheet_names:
        df = pd.read_excel(fp, sheet_name=sheet)
        if "date" not in df.columns or "close" not in df.columns:
            continue
        # 统一列名
        df = df[["date", "open", "high", "low", "close", "volume", "commodity", "symbol"]].copy()
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        df.columns = ["日期", "开盘", "最高", "最低", "收盘", "成交量", "品种", "代码"]
        # 只保留有数据的行
        df = df.dropna(subset=["收盘"])
        all_rows.append(df)
        print(f"  {sheet}: {len(df)} 行 ({df['日期'].min()} ~ {df['日期'].max()})")
    
    if not all_rows:
        return
    full = pd.concat(all_rows, ignore_index=True)
    conn = sqlite3.connect(str(DB))
    full.to_sql("price_history", conn, if_exists="replace", index=False)
    conn.close()
    print(f"  ✅ 价格历史: {len(full)} 行, {full['品种'].nunique()} 个品种")

def import_macro_data():
    """宏观经济.xlsx -> 只导入对我们有用的美国关键指标"""
    fp = SRC / "宏观经济.xlsx"
    useful = [
        "美国10年国债收益率", "美国2年国债收益率", "联邦基金利率",
        "美国CPI", "美国核心CPI", "美国失业率", "美国非农就业",
        "美国M2", "美国工业产出", "美国GDP",
        "10Y-2Y利差", "10年TIPS收益率", "5年盈亏平衡通胀率",
    ]
    xl = pd.ExcelFile(fp)
    all_rows = []
    for sheet in xl.sheet_names:
        if sheet not in useful:
            continue
        df = pd.read_excel(fp, sheet_name=sheet)
        # 找出日期列和数值列
        date_cols = [c for c in df.columns if "date" in str(c).lower()]
        val_cols = [c for c in df.columns if c not in date_cols and df[c].dtype in ("float64", "int64")]
        
        if not date_cols or not val_cols:
            continue
        
        dc = date_cols[0]
        for vc in val_cols:
            sub = df[[dc, vc]].dropna().copy()
            sub.columns = ["date", "value"]
            sub["date"] = pd.to_datetime(sub["date"]).dt.strftime("%Y-%m-%d")
            sub["indicator"] = sheet
            all_rows.append(sub)
            print(f"  {sheet}({vc}): {len(sub)} 行")
    
    if not all_rows:
        print("  ⚠️ 没有找到可用数据")
        return
    
    full = pd.concat(all_rows, ignore_index=True)
    conn = sqlite3.connect(str(DB))
    full.to_sql("macro_history", conn, if_exists="replace", index=False)
    conn.close()
    print(f"  ✅ 宏观历史: {len(full)} 行, {full['indicator'].nunique()} 个指标")

def import_cot_data():
    """期货持仓.xlsx -> hermes_cot_history 表"""
    fp = SRC / "期货持仓.xlsx"
    xl = pd.ExcelFile(fp)
    all_rows = []
    
    for sheet in xl.sheet_names:
        if "FedWatch" in sheet:
            continue
        df = pd.read_excel(fp, sheet_name=sheet)
        if "date" not in df.columns:
            continue
        # 非商业净持仓 = noncomm_long - noncomm_short
        if "noncomm_long" in df.columns and "noncomm_short" in df.columns:
            df["noncomm_net"] = df["noncomm_long"] - df["noncomm_short"]
        # 商业净持仓 = commercial_long - commercial_short
        if "commercial_long" in df.columns and "commercial_short" in df.columns:
            df["commercial_net"] = df["commercial_long"] - df["commercial_short"]
        
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        all_rows.append(df)
        print(f"  {sheet}: {len(df)} 行")
    
    if not all_rows:
        return
    full = pd.concat(all_rows, ignore_index=True)
    conn = sqlite3.connect(str(DB))
    full.to_sql("cot_history", conn, if_exists="replace", index=False)
    conn.close()
    print(f"  ✅ COT历史: {len(full)} 行, {full['commodity'].nunique() if 'commodity' in full.columns else 'N/A'} 个品种")

def import_energy_data():
    """能源.xlsx -> 合并已有eia数据"""
    fp = SRC / "能源.xlsx"
    xl = pd.ExcelFile(fp)
    all_rows = []
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(fp, sheet_name=sheet)
        if "date" not in df.columns:
            continue
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        df["sheet"] = sheet
        all_rows.append(df)
        print(f"  {sheet}: {len(df)} 行")
    
    if not all_rows:
        return
    full = pd.concat(all_rows, ignore_index=True)
    conn = sqlite3.connect(str(DB))
    full.to_sql("energy_history", conn, if_exists="replace", index=False)
    conn.close()
    print(f"  ✅ 能源历史: {len(full)} 行")

if __name__ == "__main__":
    print("📥 导入15年历史数据...")
    import_price_data()
    print()
    import_macro_data()
    print()
    import_cot_data()
    print()
    import_energy_data()
    print("\n✅ 全部导入完成")
