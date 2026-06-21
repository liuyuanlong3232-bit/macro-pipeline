# CFTC COT Report Parsing Reference

## Treasury Futures (financial_lf.htm)

URL: `https://www.cftc.gov/dea/futures/financial_lf.htm`

### Text Format
```
UST 10Y NOTE - CHICAGO BOARD OF TRADE   (CONTRACTS OF $100,000 FACE VALUE)
CFTC Code #043602                                                    Open Interest is 5,251,295
Positions
   143,614    606,092     49,038  3,306,645    893,760    465,334    349,939  2,329,450    245,931    ...
```

### Column Mapping (positions line)
Index 0: Dealer Long
Index 1: Dealer Short
Index 2: Dealer Spreading
Index 3: Asset Manager Long
Index 4: Asset Manager Short
Index 5: Asset Manager Spreading
Index 6: Leveraged Funds Long
Index 7: Leveraged Funds Short
Index 8: Leveraged Funds Spreading
Index 9+: Other Reportables, Nonreportable

### Available Instruments
- `UST 2Y NOTE` → "2Y"
- `UST 5Y NOTE` → "5Y"
- `UST 10Y NOTE` → "10Y"
- `UST BOND -` → "30Y" (note the trailing " -")

## Agricultural Futures (ag_lf.htm)

URL: `https://www.cftc.gov/dea/futures/ag_lf.htm`

### Cotton Format
```
COTTON NO. 2 - ICE FUTURES U.S.    Code-033661
Disaggregated Commitments of Traders - Futures Only, June 09, 2026

     :   Open   : Producer/Merchant : Swap Dealers : Managed Money : Other Reportables :
     : Interest : Long  : Short    : Long : Short : Long : Short  : Long : Short      :
All  :   324,979: 47,749   165,334  : ...  : ...   :68,880  26,342 : ...
```

### Column Mapping (disaggregated format)
Positions line after "All :":
- Index 0: Open Interest
- Index 1-2: Producer/Merchant Long/Short
- Index 3-5: Swap Dealers Long/Short/Spreading
- Index 6-8: Managed Money Long/Short/Spreading
- Index 9-11: Other Reportables Long/Short/Spreading

Net Managed Money = nums[6] + nums[8] - nums[7] (Long + Spreading - Short)

## oddpool.com FedWatch API

### Endpoints
```
GET /api/events/history/no_change?event_id=fomc-YYYY-MM-DD&hours=1
GET /api/events/history/cut_25bps?event_id=fomc-YYYY-MM-DD&hours=1
GET /api/events/history/hike_25bps?event_id=fomc-YYYY-MM-DD&hours=1
GET /api/events/history/cut_50bps?event_id=fomc-YYYY-MM-DD&hours=1
GET /api/events/history/hike_50bps?event_id=fomc-YYYY-MM-DD&hours=1
```

### Response Format
```json
{
  "kalshi": [{"timestamp": "2026-06-14T04:32:01", "probabilities": {"no_change": 0.99}}],
  "polymarket": [{"timestamp": "...", "probabilities": {"no_change": 0.995}}]
}
```

### Key Names
- `no_change` = Fed maintains rate
- `cut_25bps` = Cut 25bps
- `hike_25bps` = Hike 25bps
