# Tushare - China Financial Data API

## Setup
- Package: `pip install tushare`
- Token: stored in .env as `TUSHARE_TOKEN`
- Points system: 2000积分 (user's tier)
- Connection: `pro = ts.pro_api(token)`

## Key Endpoints (Verified with 2000积分)

### Macro Data (Low Point Cost)
- `pro.cn_cpi(start_m, end_m)` → columns: `month, nt_val, nt_yoy, nt_mom, nt_accu, town_val...`
  - `nt_yoy` = national CPI year-over-year %
  - Example: CPI 1.2% (202605)
- `pro.cn_pmi(start_m, end_m)` → columns: `MONTH, PMI010100, PMI010900, PMI011500...`
  - `PMI010100` = Manufacturing PMI (51.1 for 202605, above 50 = expansion)
- `pro.cn_gdp(start_q, end_q)` → columns: `quarter, gdp, gdp_yoy, pi, si, ti`
  - Example: GDP 1401879.2 (2025Q4)

### Futures Daily Data
- `pro.fut_daily(trade_date="20260612")` → returns ALL futures contracts for that date (~1075 records)
- ⚠️ Do NOT use `ts_code` parameter for individual contracts — incompatible with 2000积分
- To find main contract (主力): sort by `vol` descending, take first per product
- Contract codes: `C2607.DCE`, `SR2609.ZCE`, `M2609.DCE`, `Y2609.DCE`, `P2609.DCE`

### Chinese Agri Futures Symbol Mapping
| Pattern | Product | Exchange | Notes |
|---------|---------|----------|-------|
| `^C\d\.DCE` | Corn 玉米 | DCE | main is highest `vol` |
| `^CS\d\.DCE` | Corn Starch | DCE | |
| `^SR\d\.ZCZ` | Sugar 白糖 | CZCE | |
| `^CF\d\.ZCZ` | Cotton 棉花 | CZCE | |
| `^OI\d\.ZCZ` | Rapeseed Oil 菜籽油 | CZCE | |
| `^RM\d\.ZCZ` | Rapeseed Meal 菜粕 | CZCE | |
| `^JD\d\.DCE` | Eggs 鸡蛋 | DCE | |
| `^LH\d\.DCE` | Live Hogs 生猪 | DCE | |

### Pitfall: Prefix Matching
Using `str.startswith("A")` matches AG (白银), AO (氧化铝), AP (苹果) — NOT just soybean #1.
- Soybean #1 (豆一): use exact regex `^A\d\.DCE$` 
- Soybean #2 (豆二): `^B\d\.DCE$` but also matches BB (胶合板) — check exchange
- Soybean meal (豆粕): `^M\d\.DCE$` but M matches MA (methanol) too — always verify exchange suffix
- Soybean oil (豆油): `^Y\d\.DCE$`
- Palm oil (棕榈油): `^P\\d\\.DCE$` — careful: PP (聚丙烯) also starts with P

### Pitfall: .env Path on VPS

Tushare token is loaded from .env. On VPS, .env lives at `/root/hermes-pipeline/.env`, NOT `~/.hermes/.env`. Use:
```python
load_dotenv(Path(os.environ.get("HERMES_HOME", str(Path.home() / "hermes-pipeline"))) / ".env")
```

### Pitfall: Weekend Fallback

Use `start_date` + `end_date` range (5-day lookback), not `trade_date` alone. Sort results descending by date, take first entry.
