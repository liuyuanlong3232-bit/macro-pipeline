"""Test EIA API endpoints - round 2"""
import requests, json

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
            if items:
                # Show all unique series names
                series_set = set()
                for item in items[:20]:
                    s = item.get('series', '')
                    series_set.add(s)
                print(f"Unique series: {series_set}")
                for item in items[:5]:
                    print(f"  {json.dumps(item)}")
            else:
                print("No data. Full response keys:", list(data.get("response", {}).keys()))
                # Print the facets available
                total = data.get("response", {}).get("total", "0")
                print(f"Total reported: {total}")
        else:
            print(r.text[:1000])
    except Exception as e:
        print(f"Error: {e}")

# 1. Commercial crude stocks - list all facets available
test_endpoint("Crude Stocks - All series",
    f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&facets[duoarea][]=NUS&facets[product][]=EPC0"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=20")

# 2. Try without product facet to see different products
test_endpoint("Crude Stocks - all products",
    f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&facets[duoarea][]=NUS"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=10")

# 3. US Crude Production - monthly
test_endpoint("US Production (monthly)",
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={KEY}"
    f"&frequency=monthly&data[0]=value"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=5")

# 4. Let me find the correct path for refinery utilization
# Try different paths
for path in ["/petroleum/ref/refdwn", "/petroleum/refiner"]:
    test_endpoint(f"Refinery - path check {path}",
        f"https://api.eia.gov/v2{path}/?api_key={KEY}")

# 5. Natural gas storage - total US
test_endpoint("Nat Gas Storage - total US (all series)",
    f"https://api.eia.gov/v2/natural-gas/stor/wkly/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&facets[duoarea][]=NUS"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=10")
