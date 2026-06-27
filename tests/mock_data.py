"""Deterministic local-only data for Sentinel-Lab dry-run tests."""
import os
import sqlite3

import pandas as pd


def _dates(today):
    return pd.date_range(end=pd.Timestamp(today), periods=10, freq="D").strftime("%Y-%m-%d").tolist()


def frames(today):
    dates = _dates(today)
    fred_specs = {
        "10 年期國債": (4.10, 0.01), "TIPS": (1.80, 0.01), "美元指數": (102.0, -0.05),
        "聯邦基金利率": (4.50, 0.00), "2 年期國債": (3.90, 0.01), "5 年期國債": (4.00, 0.01),
        "30年期國債": (4.30, 0.01), "CPI": (320.0, 0.10), "核心PCE": (310.0, 0.08),
        "失業率": (4.10, 0.00), "非農": (150.0, 1.00), "平均時薪(全部員工)": (35.0, 0.02),
        "JOLTS職位空缺數": (7600.0, 5.0), "歐元區利率": (3.25, 0.00), "中國CPI": (0.30, 0.01),
    }
    fred_rows = []
    for label, (base, step) in fred_specs.items():
        for index, date in enumerate(dates):
            fred_rows.append({"日期": date, "指標": label, "系列ID": f"MOCK_{label}", "數值": base + step * index, "抓取日": today})

    cot_rows = []
    for index, name in enumerate(["美元指数", "黄金", "白银"]):
        long_position = 100000 - index * 10000
        short_position = 60000 + index * 5000
        cot_rows.append({
            "date": dates[-1], "long": long_position, "short": short_position, "net": long_position - short_position,
            "品種": name, "投機多頭": long_position, "投機空頭": short_position,
            "投機淨持倉": long_position - short_position, "COT Index(26W)": 55 - index * 5, "Z-Score": 0.4 - index * 0.2,
        })

    price_rows = []
    for index, date in enumerate(dates):
        price_rows.append({"date": date, "gold": 2300 + index * 4, "silver": 28 + index * 0.1, "dxy": 102 - index * 0.05})

    macro_rows = []
    for index, date in enumerate(dates):
        macro_rows.append({"date": date, "cpi": 3.0 + index * 0.01, "ppi": 2.0 + index * 0.01, "rates": 4.5})

    yahoo = pd.DataFrame([
        {"代碼": "^VIX", "最新價": 18.0, "日期": today},
        {"代碼": "EURUSD=X", "最新價": 1.08, "日期": today},
        {"代碼": "USDJPY=X", "最新價": 145.0, "日期": today},
        {"代碼": "CNH=X", "最新價": 7.25, "日期": today},
    ])
    vix = pd.DataFrame([{"价格": 18.0, "报告日期": today, "杠杆基金净": -12000, "资产管理净": -8000}])
    return {
        "fred_indicators": pd.DataFrame(fred_rows),
        "yahoo_futures": yahoo,
        "vix_data": vix,
        "cotdata": pd.DataFrame(cot_rows),
        "price_history": pd.DataFrame(price_rows),
        "macro_history": pd.DataFrame(macro_rows),
    }


def load_csv(name, today):
    return frames(today).get(name, pd.DataFrame()).copy()


def ensure_mock_database(data_dir, today):
    if os.getenv("HERMES_DRY_RUN") != "1":
        return
    data_dir.mkdir(parents=True, exist_ok=True)
    mock = frames(today)
    db_path = data_dir / "hermes.db"
    price_wide = mock["price_history"]
    price_long = pd.concat([
        price_wide[["date", "gold"]].rename(columns={"date": "日期", "gold": "收盘"}).assign(品种="gold"),
        price_wide[["date", "silver"]].rename(columns={"date": "日期", "silver": "收盘"}).assign(品种="silver"),
    ], ignore_index=True)
    macro_wide = mock["macro_history"]
    macro_long = pd.concat([
        macro_wide[["date", "rates"]].rename(columns={"rates": "value"}).assign(indicator="联邦基金利率"),
        macro_wide[["date", "cpi"]].rename(columns={"cpi": "value"}).assign(indicator="美国CPI"),
        macro_wide[["date", "rates"]].rename(columns={"rates": "value"}).assign(indicator="美国10年国债收益率"),
        macro_wide[["date", "rates"]].assign(value=1.8).drop(columns=["rates"]).assign(indicator="10年TIPS收益率"),
    ], ignore_index=True)
    cot_history = pd.DataFrame({"date": price_wide["date"], "commodity": "gold", "noncomm_net": 40000 + pd.RangeIndex(len(price_wide)) * 500})
    with sqlite3.connect(db_path) as db:
        mock["cotdata"].to_sql("cotdata", db, if_exists="replace", index=False)
        price_long.to_sql("price_history", db, if_exists="replace", index=False)
        macro_long.to_sql("macro_history", db, if_exists="replace", index=False)
        cot_history.to_sql("cot_history", db, if_exists="replace", index=False)


def fedwatch():
    return {"cut_25": 60.0, "hold": 35.0}


def cn_macro():
    return {"dr007": 1.70, "lpr1y": 3.10, "lpr5y": 3.60, "rrr_large": 9.50, "shibor_1w": 1.80}


def social_financing():
    return {"inc_month": 9000.0, "stk_endval": 410.0}


def pmi():
    return {"value": 50.5, "prev": 50.1, "date": "2026-06-01"}


def global_m2():
    return {"eur_m2": 16000, "jp_m2": 1600, "jp_m2_yoy": 2.1}


def treasury_cot():
    return {"10Y": {"am_net": 200000, "lev_net": -150000}}


def safe_cross_border():
    return {"total": 57700.0, "balance": -321.0}
