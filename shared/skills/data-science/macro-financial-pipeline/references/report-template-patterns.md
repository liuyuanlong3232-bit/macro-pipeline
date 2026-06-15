# Weekly Report Template Patterns

Unified format across all 5 weekly reports. Derived from the energy report template approved by the user.

## Shared Style Rules

- **Simplified Chinese only.** Headers, labels, tables, commentary.
- **Data-first, tables-only.** No prose paragraphs. Every data point has a source and as-of date.
- **No trading advice.** Words like "看多/看空/买入/卖出/目标价/推荐" are forbidden. Scores represent fundamental strength only.
- **Conclusion-first.** Each section leads with the key takeaway, then data.
- **Scope: single-day snapshot initially.** After VPS accumulates 7 days of data, auto-add week-over-week columns.

## Templates per Report

### 1. 黄金白银周度研究报告 (Metals)

| Section | Content |
|---------|---------|
| 一、本周贵金属市场总结 | 3-column table: gold/silver spot, COMEX futures, GLD/SLV, gold-silver ratio, COT Index, DXY, TIPS |
| 二、价格走势分析 | All prices + basis + ETF + ratio in table; source per row |
| 三、宏观驱动环境分析 | TIPS, DXY, Fed Funds, FedWatch, yields in 4-column table |
| 四、CFTC COT资金持仓 | COT Index, Z-Score, net positioning for gold & silver |
| 五、产业&需求基本面 | Central bank buying, solar silver demand, ETF flows |
| 六、地缘&跨资产联动 | Middle East, Fed expectations, risk sentiment |
| 七、供需强弱评分 | Gold score + Silver score (-10 to +10) |
| 八、未来30天关注方向 | Variables + risk points |

### 2. 全球能源市场周度研究报告 (Energy)

| Section | Content |
|---------|---------|
| 一、本周能源市场总结 | WTI, Brent, HH, TTF, European gas storage, CFTC oil |
| 二、原油市场分析 | Prices, EIA inventories (crude/SPR/Cushing/gasoline/distillate), supply-demand |
| 三、天然气市场分析 | US (HH + storage), Europe (TTF + storage fill rates) |
| 四、OPEC+影响分析 | Monthly MOMR, production policy |
| 五、地缘政治影响分析 | Iran, Hormuz, Red Sea, Russia-Ukraine — priority-ordered |
| 六、CFTC资金持仓 | WTI + Brent positioning, COT Index |
| 七、供需强弱评分 | Crude score + Gas score |
| 八、未来30天关注方向 | Variables + risks |

### 3. 全球宏观周度研究报告 (Macro)

| Section | Content |
|---------|---------|
| 一、本周全球宏观市场总结 | 10Y, TIPS, DXY, EUR/JPY, FedWatch, VIX, USD liquidity, China DR007 |
| 二、核心宏观指标价格走势 | Yield curve, USD, FX, VIX, rates in table |
| 三、海外央行+经济基本面 | Nonfarm, CPI, Fed Funds, ECB, PMI, global M2 |
| 四、跨境资金&机构宏观持仓 | USD, Treasury, VIX speculative positions + Z-Score |
| 五、中国本土宏观高频联动 | MLF, social financing, property, RMB, PBOC operations |
| 六、宏观流动性强弱评分 | US liquidity, global risk sentiment, China monetary |
| 七、未来30天重点观察方向 | Variables + risks |

### 4. 全球农业周度研究报告（国际版）(Agriculture - International)

| Section | Content |
|---------|---------|
| 一、本周国际农业市场总结 | Soybeans, corn, wheat, sugar, cotton, ag index, CFTC ag total, US weather, Gulf shipments |
| 二、主力品种价格走势 | All CBOT/ICE contracts + basis + spreads |
| 三、海外产业&供需环境 | USDA WASDE, US crop progress, export sales, Gulf stocks, SA carryover, Black Sea, biodiesel, freight |
| 四、CFTC农业板块COT资金持仓 | Soybeans, corn, wheat, sugar — COT Index + Z-Score |
| 五、海外天气&产区边际 | N. America forecast, Argentina/Brazil planting, Black Sea logistics |
| 六、供需强弱评分 | Soybeans, corn, wheat, softs scores |
| 七、未来30天重点观察方向 | Variables + risks |

### 5. 全球农业周度研究报告（中国本土版）(Agriculture - China Domestic)

| Section | Content |
|---------|---------|
| 一、本周国内农业市场总结 | DCE/CZCE contracts, basis, crush margin, feed demand, imports |
| 二、国内农品价格走势分析 | Futures + spot quotes + port TTC + internal/external spread |
| 三、国内政策+本土供需环境 | State reserves, crush rate, meal stocks, corn stocks, hog breeding sows, vessel schedules, harvest progress |
| 四、内盘产业资金+仓单持仓 | Exchange warehouse receipts, industrial hedging, major capital positioning |
| 五、本土产业刚需&进出口联动 | Feed demand, food processing, import quotas, seasonal consumption, weather damage |
| 六、供需强弱评分 | Oilseeds, grains, softs scores |
| 七、未来30天重点观察方向 | Variables + risks |

## Data Requirements

Reports need weekly data (7 days) for "周环比" and "周均价" columns. On first run with only 1 day of data, mark these as "—" and note "单日快照".

## Mandatory Footer

```
**数据来源**: [sources], 截至YYYY年MM月DD日
**免责声明**: 本文仅为...数据周度复盘，不构成任何投资建议。市场有风险，入市需谨慎。
**AI生成标注**: 本文AI辅助整理，全部核心数据人工核验校准。
```
