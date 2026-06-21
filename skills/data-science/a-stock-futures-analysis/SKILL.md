---
name: a-stock-futures-analysis
description: "A股期股联动分析 — 兴业银锡(000426)/锡业股份(000960) vs 沪银/沪锡期货。覆盖盘前/午间/盘后三时段报告：实时行情、资金流向、技术面、期股联动系数、LME外盘、北向资金。支持邮件推送。"
origin: custom
version: 1.0
metadata:
  hermes:
    tags: [A股, 期货, 联动分析, 有色金属, 银, 锡, finance, china]
---

# A股期股联动分析 Skill

专注**有色金属板块**两只个股的全方位分析，结合期货数据做联动研判。

## 目标

| 类别 | 标的 | 代码/合约 |
|------|------|-----------|
| 个股 | 兴业银锡 | 000426 (深圳) |
| 个股 | 锡业股份 | 000960 (深圳) |
| 期货 | 沪银主力 | ag0 (上期所) |
| 期货 | 沪锡主力 | sn0 (上期所) |
| 外盘 | LME锡/银、美元指数 | 新浪财经 |

## 三个时段

| 时段 | 时间 | 重点内容 |
|------|------|----------|
| 🌅 盘前 | 08:30 | 隔夜外盘LME、期货夜盘、宏观消息影响研判 |
| 🔔 午间 | 11:35 | 上午盘面复盘、资金流向、技术面、期股联动 |
| 📋 盘后 | 15:15 | 全日复盘、联动系数、北向资金、技术信号汇总 |

## 使用方式

### 手动运行
```bash
# 盘前报告
python3 ~/hermes-pipeline/scripts/stock_analysis/futures_stock_analysis.py --mode morning

# 午间报告
python3 ~/hermes-pipeline/scripts/stock_analysis/futures_stock_analysis.py --mode lunch

# 盘后报告（含邮件）
python3 ~/hermes-pipeline/scripts/stock_analysis/futures_stock_analysis.py --mode afternoon --email your@qq.com
```

### 定时任务（Cron）
Hermes cron 会自动在三个时段运行报告生成脚本并推送。

## 数据源

| 数据 | 来源 | 封IP风险 |
|------|------|----------|
| 个股实时行情 | 腾讯财经 qt.gtimg.cn | ✅ 不封 |
| K线/技术指标 | AKShare (东方财富) | ⚠️ 有限流 |
| 期货行情 | 新浪财经 hq.sinajs.cn | ✅ 不封 |
| 期货K线 | AKShare (新浪) | ✅ 不封 |
| 资金流向 | 东方财富 push2 | ⚠️ 有限流 |
| LME/美元指数 | 新浪外盘 | ✅ 不封 |
| 北向资金 | AKShare | ✅ 不封 |

## 关键脚本

- `~/hermes-pipeline/scripts/stock_analysis/futures_stock_analysis.py` — 主分析脚本
- `~/hermes-macro-data/reports/stock_analysis/` — 报告输出目录

## 联动分析逻辑

1. 获取个股60日K线 + 期货60日K线
2. 计算日收益率序列
3. 计算20日滚动Pearson相关系数
4. 相关性分级：|r|>0.7 强 / |r|>0.4 中 / |r|<0.4 弱
5. 结合技术面(MA/MACD/RSI)给出综合信号

## 邮件配置

需要设置环境变量（在 `~/.hermes/.env` 或系统环境变量）：
```
QQ_SMTP_USER=你的QQ邮箱@qq.com
QQ_SMTP_PASS=QQ邮箱授权码（非QQ密码，在QQ邮箱设置-账户-POP3里获取）
```

## Pitfalls

1. **AKShare导入慢**：首次import akshare需10-15秒，是正常的
2. **东财限流**：连续调用东财接口可能被限流，脚本已做异常捕获
3. **期货主力合约换月**：ag0/sn0自动映射主力合约，但换月当天数据可能不连续
4. **非交易时间**：盘前/周末运行时获取的是上一交易日数据
5. **Tushare期货**：只有历史日线，实时期货用新浪/AKShare
