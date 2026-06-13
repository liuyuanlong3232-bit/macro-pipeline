#!/usr/bin/env bash
# 每日宏观数据采集脚本 - 给 cron 用
set -e
cd "$(dirname "$0")"
echo "[$(date)] 开始宏观数据采集..."

# 运行全部数据源
python3 macro_pipeline.py 2>&1

# 记录结果
echo "[$(date)] 采集完成"
