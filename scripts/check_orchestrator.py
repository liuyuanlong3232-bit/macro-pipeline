#!/usr/bin/env python3
"""
Orchestrator 状态检查脚本
每天中午自动运行，检查风控状态和恢复能力
"""
import json
import os
from datetime import datetime
from pathlib import Path

STATE_FILE = Path.home() / "hermes-macro-data" / "meta" / "orchestrator_state.json"

def check_orchestrator():
    print("=" * 50)
    print(f"[Orchestrator检查] {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    if not STATE_FILE.exists():
        print("❌ state.json不存在")
        return

    with open(STATE_FILE) as f:
        data = json.load(f)

    mode = data.get("mode", "?")
    updated = data.get("updated_at", "?")
    sources = data.get("sources", {})

    print(f"模式: {mode}")
    print(f"最后更新: {updated}")
    print()

    # 状态统计
    states = {"NORMAL": 0, "THROTTLED": 0, "BLOCKED": 0}
    total_req = 0
    total_err = 0

    for name, s in sorted(sources.items()):
        state = s.get("state", "?")
        req = s.get("total_requests", 0)
        err = s.get("total_errors", 0)
        cd = s.get("cooldown_until", 0)
        ratio = round(err / req * 100, 1) if req > 0 else 0

        icon = "🟢" if state == "NORMAL" else "🟡" if state == "THROTTLED" else "🔴"
        cd_str = f" (冷却{cd:.0f}s)" if cd > 0 else ""

        print(f"  {icon} {name}: {state}{cd_str} | 请求{req} 错误{err} 错误率{ratio}%")

        states[state] = states.get(state, 0) + 1
        total_req += req
        total_err += err

    print()
    print(f"汇总: NORMAL={states.get('NORMAL',0)} THROTTLED={states.get('THROTTLED',0)} BLOCKED={states.get('BLOCKED',0)}")
    print(f"总请求: {total_req} | 总错误: {total_err} | 错误率: {round(total_err/total_req*100,1) if total_req > 0 else 0}%")

    # 恢复能力检查
    print()
    print("--- 恢复能力检查 ---")
    blocked_sources = [n for n, s in sources.items() if s.get("state") == "BLOCKED"]
    if blocked_sources:
        print(f"⚠️ BLOCKED数据源: {', '.join(blocked_sources)}")
        print("   需要确认：冷却结束后是否能自动恢复")
    else:
        print("✅ 无BLOCKED数据源")

    # state.json大小检查
    file_size = STATE_FILE.stat().st_size
    print(f"state.json大小: {file_size} bytes")
    if file_size > 10000:
        print("⚠️ 文件偏大，考虑清理历史数据")

    print("=" * 50)

if __name__ == "__main__":
    check_orchestrator()
