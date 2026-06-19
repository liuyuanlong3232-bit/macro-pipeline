#!/usr/bin/env python3
"""VPS记忆推送到GitHub shared/"""
import os
import subprocess
from pathlib import Path
from datetime import datetime

repo = Path.home() / "hermes-pipeline"
shared = repo / "shared" / "memories"
shared.mkdir(parents=True, exist_ok=True)

# 导出VPS记忆
vps_mem = repo / "memories" / "MEMORY.md"
if vps_mem.exists():
    content = vps_mem.read_text("utf-8")
    (shared / "VPS_MEMORY.md").write_text(content, "utf-8")

# Git push
os.chdir(str(repo))
subprocess.run(["git", "add", "shared/"], capture_output=True)
ts = datetime.now().strftime("%Y-%m-%d %H:%M")
r = subprocess.run(["git", "commit", "-m", f"shared: vps memory {ts}"], capture_output=True)
if "nothing to commit" not in r.stdout.decode() + r.stderr.decode():
    subprocess.run(["git", "push"], capture_output=True)
    print(f"[vps_memory_push] pushed at {ts}")
else:
    print(f"[vps_memory_push] nothing new at {ts}")
