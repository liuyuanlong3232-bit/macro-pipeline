"""Final checks - refinery utilization rate (weekly) + all final data"""
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
                for item in items[:10]:
                    print(f"  period={item.get('period')}, value={item.get('value')}, "
                          f"series={item.get('series')}, "
                          f"series-desc={item.get('series-description','')}")
            else:
                print("No data")
        else:
            print(r.text[:1000])
    except Exception as e:
        print(f"Error: {e}")

# 1. Weekly refinery utilization - YUP process
test_endpoint("Weekly Refinery Utilization (YUP)",
    f"https://api.eia.gov/v2/petroleum/pnp/wiup/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&facets[duoarea][]=NUS&facets[process][]=YUP"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=5")

# 2. Also try with product=Gross Inputs
test_endpoint("Weekly - just YUP NUS",
    f"https://api.eia.gov/v2/petroleum/pnp/wiup/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&facets[duoarea][]=NUS&facets[process][]=YUP"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=10")

# 3. All data for NUS from wiup to see what series exist
test_endpoint("All NUS wiup processes",
    f"https://api.eia.gov/v2/petroleum/pnp/wiup/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&facets[duoarea][]=NUS"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=40")
