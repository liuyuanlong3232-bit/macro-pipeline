"""Check EIA API facets / available duoarea codes"""
import requests, json

KEY = 'IjwseZrShGgiShL0a3jcMad41brgdVNyGN0SjZKC'

def check_facets():
    print("=== Checking EIA API available duoarea values ===")
    
    # The EIA API has a facet endpoint
    urls = [
        ("Route/data/ facet check via route", 
         f"https://api.eia.gov/v2/petroleum/stoc/wstk/route/data/?api_key={KEY}&length=1"),
        ("Just query with no facets, see what duoareas appear",
         f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={KEY}"
         f"&frequency=weekly&data[0]=value&length=2"),
        ("Try NUS + EPC0 (national crude - baseline check)",
         f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={KEY}"
         f"&frequency=weekly&data[0]=value"
         f"&facets[duoarea][]=NUS&facets[product][]=EPC0"
         f"&sort[0][column]=period&sort[0][direction]=desc&length=2"),
        ("Try different duoarea for Gulf: R3 (not R3P)",
         f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={KEY}"
         f"&frequency=weekly&data[0]=value"
         f"&facets[duoarea][]=R3"
         f"&sort[0][column]=period&sort[0][direction]=desc&length=2"),
        ("Try R1P (PADD 1)",
         f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={KEY}"
         f"&frequency=weekly&data[0]=value"
         f"&facets[duoarea][]=R1P"
         f"&sort[0][column]=period&sort[0][direction]=desc&length=2"),
        ("Try RGP (Gulf Coast - RGP code)",
         f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={KEY}"
         f"&frequency=weekly&data[0]=value"
         f"&facets[duoarea][]=RGP"
         f"&sort[0][column]=period&sort[0][direction]=desc&length=2"),
        ("Try series=WG1ST for Gulf Coast crude stocks",
         f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={KEY}"
         f"&frequency=weekly&data[0]=value"
         f"&facets[series][]=WG1ST&facets[product][]=EPC0"
         f"&sort[0][column]=period&sort[0][direction]=desc&length=2"),
    ]
    
    for name, url in urls:
        print(f"\n--- {name} ---")
        try:
            r = requests.get(url, timeout=20)
            print(f"  Status: {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                items = data.get("response", {}).get("data", [])
                print(f"  Items: {len(items)}")
                for item in items[:2]:
                    print(f"  period={item.get('period')}, value={item.get('value')}, "
                          f"duoarea={item.get('duoarea')}, series={item.get('series')}, "
                          f"product={item.get('product')}")
                if not items:
                    print(f"  No data. Total: {data.get('response', {}).get('total')}")
            else:
                print(f"  {r.text[:300]}")
        except Exception as e:
            print(f"  Error: {e}")

    # Also try petroleum/stoc/wstk to see route options
    print("\n\n=== Checking routes ===")
    urls2 = [
        f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={KEY}&length=0&facets[duoarea][]=R3P&facets[product][]=EPC0",
        f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={KEY}&length=0&facets[duoarea][]=R3",
    ]
    for url in urls2:
        print(f"\n--- {url[-60:]} ---")
        try:
            r = requests.get(url, timeout=20)
            if r.status_code == 200:
                data = r.json()
                print(f"  Total: {data.get('response', {}).get('total')}")
            else:
                print(f"  {r.status_code}")
        except Exception as e:
            print(f"  Error: {e}")

check_facets()
