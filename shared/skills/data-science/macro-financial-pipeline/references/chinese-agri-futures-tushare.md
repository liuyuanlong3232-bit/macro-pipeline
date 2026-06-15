# Chinese Agricultural Futures — Verified Tushare Data

## Access Pattern

Use a SINGLE `fut_daily(trade_date="YYYYMMDD")` call (costs 1 query), then filter:

```python
import tushare as ts
pro = ts.pro_api("your_token")
df = pro.fut_daily(trade_date="20260612")
# df has 1075+ rows for all Chinese futures markets
```

## Product → Regex Mapping

### DCE (大连商品交易所)

| Product | Regex | Code Example | Price (2026-06-12) |
|---------|-------|-------------|-------------------|
| 玉米 | `^C\d\.DCE` | C2607.DCE | 2351 |
| 玉米淀粉 | `^CS\d\.DCE` | CS2607.DCE | 2725 |
| 豆一 | `^A\.DCE$` (exact!) | A.DCE | 4744 |
| 豆二 | `^B\.DCE$` (exact!) | B.DCE | 3515 |
| 豆粕 | `^M\d\.DCE` | M2609.DCE | 2941 |
| 豆油 | `^Y\d\.DCE` | Y2609.DCE | 8357 |
| 棕榈油 | `^P\d\.DCE` | P2609.DCE | 9321 |
| 鸡蛋 | `^JD\d` | JD2608.DCE | 4690 |
| 生猪 | `^LH\d` | LH2609.DCE | 12140 |

### CZCE (郑州商品交易所)

| Product | Regex | Code Example | Price (2026-06-12) |
|---------|-------|-------------|-------------------|
| 白糖 | `^SR\d` | SR2609.ZCE | 5315 |
| 棉花 | `^CF\d` | CF2609.ZCE | 15765 |
| 菜籽油 | `^OI\d` | OI2609.ZCE | 9874 |
| 菜粕 | `^RM\d` | RM2609.ZCE | 2259 |
| 苹果 | `^AP\d` | AP2610.ZCE | 7698 |
| 红枣 | `^CJ\d` | CJ2609.ZCE | 8900 |
| 花生 | `^PK\d` | PK2610.ZCE | 8426 |

## Pitfalls

### Regex Order Matters
Always check more specific patterns BEFORE broad ones. For example, `^A\.DCE$` must come before `^A\d` because `A\d` matches AG (白银·SHFE) and AO (氧化铝·SHFE).

### Prefer `trade_date=` over `ts_code=`
- ❌ `pro.fut_daily(ts_code="C888.DCE")` — returns empty
- ✅ `pro.fut_daily(trade_date="20260612")` — returns 1075+ rows

### Point Efficiency
2000 积分 is enough for macro + futures daily. One `fut_daily()` call ≈ 1 point (exact cost TBD). For 20 trading days/month, that's ~20 points for futures — negligible.
