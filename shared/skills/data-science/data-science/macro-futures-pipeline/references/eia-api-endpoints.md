# EIA API v2 端点速查

**API Key**: 存 `.env` 文件 `EIA_API_KEY`
**基础URL**: `https://api.eia.gov/v2`
**频率**: `weekly` / `monthly`
**分页**: JSON最多5000行，用offset分页

## 能源报告用到的端点

| 数据 | 路由 | 参数 | 频率 |
|------|------|------|------|
| 商业原油库存 | `/petroleum/stoc/wstk/data` | `facets[seriesId][]=WCESTUS1` | weekly |
| 战略石油储备SPR | `/petroleum/stoc/wstk/data` | `facets[seriesId][]=WCSSTUS1` | weekly |
| 库欣库存 | `/petroleum/stoc/wstk/data` | `facets[duoarea][]=YCUOK`, `facets[process][]=SAX` | weekly |
| 美国原油产量 | `/petroleum/crd/crpdn/data` | `facets[seriesId][]=MCRFPUS2` | monthly |
| 炼厂开工率 | `/petroleum/pnp/wiup/data` | `facets[seriesId][]=WPULEUS3` | weekly |
| 天然气库存 | `/natural-gas/stor/wkly/data` | `facets[seriesId][]=NW2_EPG0_SWO_R48_BCF` | weekly |

## OPEC数据（STEO）

| 数据 | 系列ID | 频率 |
|------|--------|------|
| OPEC总石油供应（含NGL） | `STEO.PAPR_OPEC.M` | monthly |
| OPEC原油产量（不含NGL） | `STEO.PAPR_OPEC_C.M` | monthly |
| 非OPEC产量 | `STEO.PAPR_NOPEC.M` | monthly |
| 全球原油总供应 | `STEO.PAPR_WORLD.M` | monthly |

注意：STEO数据包含未来18个月预测值（非历史实际值），实时产量数据需使用EIA国际统计数据。

## 请求示例

```python
import requests
key = os.getenv("EIA_API_KEY")
url = (f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/"
       f"?api_key={key}"
       f"&frequency=weekly"
       f"&data[0]=value"
       f"&facets[seriesId][]=WCESTUS1"
       f"&sort[0][column]=period&sort[0][direction]=desc"
       f"&length=2")
r = requests.get(url, timeout=15)
data = r.json()
latest_value = data["response"]["data"][0]["value"]
```

## 已知问题

- `GET` 请求，无需 `Content-Type` header
- 同一个路由可能有多个facets，需要指定正确组合
- 库存单位：千桶（千桶/日 for产量）
- 天然气库存单位：BCF（十亿立方英尺）
