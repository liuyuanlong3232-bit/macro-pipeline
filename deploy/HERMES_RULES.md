# Hermes 工作纪律

> 2026-06-16 老大亲定，铁律

## 禁止事项

1. **禁止私自写 Python 代码** — 不问不动手
2. **禁止跳过 Skills 直接上手** — 先查有没有现成方案
3. **禁止跳过 Plugins/Tools 直接造轮子** — 缺啥装啥
4. **禁止不验证就宣布成功** — 改完必须测试

## 必须执行的流程

```
接任务 → ①查skills → ②查plugins/tools → ③缺啥装啥 → ④写代码前请示同意 → ⑤写代码 → ⑥测试 → ⑦推Git
```

## 常用代码封装

- 邮件发送 → `send_email.py`（已有）
- CSV导入SQLite → `shared/utils.py`（已有）
- Yahoo数据拉取 → `shared/utils.py`（已有）
- 新的常用代码 → 封装为 skill

## 定期清理

- 每周检查一次无效代码碎片
- 删除不用的 debug/test 文件
- 更新 skill 文档
