"""Debug Tushare fetch_china_futures"""
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv("/root/hermes-pipeline/.env")
import requests

token = os.getenv("TUSHARE_TOKEN")
today = datetime.now().strftime("%Y%m%d")
start = (datetime.now() - timedelta(days=5)).strftime("%Y%m%d")
print(f"Today: {today}")
print(f"Start: {start}")

# Test one symbol
ts_full = "M.DCE"
payload = {
    "api_name": "fut_daily",
    "token": token,
    "params": {"ts_code": ts_full, "start_date": start, "end_date": today},
    "fields": "ts_code,trade_date,close,pre_close,vol"
}
r = requests.post("http://api.tushare.pro", json=payload, timeout=10)
data = r.json()
print(f"Code: {data.get('code')}")
print(f"Msg: {data.get('msg')}")
if data.get('data') and data['data'].get('items'):
    print(f"Items: {len(data['data']['items'])}")
    for i in data['data']['items'][:3]:
        print(f"  {i}")
else:
    print("No items")
    print(f"Full response: {data}")
