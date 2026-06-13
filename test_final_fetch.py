"""Test final data fetch with change calculations"""
import requests, json

KEY = 'IjwseZrShGgiShL0a3jcMad41brgdVNyGN0SjZKC'

def fetch_eia_energy():
    """Fetch all EIA energy indicators"""
    results = {}
    
    # Helper: get last N data points for a series
    def get_series(url_fmt, length=3):
        url = url_fmt(KEY, length)
        r = requests.get(url, timeout=20)
        if r.status_code != 200:
            print(f"Error {r.status_code}: {r.text[:200]}")
            return []
        data = r.json()
        return data.get("response", {}).get("data", [])
    
    try:
        # 1. Commercial crude stocks (WCESTUS1 = Ending Stocks Excluding SPR)
        items = get_series(
            lambda k, l: f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={k}"
            f"&frequency=weekly&data[0]=value"
            f"&facets[series][]=WCESTUS1"
            f"&sort[0][column]=period&sort[0][direction]=desc&length={l}"
        )
        if items:
            results['crude_stocks'] = float(items[0]['value'])
            results['crude_stocks_period'] = items[0]['period']
            if len(items) > 1:
                results['crude_stocks_change'] = float(items[0]['value']) - float(items[1]['value'])
            print(f"Crude Stocks: {results['crude_stocks']:.0f} (change: {results.get('crude_stocks_change',0):+.0f})")
        
        # 2. SPR stocks (WCSSTUS1)
        items = get_series(
            lambda k, l: f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={k}"
            f"&frequency=weekly&data[0]=value"
            f"&facets[series][]=WCSSTUS1"
            f"&sort[0][column]=period&sort[0][direction]=desc&length={l}"
        )
        if items:
            results['spr_stocks'] = float(items[0]['value'])
            results['spr_stocks_period'] = items[0]['period']
            if len(items) > 1:
                results['spr_stocks_change'] = float(items[0]['value']) - float(items[1]['value'])
            print(f"SPR Stocks: {results['spr_stocks']:.0f} (change: {results.get('spr_stocks_change',0):+.0f})")
        
        # 3. Cushing stocks (duoarea=YCUOK)
        items = get_series(
            lambda k, l: f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={k}"
            f"&frequency=weekly&data[0]=value"
            f"&facets[duoarea][]=YCUOK&facets[product][]=EPC0&facets[process][]=SAX"
            f"&sort[0][column]=period&sort[0][direction]=desc&length={l}"
        )
        if items:
            results['cushing_stocks'] = float(items[0]['value'])
            results['cushing_stocks_period'] = items[0]['period']
            if len(items) > 1:
                results['cushing_stocks_change'] = float(items[0]['value']) - float(items[1]['value'])
            print(f"Cushing Stocks: {results['cushing_stocks']:.0f} (change: {results.get('cushing_stocks_change',0):+.0f})")
        
        # 4. US Crude Production (monthly) - MCRFPUS2 = thousand barrels/day
        items = get_series(
            lambda k, l: f"https://api.eia.gov/v2/petroleum/crd/crpdn/data/?api_key={k}"
            f"&frequency=monthly&data[0]=value"
            f"&facets[series][]=MCRFPUS2"
            f"&sort[0][column]=period&sort[0][direction]=desc&length={l}"
        )
        if items:
            results['production'] = float(items[0]['value'])
            results['production_period'] = items[0]['period']
            if len(items) > 1:
                results['production_change'] = float(items[0]['value']) - float(items[1]['value'])
            print(f"Production: {results['production']:.0f} kb/d ({results['production_period']})")
        
        # 5. Refinery Utilization (weekly) - WPULEUS3 = percentage
        items = get_series(
            lambda k, l: f"https://api.eia.gov/v2/petroleum/pnp/wiup/data/?api_key={k}"
            f"&frequency=weekly&data[0]=value"
            f"&facets[series][]=WPULEUS3"
            f"&sort[0][column]=period&sort[0][direction]=desc&length={l}"
        )
        if items:
            results['refinery_util'] = float(items[0]['value'])
            results['refinery_util_period'] = items[0]['period']
            if len(items) > 1:
                results['refinery_util_change'] = float(items[0]['value']) - float(items[1]['value'])
            print(f"Refinery Utilization: {results['refinery_util']:.1f}% (change: {results.get('refinery_util_change',0):+.1f})")
        
        # 6. Natural Gas Storage (weekly Lower 48) - NW2_EPG0_SWO_R48_BCF
        items = get_series(
            lambda k, l: f"https://api.eia.gov/v2/natural-gas/stor/wkly/data/?api_key={k}"
            f"&frequency=weekly&data[0]=value"
            f"&facets[series][]=NW2_EPG0_SWO_R48_BCF"
            f"&sort[0][column]=period&sort[0][direction]=desc&length={l}"
        )
        if items:
            results['ng_storage'] = float(items[0]['value'])
            results['ng_storage_period'] = items[0]['period']
            if len(items) > 1:
                results['ng_storage_change'] = float(items[0]['value']) - float(items[1]['value'])
            print(f"NG Storage: {results['ng_storage']:.0f} BCF (change: {results.get('ng_storage_change',0):+.0f})")
        
    except Exception as e:
        print(f"Error in fetch_eia_energy: {e}")
    
    return results

if __name__ == "__main__":
    data = fetch_eia_energy()
    print("\n=== Summary ===")
    for k, v in sorted(data.items()):
        print(f"  {k}: {v}")
