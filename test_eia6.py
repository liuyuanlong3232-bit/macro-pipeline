"""Test EIA API endpoints - round 6: route structure + Cushing/refinery"""
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

# 1. Check petroleum routes structure 
test_endpoint("Petroleum routes",
    f"https://api.eia.gov/v2/petroleum/?api_key={KEY}")

# 2. Check stoc routes
test_endpoint("stoc routes",
    f"https://api.eia.gov/v2/petroleum/stoc/?api_key={KEY}")

# 3. Try refinery - look for "ref" in routes
# From EIA, refinery utilization is under /petroleum/ref/refdwn but maybe different version
# Let me check the EIA v2 API structure
test_endpoint("Root API routes",
    f"https://api.eia.gov/v2/?api_key={KEY}")

# 4. For Cushing - from EIA weekly status report, Cushing stocks are just commercial crude
# stored at Cushing, OK. The area code might be NUS with process=something specific
# Let me look at all unique series descriptions that mention Cushing
# Actually, the correct series for Cushing is typically SWCESTUS1
# which requires a different area code. Let me try PADD 2 (midwest) area
for area in ["R20", "R10", "R30"]:
    test_endpoint(f"PADD area={area} crude stocks",
        f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={KEY}"
        f"&frequency=weekly&data[0]=value"
        f"&facets[duoarea][]={area}&facets[product][]=EPC0&facets[process][]=SAX"
        f"&sort[0][column]=period&sort[0][direction]=desc&length=3")

# 5. Try EIA weekly petroleum status report - look for the actual Cushing series
# Cushing is in PADD 2, and has a specific facility code
# From old EIA API, Cushing series was: SWCESTUS1 or similar
# Let me search the full data for any series containing "Cush" or "cush"
test_endpoint("Crude stocks full listing - look for Cushing areas",
    f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value&data[1]=series&data[2]=series-description"
    f"&facets[product][]=EPC0"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=100")

# 6. For refinery utilization - maybe it's under a different route entirely
# The EIA API v2 routes for petroleum are listed at
# Try finding via route search
test_endpoint("Check all top-level routes",
    f"https://api.eia.gov/v2/?api_key={KEY}")
