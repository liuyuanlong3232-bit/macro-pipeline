# Weekly Report Schedule

Five reports per week, following energy template style (公众号合规版).

## Schedule

| Day | Report | Report File | Key Data Dependencies |
|-----|--------|-------------|----------------------|
| 周一 | 金银周报 | `metals_weekly_YYYY-MM-DD.md` | FRED, Alpha Vantage, Yahoo, cotdata.net |
| 周二 | 能源周报 | `energy_weekly_YYYY-MM-DD.md` | Yahoo, cotdata.net, AGSI+, EIA |
| 周三 | 宏观周报 | `macro_weekly_YYYY-MM-DD.md` | FRED(22series), Tushare, Yahoo |
| 周四 | 全球农业周报 | `agri_global_YYYY-MM-DD.md` | Yahoo, cotdata.net, NOAA CPC, USDA |
| 周四 | 中国农业周报 | `agri_china_YYYY-MM-DD.md` | Tushare futures(15products) |
| 周五 | 资产配置总控 | `allocation_YYYY-MM-DD.md` | 前4份报告 |

## Data Freshness

| Data | Update | Fresh Until |
|------|--------|-------------|
| FRED macro | Monthly (staggered) | Next month's release |
| COT持仓 | Weekly, Tue 3:30pm ET | Next Tuesday |
| Yahoo futures | Daily, real-time | Same day |
| EIA STEO | Monthly | Next month |
| AGSI+ gas | Daily | Same day |
| Tushare China macro | Monthly | Next month |
| Tushare futures | Daily | Same day |

## Report Generators

All generators reside in `~/hermes-macro-pipeline/`:

- `energy_weekly.py` — 能源周报 (8 sections, 2500-3500 chars)
- `metals_weekly.py` — 金银周报 (6 sections)
- `macro_weekly.py` — 宏观周报 (7 sections)
- `agri_weekly.py` — 全球+中国农业周报 (combined file, two report functions)

**Compliance rules** (from user template):
- No "买入/卖出/看多/看空/目标价/必涨/必跌/推荐"
- All data with source name + date
- Scores are -10 to +10 fundamental strength only, not investment ratings
- Disclaimer must be included
- Simplified Chinese only
