# 数据采集与报告缓存常见问题

## 一、"第一遍显示待更新"根因分析

修改报告代码后，数据仍然显示"待更新"的几种可能：

| 症状 | 根因 | 修复 |
|------|------|------|
| EIA/OPEC数据全部待更新 | HERMES_HOME未设 | `export HERMES_HOME=/root/hermes-pipeline` |
| 报告里有旧日期数据 | 读的是旧缓存CSV | `rm -f *_2026-xx-xx.md` 重新跑 |
| 新增FRED系列但报告没显示 | 采集脚本还没跑，CSV没有该列 | 先跑macro_pipeline.py或等定时任务 |
| 爬虫返回None | VPS直连 vs 本地代理差异 | data_scrapers.py自动检测10808端口 |

## 二、数据源验证套路

每次接入新数据源：
```
1. 本地单独测试函数 → python3 -c "from file import func; print(func())"
2. VPS单独测试 → scp上去再跑
3. 集成到报告脚本 → 最后跑run_report.py
```

## 三、子代理注意事项

用 delegate_task 改报告脚本时：
- 子代理可能达到最大工具调用次数(50次)，父进程需收尾
- 子代理修改文件后，父进程需重新读取
- 多个代理并行改同一文件会冲突，串行

## 四、VPS环境

1c1g Ubuntu 22.04：
- pandas/requests/AKShare正常
- pdfplumber解析USDA PDF正常
- Scrapling StealthyFetcher (Cloudflare头浏览器) → 1G内存不够
