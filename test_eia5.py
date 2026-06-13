"""Test EIA API endpoints - round 5: find routes and Cushing"""
import requests, json

KEY = 'IjwseZrShGgiShL0a3jcMad41brgdVNyGN0SjZKC'

def test_endpoint(name, url):
    print(f"\n=== {name} ===")
    try:
        r = requests.get(url, timeout=20)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            # Check if it's a route listing
            if "routes" in data.get("response", {}):
                routes = data["response"]["routes"]
                print(f"Routes ({len(routes)}):")
                for k, v in list(routes.items())[:20]:
                    print(f"  {k}: {v.get('name', v.get('id', ''))}")
                    if "facets" in v:
                        print(f"    facets: {list(v['facets'].keys())[:10]}")
                return
            items = data.get("response", {}).get("data", [])
            print(f"Total items: {len(items)}")
            if items:
                for item in items[:5]:
                    print(f"  {json.dumps(item)}")
                series_set = set()
                for item in items:
                    s = item.get('series', '')
                    series_set.add(s)
                print(f"Unique series: {series_set}")
            else:
                print("Response keys:", list(data.get("response", {}).keys()))
                print(f"Total reported: {data.get('response', {}).get('total', '0')}")
        else:
            print(r.text[:1000])
    except Exception as e:
        print(f"Error: {e}")

# 1. Get the full route structure for petroleum
test_endpoint("Petroleum Routes",
    f"https://api.eia.gov/v2/petroleum/?api_key={KEY}")

# 2. Get stoc routes  
test_endpoint("stoc routes",
    f"https://api.eia.gov/v2/petroleum/stoc/?api_key={KEY}")

# 3. Get stoc/wstk route info - look at facets
test_endpoint("wstk route info",
    f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={KEY}")

# 4. Try to find Cushing - use facets on duoarea
test_endpoint("stoc/wstk route",
    f"https://api.eia.gov/v2/petroleum/stoc/wstk/?api_key={KEY}")

# 5. For Cushing - from EIA docs, Cushing is usually 'NUS' area with specific series
# Let me try to get all product/process combinations to find Cushing
# Actually, the series WCESTUS1 might not be Cushing. Let me check what
# "Ending Stocks excluding SPR" actually means
# Cushing stocks series is often SWCESTUS1 or similar

# Try finding Cushing via different product code or series name containing "CUSH"
test_endpoint("Search for Cushing in product name",
    f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&facets[duoarea][]=NUS"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=50")

# 6. Check if there's a specific Cushing area code - search the API for all area codes
test_endpoint("Check crd routes",
    f"https://api.eia.gov/v2/petroleum/crd/?api_key={KEY}")
