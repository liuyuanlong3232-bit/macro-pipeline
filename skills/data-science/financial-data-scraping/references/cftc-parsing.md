# CFTC COT Report Parsing Reference

## URLs
- Treasury futures (TFF): `https://www.cftc.gov/dea/futures/financial_lf.htm`
- Agricultural futures: `https://www.cftc.gov/dea/futures/ag_lf.htm`
- **DO NOT USE**: `deacotfo.htm` — returns 404

## Format
Fixed-width PLAIN TEXT. NOT HTML tables. BeautifulSoup will NOT work.

## Treasury Futures Column Layout
```
              Dealer            :           Asset Manager/       :            Leveraged           :
           Intermediary         :           Institutional        :              Funds             :
    Long  :   Short  : Spreading:    Long  :   Short  : Spreading:    Long  :   Short  : Spreading:
```
After the header, data line has 14+ numbers separated by whitespace.

## Parsing Code
```python
idx = text.find("UST 10Y NOTE")
block = text[idx:idx+600]
oi_m = re.search(r'Open Interest is ([\d,]+)', block)
for line in block.split('\n'):
    nums = line.strip().split()
    if len(nums) >= 14:
        am_net = int(nums[3].replace(",", "")) - int(nums[4].replace(",", ""))
        lev_net = int(nums[6].replace(",", "")) - int(nums[7].replace(",", ""))
        break
```

## Cotton Parsing
```python
idx = text.find("COTTON NO. 2")
block = text[idx:idx+2000]
for line in block.split('\n'):
    if line.strip().startswith('All'):
        nums = re.findall(r'[\d,]+', line)
        oi = int(nums[0].replace(",", ""))
        managed_long = int(nums[5].replace(",", ""))
        managed_short = int(nums[6].replace(",", ""))
        managed_spread = int(nums[7].replace(",", ""))
        managed_net = managed_long + managed_spread - managed_short
        break
```

## Verified Data (2026-06-09)

### Treasury Futures
| Tenor | OI | AM Net | Lev Net |
|-------|-----|--------|---------|
| 2Y | 4,276,371 | +1,879,104 | -1,680,942 |
| 5Y | 6,184,688 | +2,930,024 | -2,230,356 |
| 10Y | 5,251,295 | +2,412,885 | -1,979,511 |
| 30Y | 1,881,987 | +478,569 | -281,933 |

### Cotton
- OI: 324,979
- Managed Money Net: +42,538 (Long 68,880 + Spread 35,789 - Short 26,342)

## Pitfalls
- CFTC doesn't update on weekends. Report date is typically Tuesday.
- Data is "as of" the prior Tuesday, published Friday.
- The text format may vary slightly between reports. Always use `text.find()` not regex on full document.
