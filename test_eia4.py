"""Test EIA API endpoints - round 4"""
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
                for item in items[:5]:
                    print(f"  {json.dumps(item)}")
                series_set = set()
                for item in items[:20]:
                    s = item.get('series', '')
                    series_set.add(s)
                print(f"Unique series: {series_set}")
            else:
                print("No data. Keys:", list(data.get("response", {}).keys()))
                print(f"Total reported: {data.get('response', {}).get('total', '0')}")
        else:
            print(r.text[:1000])
    except Exception as e:
        print(f"Error: {e}")

# 1. Try Cushing with different area codes
for area in ["NUS", "SC0", "SW0", "NC0"]:
    test_endpoint(f"Cushing area={area}",
        f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={KEY}"
        f"&frequency=weekly&data[0]=value"
        f"&facets[duoarea][]={area}&facets[product][]=EPC0"
        f"&sort[0][column]=period&sort[0][direction]=desc&length=3")

# 2. Look for EIA API routes - try to find the full route list
test_endpoint("EIA Routes - petroleum",
    f"https://api.eia.gov/v2/petroleum/?api_key={KEY}")

# 3. Try different refinery-related paths
for path in ["/petroleum/stoc/wstk", "/petroleum/crd/crpdn", "/petroleum/ref"]:
    test_endpoint(f"Route info: {path}",
        f"https://api.eia.gov/v2{path}/?api_key={KEY}")

# 4. Cushing - maybe need specific series filter
# From EIA website, Cushing stocks series is generally WCESTUS1
# Let me check: WCESTUS1 is "Ending Stocks excluding SPR" not Cushing
# Cushing might need different product code
test_endpoint("Cushing via specific S series",
    f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&facets[series][]=WCESTUS1"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=5")

# 5. Let me query the API route structure
test_endpoint("EIA Root routes",
    f"https://api.eia.gov/v2/?api_key={KEY}")
