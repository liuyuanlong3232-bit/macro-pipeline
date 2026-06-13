"""Test EIA API endpoints - round 9: find refinery utilization rate"""
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
                for item in items[:8]:
                    print(f"  period={item.get('period')}, value={item.get('value')}, "
                          f"series={item.get('series')}, series-desc={item.get('series-description','')}, "
                          f"process={item.get('process')}, process-name={item.get('process-name','')}, "
                          f"product-name={item.get('product-name','')}")
                # Show all unique process names
                procs = set()
                for item in items[:50]:
                    procs.add((item.get('process',''), item.get('process-name','')))
                print(f"Unique process types: {procs}")
            else:
                print("Response keys:", list(resp.keys()))
        else:
            print(r.text[:1000])
    except Exception as e:
        print(f"Error: {e}")

# 1. unc monthly data - look for utilization rate
test_endpoint("unc monthly - all",
    f"https://api.eia.gov/v2/petroleum/pnp/unc/data/?api_key={KEY}"
    f"&frequency=monthly&data[0]=value"
    f"&facets[duoarea][]=NUS"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=20")

# 2. wiup weekly - maybe has utilization process
test_endpoint("wiup weekly - with NUS",
    f"https://api.eia.gov/v2/petroleum/pnp/wiup/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&facets[duoarea][]=NUS"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=50")

# 3. Look for refinery utilization in STEO (which has broader data)
test_endpoint("STEO - refinery utilization",
    f"https://api.eia.gov/v2/steo/data/?api_key={KEY}"
    f"&frequency=monthly&data[0]=value"
    f"&facets[seriesId][]=PAPR_OPEC"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=3")

# 4. Let me try checking what's in the stoc/ref route
test_endpoint("stoc/ref data",
    f"https://api.eia.gov/v2/petroleum/stoc/ref/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=10")

# 5. Try refinery utilization via a different product/process combination
# In EIA's weekly supply report, the utilization rate is series: W_EPC0_YIP_NUS_PCT
# Or similar. Let me look for "utilization" or "operable" in series descriptions
# Try the wiup route more broadly
test_endpoint("wiup weekly - no facets",
    f"https://api.eia.gov/v2/petroleum/pnp/wiup/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=50")
