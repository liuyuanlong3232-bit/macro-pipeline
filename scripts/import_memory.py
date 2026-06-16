#!/usr/bin/env python3
"""从Git同步的记忆文件导入到Hermes记忆"""
import os
from pathlib import Path

GIT_MEMORY = Path("/root/hermes-pipeline/memories/LOCAL_MEMORY.md")
HERMES_MEMORY = Path("/root/hermes-pipeline/memories/MEMORY.md")

def main():
    if not GIT_MEMORY.exists():
        print("[import_memory] 同步文件不存在")
        return
    
    with open(GIT_MEMORY, "r") as f:
        content = f.read()
    
    # 写入Hermes记忆文件
    HERMES_MEMORY.parent.mkdir(parents=True, exist_ok=True)
    with open(HERMES_MEMORY, "w") as f:
        f.write(content)
    
    # 统计
    entries = content.count("§")
    print(f"[import_memory] 已导入VPS记忆: {len(content)} 字符, ~{entries} 条目")
    
    # 如果Hermes gateway在跑，还需要重启才能加载新记忆
    # 或者通过hermes chat触发重新加载

if __name__ == "__main__":
    main()
