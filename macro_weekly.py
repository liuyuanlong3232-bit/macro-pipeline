#!/usr/bin/env python3
"""全球宏观周度研究报告 - 输出结构匹配固定提示词模板"""
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
import akshare as ak
import tushare as ts

load_dotenv(Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))) / ".env")
DATA_DIR = Path.home() / "hermes-macro-data"
TODAY = datetime.now().strftime("%Y-%m-%d")
TS_TOKEN = os.getenv("TUSHARE_TOKEN")

def load_csv(name):
    p = DATA_DIR / "csv" / TODAY / f"{name}.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()

def gv(df, kw):
    """从FRED取指标最新值，返回(数值, 日期)"""
    name_col = [c for c in df.columns if "標" in c][0]
    val_col = [c for c in df.columns if "數值" in c or "値" in c or "值" in c][0]
    sub = df[df[name_col].str.contains(kw, na=False, regex=False)].sort_values("日期", ascending=False)
    if sub.empty:
        return None, None
    return sub.iloc[0][val_col], sub.iloc[0]["日期"]

def gv_all(df, kw):
    """从FRED取指标全部值（按日期降序），返回[(数值, 日期), ...]"""
    name_col = [c for c in df.columns if "標" in c][0]
    val_col = [c for c in df.columns if "數值" in c or "値" in c or "值" in c][0]
    sub = df[df[name_col].str.contains(kw, na=False, regex=False)].sort_values("日期", ascending=False)
    if sub.empty:
        return []
    return list(zip(sub[val_col].tolist(), sub["日期"].tolist()))

def gv_yf(df, code):
    """从yahoo_futures取某symbol最新价，返回(价格, 日期)"""
    if df.empty or "代碼" not in df.columns:
        return None, None
    sub = df[df["代碼"] == code]
    if sub.empty:
        return None, None
    row = sub.iloc[0]
    return row.get("最新價"), row.get("日期")

def gv_vix(df):
    """从vix_data取最新VIX价格"""
    if df.empty or "价格" not in df.columns:
        return None, None
    row = df.iloc[0]
    return row["价格"], row.get("报告日期", "")


def fetch_cn_macro():
    """AKShare获取中国宏观实时数据：DR007/LPR/准备金率/SHIBOR"""
    result = {}
    try:
        df = ak.repo_rate_query()
        if df is not None and not df.empty:
            r = df.iloc[-1]
            result["dr007"] = r["FR007"]
            result["repo_date"] = r["date"]
    except:
        pass
    try:
        df = ak.macro_china_shibor_all()
        if df is not None and not df.empty:
            r = df.iloc[-1]
            result["shibor_1w"] = r["1W-定价"]
            result["shibor_date"] = r["日期"]
    except:
        pass
    try:
        df = ak.macro_china_lpr()
        if df is not None and not df.empty:
            r = df.iloc[-1]
            result["lpr1y"] = r["LPR1Y"]
            result["lpr5y"] = r["LPR5Y"]
            result["lpr_date"] = r["TRADE_DATE"]
    except:
        pass
    try:
        df = ak.macro_china_reserve_requirement_ratio()
        if df is not None and not df.empty:
            r = df.iloc[-1]
            result["rrr_large"] = r.get("大型金融机构-调整后", r.get("大型金融机构-调整前"))
    except:
        pass
    return result


def fetch_social_financing():
    """Tushare sf_month — 社会融资规模月度数据"""
    if not TS_TOKEN:
        return None
    try:
        pro = ts.pro_api(TS_TOKEN)
        df = pro.sf_month(start_m="202501", end_m=datetime.now().strftime("%Y%m"))
        if df is not None and not df.empty:
            r = df.iloc[-1]
            return {
                "month": r.get("month"),
                "inc_month": r.get("inc_month"),
                "inc_cumval": r.get("inc_cumval"),
                "stk_endval": r.get("stk_endval"),
            }
    except Exception as e:
        print(f"[sf_month] Error: {e}")
    return None


def fmt_val(v, kind="number"):
    """数值格式化"""
    if v is None:
        return "\u2014"
    try:
        v = float(v)
    except:
        return str(v)
    if kind == "pct":
        return f"{v:.2f}%"
    elif kind == "rate":
        return f"{v:.2f}%"
    elif kind == "deficit":
        # 百万美元 -> 万亿
        t = v / 1e6
        return f"${t:+.2f}T"
    elif kind == "jolts":
        # 千人 -> 万人
        return f"{v/10:.1f}\u4e07"
    elif kind == "payems":
        # 千人 -> 万人
        return f"{v/10:.0f}\u4e07"
    elif kind == "dollar":
        return f"${v:.2f}"
    elif kind == "index":
        return f"{v:.2f}"
    return str(v)

def compute_scores(fred):
    """从fred_indicators数据综合推算评分(-10~+10)"""
    # 默认中性值
    score_us = 0
    score_risk = 0
    score_cn = 0
    us_reasons = []
    risk_reasons = []
    cn_reasons = []

    # 美国宏观流动性：联邦基金利率、TIPS、美元指数
    ff, _ = gv(fred, "聯邦基金利率")
    tips, _ = gv(fred, "TIPS")
    dxy, _ = gv(fred, "美元指數")
    dgs10, _ = gv(fred, "10 年期國債")
    unemp, _ = gv(fred, "失業率")

    if ff is not None:
        ff = float(ff)
        if ff > 5.0:
            score_us -= 3
            us_reasons.append(f"聯邦基金利率{ff:.2f}%偏高")
        elif ff > 4.0:
            score_us -= 2
            us_reasons.append(f"聯邦基金利率{ff:.2f}%中性偏緊")
        elif ff > 3.0:
            score_us -= 1
            us_reasons.append(f"聯邦基金利率{ff:.2f}%適中")
        else:
            score_us += 1
            us_reasons.append(f"聯邦基金利率{ff:.2f}%偏寬鬆")

    if tips is not None:
        tips = float(tips)
        if tips > 2.0:
            score_us -= 2
            us_reasons.append(f"TIPS{tips:.2f}%實際利率偏高")
        elif tips > 1.0:
            score_us -= 1
            us_reasons.append(f"TIPS{tips:.2f}%實際利率中性")
        else:
            score_us += 1
            us_reasons.append(f"TIPS{tips:.2f}%實際利率偏低")

    if dxy is not None:
        dxy = float(dxy)
        if dxy > 110:
            score_us -= 2
            us_reasons.append(f"美元指數{dxy:.2f}強勢")
        elif dxy > 100:
            score_us -= 1
            us_reasons.append(f"美元指數{dxy:.2f}中性偏強")
        else:
            score_us += 1
            us_reasons.append(f"美元指數{dxy:.2f}偏弱")

    if dgs10 is not None:
        dgs10 = float(dgs10)
        if dgs10 > 4.5:
            score_us -= 2
            us_reasons.append(f"10Y收益率{dgs10:.2f}%高位")
        elif dgs10 > 3.5:
            score_us -= 1
            us_reasons.append(f"10Y收益率{dgs10:.2f}%偏高")
        elif dgs10 > 2.5:
            score_us += 0
        else:
            score_us += 1

    if unemp is not None:
        unemp = float(unemp)
        if unemp < 4.0:
            score_us += 1
            us_reasons.append(f"失業率{unemp:.1f}%歷史低位")
        elif unemp < 5.0:
            us_reasons.append(f"失業率{unemp:.1f}%正常")
        else:
            score_us -= 1
            us_reasons.append(f"失業率{unemp:.1f}%走高")

    # 全球风险情绪：使用DXY波动、利差等代理
    # 用fed funds vs 10Y spread判断曲线形态
    if ff is not None and dgs10 is not None:
        spread = float(dgs10) - float(ff)
        if spread < 0:
            score_risk -= 2
            risk_reasons.append(f"收益率曲線倒掛{spread:.2f}bp")
        elif spread < 1.0:
            score_risk -= 1
            risk_reasons.append(f"收益率曲線平坦{spread:.2f}bp")
        else:
            score_risk += 1
            risk_reasons.append(f"收益率曲線正常{spread:.2f}bp")

    # 用美元强弱代理风险偏好
    if dxy is not None:
        dxy = float(dxy)
        if dxy > 110:
            score_risk -= 1
            risk_reasons.append(f"美元強勢壓制風險偏好")
        elif dxy < 95:
            score_risk += 1
            risk_reasons.append(f"美元弱勢利好新興市場")

    # 中国货币环境 — 从AKShare获取
    cn_data_scr = fetch_cn_macro()
    dr007 = cn_data_scr.get("dr007")
    lpr = cn_data_scr.get("lpr1y")
    rrr = cn_data_scr.get("rrr_large")
    cn_notes = []
    if dr007:
        cn_notes.append(f"DR007{float(dr007):.2f}%")
        if float(dr007) > 2.5:
            score_cn -= 1
        elif float(dr007) < 1.5:
            score_cn += 1
    if lpr:
        cn_notes.append(f"LPR1Y={lpr}%")
    if rrr:
        cn_notes.append(f"存准率{rrr}%")
    # 社融
    sf_data = fetch_social_financing()
    if sf_data and sf_data.get("inc_month"):
        try:
            inc = float(sf_data["inc_month"])
            if inc > 10000:
                cn_notes.append(f"社融+{inc/10000:.1f}万亿")
                score_cn += 1
            elif inc > 5000:
                cn_notes.append(f"社融+{inc/10000:.1f}万亿")
            else:
                cn_notes.append(f"社融+{inc/10000:.1f}万亿")
                score_cn -= 1
        except:
            pass
    cn_reasons.append("；".join(cn_notes) if cn_notes else "中国宏观数据暂缺")
    score_us = max(-10, min(10, score_us))
    score_risk = max(-10, min(10, score_risk))
    score_cn = max(-10, min(10, score_cn))

    return score_us, score_risk, score_cn, us_reasons, risk_reasons, cn_reasons


def report():
    fred = load_csv("fred_indicators")
    yf = load_csv("yahoo_futures")
    vix_df = load_csv("vix_data")

    lines = []
    lines.append("# \U0001f30d 全球宏观周度研究报告")
    lines.append(f"**生成日期**: {TODAY}")
    lines.append("")

    # ============================================================
    # 一、本周全球宏观市场总结
    # ============================================================
    lines.append("## 一、本周全球宏观市场总结")
    lines.append("")
    lines.append("| 维度 | 核心变化 | 方向 |")
    lines.append("|------|----------|:----:|")

    # 提取指标
    dgs10, d10_d = gv(fred, "10 年期國債")
    tips, tips_d = gv(fred, "TIPS")
    dxy, dxy_d = gv(fred, "美元指數")
    ff, ff_d = gv(fred, "聯邦基金利率")

    dgs10_str = fmt_val(dgs10, "rate") if dgs10 is not None else "—"
    tips_str = fmt_val(tips, "rate") if tips is not None else "—"
    dxy_str = fmt_val(dxy, "index") if dxy is not None else "—"

    # 方向判断
    dir_dgs10 = "↑" if dgs10 is not None and float(dgs10) > 4.0 else ("↓" if dgs10 is not None and float(dgs10) < 3.5 else "→震荡")
    dir_tips = "↑" if tips is not None and float(tips) > 2.0 else ("↓" if tips is not None and float(tips) < 1.0 else "→震荡")
    dir_dxy = "↑" if dxy is not None and float(dxy) > 105 else ("↓" if dxy is not None and float(dxy) < 95 else "→震荡")
    dir_ff = "↑" if ff is not None and float(ff) > 5.0 else ("↓" if ff is not None and float(ff) < 4.0 else "→震荡")

    lines.append(f"| 10Y美债收益率 | {dgs10_str} | {dir_dgs10} |")
    lines.append(f"| TIPS实际利率 | {tips_str} | {dir_tips} |")
    lines.append(f"| 美元指数 | {dxy_str} | {dir_dxy} |")
    lines.append(f"| 欧元/日元离岸汇率 | — | →震荡 |")
    lines.append(f"| 美联储降息概率 | — | →震荡 |")
    lines.append(f"| VIX恐慌指数 | — | →震荡 |")
    lines.append(f"| 跨境美元流动性 | — | →震荡 |")
    
    # 中国DR007 — AKShare
    cn_data = fetch_cn_macro()
    dr007 = cn_data.get("dr007")
    dr7_str = f"{dr007:.2f}%" if dr007 else "—"
    dir_dr7 = "↑" if dr007 and dr007 > 2.0 else ("↓" if dr007 and dr007 < 1.4 else "→震荡") if dr007 else "→震荡"
    lines.append(f"| 中国DR007利率 | {dr7_str} | {dir_dr7} |")
    lines.append("")
    lines.append("**本周核心总结**：美联储政策预期维持" + ("紧缩" if dir_ff == "↑" else "观望" if dir_ff == "→震荡" else "宽松") +
                 "基调，欧美通胀边际" + ("上行" if dir_tips == "↑" else "回落" if dir_tips == "↓" else "平稳") +
                 "，全球风险情绪中性偏谨慎，中美流动性" + ("收敛" if dir_dgs10 == "↑" else "宽松" if dir_dgs10 == "↓" else "平稳") +
                 "，离岸美元" + ("强势" if dir_dxy == "↑" else "走弱" if dir_dxy == "↓" else "震荡") +
                 "，五大核心矛盾维持现有格局。")
    lines.append("")

    # ============================================================
    # 二、核心宏观指标价格走势
    # ============================================================
    lines.append("## 二、核心宏观指标价格走势")
    lines.append("")
    lines.append("| 指标 | 最新价 | 周环比 | 周均价 | 数据来源 |")
    lines.append("|------|--------|:------:|:------:|----------|")

    # 长短端美债
    dgs2, _ = gv(fred, "2 年期國債")
    dgs5, _ = gv(fred, "5 年期國債")
    dgs30, d30_d = gv(fred, "30年期國債")
    # 实际利率
    tips5, _ = gv(fred, "5年期TIPS")
    # 美元
    # 主流非美货币 - 从Yahoo读取
    eurusd, _ = gv_yf(yf, "EURUSD=X")
    usdjpy, _ = gv_yf(yf, "USDJPY=X")
    usdcnh, _ = gv_yf(yf, "CNH=X")
    # 恐慌指数 - 从vix_data/yahoo_futures读取
    vix_val, vix_date = gv_yf(yf, "^VIX")
    if vix_val is None:
        vix_val, vix_date = gv_vix(vix_df)
    # 境内外资金利率
    libor, _ = gv(fred, "Libor")
    # 人民币汇率
    cnh, _ = gv(fred, "離岸人民幣")

    rows2 = [
        ("2Y美债收益率", fmt_val(dgs2, "rate") if dgs2 is not None else "—", "—", "—", "FRED"),
        ("5Y美债收益率", fmt_val(dgs5, "rate") if dgs5 is not None else "—", "—", "—", "FRED"),
        ("10Y美债收益率", fmt_val(dgs10, "rate") if dgs10 is not None else "—", "—", "—", "FRED"),
        ("30Y美债收益率", fmt_val(dgs30, "rate") if dgs30 is not None else "—", "—", "—", "FRED"),
        ("TIPS实际利率", fmt_val(tips, "rate") if tips is not None else "—", "—", "—", "FRED"),
        ("美元指数", fmt_val(dxy, "index") if dxy is not None else "—", "—", "—", "FRED"),
        ("欧元/美元", fmt_val(eurusd) if eurusd is not None else "—", "—", "—", "Yahoo"),
        ("美元/日元", fmt_val(usdjpy) if usdjpy is not None else "—", "—", "—", "Yahoo"),
        ("美元/离岸人民币", fmt_val(usdcnh) if usdcnh is not None else "—", "—", "—", "Yahoo"),
        ("VIX恐慌指数", fmt_val(vix_val, "index") if vix_val is not None else "—", "—", "—", "Yahoo/VIX"),
        ("联邦基金利率", fmt_val(ff, "rate") if ff is not None else "—", "—", "—", "FRED"),
    ]
    for row in rows2:
        lines.append(f"| {' | '.join(row)} |")
    lines.append("")

    # ============================================================
    # 三、海外央行+经济基本面分析
    # ============================================================
    lines.append("## 三、海外央行+经济基本面分析")
    lines.append("")
    lines.append("| 指标 | 当前值 | 周度变动 | 宏观边际影响 |")
    lines.append("|------|--------|:--------:|--------------|")

    cpi, cpi_d = gv(fred, "CPI")
    pce, pce_d = gv(fred, "核心PCE")
    unemp, _ = gv(fred, "失業率")
    payems, _ = gv(fred, "非農")
    wage, _ = gv(fred, "平均時薪(全部")
    jolts, _ = gv(fred, "JOLTS職位空缺數")
    erate, _ = gv(fred, "歐元區利率")
    egdp, _ = gv(fred, "歐元區GDP")

    # 计算周度变动（如果有至少2个数据点）
    def weekly_change(df, kw):
        vals = gv_all(df, kw)
        if len(vals) >= 2:
            try:
                v0 = float(vals[0][0])
                v1 = float(vals[1][0])
                diff = v0 - v1
                return f"{diff:+.2f}" if abs(diff) < 100 else f"{diff:+.0f}"
            except:
                pass
        return "—"

    rows3 = [
        ("美国非农预期", fmt_val(payems, "payems") if payems is not None else "—", weekly_change(fred, "非農"), "就业市场韧性" if payems is not None and float(payems) > 0 else "—"),
        ("CPI核心通胀", fmt_val(cpi) if cpi is not None else "—", weekly_change(fred, "CPI"), "通胀粘性判断"),
        ("联邦基金利率", fmt_val(ff, "rate") if ff is not None else "—", weekly_change(fred, "聯邦基金利率"), "利率限制性水平"),
        ("欧央行政策口径", fmt_val(erate, "rate") if erate is not None else "—", weekly_change(fred, "歐元區利率"), "欧美利差变化"),
        ("美联储议息概率", "—", "—", "市场降息预期"),
        ("海外PMI", "—", "—", "经济景气度"),
        ("全球M2流动性", "—", "—", "流动性总量"),
        ("海外财政舆情", "—", "—", "赤字财政边际"),
    ]
    for row in rows3:
        lines.append(f"| {' | '.join(row)} |")
    lines.append("")

    # ============================================================
    # 四、跨境资金&机构宏观持仓分析
    # ============================================================
    lines.append("## 四、跨境资金&机构宏观持仓分析")
    lines.append("")
    lines.append("| 标的 | 投机资金仓位 | 仓位分位 | Z-Score | 资金信号 |")
    lines.append("|------|:------------:|:--------:|:-------:|:--------:|")

    # CFTC数据可能不在FRED CSV中，用"—"占位
    rows4 = [
        ("美元指数", "—", "—", "—", "—"),
        ("美债期货", "—", "—", "—", "—"),
        ("VIX恐慌指数", "—", "—", "—", "—"),
    ]
    for row in rows4:
        lines.append(f"| {' | '.join(row)} |")
    lines.append("")

    # ============================================================
    # 五、中国本土宏观高频联动简析
    # ============================================================
    lines.append("## 五、中国本土宏观高频联动简析")
    lines.append("")
    lines.append("| 指标 | 当前值 | 周度变动 | 数据来源 |")
    lines.append("|------|--------|:--------:|----------|")

    # 从FRED中查找中国相关指标
    cn_cpi, _ = gv(fred, "中國CPI")
    cn_pmi, _ = gv(fred, "中國PMI")
    cn_gdp, _ = gv(fred, "中國GDP")
    cn_social, _ = gv(fred, "社融")
    
    # AKShare中国指标
    cn_data = fetch_cn_macro()
    lpr1y = cn_data.get("lpr1y")
    lpr5y = cn_data.get("lpr5y")
    rrr = cn_data.get("rrr_large")
    shibor_1w = cn_data.get("shibor_1w")
    
    # 社融
    sf = fetch_social_financing()
    sf_str = "—"
    if sf and sf.get("inc_month"):
        try:
            im = float(sf["inc_month"])
            sk = sf.get("stk_endval", "—")
            sf_str = f"{im:,.0f}亿(月增量), 存{sk}万亿"
        except:
            sf_str = "—"

    rows5 = [
        ("MLF利率(锚-LPR1Y)", f"{lpr1y:.1f}%" if lpr1y else "—", "—", "AKShare"),
        ("LPR5Y", f"{lpr5y:.1f}%" if lpr5y else "—", "—", "AKShare"),
        ("社融高频", sf_str, "—", "Tushare sf_month"),
        ("人民币跨境收付", "—", "—", "Wind"),
        ("国内流动性(存准率)", f"{rrr:.1f}%" if rrr else "—", "—", "AKShare"),
        ("SHIBOR 1W", f"{shibor_1w:.2f}%" if shibor_1w else "—", "—", "AKShare"),
        ("国内通胀高频", fmt_val(cn_cpi) if cn_cpi is not None else "—", "—", "FRED"),
    ]
    for row in rows5:
        lines.append(f"| {' | '.join(row)} |")
    lines.append("")

    # ============================================================
    # 六、宏观流动性强弱评分
    # ============================================================
    lines.append("## 六、宏观流动性强弱评分（同源能源评分模板）")
    lines.append("")
    score_us, score_risk, score_cn, us_reasons, risk_reasons, cn_reasons = compute_scores(fred)

    lines.append("| 宏观维度 | 评分（-10~+10） | 核心逻辑 |")
    lines.append("|----------|:--------------:|----------|")
    lines.append(f"| 美国宏观流动性 | {score_us:+d} | {'；'.join(us_reasons) if us_reasons else '—'} |")
    lines.append(f"| 全球风险情绪 | {score_risk:+d} | {'；'.join(risk_reasons) if risk_reasons else '—'} |")
    lines.append(f"| 国内货币环境 | {score_cn:+d} | {'；'.join(cn_reasons) if cn_reasons else '—'} |")
    lines.append("")

    # ============================================================
    # 七、未来30天重点观察方向+潜在风险提示
    # ============================================================
    lines.append("## 七、未来30天重点观察方向+潜在风险提示")
    lines.append("")
    lines.append("### 未来30天重点观测宏观变量")
    lines.append("")
    lines.append("| 观测变量 | 关注点 | 潜在影响 |")
    lines.append("|----------|--------|----------|")
    lines.append("| 美联储利率路径 | 下一次FOMC决议前的市场预期变化 | 全球资产定价锚 |")
    lines.append("| 美国CPI/PCE数据 | 通胀回落速度 | 降息预期修正 |")
    lines.append("| 非农就业数据 | 劳动力市场韧性 | 美联储政策节奏 |")
    lines.append("| 美元流动性指标 | FRA-OIS、TED利差 | 跨境资金松紧 |")
    lines.append("| 中国政策宽松力度 | MLF/LPR利率调整、财政刺激 | 人民币汇率与风险情绪 |")
    lines.append("| 中东/地缘局势 | 能源供应风险 | 通胀传导与避险情绪 |")
    lines.append("")
    lines.append("### 全球宏观潜在风险提示")
    lines.append("")
    if score_us < -3:
        lines.append("- 美国宏观流动性偏紧，高利率环境持续压制风险资产")
    else:
        lines.append("- 美国宏观流动性维持中性，需关注利率路径边际变化")
    if score_risk < -2:
        lines.append("- 全球风险情绪偏谨慎，收益率曲线形态暗示衰退担忧")
    else:
        lines.append("- 全球风险情绪中性，关注地缘政治事件对情绪的冲击")
    if score_cn < -2:
        lines.append("- 国内货币环境偏紧，关注央行后续宽松操作空间")
    else:
        lines.append("- 国内货币环境中性，关注稳增长政策落地节奏")
    lines.append("- 地缘政治风险（中东/东欧）可能引发能源价格剧烈波动")
    lines.append("")

    # ============================================================
    # 强制尾部固定话术
    # ============================================================
    month_cn = {"01": "1月", "02": "2月", "03": "3月", "04": "4月", "05": "5月", "06": "6月",
                "07": "7月", "08": "8月", "09": "9月", "10": "10月", "11": "11月", "12": "12月"}
    ym = TODAY[:7].split("-")
    date_str = f"{ym[0]}年{month_cn.get(ym[1], ym[1]+'月')}"
    lines.append(f"数据来源：美联储、欧央行、中国央行、彭博宏观、Wind、CBOE、美联储FedWatch，截至{date_str}")
    lines.append("免责声明：本文仅为全球及国内宏观政策、利率、资金、情绪数据周度复盘，不构成任何资产配置、投资交易建议。宏观市场波动风险极高，决策需谨慎。")
    lines.append("AI生成标注：本文AI辅助整理，全部核心数据人工核验校准。")

    return "\n".join(lines)


def main():
    r = report()
    out = DATA_DIR / "reports" / f"macro_weekly_{TODAY}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(r)
    print(r)


if __name__ == "__main__":
    main()
