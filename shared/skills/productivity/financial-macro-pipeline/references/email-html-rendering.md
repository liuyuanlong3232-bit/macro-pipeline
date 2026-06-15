# send_email.py HTML渲染架构

## 设计规则（从bug中总结）

`send_email.py` 把Markdown报告转成HTML邮件。核心难点：**5份报告使用两种Markdown表格语法**。

### 两种表格格式

```
格式A（macro/metals/energy）：
| 品种 | 价格 | 来源 |
|------|------|------|
| 黄金 | $4200 | Yahoo |

格式B（agri_global/agri_china）：
品种 | 价格 | 来源
--- | --- | ---
玉米 | $411 | Yahoo
```

### 表格检测逻辑（def send_report内）

```
1. 对每行 stripped = line.strip()
2. 先检查是不是分隔行:
   def _is_sep(s):
       return "|" in s and not s.replace("|","").replace("-","").replace(":","").strip()
   if _is_sep(stripped): continue
3. 如果行含 "|" → 尝试解析为表格:
   cells_raw = [c.strip() for c in stripped.split("|")]
   过滤掉纯 -: 的假单元格
   if real_cells >= 2列 → 确认是表格行
4. 表头判断:
   - 第一张表: 行后跟分隔行 → 表头
   - 后续表: 上上行是分隔行 → 表头
   - 前一行是分隔行 → 数据行
5. 连续表格行暂存到 table_rows[]
6. 遇到非表格行 → flush_table() 输出 HTML <table>
```

### HTML输出

```html
<table style="border-collapse:collapse;width:100%;margin:10px 0;font-size:12px;">
  <tr><th style="border:1px solid #ddd;padding:6px 8px;background:#f8f9fa;font-weight:bold;text-align:center;">品种</th>...</tr>
  <tr><td style="border:1px solid #ddd;padding:6px 8px;background:#fff;font-weight:normal;text-align:center;">黄金</td>...</tr>
</table>
```

### 图表嵌入逻辑

| chart_type | 嵌入的图 |
|------------|---------|
| macro | fred_trends.png (1张) |
| metals | gold_price + silver_price + gold_silver_ratio + cot_net_history + cot_net + cot_index (6张) |
| energy | cot_net + cot_index (2张) |
| agri / agri_cn | 无图 |

### 已知坑（修复历史）

1. **格式B不被识别**（2026-06-13修复）
   - 问题：检测逻辑只认行首 `|`，格式B没有
   - 修复：用 `"|" in stripped` 替代 `stripped.startswith("|")`

2. **分隔行```|---|---|---```渲染为文本**（2026-06-13修复）
   - 问题：旧逻辑先检查is_table_row，分隔行的cleaned为空进不了检测，掉到普通段落
   - 修复：把分隔行检测提到最前面，独立拦截

3. **重复split和replace**（2026-06-13 simplify修复）
   - 问题：`cleaned`和`stripped_no_pipe`重复计算，`cells_raw`和`cells`重复split
   - 修复：提取 `_is_sep()` 函数，复用 `cells_raw[:]`

### 邮件结构

```
MIMEMultipart("alternative")
├── MIMEText(plain)     # 备用纯文本
└── MIMEText(html)      # 主内容：图表 + HTML表格
    ├── <h3>图表标题</h3>
    ├── <img src="data:image/png;base64,...">
    ├── <h3>章节标题</h3>
    └── <table>...</table>
```
