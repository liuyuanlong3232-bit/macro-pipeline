#!/usr/bin/env python3
"""本地Hermes记忆同步到VPS Hermes记忆"""
import os, sys
from pathlib import Path
from datetime import datetime

LOCAL_MEMORY = Path.home() / "AppData" / "Local" / "hermes" / "memories" / "MEMORY.md"
# 动态定位项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent
REMOTE_MEMORY = str(PROJECT_ROOT / "memories" / "MEMORY.md")

def main():
    if not LOCAL_MEMORY.exists():
        print("本地记忆文件不存在")
        return
    
    # 读取本地记忆
    with open(LOCAL_MEMORY, "r") as f:
        content = f.read()
    
    # 保存到本地Git仓库，然后再上传
    sync_file = PROJECT_ROOT / "memories" / "LOCAL_MEMORY.md"
    sync_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(sync_file, "w") as f:
        f.write(content)
    
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"已导出到: {sync_file}")
    print(f"更新时间: {ts}")
    print()
    print("手动执行")
    print(f"  cd {PROJECT_ROOT}")
    print("  git add memories/LOCAL_MEMORY.md")
    print("  git commit -m 'sync: local memory'")
    print("  git push")
    print()
    print("然后VPS上执行:")
    print(f"  cd {PROJECT_ROOT}")
    print("  git pull")
    print("  python3 scripts/import_memory.py")
    
    return sync_file

if __name__ == "__main__":
    main()
