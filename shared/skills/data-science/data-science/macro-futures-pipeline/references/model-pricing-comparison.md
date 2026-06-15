# 模型价格与能力对比（2026-06-13）

## 当前使用
- 默认模型：MiMo 2.5 Pro（MiMo Token Plan Lite ¥39/月，41亿Credits）
- 周报：不花模型钱（Python脚本生成）
- 切换命令：`hermes config set model.default xiaomi/mimo-v2.5-pro`

## 价格对比

| 模型 | Input/M | Output/M | 基准分 |
|------|:-------:|:--------:|:------:|
| DeepSeek V4 Flash | $0.14 | $0.28 | 57 |
| DeepSeek V4 Pro | $0.435 | $0.87 | ~51 |
| **MiMo 2.5 Pro** | **$0.435** | **$0.87** | **86** |

## 关键发现
- MiMo 2.5 Pro 和 DeepSeek V4 Pro 定价完全一样
- MiMo 基准分86 vs V4 Flash 57，智能差距显著
- Agentic能力：68.4 vs 49.1
- MiMo是推理模型，token消耗更多

## 推荐
升级→MiMo 2.5 Pro（同价位更强）
省钱→继续V4 Flash
