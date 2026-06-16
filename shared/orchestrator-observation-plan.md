# Orchestrator 观察期计划

> 2026-06-16 老大制定

## 观察周期

1~3天，中午自动检查日志

## 必须观察的3个问题

### 问题1：BLOCKED逻辑偏激进

当前规则：
- 3次429 → BLOCKED 10-30分钟
- 2次403 → BLOCKED 1小时

风险：短暂429抖动是常态，容易误封正常数据源，导致系统"假死感"

观察指标：
- 是否有数据源被误BLOCKED
- BLOCKED后恢复是否正常
- 实际429频率

### 问题2：mode+orchestrator叠加降速

场景：
- TEST模式 + THROTTLED
- PROD + BLOCKED

风险：系统自己把自己"限死"

观察指标：
- 模式切换后采集是否正常
- 降速是否合理

### 问题3：state.json长期运行偏保守

原因：失败累计只增不减（无衰减机制）

风险：系统越来越"胆小"

观察指标：
- total_errors是否持续增长
- 冷却时间是否越来越长
- 是否需要加入衰减机制

## 自动检查时间

每天中午12:00，检查VPS日志：
- /var/log/hermes_data.log
- /root/hermes-macro-data/meta/orchestrator_state.json

## 检查内容

1. 各数据源状态（NORMAL/THROTTLED/BLOCKED）
2. 429/403触发次数
3. 冷却时间是否合理
4. 采集是否正常完成

## 判断标准

- 如果1-3天内无异常 → 可以进入PROD
- 如果有误BLOCKED → 需要调整阈值
- 如果系统假死 → 需要加入衰减机制
