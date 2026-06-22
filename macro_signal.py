#!/usr/bin/env python3
"""
宏观信号引擎 v2.0 — 双层架构
三因子评分系统 + 资产线性函数模型

三因子定义（双层架构）:
  USD_macro  = [-2.0, +2.0]  美元宏观趋势（CPI/NFP/Fed）
  USD_market = [-2.0, +2.0]  美元市场偏离（TIP/DXY/实时）
  USD_final  = 0.6 × USD_macro + 0.4 × USD_market
  Liquidity  = [-2.0, +2.0]  流动性（EUR/JPY驱动）
  Demand     = [-2.0, +2.0]  中国需求

资产函数:
  Gold   = -1.0 × USD_final + 0.6 × Liquidity
  Silver = Gold + 0.5 × Demand
  Tin    = 0.8 × Demand + 0.4 × Liquidity
  Oil    = 0.8 × Liquidity + 0.2 × Demand
"""
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DB = str(Path.home() / "hermes-macro-data" / "hermes.db")

# ═══════ 数据读取 ═══════
def db_one(sql, params=None):
    try:
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute(sql, params or ())
        r = cur.fetchone()
        conn.close()
        return r
    except:
        return None

def get_macro(table, indicator=None, country=None):
    """从macro表获取最新值"""
    try:
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        if country:
            cur.execute(f"SELECT value FROM [{table}] WHERE country=? ORDER BY date DESC LIMIT 1", (country,))
        elif indicator:
            cur.execute(f"SELECT value FROM [{table}] WHERE indicator_name LIKE ? ORDER BY date DESC LIMIT 1", (f"%{indicator}%",))
        else:
            cur.execute(f"SELECT value FROM [{table}] ORDER BY date DESC LIMIT 1")
        r = cur.fetchone()
        conn.close()
        return float(r[0]) if r else None
    except:
        return None

def get_fred(series_id):
    """从FRED获取最新值"""
    r = db_one('SELECT "數值" FROM fred_indicators WHERE "系列ID"=? ORDER BY "日期" DESC LIMIT 1', (series_id,))
    return float(r[0]) if r and r[0] != "—" else None

def get_yahoo(keyword):
    """从Yahoo获取最新价格"""
    r = db_one('SELECT "最新價", "日漲跌幅%" FROM yahoo_futures WHERE "品種" LIKE ? ORDER BY "日期" DESC LIMIT 1', (f"%{keyword}%",))
    if r and r[0]:
        return {"price": float(r[0]), "change": float(r[1]) if r[1] else 0}
    return None

def get_exchange_rate(pair):
    """获取汇率"""
    r = db_one(f"SELECT value FROM [macro_美元{pair}汇率] ORDER BY date DESC LIMIT 1")
    return float(r[0]) if r else None

def get_jin10_quote(code):
    """获取金十实时报价"""
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path.home() / "hermes-pipeline"))
        from jin10_api import get_quote
        result = get_quote(code)
        if result and result.get("close"):
            return {
                "price": float(result["close"]),
                "change": float(result.get("ups_percent", 0))
            }
    except Exception:
        pass
    return None

# ═══════ 三因子计算 ═══════
def calc_usd_macro():
    """
    USD宏观层：美元趋势方向（慢变量）
    数据源：CPI、非农、Fed利率、失业率
    范围：[-2.0, +2.0]
    权重：0.6（定方向）
    
    逻辑：
    - CPI高于预期 → 通胀压力 → Fed偏鹰 → USD↑
    - 非农强劲 → 经济好 → USD↑
    - 利率高 → USD↑
    """
    score = 0.0
    
    # CPI（最新 vs 前值）
    cpi = get_macro("macro_美国CPI")
    if cpi:
        if cpi > 335:
            score += 1.0
        elif cpi < 325:
            score -= 0.5
    
    # 非农就业
    nfp = get_macro("macro_美国非农就业")
    if nfp:
        if nfp > 250:
            score += 0.5
        elif nfp < 100:
            score -= 0.5
    
    # 联邦基金利率
    fed_rate = get_macro("macro_联邦基金利率")
    if fed_rate:
        if fed_rate > 5.0:
            score += 0.5
        elif fed_rate < 3.0:
            score -= 0.5
    
    # 失业率
    unemployment = get_macro("macro_美国失业率")
    if unemployment:
        if unemployment < 4.0:
            score += 0.5
        elif unemployment > 5.0:
            score -= 0.5
    
    return max(-2.0, min(2.0, score))


def calc_usd_market():
    """
    USD市场层：美元短期偏离（快变量）
    数据源：TIP ETF、DXY、金十实时
    范围：[-2.0, +2.0]
    权重：0.4（定节奏）
    
    逻辑：
    - TIP下跌 → TIPS上升 → USD↑
    - DXY上涨 → USD↑
    - 金十实时数据 → 即时偏离
    """
    score = 0.0
    
    # TIP ETF (反向：TIP跌 = TIPS涨 = USD强)
    tip = get_yahoo("TIP ETF")
    if tip:
        if tip["change"] < -0.5:
            score += 1.0
        elif tip["change"] > 0.5:
            score -= 1.0
    
    # DXY 美元指数
    dxy = get_yahoo("ICE美元")
    if dxy:
        if dxy["change"] > 0.3:
            score += 0.8
        elif dxy["change"] < -0.3:
            score -= 0.8
    
    # 金十实时（XAUUSD反向：黄金跌 = USD强）
    gold_jin10 = get_jin10_quote("XAUUSD")
    if gold_jin10:
        if gold_jin10["change"] < -1.0:
            score += 0.5
        elif gold_jin10["change"] > 1.0:
            score -= 0.5
    
    return max(-2.0, min(2.0, score))


def calc_usd_factor():
    """
    USD最终因子：双层加权
    USD_final = 0.6 × USD_macro + 0.4 × USD_market
    """
    macro = calc_usd_macro()
    market = calc_usd_market()
    final = 0.6 * macro + 0.4 * market
    return {
        "final": max(-2.0, min(2.0, final)),
        "macro": macro,
        "market": market
    }


def calc_liquidity_factor():
    """
    Liquidity因子：流动性
    数据源：EUR/JPY汇率
    范围：[-2.0, +2.0]
    
    逻辑：
    - EUR强 + JPY弱 = risk-on = 流动性充裕 → +2
    - EUR弱 + JPY强 = risk-off = 流动性紧张 → -2
    """
    score = 0.0
    
    # EUR/USD (隐含在Yahoo数据中)
    eur = get_yahoo("欧元")
    if eur:
        if eur["change"] > 0.5:
            score += 1.0
        elif eur["change"] < -0.5:
            score -= 1.0
    
    # USD/JPY
    jpy = get_yahoo("日元")
    if jpy:
        if jpy["change"] > 0.5:
            score += 0.5
        elif jpy["change"] < -0.5:
            score -= 0.5
    
    # VIX（恐慌指数，反向）
    vix = get_yahoo("VIX")
    if vix:
        if vix["price"] > 25:
            score -= 1.0
        elif vix["price"] < 15:
            score += 0.5
    
    return max(-2.0, min(2.0, score))


def calc_demand_factor():
    """
    Demand因子：中国需求
    数据源：人民币汇率、铜价
    范围：[-2.0, +2.0]
    
    逻辑：
    - 人民币强 → 中国需求好 → +2
    - 铜价上涨 → 经济好 → +2
    """
    score = 0.0
    
    # 美元/人民币（反向：人民币强 = CNH下跌）
    cnh = get_yahoo("離岸人民幣")
    if cnh:
        if cnh["change"] < -0.3:
            score += 1.0
        elif cnh["change"] > 0.3:
            score -= 1.0
    
    # 铜价（经济晴雨表）
    copper = get_yahoo("铜")
    if copper:
        if copper["change"] > 1.0:
            score += 0.5
        elif copper["change"] < -1.0:
            score -= 0.5
    
    return max(-2.0, min(2.0, score))


def _strength(score):
    """强度描述"""
    if score > 1.5:
        return "极强"
    elif score > 0.8:
        return "强"
    elif score > 0.3:
        return "中"
    elif score > -0.3:
        return "弱"
    elif score > -0.8:
        return "中"
    elif score > -1.5:
        return "强"
    else:
        return "极强"


def _summary(usd, liquidity, demand, gold, silver, tin, oil):
    """生成总结"""
    # 判断 regime
    if usd > 0.5 and liquidity < -0.5:
        regime = "risk-off"
    elif usd < -0.5 and liquidity > 0.5:
        regime = "risk-on"
    else:
        regime = "MIXED"
    
    # 主导因子
    factors = {"USD": abs(usd), "Liquidity": abs(liquidity), "Demand": abs(demand)}
    dominant = max(factors, key=factors.get)
    
    # 主线资产
    assets = {"Gold": abs(gold), "Silver": abs(silver), "Tin": abs(tin), "Oil": abs(oil)}
    leader = max(assets, key=assets.get)
    
    return {
        "regime": regime,
        "dominant": dominant,
        "leader": leader
    }


def calc_signals():
    """计算三因子信号（双层架构）"""
    usd = calc_usd_factor()  # 返回 dict: {final, macro, market}
    liquidity = calc_liquidity_factor()
    demand = calc_demand_factor()
    
    usd_final = usd["final"]
    
    # 资产信号
    gold_score = -1.0 * usd_final + 0.6 * liquidity
    silver_score = gold_score + 0.5 * demand
    tin_score = 0.8 * demand + 0.4 * liquidity
    oil_score = 0.8 * liquidity + 0.2 * demand
    
    return {
        "factors": {
            "USD": usd_final,
            "USD_macro": usd["macro"],
            "USD_market": usd["market"],
            "Liquidity": liquidity,
            "Demand": demand
        },
        "assets": {
            "Gold": {"score": gold_score, "dir": "↑" if gold_score > 0.3 else "↓" if gold_score < -0.3 else "→", "str": _strength(gold_score)},
            "Silver": {"score": silver_score, "dir": "↑" if silver_score > 0.3 else "↓" if silver_score < -0.3 else "→", "str": _strength(silver_score)},
            "Tin": {"score": tin_score, "dir": "↑" if tin_score > 0.3 else "↓" if tin_score < -0.3 else "→", "str": _strength(tin_score)},
            "Oil": {"score": oil_score, "dir": "↑" if oil_score > 0.3 else "↓" if oil_score < -0.3 else "→", "str": _strength(oil_score)}
        },
        "summary": _summary(usd_final, liquidity, demand, gold_score, silver_score, tin_score, oil_score)
    }


if __name__ == "__main__":
    signals = calc_signals()
    print("=== 三因子信号 v2.0 (双层架构) ===")
    print(f"USD_final:  {signals['factors']['USD']:+.2f}")
    print(f"  USD_macro:  {signals['factors']['USD_macro']:+.2f}")
    print(f"  USD_market: {signals['factors']['USD_market']:+.2f}")
    print(f"Liquidity:  {signals['factors']['Liquidity']:+.2f}")
    print(f"Demand:     {signals['factors']['Demand']:+.2f}")
    print()
    for name, info in signals["assets"].items():
        print(f"{name}: {info['dir']} {info['score']:+.2f} ({info['str']})")
    print()
    print(f"Regime: {signals['summary']['regime']}")
    print(f"Dominant: {signals['summary']['dominant']}")
    print(f"Leader: {signals['summary']['leader']}")
