"""Check EIA API for Gulf Coast (PADD 3) stocks"""
import requests, json

KEY = 'IjwseZrShGgiShL0a3jcMad41brgdVNyGN0SjZKC'

def test(name, url):
    print(f"\n=== {name} ===")
    try:
        r = requests.get(url, timeout=20)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            items = data.get("response", {}).get("data", [])
            print(f"Total items: {len(items)}")
            for item in items[:3]:
                print(json.dumps(item, indent=2))
            if not items:
                print("No data. Response keys:", list(data.get("response", {}).keys()))
                print(json.dumps(data, indent=2)[:1500])
        else:
            print(r.text[:500])
    except Exception as e:
        print(f"Error: {e}")

# Test 1: PADD 3 Gulf Coast - all products (broad query)
test("PADD 3 - All products (R3P)",
    f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&facets[duoarea][]=R3P"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=5")

# Test 2: PADD 3 Crude (EPC0)
test("PADD 3 Crude (R3P, EPC0)",
    f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&facets[duoarea][]=R3P&facets[product][]=EPC0"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=5")

# Test 3: PADD 3 Motor Gasoline (EPM0)
test("PADD 3 Gasoline (R3P, EPM0)",
    f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&facets[duoarea][]=R3P&facets[product][]=EPM0"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=5")

# Test 4: PADD 3 Distillate (EPD0)
test("PADD 3 Distillate (R3P, EPD0)",
    f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&facets[duoarea][]=R3P&facets[product][]=EPD0"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=5")

# Test 5: Try series filter for Gulf Coast
test("PADD 3 by series",
    f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&facets[series][]=WCEST"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=5")

# Test 6: US Gulf Coast by series WG1ST (end stocks - Gulf Coast PADD 3)
test("Gulf Coast WG1ST series",
    f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&facets[series][]=WG1ST"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=5")

# Test 7: Try duoarea=R3P with FED (all refined products)
test("PADD 3 Refined by series",
    f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={KEY}"
    f"&frequency=weekly&data[0]=value"
    f"&facets[duoarea][]=R3P&facets[process][]=FED"
    f"&sort[0][column]=period&sort[0][direction]=desc&length=5")
