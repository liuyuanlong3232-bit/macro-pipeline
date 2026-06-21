#!/usr/bin/env python3
"""Test Jin10 MCP connection"""
import json
import urllib.request

# 直接使用 token
TOKEN = "Bearer sk-U2h...LUGA"

payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-11-25",
        "capabilities": {},
        "clientInfo": {"name": "test", "version": "1.0"}
    }
}

headers = {
    "Content-Type": "application/json",
    "Authorization": TOKEN
}

req = urllib.request.Request(
    "https://mcp.jin10.com/mcp",
    data=json.dumps(payload).encode(),
    headers=headers,
    method="POST"
)

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode())
        print(f"Success! Result: {json.dumps(result)[:200]}")
except Exception as e:
    print(f"Error: {e}")
