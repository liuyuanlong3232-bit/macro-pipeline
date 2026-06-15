# Weekly Data Release Schedule (Beijing Time)

Schedule optimized so each report runs AFTER its key data sources update.

## Data Release Times

| Data | Release Time (Beijing) | Covers Period | Report That Uses It |
|------|----------------------|---------------|-------------------|
| **EIA Petroleum Status** | Wed 22:30 (夏令时) / Wed 23:30 (冬令时) | Week prior | 能源周报 (Thu 9:00) |
| **USDA Export Sales** | Thu 20:30 (夏令时) / Thu 21:30 (冬令时) | Week prior | 国际农业周报 (Fri 9:00) |
| **COT Commitment of Traders** | Sat 03:30-04:30 (夏令时) / Sat 04:30-05:30 (冬令时) | Through prior Tuesday | 贵金属周报 (Sat 9:00) |
| **Tushare Chinese Futures** | Daily ~15:00 (market close) | Current trading day | 中国农业周报 (Fri 20:00) |
| **OPEC MOMR** | Monthly 11th-15th | Prior month | 能源周报 |
| **CONAB Brazil** | Monthly 10th-15th | Prior month | 国际农业周报 |
| **USDA WASDE** | Monthly 9th-12th | Prior month | 国际农业周报 |

## Weekly Report Schedule

| Day | Time | Report | Latest Data Included |
|-----|------|--------|---------------------|
| Mon | 09:00 | 宏观周报 | All prior week FRED data (GDPNow, CPI, PCE lag by ~1 month) |
| Wed | 09:00 | 能源周报 | EIA inventory from Tue 22:30 |
| Fri | 09:00 | 国际农业周报 | USDA export sales from Thu 20:30 |
| Fri | 20:00 | 中国农业周报 | Tushare full week futures data (market just closed) |
| Sat | 09:00 | 贵金属周报 | Fresh COT data released ~3:30-4:30am |
| Sun | 10:00 | 资产配置总控 | All 5 weekly reports published |

## Reasoning

- **宏观第一** because macro sets the tone for all asset classes
- **COT贵金属周六** because COT data only arrives Sat 3:30am Beijing time
- **中国农业周五晚** because Tushare updates at market close ~15:00
- **能源周三** because EIA inventory released Tue 22:30 Beijing
- **总控周日** because needs all 5 reports to synthesize cross-asset conclusions
