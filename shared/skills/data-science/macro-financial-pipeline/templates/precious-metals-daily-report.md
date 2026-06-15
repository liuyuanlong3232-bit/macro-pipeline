# Daily Precious Metals Report Template

Use this template for daily reports. Fill from pipeline collection data.

```
📅 贵金属日报 | {{DATE}}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 关键数据速览
  黄金: ${{GOLD_PRICE}} ({{GOLD_CHANGE}})  |  白银: ${{SILVER_PRICE}} ({{SILVER_CHANGE}})
  原油(WTI): ${{OIL_PRICE}} ({{OIL_CHANGE}})
  
  美债10Y: {{DGS10}}%  |  TIPS: {{TIPS}}%  |  美元: {{DXY}}
  CPI: {{CPI}}  |  核心PCE: {{PCE_CORE}}  |  失业率: {{UNEMPLOYMENT}}%
  联邦基金利率: {{FEDFUNDS}}%
  FOMC 6月: 维持 {{FOMC_HOLD}}%  |  加息 {{FOMC_HIKE}}%  |  降息 {{FOMC_CUT}}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏛️ 宏观环境

  联邦基金利率: {{FEDFUNDS}} ({{DATE_FF}})
  CPI: {{CPI}} ({{DATE_CPI}})
  核心PCE: {{PCE_CORE}} ({{DATE_PCE}})
  非农就业: {{PAYEMS}} ({{DATE_PAYEMS}})
  失业率: {{UNEMPLOYMENT}}% ({{DATE_UNEMP}})
  10年国债: {{DGS10}}% ({{DATE_DGS10}})
  2年国债: {{DGS2}}% ({{DATE_DGS2}})
  10年期TIPS: {{TIPS}}% ({{DATE_TIPS}})
  5Y盈亏平衡通胀: {{BREAK5}}% ({{DATE_BREAK5}})
  10Y盈亏平衡通胀: {{BREAK10}}% ({{DATE_BREAK10}})
  美元指数: {{DXY}} ({{DATE_DXY}})
  PPI: {{PPI}} ({{DATE_PPI}})
  工业产出: {{INDPRO}} ({{DATE_INDPRO}})
  
  来源: FRED (api.stlouisfed.org)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🥇 黄金分析

  现货黄金: ${{GOLD_PRICE}}
  
  TIPS分析:
  - TIPS实际利率 {{TIPS}}% — {{TIPS_ANALYSIS}}
  
  美元分析:
  - 美元指数 {{DXY}} — {{DXY_ANALYSIS}}
  
  地缘政治:
  {{GEOPOLITICAL_NOTES}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🥈 白银分析

  现货白银: ${{SILVER_PRICE}}
  金银比: {{GOLD_SILVER_RATIO}}x
  
  {{SILVER_ANALYSIS}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 资金面

  FOMC利率预期: 维持 {{FOMC_HOLD}}% (市场几乎100%定价不变)
  当前利率: {{FEDFUNDS}}% (Taylor规则隐含利率 4.75%, 政策偏宽松)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌍 地缘政治与风险事件

  {{TOP_NEWS_1}}
  {{TOP_NEWS_2}}
  {{TOP_NEWS_3}}
  {{TOP_NEWS_4}}
  {{TOP_NEWS_5}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  数据来源: FRED, Alpha Vantage, Finnhub, AGSI+, Oddpool(FedWatch)
  生成时间: {{GENERATED_AT}}
  声明: 不构成投资建议
```

## Analysis Logic

### TIPS Analysis
- TIPS > 0: 正实际利率环境, 黄金持有成本上升 (利空)
- TIPS < 0: 负实际利率, 利好黄金
- TIPS trend rising: 实际利率走高, 压制黄金

### USD Analysis (from FRED DTWEXBGS, trade-weighted)
- DXY > 120: 美元走强, 对黄金构成压制
- DXY 110-120: 中性偏强
- DXY < 100: 美元偏弱, 利好黄金

### Gold-Silver Ratio
- ratio > 85: 金银比高位, 白银相对低估
- ratio 70-85: 中性偏高
- ratio < 70: 白银相对强势
