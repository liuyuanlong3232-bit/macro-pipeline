# Open-Meteo Free Weather API

> 免费，无需API Key，无限量（非商业用途）

## 基础端点

```
https://api.open-meteo.com/v1/forecast
```

## 农业降水查询

```python
import requests

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": lat, "longitude": lon,
    "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min",
    "timezone": "America/Chicago",
    "forecast_days": 7,
}
r = requests.get(url, params=params, timeout=10)
data = r.json()
daily = data.get("daily", {})
# daily["precipitation_sum"] = [0.0, 5.2, ...]  # 7天降水mm
```

## 美国农业区坐标

| 产区 | 纬度 | 经度 | 代表品种 |
|------|------|------|---------|
| 玉米带(IL) | 40.0 | -89.0 | 玉米、大豆 |
| 小麦带(KS) | 38.0 | -98.0 | 冬小麦 |
| 棉花带(MS) | 33.0 | -90.0 | 棉花 |
| 大平原(NE) | 41.5 | -100.0 | 春小麦、玉米 |
| 三角洲(AR) | 34.5 | -91.0 | 水稻、大豆 |

## 可用参数

| 参数 | 说明 | 示例 |
|------|------|------|
| daily=precipitation_sum | 日降水总量(mm) | [0.0, 5.2, ...] |
| daily=temperature_2m_max | 日最高温(°C) | [28.1, ...] |
| daily=temperature_2m_min | 日最低温(°C) | [17.3, ...] |
| current_weather=true | 当前天气 | 温度/风速/天气码 |

## 注意事项

- 响应速度约1-2秒/请求，5个产区串行约5-10秒
- 7天预报足够覆盖农业降水趋势
- 返回数据中的 `|` 管道符会破坏Markdown表格，`summary` 字段用 `,` 拼接而非 `|`
- 使用 `forecast_days=7` 获取未来7天累计降水
