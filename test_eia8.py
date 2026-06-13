"""Test EIA API endpoints - round 8: refinery utilization + final checks"""
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
                    for r2 in routes[:15]:
                        print(f"  {r2.get('id', '?')}: {r2.get('name', '?')}")
                elif isinstance(routes, dict):
                    print(f"Routes ({len(routes)}):")
                    for k, v in list(routes.items())[:15]:
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

# 1. pnp/unc (Refinery Utilization) - find sub-routes
test_endpoint("pnp/unc routes", f"https://api.eia.gov/v2/petroleum/pnp/unc/?api_key={KEY}")

# 2. pnp/unc data - try weekly
test_endpoint("pnp/unc data weekly",
    f"https://api.eia.gov/v2/petroleum/pnp/unc/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&facets[duoarea][]=NUS"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=10")

# 3. pnp/wiup (Weekly Inputs & Utilization) - this sounds promising!
test_endpoint("pnp/wiup routes", f"https://api.eia.gov/v2/petroleum/pnp/wiup/?api_key={KEY}")

# 4. pnp/wiup data
test_endpoint("pnp/wiup data",
    f"https://api.eia.gov/v2/petroleum/pnp/wiup/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=10")

# 5. Nat Gas - Lower 48 working gas (R48)
test_endpoint("Nat Gas - Lower 48 (R48)",
    f"https://api.eia.gov/v2/natural-gas/stor/wkly/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&facets[duoarea][]=R48"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=5")

# 6. Try unc data without duoarea
test_endpoint("pnp/unc data no facets",
    f"https://api.eia.gov/v2/petroleum/pnp/unc/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=20")
