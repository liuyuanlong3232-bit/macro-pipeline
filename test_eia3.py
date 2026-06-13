"""Test EIA API endpoints - round 3"""
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

# 1. Cushing - need specific duoarea for Cushing, OK
test_endpoint("Cushing stocks",
    f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&facets[duoarea][]=NC0&facets[product][]=EPC0"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=5")

# 2. Total US crude production (monthly, NUS)
test_endpoint("US Crude Production Total (monthly, NUS)",
    f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={KEY}"
    f"&frequency=monthly&data[0]=value"
    f"&facets[duoarea][]=NUS"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=5")

# 3. Explore refinery endpoints - try different paths
for path in ["/petroleum/ref", "/petroleum/refining", "/petroleum/ref/refining"]:
    test_endpoint(f"Refine path check: {path}",
        f"https://api.eia.gov/v2{path}/?api_key={KEY}")

# 4. Try refinery utilization - maybe it's under stoc/wstk with different process
test_endpoint("Refinery Utilization - try different approach",
    f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&facets[duoarea][]=NUS&facets[process][]=RIR"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=5")

# 5. Nat gas - try different duoarea
test_endpoint("Nat Gas - Try R1K (east)",
    f"https://api.eia.gov/v2/natural-gas/stor/wkly/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&facets[duoarea][]=R1K"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=5")

# 6. Nat gas - try without duoarea facet
test_endpoint("Nat Gas - no duoarea facet",
    f"https://api.eia.gov/v2/natural-gas/stor/wkly/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=10")

# 7. Look for global crude production (not US-specific) - might need different API
# Let me check for weekly crude production by looking at the EIA API catalog
test_endpoint("Petroleum Weekly Supply Estimate",
    f"https://api.eia.gov/v2/petroleum/supd/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=5")
