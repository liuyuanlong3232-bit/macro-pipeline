"""Test EIA API endpoints - round 7: pnp (refining), cu (cushing)"""
import requests, json

KEY = 'IjwseZrShGgiShL0a3jcMad41brgdVNyGN0SjZKC'

def test_endpoint(name, url):
    print(f"\n=== {name} ===")
    try:
        r = requests.get(url, timeout=20)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            resp = data.get("response", {})
            if "routes" in resp:
                routes = resp["routes"]
                if isinstance(routes, list):
                    print(f"Routes ({len(routes)}):")
                    for r2 in routes[:20]:
                        print(f"  {r2.get('id', '?')}: {r2.get('name', '?')}")
                elif isinstance(routes, dict):
                    print(f"Routes ({len(routes)}):")
                    for k, v in list(routes.items())[:20]:
                        print(f"  {k}: {v.get('name', v.get('id', ''))}")
                return
            items = resp.get("data", [])
            print(f"Total items: {len(items)}")
            if items:
                for item in items[:5]:
                    print(f"  {json.dumps(item)}")
            else:
                print("Response keys:", list(resp.keys()))
        else:
            print(r.text[:1000])
    except Exception as e:
        print(f"Error: {e}")

# 1. Check pnp (Refining and Processing) routes
print("--- Exploring pnp (Refining & Processing) ---")
test_endpoint("pnp routes", f"https://api.eia.gov/v2/petroleum/pnp/?api_key={KEY}")

# 2. Check cu (Crude Oil Stocks at Tank Farms & Pipelines) - might have Cushing
test_endpoint("cu routes", f"https://api.eia.gov/v2/petroleum/stoc/cu/?api_key={KEY}")

# 3. Check ref (Refinery Stocks) routes
test_endpoint("stoc/ref routes", f"https://api.eia.gov/v2/petroleum/stoc/ref/?api_key={KEY}")

# 4. Try the pnp data endpoint
test_endpoint("pnp data", f"https://api.eia.gov/v2/petroleum/pnp/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=10")

# 5. Try cu data
test_endpoint("cu data", f"https://api.eia.gov/v2/petroleum/stoc/cu/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=10")

# 6. For Cushing specifically - look at EIA web API docs
# The Cushing, OK crude oil stocks series ID is typically: SWCESTUS1 or similar
# Let me try searching without filters to see all area codes
test_endpoint("All stoc/wstk areas for crude",
    f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&facets[product][]=EPC0&facets[process][]=SAX"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=100")
