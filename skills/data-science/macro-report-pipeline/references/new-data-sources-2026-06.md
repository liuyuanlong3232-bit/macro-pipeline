# New Data Sources Added (2026-06-14)

## SAFE Cross-border RMB Payments
- Page: https://www.safe.gov.cn/safe/2018/0419/8806.html
- Downloads Excel files with monthly RMB cross-border payment data
- Columns: 人民币收入, 人民币支出, 差额
- Data as of 2026-04: 收付总额5.77万亿, 差额-321亿
- Fallback: hardcode latest verified values

## ECB Eurozone M2
- Series: BSI.M.U2.Y.V.M20.X.1.U2.2300.Z01.E
- As of 2026-04: 16,289,850 million EUR
- FRED series MYAGM2EZM196N is DISCONTINUED (only to 2017)

## BOJ Japan M2
- Source: BOJ Money Stock Statistics
- As of 2026-05: 1,298.1 万亿JPY, YoY +2.5%
- FRED series MYAGM2JPM189N is DISCONTINUED

## CFTC Treasury Futures COT
- URL: https://www.cftc.gov/dea/futures/financial_lf.htm
- Format: Fixed-width plain text (NOT HTML tables)
- Key data (2026-06-09):
  - 10Y: OI 5,251,295 | AM net +2,412,885 | Leveraged net -1,979,511
  - 5Y: OI 6,184,688 | AM net +2,930,024 | Leveraged net -2,230,356
  - 2Y: OI 4,276,371 | AM net +1,879,104 | Leveraged net -1,680,942
  - 30Y: OI 1,881,987 | AM net +478,569 | Leveraged net -281,933

## CFTC Cotton COT
- URL: https://www.cftc.gov/dea/futures/ag_lf.htm (NOT deacotfo.htm which 404s)
- Format: Fixed-width plain text
- Key data (2026-06-09): OI 324,979 | Managed Money net +42,538

## Chinese Futures Warehouse Receipts (DCE/CZCE)
- Source: 99qh.com aggregates exchange daily reports
- Key data (2026-06-12):
  - 豆粕: 40,204手 | 豆油: 24,164手 | 玉米: 52,946手
  - 棕榈油: 1,057手 | 白糖: 23,134张 | 棉花: 11,583张
  - 菜籽油: 0张

## ISM PMI
- Use FRED series NAPM (not TradingEconomics which blocks requests)
- As of 2026-05: 54.0% (prev 52.7%)
