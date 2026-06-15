# Cron 重复浪费钱 — 诊断与修复

## 背景
VPS 系统 cron 已经用 Python 脚本免费生成+发送全部5份周报。
但早期还创建了 Hermes 本地 cron（走 DeepSeek V4 Pro LLM 写报告），两者重复运行，白烧钱。

## 症状
- TokScale 显示 V4 Pro 有使用量，但当天没做复杂对话
- QQ邮箱收到两份相同的报告（来自LLM和Python脚本各一份）
- Hermes Desktop 中 `hermes cron list` 有周报/资产配置等6+个 cron（全用 V4 Pro）

## 解决
```bash
hermes cron list          # 查看所有cron
hermes cron remove <id>   # 逐个删除周报类cron
```
保留 1 个数据采集 cron（走 DeepSeek Flash 便宜）。

## 验证
```bash
hermes cron list          # 确认只剩数据采集cron
tokscale models --client hermes --today  # 确认V4 Pro用量归零
```

## 注意
如果未来需要 Hermes cron 跑报告，模型应设为 `deepseek/deepseek-chat`（Flash）而不是 V4 Pro。
周报也不值当花模型钱。

## 报告成本结构
- 数据采集（VPS Python脚本）：免费
- 报告生成（VPS Python脚本）：免费
- 图表生成（VPS Python脚本）：免费
- 邮件发送（QQ SMTP）：免费
- 聊天对话（Hermes Desktop）：按模型付费（当前用V4 Flash $0.14/$0.28）
- **总周成本**：约 $0（不含聊天）
