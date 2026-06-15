# PNG报告渲染

## 工具
- `wkhtmltoimage`（来自 `wkhtmltopdf` 包，~5MB）
- `render_report.py`（VPS: /root/hermes-pipeline/render_report.py）

## 用法
```bash
# 单独渲染
python3 /root/hermes-pipeline/render_report.py /path/to/report.md macro

# 通过send_email.py自动附加
python3 /root/hermes-pipeline/send_email.py /path/to/report.md macro
```

## chart_type参数
- `macro` → 嵌入4张宏观指标图（fred_fed_rate/cpi/10y/tips）
- `metals` → 嵌入贵金属图表
- `energy` → 嵌入能源图表
- 空 → 纯文本报告

## 输出
- HTML: /path/to/report.html
- PNG: /path/to/report_report.png（10-18MB，含图表）

## 已知问题
- PNG文件较大（图表base64嵌入），可考虑降低DPI
- 中文字体需要Noto Sans CJK（已安装在VPS）
