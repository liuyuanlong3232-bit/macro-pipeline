"""Test EIA API endpoints for energy data"""
import requests, json, sys

KEY = 'IjwseZrShGgiShL0a3jcMad41brgdVNyGN0SjZKC'

def test_endpoint(name, url):
    print(f"\n=== {name} ===")
    try:
        r = requests.get(url, timeout=20)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            items = data.get("response", {}).get("data", [])
            print(f"Total items: {len(items)}")
            for item in items[:3]:
                print(f"  period={item.get('period')}, value={item.get('value')}, "
                      f"duoarea={item.get('duoarea')}, product={item.get('product')}, "
                      f"series={item.get('series')}")
            if not items:
                print("No data items found. Full response keys:", list(data.get("response", {}).keys()))
                print(json.dumps(data, indent=2)[:1000])
        else:
            print(r.text[:500])
    except Exception as e:
        print(f"Error: {e}")

# 1. 商业原油库存 (NUS=全美, EPC0=原油)
test_endpoint("Commercial Crude Stocks", 
    f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&facets[duoarea][]=NUS&facets[product][]=EPC0"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=5")

# 2. SPR - try different product codes
for pcode in ["EPC0", "EPC0SPR", "SPR"]:
    test_endpoint(f"SPR Stocks (product={pcode})",
        f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={KEY}"
        f"&frequency=weekly&data[0]=value"
        f"&facets[duoarea][]=NUS&facets[product][]={pcode}"
        f"&sort[0][column]=period&sort[0][direction]=desc&length=3")

# 3. 库欣库存
test_endpoint("Cushing Stocks",
    f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&facets[duoarea][]=NUS&facets[product][]=EPC0"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=5")

# 4. 美国原油产量
test_endpoint("US Crude Production",
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=5")

# 5. 炼厂开工率
test_endpoint("Refinery Utilization",
    f"https://api.eia.gov/v2/petroleum/ref/refdwn/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=5")

# 6. 天然气库存
test_endpoint("Natural Gas Storage",
    f"https://api.eia.gov/v2/natural-gas/stor/wkly/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=5")
