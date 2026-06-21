#!/usr/bin/env python3
import json
import urllib.request
from pathlib import Path

MCP_URL = "https://mcp.jin10.com/mcp"

def _get_token():
    for p in [Path("/root/hermes-pipeline/config.yaml"), Path.home() / ".hermes" / "config.yaml"]:
        if p.exists():
            with open(p) as f:
                for line in f:
                    if "Authorization:" in line and "sk-" in line:
                        return line.split("Authorization:")[1].strip().strip(chr(34))
    return None

def _parse_sse(data):
    for line in data.split("\n"):
        if line.startswith("data: "):
            return json.loads(line[6:])
    return None

def _mcp_call(tool, args=None):
    token = _get_token()
    if not token:
        return None
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": token
    }
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"h","version":"1.0"}}}).encode()
    req = urllib.request.Request(MCP_URL, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            sid = r.headers.get("Mcp-Session-Id")
            r.read()
            if sid:
                headers["Mcp-Session-Id"] = sid
            urllib.request.urlopen(urllib.request.Request(MCP_URL, data=json.dumps({"jsonrpc":"2.0","method":"notifications/initialized"}).encode(), headers=headers, method="POST"), timeout=10)
            body = json.dumps({"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":tool,"arguments":args or {}}}).encode()
            with urllib.request.urlopen(urllib.request.Request(MCP_URL, data=body, headers=headers, method="POST"), timeout=30) as r2:
                resp = r2.read().decode()
                result = _parse_sse(resp)
                if result:
                    sc = result.get("result", {}).get("structuredContent", {})
                    return sc.get("data")
                return None
    except Exception as e:
        print("[jin10] " + tool + " error: " + str(e))
        return None

def get_quote(code):
    return _mcp_call("get_quote", {"code": code})

def list_calendar():
    return _mcp_call("list_calendar") or []

def list_flash(cursor=None):
    data = _mcp_call("list_flash", {"cursor": cursor} if cursor else {})
    return data.get("items", []) if data else []
