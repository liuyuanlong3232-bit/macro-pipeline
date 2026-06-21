#!/usr/bin/env python3
"""VPS数据库备份 - 压缩并保留最近30天"""
import os, shutil, gzip
from pathlib import Path
from datetime import datetime, timedelta

DB = Path.home() / "hermes-macro-data" / "hermes.db"
BACKUP_DIR = Path.home() / "hermes-macro-data" / "backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
backup_file = BACKUP_DIR / f"hermes_{today}.db.gz"

# 压缩备份
with open(DB, "rb") as f_in:
    with gzip.open(backup_file, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

size_mb = backup_file.stat().st_size / 1024 / 1024
print(f"[backup] ✅ {backup_file.name} ({size_mb:.1f}MB)")

# 清理30天前的备份
cutoff = datetime.now() - timedelta(days=30)
for f in BACKUP_DIR.glob("hermes_*.db.gz"):
    date_str = f.stem.replace("hermes_", "")
    try:
        fdate = datetime.strptime(date_str, "%Y-%m-%d")
        if fdate < cutoff:
            f.unlink()
            print(f"[backup] 🗑️ 清理旧备份: {f.name}")
    except:
        pass

# 统计
backups = sorted(BACKUP_DIR.glob("hermes_*.db.gz"))
latest = backups[-1].name if backups else "无"; print("[backup] 📦 共%d个备份，最新: %s" % (len(backups), latest))
