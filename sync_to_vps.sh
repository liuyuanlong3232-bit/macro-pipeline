#!/bin/bash
# 一键同步到VPS
# 先推送到 GitHub，VPS 再拉取

set -e

echo "=== 1. 本地提交 ==="
cd "$(dirname "$0")"
git add -A
git commit -m "$(date '+%Y-%m-%d %H:%M') 更新" || echo "无变更"
git push

echo "=== 2. VPS拉取 ==="
ssh -p 58234 -i /d/hermes-ssh/id_ed25519 root@45.77.126.71 '
cd /root/hermes-pipeline
git pull
echo "✅ VPS已同步最新代码"
'

echo "✅ 全部完成"
