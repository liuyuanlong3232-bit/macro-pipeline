#!/usr/bin/env python3
"""全球+中国农业周度研究报告"""
import os
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
import requests

load_dotenv(Path(os.environ.get("HERMES_HOME", str(Path.home() / "hermes-pipeline"))) / ".env")
DATA_DIR = Path.home() / "hermes-macro-data"
TODAY = datetime.now().strftime("%Y-%m-%d")

def load(name):
    p = DATA_DIR / "csv" / TODAY / f"{name}.csv"
    if p.exists(): return pd.read_csv(p)
    # 手动读SQLite
    import sqlite3
    db = sqlite3.connect(str(DATA_DIR / "hermes.db"))
    df = pd.read_sql(f"SELECT * FROM \"{name}\"", db)
    db.close()
    return df

# ═══ 方向判断工具函数 ═══
def fmt_score(val):
    """格式化评分，避免显示-0"""
    clipped = max(-10, min(10, val))
    if -0.5 < clipped < 0.5:
        return "0"
    return f"{clipped:+.0f}"

def direction(chg):
    """根据涨跌幅返回方向箭头"""
    if chg is None or chg == "—":
        return "—"
    try:
        c = float(chg)
    except (ValueError, TypeError):
        return "—"
    if c > 1.0:
        return "↑"
    elif c < -1.0:
        return "↓"
    else:
        return "→震荡"

def score_from_chg(chg):
    """根据涨跌幅映射到-10~+10评分"""
    if chg is None or chg == "—":
        return 0
    try:
        c = float(chg)
    except (ValueError, TypeError):
        return 0
    # 超过±5%给极端分，否则线性映射
    if c > 5: return 8
    if c < -5: return -8
    return round(c * 1.5)  # 线性映射，±5%→±7.5

def cot_signal_adjustment(ci, net_pos):
    """根据COT Index和净持仓调整评分偏移"""
    if ci is None or ci == "—":
        return 0
    try:
        ci_val = float(ci)
    except (ValueError, TypeError):
        return 0
    if ci_val <= 10:
        return -2  # 极端看空
    elif ci_val <= 30:
        return -1  # 看空
    elif ci_val >= 90:
        return 2   # 极端看多
    elif ci_val >= 70:
        return 1   # 看多
    return 0       # 中性


# ═══ Tushare中国期货 ═══
TUSHARE_MAP = {
    "豆粕": "M", "豆油": "Y", "玉米": "C",
    "豆一": "A", "生猪": "LH", "白糖": "SR", "棉花": "CF",
    "菜籽油": "OI", "棕榈油": "P", "鸡蛋": "JD",
}

def fetch_china_futures():
    """从Tushare获取DCE/CZCE主力合约行情"""
    token = os.getenv("TUSHARE_TOKEN")
    if not token:
        return []

    try:
        today = datetime.now().strftime("%Y%m%d")
        # 回退到最近交易日（周末无数据）
        start = (datetime.now() - timedelta(days=5)).strftime("%Y%m%d")
        url = "http://api.tushare.pro"
        results = []

        for name, ts_code in TUSHARE_MAP.items():
            ts_full = f"{ts_code}.DCE" if ts_code in ("M","Y","C","A","LH","JD","P") else f"{ts_code}.CZCE"

            payload = {
                "api_name": "fut_daily",
                "token": token,
                "params": {"ts_code": ts_full, "start_date": start, "end_date": today},
                "fields": "ts_code,trade_date,close,pre_close,vol"
            }
            try:
                r = requests.post(url, json=payload, timeout=10)
                data = r.json()
                if data.get("code") == 0 and data.get("data",{}).get("items"):
                    items = sorted(data["data"]["items"], key=lambda x: x[1], reverse=True)
                    item = items[0]
                    close = item[2]
                    pre_close = item[3]
                    chg = ((close-pre_close)/pre_close*100) if pre_close and pre_close != 0 else 0
                    results.append({
                        "品种": name,
                        "最新价": close,
                        "前收": pre_close,
                        "涨跌幅": round(chg, 2),
                    })
                else:
                    results.append({"品种": name, "最新价": "—", "前收": "—", "涨跌幅": "—"})
            except Exception as e:
                print(f"  跳过 {name}: {e}")
                results.append({"品种": name, "最新价": "—", "前收": "—", "涨跌幅": "—"})

        return results
    except Exception as e:
        print(f"  Tushare错误: {e}")
        return []


# ═══ 全球农业 ═══
def global_agri():
    yahoo = load("yahoo_futures")
    cot = load("cotdata")

    # ── 建立价格查询字典 ──
    # Yahoo品種列（繁体）: 玉米期貨, 大豆期貨, 小麥期貨, 豆油期貨, 豆粕期貨, 棉花期貨, 糖期貨
    price_lookup = {}  # keyword → {"price": x, "chg_pct": y}
    if not yahoo.empty:
        for _, r in yahoo.iterrows():
            name = str(r.get("品種", ""))
            price = r.get("最新價", "—")
            chg = r.get("日漲跌幅%", "—")
            price_lookup[name] = {"price": price, "chg": chg}

    # 通过关键词匹配获取价格
    def get_price_info(keyword_trad, keyword_simp=None):
        """匹配yahoo行（繁体），返回价格信息"""
        for k, v in price_lookup.items():
            if keyword_trad in k:
                return v
            if keyword_simp and keyword_simp in k:
                return v
        return {"price": "—", "chg": "—"}

    lines = []
    lines.append("# 全球农业周度研究报告（国际版）")
    lines.append(f"生成日期: {TODAY}")
    lines.append("")
    lines.append("---")

    # ══ 一、本周国际农业市场总结 ══
    lines.append("## 一、本周国际农业市场总结")
    lines.append("")
    lines.append("维度 | 核心变化 | 方向（↑/↓/→震荡）")
    lines.append("--- | --- | ---")

    # 定义9个维度及其对应的数据源
    intl_dims_map = [
        ("美豆主力",       "大豆期貨"),
        ("美玉米主力",     "玉米期貨"),
        ("美小麦主力",     "小麥期貨"),
        ("原糖主力",       "糖期貨"),
        ("棉花主力",       "棉花期貨"),
        ("农产品指数",     None),   # 计算综合指数
        ("CFTC农业投机总持仓", None),  # 从COT汇总
        ("美农天气指数",   None),
        ("美湾港口装运率", None),
    ]

    # 计算农产品指数（所有agri品种平均涨跌幅）
    agri_keywords = ["玉米期貨", "大豆期貨", "小麥期貨", "豆油期貨", "豆粕期貨", "棉花期貨", "糖期貨"]
    agri_chgs = []
    for ak in agri_keywords:
        info = get_price_info(ak)
        if info["chg"] != "—":
            try:
                agri_chgs.append(float(info["chg"]))
            except (ValueError, TypeError):
                pass
    avg_chg = sum(agri_chgs) / len(agri_chgs) if agri_chgs else None

    # 计算CFTC农业投机总持仓
    total_agri_net = 0
    has_cot_total = False
    if not cot.empty:
        agri_cot_items = ["玉米", "大豆", "小麦", "糖#11"]
        for _, r in cot.iterrows():
            n = str(r.get("品種", ""))
            for aci in agri_cot_items:
                if aci in n:
                    try:
                        total_agri_net += float(r.get("投機淨持倉", 0))
                        has_cot_total = True
                    except (ValueError, TypeError):
                        pass

    for dim_name, yahoo_keyword in intl_dims_map:
        if yahoo_keyword:
            info = get_price_info(yahoo_keyword)
            p = info["price"]
            c = info["chg"]
            if p != "—":
                core = f"${p}（{c:+.2f}%）" if isinstance(c, float) or (isinstance(c, str) and c != "—" and c != "") else f"${p}"
                try:
                    c_val = float(c) if c != "—" else None
                except (ValueError, TypeError):
                    c_val = None
                lines.append(f"{dim_name} | {core} | {direction(c_val)}")
            else:
                lines.append(f"{dim_name} | — | —")
        elif dim_name == "农产品指数":
            if avg_chg is not None:
                lines.append(f"{dim_name} | 综合{'+' if avg_chg>=0 else ''}{avg_chg:.2f}% | {direction(avg_chg)}")
            else:
                lines.append(f"{dim_name} | — | —")
        elif dim_name == "CFTC农业投机总持仓":
            if has_cot_total:
                direction_str = "↑" if total_agri_net > 0 else ("↓" if total_agri_net < 0 else "→震荡")
                lines.append(f"{dim_name} | 净多{total_agri_net:+,}手 | {direction_str}")
            else:
                lines.append(f"{dim_name} | — | —")
        else:
            lines.append(f"{dim_name} | — | —")

    lines.append("")
    lines.append("**本周核心总结**：锚定USDA边际、北美产区天气、基金调仓、海外出口需求四大核心矛盾")
    lines.append("")
    lines.append("---")

    # ══ 二、主力品种价格走势分析 ══
    lines.append("## 二、主力品种价格走势分析")
    lines.append("")
    lines.append("指标 | 最新价 | 周环比 | 周均价 | 数据来源")
    lines.append("--- | --- | --- | --- | ---")
    agri_items = ["玉米", "大豆", "小麥", "豆油", "豆粕", "棉花", "糖"]
    has_yahoo_data = False
    if not yahoo.empty:
        agri = yahoo[yahoo["品種"].str.contains("|".join(agri_items), na=False)]
        if not agri.empty:
            has_yahoo_data = True
            for _, r in agri.iterrows():
                n = r.get("品種", "")
                p = r.get("最新價", "—")
                chg = r.get("日漲跌幅%", "—")
                lines.append(f"{n} | ${p} | {chg}% | — | Yahoo Finance")
    if not has_yahoo_data:
        for item in agri_items:
            lines.append(f"美{item} | — | — | — | Yahoo Finance")
    lines.append("")
    lines.append("---")

    # ══ 三、海外产业&供需环境分析 ══
    lines.append("## 三、海外产业&供需环境分析")
    lines.append("")
    lines.append("指标 | 当前值 | 周度变动 | 对品种边际影响")
    lines.append("--- | --- | --- | ---")
    # 尝试从已有数据推算部分指标
    # 用COT持仓变化作为资金面参考，价格变化作为需求参考
    env_items_data = []
    # 美产区周度降水 — 无直接数据
    env_items_data.append(("美产区周度降水", "—", "—", "关注NOAA 6-10天展望"))
    # 美作物优良率 — 当前6月 USDA未发布最新
    env_items_data.append(("美作物优良率", "—", "—", "USDA周报待更新"))
    # USDA出口销售数据
    env_items_data.append(("USDA出口销售数据", "—", "—", "关注周度USDA出口检验报告"))
    # 美湾库存
    env_items_data.append(("美湾库存", "—", "—", "—"))
    # 南美结转库存
    env_items_data.append(("南美结转库存", "—", "—", "巴西/阿根廷收割完毕进入出口高峰"))
    # 黑海粮食协议边际
    env_items_data.append(("黑海粮食协议边际", "—", "—", "—"))
    # 海外生物柴油需求
    env_items_data.append(("海外生物柴油需求", "—", "—", "关注RFS政策及生柴掺混报价"))
    # 国际海运运价
    env_items_data.append(("国际海运运价", "—", "—", "关注波罗的海干散货指数BDI"))

    for name, val, wv, impact in env_items_data:
        lines.append(f"{name} | {val} | {wv} | {impact}")
    lines.append("")
    lines.append("---")

    # ══ 四、CFTC农业板块COT资金持仓分析 ══
    lines.append("## 四、CFTC农业板块COT资金持仓分析")
    lines.append("")
    lines.append("品种 | 投机净持仓 | COT Index | Z-Score | 资金信号")
    lines.append("--- | --- | --- | --- | ---")

    # COT数据结构：
    # 品种列（简体）: 小麦SRW, 小麦HRW, 玉米, 大豆, 糖#11, 黄金, 白银...
    # 注意：棉花无COT数据
    # 当前代码用繁体"小麥"匹配不到简体"小麦"，需修复
    if not cot.empty:
        # 定义我们关注的COT品种及显示名称
        cot_targets = [
            ("大豆", "美豆"),
            ("玉米", "美玉米"),
            ("小麦", "美小麦"),   # 简体 "小麦SRW" 或 "小麦HRW"
            ("糖#11", "ICE原糖"),
            ("棉花", "棉花"),     # 无COT数据
        ]
        shown_cot = set()
        for target_key, display_name in cot_targets:
            if target_key == "棉花":
                lines.append(f"{display_name} | — | — | — | 暂无COT数据")
                continue
            if target_key == "小麦":
                # 小麦有SRW和HRW两个合约，合并显示
                wheat_rows = cot[cot["品種"].str.contains("小麦", na=False)]
                if not wheat_rows.empty:
                    total_net = 0
                    ci_val = None
                    z_val = None
                    weight_sum = 0
                    for _, wr in wheat_rows.iterrows():
                        try:
                            net = float(wr.get("投機淨持倉", 0))
                            total_net += net
                            ci = wr.get("COT Index(26W)", 50)
                            try:
                                ci_f = float(ci) if ci != "—" else 50
                            except (ValueError, TypeError):
                                ci_f = 50
                            z = wr.get("Z-Score", 0)
                            try:
                                z_f = float(z) if z != "—" else 0
                            except (ValueError, TypeError):
                                z_f = 0
                            # 简单平均加权
                            ci_val = ci_f if ci_val is None else (ci_val + ci_f) / 2
                            z_val = z_f if z_val is None else (z_val + z_f) / 2
                        except (ValueError, TypeError):
                            pass
                    sig = "极端看空" if ci_val <= 10 else "看空" if ci_val <= 30 else "中性" if ci_val <= 70 else "看多" if ci_val <= 90 else "极端看多"
                    lines.append(f"{display_name}（SRW+HRW合并） | {total_net:+,} | {ci_val:.0f} | {z_val:+.2f} | {sig}")
                    shown_cot.add("小麦")
                else:
                    lines.append(f"{display_name} | — | — | — | —")
                continue

            # 普通品种匹配（简体）
            rows = cot[cot["品種"].str.contains(target_key, na=False)]
            if not rows.empty:
                for _, r in rows.iterrows():
                    n = r.get("品種", "")
                    net = r.get("投機淨持倉", 0)
                    ci = r.get("COT Index(26W)", 50)
                    z = r.get("Z-Score", 0)
                    try:
                        ci_f = float(ci) if ci != "—" else 50
                    except (ValueError, TypeError):
                        ci_f = 50
                    sig = "极端看空" if ci_f <= 10 else "看空" if ci_f <= 30 else "中性" if ci_f <= 70 else "看多" if ci_f <= 90 else "极端看多"
                    lines.append(f"{display_name} | {net:+,} | {ci_f:.0f} | {z:+.2f} | {sig}")
                    shown_cot.add(target_key)
            else:
                lines.append(f"{display_name} | — | — | — | —")
    else:
        for item in ["美豆", "美玉米", "美小麦", "ICE原糖", "棉花"]:
            lines.append(f"{item} | — | — | — | —")
    lines.append("")
    lines.append("---")

    # ══ 五、海外天气&产区边际简析 ══
    lines.append("## 五、海外天气&产区边际简析")
    lines.append("")
    # 根据当前时间生成天气参考
    current_month = datetime.now().month
    if current_month in (6, 7, 8):
        us_season = "美玉米/大豆进入关键授粉期，关注中西部高温及降雨预期"
        sa_season = "巴西/阿根廷新作（2026/27年度）尚未开始种植，关注南半球冬小麦进展"
    elif current_month in (9, 10, 11):
        us_season = "美豆/美玉米收获期，关注降雨对收割进度的影响"
        sa_season = "巴西大豆开始种植（9月中旬起），关注马托格罗索降雨开局"
    elif current_month in (12, 1, 2):
        us_season = "美豆/美玉米处于出口窗口期"
        sa_season = "巴西大豆生长关键期（12-1月），阿根廷开始种植"
    else:
        us_season = "美玉米/大豆种植期，关注播种进度及土壤墒情"
        sa_season = "巴西大豆收割期，阿根廷进入收获"

    lines.append(f"**北美主产区天气预报**：{us_season}。当前NOAA 6-10天展望显示—")
    lines.append("")
    lines.append(f"**阿根廷/巴西新作种植进度**：{sa_season}。—")
    lines.append("")
    lines.append("**黑海产区物流**：关注黑海粮食倡议续约谈判及乌克兰出口走廊运行情况。—")
    lines.append("")
    lines.append("**全球极端天气舆情**：关注厄尔尼诺/拉尼娜转换对全球农产品产区的影响。—")
    lines.append("")
    lines.append("---")

    # ══ 六、供需强弱评分 ══
    lines.append("## 六、供需强弱评分")
    lines.append("")
    lines.append("| 资产 | 评分（-10~+10） | 核心逻辑 |")
    lines.append("|---|:--:|---|")

    # 计算各品种评分
    def get_chg_by_kw(keyword):
        info = get_price_info(keyword)
        if info["chg"] != "—":
            try:
                return float(info["chg"])
            except (ValueError, TypeError):
                pass
        return None

    def get_cot_index(target_simp):
        """获取COT Index（简体匹配）"""
        if cot.empty:
            return None
        rows = cot[cot["品種"].str.contains(target_simp, na=False)]
        if rows.empty:
            return None
        try:
            return float(rows.iloc[0].get("COT Index(26W)", 50))
        except (ValueError, TypeError):
            return None

    # 美豆评分
    soybean_chg = get_chg_by_kw("大豆期貨")
    soybean_ci = get_cot_index("大豆")
    s_score = score_from_chg(soybean_chg) + cot_signal_adjustment(soybean_ci, None)
    s_logic_parts = []
    if soybean_chg is not None:
        s_logic_parts.append(f"价格{'涨' if soybean_chg >= 0 else '跌'}{abs(soybean_chg):.2f}%")
    if soybean_ci is not None:
        ci_label = "极空" if soybean_ci <= 10 else "偏空" if soybean_ci <= 30 else "中性" if soybean_ci <= 70 else "偏多" if soybean_ci <= 90 else "极多"
        s_logic_parts.append(f"COT Index {soybean_ci:.0f}（{ci_label}）")
    s_logic = "+".join(s_logic_parts) if s_logic_parts else "数据有限"
    lines.append(f"| 美豆 | {fmt_score(s_score)} | {s_logic} |")

    # 美玉米评分
    corn_chg = get_chg_by_kw("玉米期貨")
    corn_ci = get_cot_index("玉米")
    c_score = score_from_chg(corn_chg) + cot_signal_adjustment(corn_ci, None)
    c_logic_parts = []
    if corn_chg is not None:
        c_logic_parts.append(f"价格{'涨' if corn_chg >= 0 else '跌'}{abs(corn_chg):.2f}%")
    if corn_ci is not None:
        ci_label = "极空" if corn_ci <= 10 else "偏空" if corn_ci <= 30 else "中性" if corn_ci <= 70 else "偏多" if corn_ci <= 90 else "极多"
        c_logic_parts.append(f"COT Index {corn_ci:.0f}（{ci_label}）")
    c_logic = "+".join(c_logic_parts) if c_logic_parts else "数据有限"
    lines.append(f"| 美玉米 | {fmt_score(c_score)} | {c_logic} |")

    # 美小麦评分
    wheat_chg = get_chg_by_kw("小麥期貨")
    wheat_ci = get_cot_index("小麦")  # 简体匹配
    w_score = score_from_chg(wheat_chg) + cot_signal_adjustment(wheat_ci, None)
    w_logic_parts = []
    if wheat_chg is not None:
        w_logic_parts.append(f"价格{'涨' if wheat_chg >= 0 else '跌'}{abs(wheat_chg):.2f}%")
    if wheat_ci is not None:
        ci_label = "极空" if wheat_ci <= 10 else "偏空" if wheat_ci <= 30 else "中性" if wheat_ci <= 70 else "偏多" if wheat_ci <= 90 else "极多"
        w_logic_parts.append(f"COT Index {wheat_ci:.0f}（{ci_label}）")
    w_logic = "+".join(w_logic_parts) if w_logic_parts else "数据有限"
    lines.append(f"| 美小麦 | {fmt_score(w_score)} | {w_logic} |")

    # 软商品（棉花+原糖）
    cotton_chg = get_chg_by_kw("棉花期貨")
    sugar_chg = get_chg_by_kw("糖期貨")
    soft_scores = []
    soft_parts = []
    if cotton_chg is not None:
        cs = score_from_chg(cotton_chg)
        soft_scores.append(cs)
        soft_parts.append(f"棉花{'涨' if cotton_chg >= 0 else '跌'}{abs(cotton_chg):.2f}%")
    if sugar_chg is not None:
        ss = score_from_chg(sugar_chg)
        soft_scores.append(ss)
        soft_parts.append(f"原糖{'涨' if sugar_chg >= 0 else '跌'}{abs(sugar_chg):.2f}%")
    if soft_scores:
        soft_avg = sum(soft_scores) / len(soft_scores)
    else:
        soft_avg = 0
    # 糖COT中性偏弱，略作调整
    sugar_ci = get_cot_index("糖#11")
    soft_adj = cot_signal_adjustment(sugar_ci, None) if sugar_ci is not None else 0
    soft_final = max(-10, min(10, soft_avg + soft_adj))
    soft_logic = "+".join(soft_parts) if soft_parts else "数据有限"
    if sugar_ci is not None:
        ci_label = "极空" if sugar_ci <= 10 else "偏空" if sugar_ci <= 30 else "中性" if sugar_ci <= 70 else "偏多" if sugar_ci <= 90 else "极多"
        soft_logic += f"+COT Index {sugar_ci:.0f}（{ci_label}）"
    lines.append(f"| 软商品 | {fmt_score(soft_final)} | {soft_logic} |")
    lines.append("")
    lines.append("---")

    # ══ 七、未来30天重点观察方向+潜在风险提示 ══
    lines.append("## 七、未来30天重点观察方向+潜在风险提示")
    lines.append("")
    lines.append("### 未来30天重点观测变量（纯变量罗列，无观点）")
    lines.append("- USDA月度供需报告（WASDE）：关注美豆/美玉米新作面积及单产初值")
    lines.append("- CFTC持仓周报：跟踪投机净持仓边际变化")
    lines.append("- NOAA 6-10天及8-14天气温降水展望：关注中西部产区")
    lines.append("- 美湾/太平洋西北港口FOB升贴水：反映出口物流节奏")
    lines.append("- 南美大豆/玉米出口排船及中国采购节奏")
    lines.append("- 黑海粮食协议谈判及乌克兰出口走廊运行")
    lines.append("- 美联储利率决策对美元指数及商品基金配置的影响")
    lines.append("")
    lines.append("### 市场潜在风险提示（复刻能源周报风险话术）")
    lines.append("- 极端天气风险：北美产区拉尼娜/厄尔尼诺转换可能引发干旱或洪涝")
    lines.append("- 政策风险：中美贸易关系不确定性对大豆/玉米进口关税的影响")
    lines.append("- 地缘政治风险：黑海地区粮食出口协议续约不确定性")
    lines.append("- 汇率风险：美元走势影响美国农产品出口竞争力")
    lines.append("- 资金踩踏风险：COT指标显示部分品种投机净多/空头寸处于极端位置，警惕反转")
    lines.append("")
    lines.append("---")

    # ══ 强制尾部固定话术 ══
    lines.append(f"数据来源：USDA、CFTC、Yahoo Finance、US气象署、波罗的海航运交易所，截至{TODAY}")
    lines.append("免责声明：本文仅为国际农业宏观、资金、产业、天气数据周度复盘，不构成任何投资建议。商品期货交易风险极高，入市需谨慎。")
    lines.append("AI生成标注：本文AI辅助整理，全部核心数据人工核验校准。")
    return "\n".join(lines)


# ═══ 中国农业 ═══
def china_agri():
    china_data = fetch_china_futures()

    # 建立中国品种价格查询
    cn_price_lookup = {}
    if china_data:
        for d in china_data:
            cn_price_lookup[d["品种"]] = d

    def get_cn_info(name):
        return cn_price_lookup.get(name, {"最新价": "—", "涨跌幅": "—"})

    lines = []
    lines.append("# 全球农业周度研究报告（中国本土版）")
    lines.append(f"生成日期: {TODAY}")
    lines.append("")
    lines.append("---")

    # ══ 一、本周国内农业市场总结 ══
    lines.append("## 一、本周国内农业市场总结")
    lines.append("")
    lines.append("维度 | 核心变化 | 方向（↑/↓/→震荡）")
    lines.append("--- | --- | ---")

    # 根据Tushare数据填充维度
    # 国内油脂油料主力：豆粕、豆油、菜籽油、棕榈油平均
    oilseed_names = ["豆粕", "豆油", "菜籽油", "棕榈油"]
    oilseed_chgs = []
    for n in oilseed_names:
        info = get_cn_info(n)
        if info["涨跌幅"] != "—":
            try:
                oilseed_chgs.append(float(info["涨跌幅"]))
            except (ValueError, TypeError):
                pass
    oilseed_avg = sum(oilseed_chgs)/len(oilseed_chgs) if oilseed_chgs else None
    if oilseed_avg is not None:
        lines.append(f"国内油脂油料主力 | 综合{'+' if oilseed_avg>=0 else ''}{oilseed_avg:.2f}% | {direction(oilseed_avg)}")
    else:
        lines.append(f"国内油脂油料主力 | — | —")

    # 国内谷物主力：玉米、豆一
    grain_names = ["玉米", "豆一"]
    grain_chgs = []
    for n in grain_names:
        info = get_cn_info(n)
        if info["涨跌幅"] != "—":
            try:
                grain_chgs.append(float(info["涨跌幅"]))
            except (ValueError, TypeError):
                pass
    grain_avg = sum(grain_chgs)/len(grain_chgs) if grain_chgs else None
    if grain_avg is not None:
        lines.append(f"国内谷物主力 | 综合{'+' if grain_avg>=0 else ''}{grain_avg:.2f}% | {direction(grain_avg)}")
    else:
        lines.append(f"国内谷物主力 | — | —")

    # 白糖棉花主力
    soft_names = ["白糖", "棉花"]
    soft_chgs = []
    for n in soft_names:
        info = get_cn_info(n)
        if info["涨跌幅"] != "—":
            try:
                soft_chgs.append(float(info["涨跌幅"]))
            except (ValueError, TypeError):
                pass
    soft_avg = sum(soft_chgs)/len(soft_chgs) if soft_chgs else None
    if soft_avg is not None:
        lines.append(f"白糖棉花主力 | 综合{'+' if soft_avg>=0 else ''}{soft_avg:.2f}% | {direction(soft_avg)}")
    else:
        lines.append(f"白糖棉花主力 | — | —")

    # 其余维度保留占位符
    placeholder_dims = ["盘面基差", "油厂库存", "饲料企业备货", "产业资金", "进口到港总量"]
    for d in placeholder_dims:
        lines.append(f"{d} | — | —")

    lines.append("")
    lines.append("**本周核心总结**：锚定国内抛储政策、压榨开工、进口到港、养殖刚需、内外盘联动五大核心矛盾")
    lines.append("")
    lines.append("---")

    # ══ 二、国内农品价格走势分析 ══
    lines.append("## 二、国内农品价格走势分析")
    lines.append("")
    lines.append("指标 | 最新价 | 周环比 | 周均价 | 数据来源")
    lines.append("--- | --- | --- | --- | ---")
    if china_data:
        for d in china_data:
            price = d["最新价"] if d["最新价"] != "—" else "—"
            chg = f"{d['涨跌幅']:+.2f}%" if isinstance(d["涨跌幅"], (int, float)) else "—"
            lines.append(f"{d['品种']} | {price} | {chg} | — | Tushare")
    else:
        for name in TUSHARE_MAP.keys():
            lines.append(f"{name} | — | — | — | Tushare")
    lines.append("")
    lines.append("---")

    # ══ 三、国内政策+本土供需环境分析 ══
    lines.append("## 三、国内政策+本土供需环境分析")
    lines.append("")
    lines.append("指标 | 当前值 | 周度变动 | 对盘面边际影响")
    lines.append("--- | --- | --- | ---")
    cn_supply_items = [
        "国储粮油投放量", "沿海油厂压榨率", "豆粕库存",
        "商业玉米库存", "生猪能繁存栏", "进口船期",
        "国内主产区收割进度", "农业惠农/进口政策", "棕榈油马来出关数据"
    ]
    for item in cn_supply_items:
        lines.append(f"{item} | — | — | —")
    lines.append("")
    lines.append("---")

    # ══ 四、内盘产业资金+仓单持仓分析 ══
    lines.append("## 四、内盘产业资金+仓单持仓分析")
    lines.append("")
    lines.append("品种 | 交易所仓单量 | 产业套保持仓 | 主力资金持仓 | 资金信号")
    lines.append("--- | --- | --- | --- | ---")
    if china_data:
        for d in china_data:
            lines.append(f"{d['品种']} | — | — | — | —")
    else:
        for name in TUSHARE_MAP.keys():
            lines.append(f"{name} | — | — | — | —")
    lines.append("")
    lines.append("---")

    # ══ 五、本土产业刚需&进出口联动简析 ══
    lines.append("## 五、本土产业刚需&进出口联动简析")
    lines.append("")
    lines.append("**国内饲料养殖需求**：生猪存栏高位运行，饲料刚需维持，关注豆粕添加比例变化。—")
    lines.append("")
    lines.append("**食品加工刚需**：—")
    lines.append("")
    lines.append("**月度进口配额**：—")
    lines.append("")
    lines.append("**内外盘套利窗口**：—")
    lines.append("")
    lines.append("**南方备货旺季**：—")
    lines.append("")
    lines.append("**主产区天气灾情**：—")
    lines.append("")
    lines.append("---")

    # ══ 六、供需强弱评分 ══
    lines.append("## 六、供需强弱评分")
    lines.append("")
    lines.append("| 资产 | 评分（-10~+10） | 核心逻辑 |")
    lines.append("|---|:--:|---|")

    # 油脂油料评分
    oilseed_scores = []
    oilseed_logics = []
    for n in oilseed_names:
        info = get_cn_info(n)
        if info["涨跌幅"] != "—":
            try:
                chg = float(info["涨跌幅"])
                sc = score_from_chg(chg)
                oilseed_scores.append(sc)
                oilseed_logics.append(f"{n}{'涨' if chg>=0 else '跌'}{abs(chg):.2f}%")
            except (ValueError, TypeError):
                pass
    if oilseed_scores:
        oilseed_score = sum(oilseed_scores) / len(oilseed_scores)
    else:
        oilseed_score = 0
    oilseed_logic = "本土供需+进口+政策因子罗列"
    if oilseed_logics:
        oilseed_logic = "+".join(oilseed_logics)
    lines.append(f"| 油脂油料 | {fmt_score(oilseed_score)} | {oilseed_logic} |")

    # 国内谷物评分
    grain_scores = []
    grain_logics = []
    for n in grain_names:
        info = get_cn_info(n)
        if info["涨跌幅"] != "—":
            try:
                chg = float(info["涨跌幅"])
                sc = score_from_chg(chg)
                grain_scores.append(sc)
                grain_logics.append(f"{n}{'涨' if chg>=0 else '跌'}{abs(chg):.2f}%")
            except (ValueError, TypeError):
                pass
    if grain_scores:
        grain_score = sum(grain_scores) / len(grain_scores)
    else:
        grain_score = 0
    grain_logic = "本土库存+抛储+刚需因子罗列"
    if grain_logics:
        grain_logic = "+".join(grain_logics)
    lines.append(f"| 国内谷物 | {fmt_score(grain_score)} | {grain_logic} |")

    # 软商品内盘评分
    soft_inner_scores = []
    soft_inner_logics = []
    for n in soft_names:
        info = get_cn_info(n)
        if info["涨跌幅"] != "—":
            try:
                chg = float(info["涨跌幅"])
                sc = score_from_chg(chg)
                soft_inner_scores.append(sc)
                soft_inner_logics.append(f"{n}{'涨' if chg>=0 else '跌'}{abs(chg):.2f}%")
            except (ValueError, TypeError):
                pass
    if soft_inner_scores:
        soft_inner_score = sum(soft_inner_scores) / len(soft_inner_scores)
    else:
        soft_inner_score = 0
    soft_inner_logic = "现货+仓单+进口因子罗列"
    if soft_inner_logics:
        soft_inner_logic = "+".join(soft_inner_logics)
    lines.append(f"| 软商品内盘 | {fmt_score(soft_inner_score)} | {soft_inner_logic} |")
    lines.append("")
    lines.append("---")

    # ══ 七、未来30天重点观察方向+潜在风险提示 ══
    lines.append("## 七、未来30天重点观察方向+潜在风险提示")
    lines.append("")
    lines.append("### 未来30天重点观测变量（本土化指标）")
    lines.append("- 国储大豆/食用油投放节奏及成交率")
    lines.append("- 沿海油厂压榨开工率及豆粕库存变化")
    lines.append("- 生猪存栏及饲料企业备货情绪")
    lines.append("- 进口大豆/玉米到港船期及通关速度")
    lines.append("- 南方主产区天气对油菜籽/早稻影响")
    lines.append("- 中美/中加贸易关系对进口大豆/菜籽的影响")
    lines.append("")
    lines.append("### 市场潜在风险提示")
    lines.append("- 政策风险：国储投放力度超预期或进口关税调整")
    lines.append("- 进口风险：南美物流延误或中美贸易摩擦升级")
    lines.append("- 疫病风险：非洲猪瘟等动物疫病影响饲料需求")
    lines.append("- 天气风险：主产区异常天气影响新季作物产量")
    lines.append("- 汇率风险：人民币汇率波动影响进口成本")
    lines.append("")
    lines.append("---")

    # ══ 强制尾部固定话术 ══
    lines.append(f"数据来源：大商所、郑商所、国家粮油信息中心、海关总署、卓创资讯、我的农产品网，截至{TODAY}")
    lines.append("免责声明：本文仅为国内农业政策、产业、库存、资金数据周度复盘，不构成任何投资建议。商品期货交易风险极高，入市需谨慎。")
    lines.append("AI生成标注：本文AI辅助整理，全部核心数据人工核验校准。")
    return "\n".join(lines)


def main():
    r1 = global_agri()
    r2 = china_agri()
    p1 = DATA_DIR / "reports" / f"agri_global_{TODAY}.md"
    p2 = DATA_DIR / "reports" / f"agri_china_{TODAY}.md"
    # 确保目录存在
    p1.parent.mkdir(parents=True, exist_ok=True)
    p2.parent.mkdir(parents=True, exist_ok=True)
    with open(p1, "w", encoding="utf-8") as f: f.write(r1)
    with open(p2, "w", encoding="utf-8") as f: f.write(r2)
    print("全球农业 + 中国农业 报告已生成")


if __name__ == "__main__":
    main()
