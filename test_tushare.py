"""Test Tushare API connection"""
import requests, os
from dotenv import load_dotenv
load_dotenv("/root/hermes-pipeline/.env")

token = os.getenv("TUSHARE_TOKEN")
print(f"Token: {token[:10]}...")

url = "http://api.tushare.pro"

# Test 1: Basic API connection
payload = {
    "api_name": "fut_daily",
    "token": token,
    "params": {"ts_code": "M.DCE", "start_date": "20260611", "end_date": "20260613"},
    "fields": "ts_code,trade_date,close"
}
r = requests.post(url, json=payload, timeout=15)
data = r.json()
print(f"Code: {data.get('code', '')}")
print(f"Msg: {data.get('msg', '')}")
if data.get('data') and data['data'].get('items'):
    items = data['data']['items']
    print(f"Items: {len(items)}")
    for i in items[:3]:
        print(f"  {i}")
else:
    print("No items returned")

# Test 2: Try daily instead of fut_daily
print("\n=== Test 2: fut_basic ===")
payload2 = {
    "api_name": "fut_basic",
    "token": token,
    "params": {"ts_code": "M.DCE"},
    "fields": "ts_code,name,list_date"
}
r2 = requests.post(url, json=payload2, timeout=15)
data2 = r2.json()
print(f"Code: {data2.get('code', '')}")
if data2.get('data') and data2['data'].get('items'):
    for i in data2['data']['items'][:2]:
        print(f"  {i}")
else:
    print(f"Error: {data2.get('msg', '')}")
