# Tushare Pro 可用宏观接口 (2026-06-13测试)

## 配置
```python
import tushare as ts
ts.set_token("你的TUSHARE_TOKEN")
pro = ts.pro_api()
```

## 可用接口（已测试通过）
| 接口名 | 数据内容 | 字段 |
|--------|---------|------|
| `cn_cpi` | 中国CPI月度数据 | month, nt_val, nt_yoy, nt_mom, town_val, town_yoy, cnt_val, cnt_yoy |
| `cn_gdp` | 中国GDP（季度） | quarter, gdp, gdp_yoy, pi, si, ti |
| `cn_ppi` | 中国PPI | month, ppi_yoy, ppi_mp_yoy, ppi_cg_yoy... |
| `shibor` | SHIBOR利率（日） | date, on, 1w, 2w, 1m, 3m, 6m, 9m, 1y |
| `shibor_lpr` | LPR贷款基础利率 | date, 1y(LPR1Y), 5y(LPR5Y) |

## 不可用接口
| 尝试的接口名 | 结果 |
|------------|------|
| social_financing | 40101 请指定正确的接口名 |
| social_finance | 同上 |
| shrzgm | 同上 |
| aggregate_financing | 同上 |
| total_financing | 同上 |
| repo | 40101 |
| mlf | 40101 |

## 替代方案
- **DR007/利率**: AKShare `repo_rate_query()`, `macro_china_shibor_all()`, `macro_china_lpr()`
- **社融**: 暂无可替代免费源（AKShare macro_china_shrzgm SSL握手失败）
