#!/usr/bin/env python3
"""Write financial API keys to Hermes .env file"""
import os

env_path = r"C:\Users\Administrator\AppData\Local\hermes\.env"

# The actual full API key values from user
fred = "40fa26cf844e61f5be94820c5ded91b2"
alpha_vantage = "RI57V9BWVTLRCI1S"
news = "a74572a6ebc64ba9b2ca58b6c6ad7472"
weather = "a0bc637c35a1386de7ede34d7e2635f3"
estat = "8d989208261e170151339945bf719cbfbb53fac1"
eia = "IjwseZrShGgiShL0a3jcMad41brgdVNyGN0SjZKC"
usda = "7CE43998-6097-3436-B1A8-E326114EFA5E"
cot_id = "8y3ia95oiygxylkpo9nvzlen3"
cot_secret = "g991hm0rqcsc10q9drlj4pbz4s7qq59kqptshlukpvfs9lpd5"
finnhub = "d8jdg99r01qh6g3pktd0d8jdg99r01qh6g3pktdg"
finnhub_webhook = "d8jdg99r01qh6g3pkteg"
agsi = "35ae75c3734ce3dfa627f26474c4cb8f"

section = f"""
# =============================================================================
# FINANCIAL MACRO DATA API KEYS (完整密钥 - 已激活)
# =============================================================================
FRED_API_KEY={fred}
ALPHA_VANTAGE_API_KEY={alpha_vantage}
NEWSAPI_KEY={news}
OPENWEATHER_API_KEY={weather}
ESTAT_API_KEY={estat}
EIA_API_KEY={eia}
USDA_NASS_API_KEY={usda}
CFTC_COT_ID={cot_id}
CFTC_COT_SECRET={cot_secret}
FINNHUB_API_KEY={finnhub}
FINNHUB_WEBHOOK_SECRET={finnhub_webhook}
AGSI_API_KEY={agsi}
"""

with open(env_path, "a", newline="\r\n") as f:
    f.write(section)

# Verify
with open(env_path, "rb") as f:
    raw = f.read()

for key in ["FRED_API_KEY", "ALPHA_VANTAGE_API_KEY", "FINNHUB_API_KEY", "CFTC_COT_SECRET"]:
    idx = raw.find(key.encode())
    if idx >= 0:
        end = raw.find(b"\n", idx)
        line = raw[idx:end]
        val = line.split(b"=", 1)[1]
        print(f"{key}: {len(val)} chars")
        if len(val) > 15:
            print(f"  ✅ 完整密钥已写入")
        else:
            print(f"  ❌ 值太短: {val}")

print("\nDone!")
