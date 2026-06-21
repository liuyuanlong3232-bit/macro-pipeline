#!/usr/bin/env python3
"""
宏观信号引擎 v1.1
三因子评分系统 + 资产线性函数模型

三因子定义:
  USD       = [-2.0, +2.0]  美元强度
  Liquidity = [-2.0, +2.0]  流动性（EUR/JPY驱动）
  Demand    = [-2.0, +2.0]  中国需求

资产函数:
  Gold   = -1.0 × USD + 0.6 × Liquidity
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

# ═══════ 三因子计算 ═══════
def calc_usd_factor():
    """
    USD因子：美元强度
    数据源：CPI、非农、Fed利率 vs 预期
    范围：[-2.0, +2.0]
    
    逻辑：
    - CPI高于预期 → 通胀压力 → Fed偏鹰 → USD↑
    - 非农强劲 → 经济好 → USD↑
    - 利率高 → USD↑
    """
    score = 0.0
    
    # CPI（最新 vs 前值）
    cpi = get_macro("macro_美国CPI")
    if cpi:
        # 简化：CPI > 330 视为偏高
        if cpi > 335:
            score += 1.0
        elif cpi < 325:
            score -= 0.5
    
    # 非农就业
    nfp = get_macro("macro_美国非农就业")
    if nfp:
        # NFP > 200K 视为强劲
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
        # EUR上涨 = 流动性充裕
        if eur["change"] > 0.5:
            score += 1.0
        elif eur["change"] < -0.5:
            score -= 1.0
    
    # USD/JPY
    jpy = get_yahoo("日元")
    if jpy:
        # JPY下跌(USD/JPY上涨) = risk-on
        if jpy["change"] > 0.5:
            score += 0.5
        elif jpy["change"] < -0.5:
            score -= 0.5
    
    # VIX（恐慌指数，反向）
    vix = get_yahoo("VIX")
    if vix:
        # VIX < 15 = 低恐慌 = 流动性好
        if vix["price"] < 15:
            score += 0.5
        elif vix["price"] > 25:
            score -= 1.0
    
    return max(-2.0, min(2.0, score))

def calc_demand_factor():
    """
    Demand因子：中国需求
    数据源：PMI、信贷、进出口
    范围：[-2.0, +2.0]
    
    逻辑：
    - 出口强劲 → 中国需求好 → +1
    - 进口增长 → 内需好 → +1
    - LPR下降 → 刺激经济 → +0.5
    """
    score = 0.0
    
    # 出口
    export = get_macro("macro_中国出口")
    if export:
        # 出口增长（简化判断）
        if export > 3000:  # 亿美元
            score += 1.0
        elif export < 2000:
            score -= 0.5
    
    # 进口
    import_data = get_macro("macro_中国进口")
    if import_data:
        if import_data > 2500:
            score += 0.5
        elif import_data < 1500:
            score -= 0.5
    
    # LPR利率（低利率 = 刺激）
    lpr = get_macro("macro_中国LPR利率")
    if lpr:
        if lpr < 3.5:
            score += 0.5
        elif lpr > 4.5:
            score -= 0.5
    
    return max(-2.0, min(2.0, score))

# ═══════ 资产函数 ═══════
def calc_gold(usd, liquidity):
    """Gold = -1.0 × USD + 0.6 × Liquidity"""
    return -1.0 * usd + 0.6 * liquidity

def calc_silver(gold, demand):
    """Silver = Gold + 0.5 × Demand"""
    return gold + 0.5 * demand

def calc_tin(demand, liquidity):
    """Tin = 0.8 × Demand + 0.4 × Liquidity"""
    return 0.8 * demand + 0.4 * liquidity

def calc_oil(liquidity, demand):
    """Oil = 0.8 × Liquidity + 0.2 × Demand"""
    return 0.8 * liquidity + 0.2 * demand

# ═══════ 信号判断 ═══════
def score_to_signal(score):
    """分数转信号"""
    if score > 0.5:
        return "↑", "强" if score > 1.0 else "中"
    elif score < -0.5:
        return "↓", "强" if score < -1.0 else "中"
    else:
        return "→", "弱"

# ═══════ 主函数 ═══════
def calc_all_signals():
    """计算所有信号"""
    # 三因子
    usd = calc_usd_factor()
    liquidity = calc_liquidity_factor()
    demand = calc_demand_factor()
    
    # 资产分数
    gold_score = calc_gold(usd, liquidity)
    silver_score = calc_silver(gold_score, demand)
    tin_score = calc_tin(demand, liquidity)
    oil_score = calc_oil(liquidity, demand)
    
    # 信号
    gold_dir, gold_str = score_to_signal(gold_score)
    silver_dir, silver_str = score_to_signal(silver_score)
    tin_dir, tin_str = score_to_signal(tin_score)
    oil_dir, oil_str = score_to_signal(oil_score)
    
    # 市场状态
    if usd < 0 and liquidity > 0:
        regime = "risk-on"
    elif usd > 0 and liquidity < 0:
        regime = "risk-off"
    else:
        regime = "mixed"
    
    # 主导因子
    abs_factors = {"USD": abs(usd), "Liquidity": abs(liquidity), "Demand": abs(demand)}
    dominant = max(abs_factors, key=abs_factors.get)
    
    # 主线资产
    asset_scores = {"贵金属": abs(gold_score) + abs(silver_score), 
                    "工业金属": abs(tin_score), 
                    "能源": abs(oil_score)}
    leader = max(asset_scores, key=asset_scores.get)
    
    return {
        "factors": {
            "USD": round(usd, 2),
            "Liquidity": round(liquidity, 2),
            "Demand": round(demand, 2)
        },
        "assets": {
            "Gold": {"score": round(gold_score, 2), "dir": gold_dir, "str": gold_str},
            "Silver": {"score": round(silver_score, 2), "dir": silver_dir, "str": silver_str},
            "Tin": {"score": round(tin_score, 2), "dir": tin_dir, "str": tin_str},
            "Oil": {"score": round(oil_score, 2), "dir": oil_dir, "str": oil_str}
        },
        "summary": {
            "regime": regime,
            "dominant": dominant,
            "leader": leader
        }
    }

# ═══════ 测试 ═══════
if __name__ == "__main__":
    result = calc_all_signals()
    
    print("=== 三因子评分 ===")
    for k, v in result["factors"].items():
        print(f"  {k}: {v:+.2f}")
    
    print("\n=== 资产信号 ===")
    for k, v in result["assets"].items():
        print(f"  {k}: {v['dir']} {v['score']:+.2f} ({v['str']})")
    
    print("\n=== 市场总结 ===")
    print(f"  状态: {result['summary']['regime']}")
    print(f"  主导因子: {result['summary']['dominant']}")
    print(f"  主线资产: {result['summary']['leader']}")
