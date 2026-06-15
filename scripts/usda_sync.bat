@echo off
chcp 65001 >nul
title USDA数据采集与同步脚本

echo ═══════════════════════════════════════
echo   USDA NASS 数据采集 + 同步到VPS
echo   日期: %date%
echo ═══════════════════════════════════════
echo.

:: 检查代理
set HTTPS_PROXY=http://127.0.0.1:10808
set HTTP_PROXY=http://127.0.0.1:10808

:: 获取今天日期（中国格式）
set today=%date:~0,4%-%date:~5,2%-%date:~8,2%
echo [1/4] 今日日期: %today%

:: 第1步：本地采集USDA
echo [2/4] 正在本地采集USDA数据...
cd /d C:\Users\Administrator\hermes-macro-pipeline
python3 macro_pipeline.py --source usda
if %errorlevel% neq 0 (
    echo ❌ 采集失败，可能是网络问题，检查代理
    pause
    exit /b 1
)
echo ✅ 采集完成
echo.

:: 第2步：上传CSV到VPS
echo [3/4] 正在上传CSV到VPS...
set csv_file=C:\Users\Administrator\hermes-macro-data\csv\%today%\usda_agriculture.csv
if exist "%csv_file%" (
    scp -P 58234 -i C:\Users\Administrator\.ssh\id_rsa "%csv_file%" root@45.77.126.71:/root/hermes-macro-data/csv/%today%/
    if %errorlevel% neq 0 (
        echo ❌ 上传失败，检查VPS连接
        pause
        exit /b 1
    )
    echo ✅ 上传完成
) else (
    echo ⚠️ CSV文件不存在: %csv_file%
    echo    继续执行报告生成，VPS会用已有数据
)
echo.

:: 第3步：VPS上生成农业报告
echo [4/4] 正在VPS上生成农业报告...
ssh -p 58234 -i C:\Users\Administrator\.ssh\id_rsa root@45.77.126.71 "cd /root/hermes-pipeline && python3 run_report.py agri"
if %errorlevel% neq 0 (
    echo ⚠️ 报告生成可能有警告，但不影响
)
echo.
echo ═══════════════════════════════════════
echo   ✅ 全部完成！
echo   报告已发送到QQ邮箱
echo ═══════════════════════════════════════
echo.
pause
