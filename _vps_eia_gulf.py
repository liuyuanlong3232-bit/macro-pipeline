"""在VPS上查EIA美湾库存 + Tushare DR007"""
import os, json, requests

# 查EIA - 美湾(PADD 3)库存
key = os.getenv("EIA_API_KEY")
if key:
    url = f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={key}&frequency=weekly&data[0]=value&facets[duoarea][]=R3P&facets[product][]=EPC0&sort[0][column]=period&sort[0][direction]=desc&length=2"
    r = requests.get(url, timeout=15)
    d = r.json()
    data = d.get("response", {}).get("data", [])
    print("=== EIA美湾(PADD 3)原油库存 ===")
    if data:
        for i in data:
            print(f"  {i['period']}: {i.get('value','?')} 千桶")
    else:
        print("  无数据")
        print(json.dumps(d, ensure_ascii=False)[:300])

# 南美库存 - 查EIA国际数据
url2 = f"https://api.eia.gov/v2/international/data/?api_key={key}&frequency=monthly&data[0]=value&facets[countryRegionId][]=SAS&sort[0][column]=period&sort[0][direction]=desc&length=2"
# 简化 - 直接查steo有没有南美相关
url3 = f"https://api.eia.gov/v2/steo/data/?api_key={key}&frequency=monthly&data[0]=value&facets[seriesId][]=PAPR_OPEC&sort[0][column]=period&sort[0][direction]=desc&length=1"
r3 = requests.get(url3, timeout=10)
print("\n=== 南美OPEC产量(代理库存) ===")
print(json.dumps(r3.json(), ensure_ascii=False)[:200])

# Tushare - DR007
import requests
ts_token = os.getenv("TUSHARE_TOKEN")
if ts_token:
    print("\n=== Tushare DR007 ===")
    payload = {
        "api_name": "shibor",
        "token": ts_token,
        "params": {"start_date": "20260601", "end_date": "20260613"},
        "fields": "date,7_days"
    }
    r = requests.post("http://api.tushare.pro", json=payload, timeout=10)
    print(json.dumps(r.json(), ensure_ascii=False)[:300])

print("\n=== done ===")
