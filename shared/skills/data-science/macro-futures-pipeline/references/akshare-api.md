# AKShare 中国宏观数据速查

本地已安装 `akshare>=1.18`，无需API Key，免费开源。
VPS上已通过 `pip3 install akshare` 安装。

## 可用数据及函数

| 数据 | 函数 | 返回字段 | 最新值(2026-06) |
|------|------|---------|----------------|
| 银行间回购利率(DR007) | `repo_rate_query()` | date, FR001, FR007, FR014 | FR007=1.47% |
| SHIBOR利率 | `macro_china_shibor_all()` | 日期, O/N-定价, 1W-定价, 1M-定价, 1Y-定价 | SHIBOR 1W=1.45% |
| LPR(贷款基础利率) | `macro_china_lpr()` | TRADE_DATE, LPR1Y, LPR5Y | LPR1Y=3.0%, LPR5Y=3.5% |
| 存款准备金率 | `macro_china_reserve_requirement_ratio()` | 大型金融机构-调整后, 中小金融机构-调整后 | 9.5%/7.5% |

## 代码模式

```python
import akshare as ak

# DR007
df = ak.repo_rate_query()
latest = df.iloc[-1]
dr007 = latest["FR007"]  # 1.47

# LPR
df = ak.macro_china_lpr()
latest = df.iloc[-1]
lpr1y = latest["LPR1Y"]  # 3.0

# SHIBOR
df = ak.macro_china_shibor_all()
latest = df.iloc[-1]
shibor_1w = latest["1W-定价"]  # 1.45

# 准备金率
df = ak.macro_china_reserve_requirement_ratio()
latest = df.iloc[-1]
rrr = latest.get("大型金融机构-调整后", latest.get("大型金融机构-调整前"))
```

## 集成到macro_weekly.py

调用一次 `fetch_cn_macro()` 即可获取全部指标。
该函数定义在 macro_weekly.py 顶部（2026-06-13版本）。
不重复调用，在 report() 中调一次即可。

## 注意

- repo_rate_query() 返回列名是 'FR001','FR007','FR014'（无FDR前缀）
- repo_rate_hist() 有FDR007但数据只到2020年
- 社融接口(macro_china_shrzgm)已失效(SSL握手失败)
