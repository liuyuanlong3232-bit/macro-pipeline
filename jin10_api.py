#!/usr/bin/env python3
"""
金十数据 MCP API 封装
通过 MCP JSON-RPC 协议调用金十数据接口
提供：get_quote, list_flash, search_flash, list_calendar
"""
import json
import urllib.request
from pathlib import Path
from datetime import datetime

# ═══════ 配置 ═══════
MCP_URL = "https://mcp.jin10.com/mcp"

def _get_token():
    """从 config.yaml 读取 Bearer token"""
    for p in [Path("/root/hermes-pipeline/config.yaml"), Path.home() / ".hermes" / "config.yaml"]:
        if p.exists():
            with open(p) as f:
                for line in f:
                    if "Authorization:" in line and "Bearer" in line:
                        return line.split("Authorization:")[1].strip().strip('"').strip("'")
    return None

def _parse_sse(data):
    """解析 SSE 格式的 MCP 响应"""
    for line in data.split("\n"):
        if line.startswith("data: "):
            try:
                return json.loads(line[6:])
            except json.JSONDecodeError:
                continue
    return None

def _mcp_call(tool, args=None):
    """
    MCP JSON-RPC 调用
    1. initialize 建立会话
    2. notifications/initialized 通知
    3. tools/call 调用工具
    """
    token = _get_token()
    if not token:
        print("[jin10_api] 未找到 token")
        return None

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": token
    }

    try:
        # Step 1: Initialize
        init_body = json.dumps({
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": "2025-11-25",
                "capabilities": {},
                "clientInfo": {"name": "hermes-jin10", "version": "1.0"}
            }
        }).encode()
        req = urllib.request.Request(MCP_URL, data=init_body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as r:
            sid = r.headers.get("Mcp-Session-Id")
            r.read()

        if sid:
            headers["Mcp-Session-Id"] = sid

        # Step 2: Notify initialized
        notif_body = json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}).encode()
        notif_req = urllib.request.Request(MCP_URL, data=notif_body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(notif_req, timeout=10) as nr:
                nr.read()
        except Exception:
            pass  # notifications don't require a response

        # Step 3: Call tool
        call_body = json.dumps({
            "jsonrpc": "2.0", "id": 2, "method": "tools/call",
            "params": {"name": tool, "arguments": args or {}}
        }).encode()
        call_req = urllib.request.Request(MCP_URL, data=call_body, headers=headers, method="POST")
        with urllib.request.urlopen(call_req, timeout=30) as r2:
            resp = r2.read().decode()
            result = _parse_sse(resp)
            if result:
                sc = result.get("result", {}).get("structuredContent", {})
                return sc.get("data")
            return None

    except Exception as e:
        print(f"[jin10_api] {tool} 调用失败: {e}")
        return None


# ═══════ 公开 API ═══════

def get_quote(code):
    """
    获取实时行情
    Args:
        code: 品种代码，如 XAUUSD, XAGUSD, CL, NG 等
    Returns:
        dict: {close, code, high, low, name, open, time, ups_percent, ups_price, volume}
    """
    return _mcp_call("get_quote", {"code": code})


def list_flash(cursor=None):
    """
    获取财经快讯列表
    Args:
        cursor: 分页游标（可选）
    Returns:
        list[dict]: [{content, time, url}, ...]
    """
    data = _mcp_call("list_flash", {"cursor": cursor} if cursor else {})
    if data and isinstance(data, dict):
        return data.get("items", [])
    return data if isinstance(data, list) else []


def search_flash(keyword):
    """
    搜索财经快讯
    Args:
        keyword: 搜索关键词
    Returns:
        list[dict]: [{content, time, url}, ...]
    """
    data = _mcp_call("search_flash", {"keyword": keyword})
    if data and isinstance(data, dict):
        return data.get("items", [])
    return data if isinstance(data, list) else []


def list_calendar():
    """
    获取财经日历
    Returns:
        list[dict]: [{actual, affect_txt, consensus, previous, pub_time, revised, star, title}, ...]
    """
    data = _mcp_call("list_calendar")
    if data and isinstance(data, dict):
        return data.get("items", [])
    return data if isinstance(data, list) else []


# ═══════ 便捷函数 ═══════

def get_weekly_calendar(stars_min=3):
    """
    获取本周重要财经日历（star >= stars_min）
    Returns:
        list[dict]: 按时间排序的高重要性经济事件
    """
    now = datetime.now()
    week_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    from datetime import timedelta
    # 本周一
    week_start = week_start - timedelta(days=week_start.weekday())
    week_end = week_start + timedelta(days=7)

    all_cal = list_calendar()
    weekly = []
    for item in all_cal:
        try:
            pub = datetime.strptime(item["pub_time"], "%Y-%m-%d %H:%M")
            if week_start <= pub <= week_end and (item.get("star") or 0) >= stars_min:
                weekly.append(item)
        except Exception:
            continue
    weekly.sort(key=lambda x: x["pub_time"])
    return weekly


def get_latest_flash(count=5):
    """
    获取最新快讯（Top N）
    Args:
        count: 返回条数，默认5
    Returns:
        list[dict]: 最新快讯列表
    """
    return list_flash()[:count]


# ═══════ 测试 ═══════
if __name__ == "__main__":
    print("=== 金十数据 MCP API 测试 ===\n")

    # 测试行情
    q = get_quote("XAUUSD")
    if q:
        print(f"黄金: ${q['close']} ({q['ups_percent']}%)")

    # 测试快讯
    flash = get_latest_flash(3)
    print(f"\n最新 {len(flash)} 条快讯:")
    for f in flash:
        print(f"  [{f['time'][:16]}] {f['content'][:60]}...")

    # 测试日历
    cal = get_weekly_calendar(3)
    print(f"\n本周重要日历 ({len(cal)} 条):")
    for c in cal[:5]:
        print(f"  [{c['pub_time']}] ★{c['star']} {c['title']}")
