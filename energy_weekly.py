#!/usr/bin/env python3
"""
能源周报生成器 - 按公众号模板
"""
import os, sys, re, json, requests
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

# 公共工具函数
sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared.utils import load_csv, yahoo_quote_direct, load_env, DATA_DIR, TODAY

load_env()
EIA_API_KEY = os.getenv("EIA_API_KEY")

# 兼容：load_csv 在本文件中仍叫 load
load = load_csv

def gv(df, kw):
    for c in df.columns:
        if "指標" in c or "品種" in c:
            vc = [x for x in df.columns if "數值" in x or "最新" in x or "價" in x][0]
            sub = df[df[c].str.contains(kw, na=False, regex=False)]
            if not sub.empty:
                return str(sub.iloc[0][vc]), str(sub.iloc[0].get("日期",""))
    return None, None

def gv_chg(df, kw):
    """返回(价格, 日涨跌幅%)"""
    for c in df.columns:
        if "指標" in c or "品種" in c:
            vc = [x for x in df.columns if "數值" in x or "最新" in x or "價" in x][0]
            chg_cols = [x for x in df.columns if "漲跌幅" in x or "涨跌幅" in x]
            chg_col = chg_cols[0] if chg_cols else None
            sub = df[df[c].str.contains(kw, na=False, regex=False)]
            if not sub.empty:
                price = str(sub.iloc[0][vc])
                chg_val = sub.iloc[0][chg_col] if chg_col else None
                chg = f"{chg_val}%" if chg_val is not None else "—"
                return price, chg
    return None, None

def fetch_eia_energy():
    """通过EIA v2 API实时获取能源库存/产量/开工率/天然气数据"""
    if not EIA_API_KEY:
        print("EIA_API_KEY未设置")
        return {}
    results = {}
    def _get(base_url, facets, length=3):
        facet_parts = []
        for k, v in facets.items():
            for val in v if isinstance(v, list) else [v]:
                facet_parts.append(f"&facets[{k}][]={val}")
        url = (f"{base_url}?api_key={EIA_API_KEY}"
               f"&frequency=weekly&data[0]=value"
               f"{''.join(facet_parts)}"
               f"&sort[0][column]=period&sort[0][direction]=desc&length={length}")
        r = requests.get(url, timeout=20)
        if r.status_code != 200:
            return []
        return r.json().get("response", {}).get("data", [])
    try:
        # 1. 商业原油库存 (WCESTUS1 = Ending Stocks Excluding SPR)
        items = _get("https://api.eia.gov/v2/petroleum/stoc/wstk/data",
                     {"series": ["WCESTUS1"]})
        if items:
            results["crude_stocks"] = float(items[0]["value"])
            results["crude_stocks_period"] = items[0]["period"]
            results["crude_stocks_chg"] = float(items[0]["value"]) - float(items[1]["value"]) if len(items) > 1 else 0
        # 2. 战略石油储备 (WCSSTUS1)
        items = _get("https://api.eia.gov/v2/petroleum/stoc/wstk/data",
                     {"series": ["WCSSTUS1"]})
        if items:
            results["spr_stocks"] = float(items[0]["value"])
            results["spr_stocks_period"] = items[0]["period"]
            results["spr_stocks_chg"] = float(items[0]["value"]) - float(items[1]["value"]) if len(items) > 1 else 0
        # 3. 库欣库存 (duoarea=YCUOK)
        items = _get("https://api.eia.gov/v2/petroleum/stoc/wstk/data",
                     {"duoarea": ["YCUOK"], "product": ["EPC0"], "process": ["SAX"]})
        if items:
            results["cushing_stocks"] = float(items[0]["value"])
            results["cushing_stocks_period"] = items[0]["period"]
            results["cushing_stocks_chg"] = float(items[0]["value"]) - float(items[1]["value"]) if len(items) > 1 else 0
        # 4. 美国原油产量 (MCRFPUS2, monthly)
        url4 = (f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={EIA_API_KEY}"
                f"&frequency=monthly&data[0]=value"
                f"&facets[series][]=MCRFPUS2"
                f"&sort[0][column]=period&sort[0][direction]=desc&length=3")
        r4 = requests.get(url4, timeout=20)
        if r4.status_code == 200:
            items = r4.json().get("response", {}).get("data", [])
            if items:
                results["production"] = float(items[0]["value"])
                results["production_period"] = items[0]["period"]
                results["production_chg"] = float(items[0]["value"]) - float(items[1]["value"]) if len(items) > 1 else 0
        # 5. 炼厂开工率 (WPULEUS3)
        items = _get("https://api.eia.gov/v2/petroleum/pnp/wiup/data",
                     {"series": ["WPULEUS3"]})
        if items:
            results["refinery_util"] = float(items[0]["value"])
            results["refinery_util_period"] = items[0]["period"]
            results["refinery_util_chg"] = float(items[0]["value"]) - float(items[1]["value"]) if len(items) > 1 else 0
        # 6. 天然气库存 (NW2_EPG0_SWO_R48_BCF = Lower 48 Working Gas)
        items = _get("https://api.eia.gov/v2/natural-gas/stor/wkly/data",
                     {"series": ["NW2_EPG0_SWO_R48_BCF"]})
        if items:
            results["ng_storage"] = float(items[0]["value"])
            results["ng_storage_period"] = items[0]["period"]
            results["ng_storage_chg"] = float(items[0]["value"]) - float(items[1]["value"]) if len(items) > 1 else 0
    except Exception as e:
        print(f"fetch_eia_energy error: {e}")
    return results

def fmt_chg(chg):
    """格式化变化量，帶箭頭"""
    if chg is None: return "—"
    arrow = "↑" if chg > 0 else "↓" if chg < 0 else "→"
    return f"{arrow} {abs(chg):.0f}"


def report():
    yahoo = load("yahoo_futures")
    cot = load("cotdata")
    fred = load("fred_indicators")
    agsi = load("agsi_eu_gas")

    # Yahoo CSV数据时效检查 — 如果CSV最新日期落后2天以上，用直连API补充
    yahoo_stale = True
    days_diff = 999  # 默认值，异常时视为过期
    if yahoo is not None and not yahoo.empty and "日期" in yahoo.columns:
        try:
            latest_yahoo_date = yahoo["日期"].max()
            from datetime import datetime as dt
            days_diff = (dt.strptime(TODAY, "%Y-%m-%d") - dt.strptime(str(latest_yahoo_date), "%Y-%m-%d")).days
            yahoo_stale = days_diff > 2  # 超过2天视为过期(覆盖周末)
        except Exception:
            yahoo_stale = True  # 解析失败时视为过期

    if yahoo_stale:
        print(f"[能源报告] Yahoo CSV数据过期({days_diff}天)，使用直连API获取最新价格...")
        for sym, keyword in [("CL=F", "WTI"), ("BZ=F", "Brent"), ("NG=F", "天然氣")]:
            price, prev, date = yahoo_quote_direct(sym)
            if price is not None:
                # 用直连数据覆盖/补充
                import pandas as pd
                new_row = pd.DataFrame([{
                    "來源": "Yahoo Finance (直连)", "品種": f"{keyword}期货",
                    "代碼": sym, "日期": date, "最新價": price,
                    "前收盤": prev, "抓取日": TODAY
                }])
                if yahoo is not None and not yahoo.empty:
                    yahoo = pd.concat([yahoo, new_row], ignore_index=True)
                else:
                    yahoo = new_row
                print(f"  ✅ {keyword}: ${price} ({date})")
    
    lines = []
    lines.append("# ⛽ 全球能源市场周度研究报告")
    lines.append(f"**生成日期**: {TODAY} | **数据覆盖**: 单日快照")
    lines.append("")
    lines.append("---")
    
    # 一、本周总结
    lines.append("## 一、本周能源市场总结")
    lines.append("")
    lines.append("| 维度 | 核心变化 | 方向 |")
    lines.append("|------|---------|------|")
    
    wti_p, wti_d = gv(yahoo, "WTI")
    brent_p, _ = gv(yahoo, "Brent")
    ng_p, _ = gv(yahoo, "天然氣")
    if wti_p:
        lines.append(f"| WTI原油 | ${wti_p} | ↓ 周内走弱 |")
    if brent_p:
        lines.append(f"| 布伦特原油 | ${brent_p} | ↓ 跟随WTI |")
    if ng_p:
        lines.append(f"| 亨利港天然气 | ${ng_p} | ↓ 小幅回落 |")
    if agsi is not None and not agsi.empty:
        fr = agsi.iloc[0].get("填充率%", "—")
        lines.append(f"| 欧洲天然气库存 | 德国填充率 {fr}% | ↑ 补充季正常 |")
    
    if not cot.empty and "品種" in cot.columns:
        cot_wti = cot[cot["品種"].str.contains("WTI", na=False)]
        if not cot_wti.empty:
            ci = cot_wti.iloc[0].get("COT Index(26W)", 50)
            sig = "极端看空" if ci <= 10 else "偏空" if ci <= 30 else "中性"
            lines.append(f"| CFTC原油持仓 | COT指数 {ci:.0f} | {sig} |")
    lines.append("")
    
    # 二、原油
    lines.append("---")
    lines.append("## 二、原油市场分析")
    lines.append("")
    lines.append("### 2.1 价格走势")
    lines.append("")
    lines.append("| 指标 | WTI | Brent | 来源 |")
    lines.append("|------|-----|-------|------|")
    lines.append(f"| 最新收盘 | ${wti_p or '—'} | ${brent_p or '—'} | Yahoo |")
    wti_chg_price, wti_chg_pct = gv_chg(yahoo, "WTI")
    brent_chg_price, brent_chg_pct = gv_chg(yahoo, "Brent")
    lines.append(f"| 周涨跌幅 | {wti_chg_pct if wti_chg_pct else '—'} | {brent_chg_pct if brent_chg_pct else '—'} | Yahoo |")
    spread = ""
    if brent_p and wti_p:
        try: spread = f"${float(brent_p)-float(wti_p):+.2f}"
        except Exception: spread = "—"
    lines.append(f"| 布伦特-WTI价差 | — | {spread} | 计算 |")
    lines.append("")
    
    # EIA实时数据
    eia = fetch_eia_energy()
    eia_ok = bool(eia.get("crude_stocks"))

    # 2.2 EIA库存
    lines.append("### 2.2 EIA库存数据")
    lines.append("")
    if eia_ok:
        lines.append(f"> 数据更新至 {eia.get('crude_stocks_period','—')} | 来源: EIA Weekly Status Report")
    else:
        lines.append("> 注：EIA库存数据每周三公布，本周数据暂未获取")
    lines.append("")
    lines.append("| 指标 | 最新值 | 周变化 | 来源 |")
    lines.append("|------|--------|--------|------|")
    if eia_ok:
        cs = f"{eia['crude_stocks']:,.0f} 千桶"
        cs_chg = fmt_chg(eia.get('crude_stocks_chg'))
        spr = f"{eia['spr_stocks']:,.0f} 千桶"
        spr_chg = fmt_chg(eia.get('spr_stocks_chg'))
        cus = f"{eia['cushing_stocks']:,.0f} 千桶"
        cus_chg = fmt_chg(eia.get('cushing_stocks_chg'))
    else:
        cs = cs_chg = spr = spr_chg = cus = cus_chg = "待更新"
    lines.append(f"| 商业原油库存 | {cs} | {cs_chg} | EIA |")
    lines.append(f"| 战略石油储备(SPR) | {spr} | {spr_chg} | EIA |")
    lines.append(f"| 库欣库存 | {cus} | {cus_chg} | EIA |")
    lines.append("")
    
    # 2.3 供需
    lines.append("### 2.3 供需基本面")
    lines.append("")
    lines.append("| 指标 | 最新值 | 来源 |")
    lines.append("|------|--------|------|")
    if eia_ok:
        prod = f"{eia['production']:,.0f} 千桶/日 ({eia.get('production_period','')})"
        ru = f"{eia['refinery_util']:.1f}%"
    else:
        prod = "待更新"
        ru = "待更新"
    lines.append(f"| 美国原油产量 | {prod} | EIA |")
    lines.append(f"| 炼厂开工率 | {ru} | EIA |")
    
    # Baker Hughes钻机数（AOGR数据源，无Cloudflare拦截）
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from data_scrapers import fetch_baker_hughes
    bh = fetch_baker_hughes()
    if bh:
        oil_s = f"油{bh['oil']}" if bh.get('oil') else ""
        gas_s = f"气{bh['gas']}" if bh.get('gas') else ""
        misc_s = f"杂{bh['misc']}" if bh.get('misc') else ""
        detail = " / ".join(filter(None, [oil_s, gas_s, misc_s]))
        lines.append(f"| 钻机数量 | US {bh['total']} ({detail}) ({bh['date']}) | 贝克休斯 |")
    else:
        lines.append(f"| 钻机数量 | 待手动查 | 贝克休斯 |")
    lines.append("")
    
    # 三、天然气
    lines.append("---")
    lines.append("## 三、天然气市场分析")
    lines.append("")
    lines.append("### 3.1 美国市场")
    lines.append("")
    lines.append(f"| 指标 | 最新值 | 来源 |")
    lines.append(f"|------|--------|------|")
    lines.append(f"| 亨利港 | ${ng_p or '—'} | Yahoo |")
    if eia_ok:
        ng = f"{eia['ng_storage']:,.0f} BCF"
        ng_chg = fmt_chg(eia.get('ng_storage_chg'))
        lines.append(f"| 库存(Lower 48) | {ng} | {ng_chg} | EIA |")
    else:
        lines.append(f"| 库存 | 待更新 | EIA |")
    lines.append("")
    lines.append("### 3.2 欧洲市场")
    lines.append("")
    if agsi is not None and not agsi.empty:
        for _, r in agsi.iterrows():
            lines.append(f"- {r['國家']} {r['日期']}: 库存 {r['庫存(TWh)']} TWh, 填充率 {r['填充率%']}%")
    else:
        lines.append("数据待更新")
    lines.append("")
    
    # 四、欧佩克+
    lines.append("---")
    lines.append("## 四、欧佩克+影响分析")
    lines.append("")
    
    # 获取OPEC数据
    from opec_data import fetch_eia_opec
    opec = fetch_eia_opec()
    if opec and opec.get("latest"):
        chg = opec.get("change", 0)
        em = "↑" if chg and chg > 0 else "↓" if chg and chg < 0 else "→"
        lines.append(f"| 指标 | 当前值 | 月环比 | 数据来源 |")
        lines.append(f"|------|--------|--------|----------|")
        lines.append(f"| {opec['series']}（{opec['unit']}）| {opec['latest']} | {em} {abs(chg):.2f} | {opec['source']} |")
        lines.append(f"| 数据截止 | {opec['period']} | — | — |")
    else:
        lines.append("| 指标 | 当前值 | 数据来源 |")
        lines.append("|------|--------|----------|")
        lines.append(f"| 欧佩克产量 | 待更新 | EIA STEO |")
    lines.append("")
    
    # 欧佩克政策要点
    lines.append("### 当前产量政策")
    lines.append("")
    lines.append("- 欧佩克+减产协议延长至2026年底，合计约220万桶/日自愿减产")
    lines.append("- 沙特主导减产执行，超额补偿机制约束伊拉克、哈萨克斯坦等国")
    lines.append("- 阿联酋获得逐步增产配额，2026年起小幅提升")
    lines.append("- 俄罗斯产量受制裁影响，实际产量低于配额")
    lines.append("")
    
    # 五、地缘
    lines.append("---")
    lines.append("## 五、地缘政治影响分析")
    lines.append("")

    # 新闻速览
    news_df = load("financial_news")
    if news_df is not None and not news_df.empty:
        # 用中文关键词搜索
        kw = "伊朗|中东|霍尔木兹|原油|俄罗斯|乌克兰|制裁"
        energy_news = news_df[news_df["標題"].str.contains(kw, na=False)]
        if not energy_news.empty:
            lines.append("### 本周能源地缘新闻")
            lines.append("")
            for _, r in energy_news.head(4).iterrows():
                lines.append(f"- {r['標題'][:80]}")
            lines.append("")
    
    # 结构化地缘分析
    lines.append("### 中东局势")
    lines.append("")
    lines.append("- 伊朗：伊核谈判进展反复，霍尔木兹海峡航运风险持续存在")
    lines.append("- 以色列-哈马斯：停火谈判前景影响中东整体风险溢价")
    lines.append("- 沙特：欧佩克+产量政策维稳，沙特主导减产延长执行")
    lines.append("")
    lines.append("### 俄乌冲突")
    lines.append("")
    lines.append("- 俄罗斯原油出口：西方制裁执行力度影响俄油出口流向")
    lines.append("- 欧洲能源替代：欧洲加速液化天然气(LNG)进口设施建设")
    lines.append("")
    lines.append("### 制裁与贸易政策")
    lines.append("")
    lines.append("- 美国对伊朗石油出口制裁执行力度直接影响全球供应")
    lines.append("- 委内瑞拉制裁松紧程度影响重质原油市场平衡")
    lines.append("")
    
    # 六、CFTC
    lines.append("---")
    lines.append("## 六、CFTC资金持仓分析")
    lines.append("")
    cot_report_date = str(cot.iloc[0].get("報告日期", "—")) if not cot.empty and "報告日期" in cot.columns else "—"
    cot_publish_date = str(cot.iloc[0].get("抓取日", "—")) if not cot.empty and "抓取日" in cot.columns else "—"
    lines.append(f"**报告日期**: {cot_report_date} | **公布日期**: {cot_publish_date}")
    lines.append("")
    lines.append("| 品种 | 投机净持仓 | COT指数 | Z分数 | 信号 |")
    lines.append("|------|-----------|---------|-------|------|")
    for _, r in cot.iterrows() if cot is not None else []:
        n = r.get("品種","")
        if "原油" in n or "天然气" in n:
            ci = r.get("COT Index(26W)",50)
            sig = "极端看空" if ci <= 10 else "偏空" if ci <= 30 else "中性" if ci <= 70 else "偏多" if ci <= 90 else "极端偏多"
            lines.append(f"| {n} | {r.get('投機淨持倉',0):+,} | {ci:.0f} | {r.get('Z-Score',0):+.2f} | {sig} |")
    lines.append("")
    
    # 七、评分
    lines.append("---")
    lines.append("## 七、供需强弱评分")
    lines.append("")
    lines.append("| 资产 | 评分 | 核心逻辑 |")
    lines.append("|------|------|---------|")
    lines.append("| 原油 | -3 | 全球需求前景疲软+制造业PMI走弱压制油价；地缘风险溢价与欧佩克减产提供部分对冲 |")
    lines.append("| 天然气 | -1 | 库存高位+需求季节性偏低；LNG出口支撑有限 |")
    lines.append("")
    
    # 八、关注
    lines.append("---")
    lines.append("## 八、未来30天关注方向")
    lines.append("")
    lines.append("### 核心关注变量")
    lines.append("- 原油：EIA库存趋势、欧佩克+产量政策、伊朗谈判进展")
    lines.append("- 天然气：美国库存注入速度、欧洲补库进度")
    lines.append("- 地缘：霍尔木兹海峡航运安全、中东停火谈判")
    lines.append("")
    lines.append("### 潜在风险点")
    lines.append("- 伊朗局势升级：霍尔木兹海峡通行受阻，可能影响全球原油供应的20%")
    lines.append("- 全球经济放缓：制造业PMI持续走弱可能压制能源需求预期")
    lines.append("- 天气风险：飓风季节可能影响墨西哥湾油气生产")
    lines.append("")
    
    # 结尾
    lines.append("---")
    lines.append(f"**数据来源**: Yahoo Finance、CFTC COT、AGSI+、EIA API（实时），截至{TODAY}")
    lines.append("**免责声明**: 本文仅为全球能源市场宏观数据与产业动态复盘，不构成任何投资建议。市场有风险，入市需谨慎。")
    
    return "\n".join(lines)

def main():
    r = report()
    p = DATA_DIR / "reports" / f"energy_weekly_{TODAY}.md"
    with open(p, "w", encoding="utf-8") as f: f.write(r)
    print(r)

if __name__ == "__main__":
    main()
