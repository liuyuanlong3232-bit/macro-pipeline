# Weekly Report — Cron Job Format (V2)

This is the 8-section format requested by the automated weekly metals cron job. It differs from the V1 template in the skill body — use this when the cron job explicitly specifies this structure.

**Language**: Simplified Chinese (简体中文) — the cron job overrides the default Traditional Chinese preference.

## Section Structure

### 一、本周贵金属市场总结
Three-column table: `维度 | 核心变化 | 方向`
Rows: 黄金现货 / 白银现货 / COMEX黄金期货 / COMEX白银期货 / GLD / SLV / 金银比 / CFTC持仓(COT) / 美元指数(DXY) / 10Y TIPS
Direction indicators: 📉偏空 / 📈偏多 / ➡️中性 / ⚠️警告
Followed by a one-paragraph narrative summary ("本周主线").

### 二、价格走势
Five-column table: `指标 | 最新价 | 周环比 | 周均价 | 数据来源`
Cover: 黄金现货 / 白银现货 / COMEX黄金 / COMEX白银 / GLD / SLV / 金银比 / WTI原油 / VIX
Include note explaining how weekly change was calculated (especially when only snapshot data is available).
Add a bulleted "周内价格轨迹" section with high→low→close.

### 三、宏观驱动环境
Four-column table: `指标 | 当前值 | 周度变动 | 边际影响`
Cover: 10Y TIPS, DXY, 10Y/2Y/30Y yields, 10-2 spread, break-evens (10Y/5Y), Fed Funds, CPI, Core PCE, Unemployment, NFP, Consumer Sentiment, M2
Use emoji indicators: 🔴利空 / 🟢利多 / 🟡中性
End with a one-paragraph "宏观总结".

### 四、CFTC持仓分析
Five-column table: `品种 | 投机净持仓 | COT Index (26W) | Z-Score | 信号`
Rows: 黄金 / 白银 / 美元指数 / WTI原油 (for cross-reference)
Follow with "COT深度解读" subsections for gold (⚠️极度拥挤), silver (中性健康), DXY.

Use COT interpretation table from SKILL.md for signal labels.

### 五、产业需求简析
- 黄金: 央行购金 / ETF资金流 / 印度需求 / 矿区供应
- 白银: 光伏需求 / ETF资金流 / 工业需求 / 传统需求
- 金银比分析 subsection

### 六、地缘政治 & 跨资产联动
- 本周核心地缘事件 (three-column: 时间|事件|市场影响)
- 跨资产联动矩阵 (three-column: 资产|本周表现|与黄金关联)
- One-paragraph summary

### 七、供需强弱评分
Multi-column scoring table: `评分维度 | 黄金 | 白银 | 说明`
Scale: -10 (极度利空) to +10 (极度利多)
Dimensions: 宏观/实际利率, 美元, 通胀预期, ETF资金流, COT持仓结构, 央行/机构购金, 地缘政治, 产业需求, 市场情绪/VIX
Final row: 综合评分
Follow with per-metal analysis paragraph.

### 八、未来30天关注 & 风险提示
- 关键事件日历 (three-column: 日期|事件|预期影响, with star ratings ⭐-⭐⭐⭐⭐⭐)
- 风险矩阵 (four-column: 风险因素|方向|概率|影响程度)

### 尾部固定话术
⚠️ 免责声明 — must include:
- Data sources: FRED, CFTC COT, Yahoo Finance, Alpha Vantage, cotdata.net, Finnhub
- **不构成任何投资建议** (bold)
- 本报告不含任何价格预测、目标价位、买卖时机建议或交易策略推荐
- Footer: 数据抓取日 | 生成工具 | 下次更新

## Data Sources Used
- `~/hermes-macro-data/csv/YYYY-MM-DD/yahoo_futures.csv` — COMEX GC/SI futures
- `~/hermes-macro-data/csv/YYYY-MM-DD/commodity_prices.csv` — spot XAU/XAG, GLD, SLV
- `~/hermes-macro-data/csv/YYYY-MM-DD/cotdata.csv` — COT positioning
- `~/hermes-macro-data/csv/YYYY-MM-DD/fred_indicators.csv` — all macro indicators
- `~/hermes-macro-data/csv/YYYY-MM-DD/vix_data.csv` — VIX
- `~/hermes-macro-data/csv/YYYY-MM-DD/financial_news.csv` — news headlines
- `~/hermes-macro-data/csv/YYYY-MM-DD/cftc_cot.csv` — supplementary COT with ratios

## Pitfalls
- When only one snapshot of data exists (no prior week CSV), compute weekly change from the 5-day high/low range in the futures data. State this explicitly in the report.
- Write files with absolute Windows paths (C:\Users\...) not MSYS /c/... paths — the latter can resolve incorrectly in some tooling.
- COT Index = 100.0 means the current reading is the highest in the 26-week window. Label it "极度看多拥挤" with ⚠️.
- The language for cron-generated reports is Simplified Chinese (简体中文), while interactive reports may use Traditional Chinese (繁體中文). The cron job's instruction overrides the skill default.
