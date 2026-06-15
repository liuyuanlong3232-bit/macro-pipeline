---
name: precious-metals-reporting
description: "Generate daily/weekly precious metals research reports — macro analysis, COT positioning, gold-silver ratio, TIPS/dollar context. Data-first, no predictions, no advice."
version: 1.0.0
author: Hermes Agent
platforms: [linux, macos, windows]
---

# Precious Metals Reporting

Generate structured daily/weekly research reports focused on gold and silver. Output format is data-first with all values sourced and dated. No price targets, no buy/sell recommendations, no action plans.

## User Preferences

This skill was built for a professional precious metals trader/analyst. Critical preferences:

- **Data-first**: Lead with tables and numbers, not narrative prose
- **No fluff**: Skip introductory paragraphs, motivational language, and "sunny today" intros
- **Source everything**: Every number must have a date and source
- **No predictions**: Never give price targets or trading recommendations
- **No action plans**: Don't suggest what to do — just present the data
- **Structured format**: Tables > paragraphs. Bullet lists > sentences.
- **Simplified Chinese**: Reports use Simplified Chinese (简体中文), NOT Traditional Chinese
- **公众号排版**: 表格为主、数据优先、合规无交易建议、每项标注日期来源

## Report Structure

### Daily Report

```
📅 贵金属日报 | YYYY-MM-DD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 关键数据速览
    黄金: $X (Δ%)  |  白银: $X (Δ%)
    原油(WTI): $X (Δ%)
    美债10Y: X%  |  TIPS: X%  |  美元: X
    CPI: X  |  核心PCE: X  |  失业率: X%
    联邦基金利率: X%
    FOMC 6月: 维持 X%

🏛️ 宏观环境
    CPI: X (date) | 核心PCE: X (date) | TIPS: X (date) ...

🥇 黄金分析
    现货黄金: $X
    TIPS X%: 正/负利率环境分析
    地缘风险: On/Off

🥈 白银分析
    现货白银: $X
    金银比: X.Xx (高位/低位分析)

💰 资金面
    CFTC黄金: 净多+X  COT Index X (极度看多/看空)
    CFTC白银: 净多+X  COT Index X
    FOMC利率预期

🌍 地缘政治与风险事件
    · Top 5 news headlines
```

### Weekly Report (template)
```
一、本周核心事实
二、关键数据表 (指标|当前值|周变化|日期|来源)
三、黄金分析 (核心逻辑链, 最大利多, 最大利空)
四、白银分析 (核心逻辑链, 最大利多, 最大利空)
五、资金面分析 (CFTC+ETF)
六、市场定价程度 (多空定价表)
七、周期位置分析 (1W/1M/3M/6M/1Y)
八、评分系统 (宏观/实际利率/美元/ETF/CFTC/央行/供需)
九、下周关注事项
```

## Key Analysis Patterns

### Gold Analysis Logic Chain
1. Check TIPS (real yield) — positive = headwind (carry cost), negative = tailwind
2. Check DXY — strong dollar = headwind, weak = tailwind
3. Check COT Index — extreme readings (>90 or <10) signal crowding
4. Check geopolitical risk from news headlines
5. Assess gold-silver ratio for relative value

### COT Interpretation
| COT Index | Meaning | Signal |
|-----------|---------|--------|
| >90 | Extreme long | Crowded, vulnerable to reversal |
| 70-90 | Bullish | Strong trend |
| 30-70 | Neutral | No clear signal |
| 10-30 | Bearish | Weak sentiment |
| <10 | Extreme short | Potential bottom |

### Gold-Silver Ratio
| Ratio | Interpretation |
|-------|---------------|
| >85 | Silver relatively cheap vs gold (potential mean reversion) |
| 70-85 | Neutral-high range |
| 55-70 | Neutral range |
| <55 | Silver expensive vs gold |

## Data Dependencies

| Report Section | Data Source | Frequency |
|---------------|-------------|-----------|
| Spot prices | Yahoo Finance (GC=F, SI=F) | Daily |
| Macro indicators | FRED (75 series) | Daily-Monthly |
| COT positioning | cotdata.net API | Weekly (Tue) |
| Dollar index | Yahoo Finance DX-Y.NYB | Daily |
| FedWatch | oddpool.com | Daily |
| News | Finnhub API | Daily |
| European gas | AGSI+ API | Daily |
| Energy | EIA API | Monthly |
| China futures | Tushare API | Daily (trading days) |
| China macro | AKShare (DR007, LPR, SHIBOR, RRR) | Daily-Monthly |
| Social financing | Tushare sf_month | Monthly |
| Baker Hughes rig count | AOGR website (static HTML) | Weekly |
| BDI Baltic Dry | TradingEconomics | Daily |
| Weather/Open-Meteo | Open-Meteo API | Daily |

## Implementation Notes

- Report generator is `generate_report.py` in the pipeline directory
- Pipeline script is `macro_pipeline.py` 
- All data saved as CSV under `~/hermes-macro-data/csv/YYYY-MM-DD/`
- Reports output to `~/hermes-macro-data/reports/YYYY-MM-DD.md`

## Report Format Variants

Two weekly report formats exist. Check the request for which to use:

| Variant | Sections | Language | When |
|---------|----------|----------|------|
| V1 (inline below) | 9 sections | 繁體中文 | Interactive / ad-hoc |
| V2 (cron format) | 8 sections | 简体中文 | Cron job explicitly requests 8-section structure |

**V2 format** is defined in `references/weekly-report-cron-format.md`. Its sections are:
一、本周贵金属市场总结 (三列表格) → 二、价格走势 → 三、宏观驱动环境 (四列表格) → 四、CFTC持仓 → 五、产业需求简析 → 六、地缘&跨资产联动 → 七、供需强弱评分 (-10~+10) → 八、未来30天关注+风险提示 → 尾部固定话术

The V2 format uses directional emoji indicators (📉📈➡️⚠️), star-ratings for event importance (⭐-⭐⭐⭐⭐⭐), and a -10 to +10 scoring system. Load the reference for full table column specs and pitfall notes.

## Common Issues

- **COT data not found**: cotdata.net free tier only provides latest week. On Tuesday after 3:30pm ET new data is available. Before that, return latest available.
- **FedWatch empty**: CME website blocks requests. Use oddpool.com fallback.
- **Language**: Reports use Simplified Chinese (简体中文). Some CSV columns may use Traditional Chinese (繁體) — match exactly when reading with pandas.
- **Currency encoding**: Traditional Chinese column names (`指標`, `數值`, `日期`) in CSV — match exactly when reading with pandas.
- **Windows path resolution**: When writing files via write_file on Windows, use absolute `C:\Users\...` paths rather than MSYS `/c/Users/...` notation, which can resolve incorrectly.
- **Single-snapshot weekly change**: When only one date-folder of data exists, compute weekly change from the 5-day high/low range in futures data, and state this approximation explicitly in the report.
