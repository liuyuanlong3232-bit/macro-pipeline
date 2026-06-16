@echo off
chcp 65001 >nul
title 记忆同步: 本地 → Git → VPS

echo ═══════════════════════════════════════
echo   记忆同步系统
echo   本地Hermes → GitHub → VPS Hermes
echo ═══════════════════════════════════════
echo.

:: 1. 导出本地记忆
echo [1/4] 导出本地记忆...
cd /d D:\hermes\pipeline
python scripts/sync_memory.py
if %errorlevel% neq 0 (
    echo ❌ 导出失败
    pause
    exit /b 1
)
echo.

:: 2. Git提交推送
echo [2/4] 推送到GitHub...
set HTTPS_PROXY=http://127.0.0.1:10808
git add memories/LOCAL_MEMORY.md
git commit -m "sync: local memory" 2>nul
git push 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ GitHub推送失败，跳过
)
echo.

:: 3. VPS拉取
echo [3/4] VPS拉取Git...
ssh -p 58234 -i C:\Users\Administrator\.ssh\id_rsa root@45.77.126.71 "cd /root/hermes-pipeline && git pull" 2>&1
echo.

:: 4. VPS导入记忆
echo [4/4] VPS导入记忆...
ssh -p 58234 -i C:\Users\Administrator\.ssh\id_rsa root@45.77.126.71 "cd /root/hermes-pipeline && python3 scripts/import_memory.py" 2>&1
echo.

echo ═══════════════════════════════════════
echo   ✅ 同步完成
echo ═══════════════════════════════════════
pause
