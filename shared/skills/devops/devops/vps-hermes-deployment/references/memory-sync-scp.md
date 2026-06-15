# Memory Sync: Local → VPS via scp

## Why scp, not Git

Git sync between VPS and GitHub fails when VPS has untracked test files, local changes, or merge
conflicts (common when VPS Hermes modifies report scripts and the pipeline repo has evolved
independently on local). `scp` bypasses all Git state issues and syncs memory directly.

## Setup

### 1. Local export script
Save at `hermes-macro-pipeline/scripts/sync_memory.py`:
```python
from pathlib import Path
src = Path.home() / "AppData" / "Local" / "hermes" / "memories" / "MEMORY.md"
dst = Path.home() / "hermes-macro-pipeline" / "memories" / "LOCAL_MEMORY.md"
dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_text(src.read_text("utf-8"), "utf-8")
```

### 2. VPS import script  
Save at `/root/hermes-pipeline/scripts/import_memory.py`:
```python
from pathlib import Path
src = Path("/root/hermes-pipeline/memories/LOCAL_MEMORY.md")
dst = Path("/root/hermes-pipeline/memories/MEMORY.md")
dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_text(src.read_text("utf-8"), "utf-8")
```

### 3. One-click sync (sync_memory.bat)
```batch
scp -q -P 58234 -i C:\Users\Administrator\.ssh\id_rsa ^
  C:\Users\Administrator\hermes-macro-pipeline\memories\LOCAL_MEMORY.md ^
  root@45.77.126.71:/root/hermes-pipeline/memories/
ssh -p 58234 -i C:\Users\Administrator\.ssh\id_rsa root@45.77.126.71 ^
  "python3 /root/hermes-pipeline/scripts/import_memory.py"
```

## When VPS Hermes Loads the Memory

VPS Hermes reads `MEMORY.md` on **new session start only**:
- `hermes chat` new conversation → picks up fresh memory
- QQ Bot message triggers new session → picks up fresh memory  
- Running gateway session → does NOT re-read memory

To force a reload: kill and restart the gateway, or start a new `hermes chat` session.
