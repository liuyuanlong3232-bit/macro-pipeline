# Audit Report Template

Use this structure when presenting audit findings to the user.

## Format

```
================================================================
           报告数据审计报告 (日期范围)
================================================================

一、数据缺失问题
================================================================
(Files missing, columns showing "—" when data exists, etc.)

二、数据错误 & 文字不匹配
================================================================
【报告名 文件名】
错误N: 简短描述
  报告显示: "..."
  实际数据: ...
  原因: 代码第X行...
  >> 需要修改: 具体修复方案

三、不应该出现的内容
================================================================
(Dev notes, hardcoded test values, wrong language, etc.)

四、数据源对照表
================================================================
指标 | 数据源CSV | 报告A | 报告B | 报告C

五、优先修复建议 (按影响程度排序)
================================================================
P0 - 数据错误(影响可信度):
  1. ...
P1 - 数据缺失(影响完整性):
  2. ...
P2 - 文字问题(影响专业性):
  3. ...
```

## Severity Levels

- **P0**: Data is factually wrong (wrong number, impossible value, contradicts source)
- **P1**: Data missing or format wrong (shows "—" when source has value, wrong units)
- **P2**: Cosmetic issues (dev notes, language mixing, wording)

## User Expectations

- Show the FULL audit before starting any fixes
- Include a comparison table showing every data point traced to its source
- Group by report file, then by severity
- After audit, ask user to confirm before fixing (or user will say "逐一修复")
