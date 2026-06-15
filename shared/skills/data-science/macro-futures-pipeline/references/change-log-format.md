# 修改记录格式

## 每次修改后必须遵守的格式

以"改了什么+为什么"的结构逐条列在commit message或回复中：

```
| 文件 | 改动 | 原因 |
|------|------|------|
| macro_weekly.py | 新增fetch_cn_macro()函数 | 从AKShare获取DR007/LPR |
| macro_weekly.py | compute_scores()改用AKShare | 替代FRED无数据 |
| metals_weekly.py | gold_wow/gold_avg写入现货行 | 修复"周环比=—"bug |
```

## commit 命名规范

```
feat: 新功能（新数据源接入）
fix: 修复bug（"—"→真实数据）
docs: 文档/提示词更新
refactor: 重构不改逻辑
```

## 不可修改的文件

- prompts/*.txt — 提示词模板，绝对不改
- energy_weekly.py — 用户明确要求不修改（但数据采集可加）
