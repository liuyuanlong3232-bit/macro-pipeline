#!/usr/bin/env python3
"""
金十数据 MCP 客户端
通过 hermes mcp 命令调用
"""
import subprocess
import json

def call_mcp_tool(tool_name, args=None):
    """通过 hermes mcp 调用工具"""
    # 构建命令
    cmd = ["hermes", "mcp", "call", "jin10", tool_name]
    if args:
        cmd.extend(["--args", json.dumps(args)])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"[jin10_mcp] Error: {result.stderr}")
            return None
    except Exception as e:
        print(f"[jin10_mcp] Error: {e}")
        return None

def get_quote(code):
    """获取实时行情"""
    return call_mcp_tool("get_quote", {"code": code})

def get_kline(code, count=10):
    """获取K线数据"""
    return call_mcp_tool("get_kline", {"code": code, "count": count})

def list_flash(cursor=None):
    """获取快讯列表"""
    args = {}
    if cursor:
        args["cursor"] = cursor
    return call_mcp_tool("list_flash", args)

def search_flash(keyword):
    """搜索快讯"""
    return call_mcp_tool("search_flash", {"keyword": keyword})

def list_calendar():
    """获取财经日历"""
    return call_mcp_tool("list_calendar", {})

if __name__ == "__main__":
    print("=== 测试金十 MCP ===")
    quote = get_quote("XAUUSD")
    print(f"黄金报价: {quote}")
