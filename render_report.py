#!/usr/bin/env python3
"""
把Markdown周报 + 图表 渲染成1张PNG长图
用法: python3 render_report.py <报告路径> [chart_type]
输出: 同目录下 <报告名>_report.png
"""
import os, sys, base64, subprocess, re, tempfile
from pathlib import Path
from datetime import datetime

CHART_DIR = Path.home() / "hermes-macro-data" / "charts"

def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def md_table_to_html(lines, start_idx):
    """Convert markdown table lines to HTML table, return (html, end_idx)"""
    rows = []
    i = start_idx
    while i < len(lines):
        line = lines[i].strip()
        if not line or '|' not in line:
            break
        # skip separator lines like |---|---|
        if re.match(r'^[\s|:\-]+$', line):
            i += 1
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        rows.append(cells)
        i += 1

    if not rows:
        return '', start_idx

    html = '<table style="border-collapse:collapse;width:100%;margin:12px 0;font-size:12px;">\n'
    # first row as header
    html += '<tr>'
    for ci, cell in enumerate(rows[0]):
        html += '<th style="border:1px solid #ccc;padding:6px 10px;background:#f0f4f8;font-weight:bold;text-align:center;color:#2C3E50;">' + cell + '</th>\n'
    html += '</tr>\n'
    for row in rows[1:]:
        html += '<tr>'
        for cell in row:
            html += '<td style="border:1px solid #ddd;padding:5px 8px;text-align:center;">' + cell + '</td>\n'
        html += '</tr>\n'
    html += '</table>\n'
    return html, i

def md_to_html(content, chart_type=''):
    """Convert markdown content + charts to full HTML"""
    lines = content.split('\n')

    # Extract title
    title = "研究报告"
    for line in lines:
        if line.startswith('# '):
            title = line.replace('# ', '').strip()
            break

    date_str = datetime.now().strftime('%Y-%m-%d')

    html_parts = []
    html_parts.append('<!DOCTYPE html>')
    html_parts.append('<html><head><meta charset="utf-8">')
    html_parts.append('<style>')
    html_parts.append('  body { font-family: "Noto Sans CJK SC", "Microsoft YaHei", "PingFang SC", "Helvetica Neue", Arial, sans-serif;')
    html_parts.append('         color: #333; max-width: 800px; margin: 0 auto; padding: 15px 20px;')
    html_parts.append('         background: #fff; line-height: 1.6; }')
    html_parts.append('  h1 { color: #1a1a2e; font-size: 20px; text-align: center; margin-bottom: 5px;')
    html_parts.append('       border-bottom: 3px solid #3498DB; padding-bottom: 10px; }')
    html_parts.append('  h2 { color: #2C3E50; font-size: 16px; margin-top: 25px; border-left: 4px solid #3498DB;')
    html_parts.append('       padding-left: 12px; }')
    html_parts.append('  h3 { color: #E67E22; font-size: 14px; margin-top: 18px; }')
    html_parts.append('  p { font-size: 12.5px; margin: 4px 0; color: #444; }')
    html_parts.append('  .chart-section { margin: 15px 0; text-align: center; }')
    html_parts.append('  .chart-section img { width: 100%; max-width: 720px; border-radius: 6px; border: 1px solid #eee; }')
    html_parts.append('  .chart-title { font-size: 13px; font-weight: bold; color: #2C3E50; margin: 8px 0 4px 0;')
    html_parts.append('                 border-left: 4px solid #E67E22; padding-left: 10px; }')
    html_parts.append('  table { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 12px; }')
    html_parts.append('  th { background: #f0f4f8; border: 1px solid #ccc; padding: 6px 10px; font-weight: bold;')
    html_parts.append('       color: #2C3E50; text-align: center; }')
    html_parts.append('  td { border: 1px solid #ddd; padding: 5px 8px; text-align: center; }')
    html_parts.append('  .footer { text-align: center; color: #999; font-size: 10px; margin-top: 20px;')
    html_parts.append('            border-top: 1px solid #eee; padding-top: 10px; }')
    html_parts.append('</style>')
    html_parts.append('</head><body>')

    # Add title
    html_parts.append('<h1>' + title + '</h1>')
    html_parts.append('<p style="text-align:center;color:#888;font-size:11px;margin-bottom:15px;">生成日期: ' + date_str + '</p>')

    # Add charts based on chart_type
    chart_configs = {
        'macro': [
            ("fred_fed_rate", "联邦基金利率走势（15年）"),
            ("fred_cpi", "美国CPI走势（15年）"),
            ("fred_10y", "美国10年国债收益率走势（15年）"),
            ("fred_tips", "10年TIPS收益率走势（15年）"),
        ],
        'metals': [
            ("gold_price", "黄金走势（15年）"),
            ("silver_price", "白银走势（15年均线）"),
            ("gold_silver_ratio", "金银比（15年）"),
            ("cot_net_history", "黄金COT投机净持仓历史"),
            ("cot_net", "COT投机净持仓排行榜"),
            ("cot_index", "COT Index一览"),
        ],
        'energy': [
            ("cot_net", "COT投机净持仓"),
            ("cot_index", "COT Index"),
        ],
    }

    if chart_type in chart_configs:
        html_parts.append('<div style="margin: 10px 0;">')
        for name, title_text in chart_configs[chart_type]:
            p = CHART_DIR / (name + ".png")
            if p.exists():
                b64 = img_to_base64(p)
                html_parts.append('<div class="chart-section">')
                html_parts.append('<div class="chart-title">' + title_text + '</div>')
                html_parts.append('<img src="data:image/png;base64,' + b64 + '">')
                html_parts.append('</div>')
        html_parts.append('</div>')

    # Convert markdown body
    i = 0
    skip_h1 = True
    html_body = ''

    while i < len(lines):
        line = lines[i].strip()

        # Skip the first H1 (already rendered as title)
        if skip_h1 and line.startswith('# ') and not line.startswith('## '):
            skip_h1 = False
            i += 1
            continue

        # Table detection
        if '|' in line and not re.match(r'^[\s|:\-]+$', line):
            table_html, end_i = md_table_to_html(lines, i)
            html_body += table_html
            i = end_i
            continue

        # Headings
        if line.startswith('## '):
            html_body += '<h2>' + line[3:] + '</h2>\n'
        elif line.startswith('### '):
            html_body += '<h3>' + line[4:] + '</h3>\n'
        elif line.startswith('#### '):
            html_body += '<p style="font-weight:bold;color:#2C3E50;font-size:13px;margin-top:12px;">' + line[5:] + '</p>\n'
        elif line.startswith('**') and line.endswith('**'):
            html_body += '<p style="font-weight:bold;color:#2C3E50;font-size:13px;margin-top:10px;">' + line.strip('*') + '</p>\n'
        elif line.startswith('- ') or line.startswith('* '):
            html_body += '<p style="margin:2px 0;padding-left:18px;font-size:12px;">• ' + line[2:] + '</p>\n'
        elif line.startswith('> '):
            html_body += '<p style="color:#888;font-style:italic;padding-left:12px;border-left:3px solid #ddd;font-size:12px;">' + line[2:] + '</p>\n'
        elif line == '---':
            html_body += '<hr style="border:none;border-top:1px solid #eee;margin:15px 0;">\n'
        elif line == '':
            html_body += '<br>\n'
        elif line.startswith('```'):
            # Skip code blocks
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                i += 1
        elif line.startswith('# '):
            # other H1s
            html_body += '<h2>' + line[2:] + '</h2>\n'
        else:
            # Normal paragraph - handle inline bold
            text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
            html_body += '<p style="line-height:1.6;color:#333;font-size:12.5px;margin:4px 0;">' + text + '</p>\n'

        i += 1

    html_parts.append('<div style="margin-top:15px;">' + html_body + '</div>')
    html_parts.append('<div class="footer">📊 Hermes Research · ' + date_str + '</div>')
    html_parts.append('</body></html>')

    return '\n'.join(html_parts)

def render_to_png(html_content, output_path):
    """Use wkhtmltoimage to render HTML to PNG"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html_content)
        tmp_html = f.name

    try:
        cmd = [
            'wkhtmltoimage',
            '--quality', '90',
            '--width', '800',
            '--enable-local-file-access',
            '--encoding', 'utf-8',
            '--javascript-delay', '500',
            tmp_html,
            str(output_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print("  ⚠️ wkhtmltoimage stderr: " + result.stderr[:500])
        return Path(output_path).exists()
    finally:
        os.unlink(tmp_html)

def generate_report_png(filepath, chart_type=''):
    """Main function: read markdown, render to PNG"""
    if not os.path.exists(filepath):
        print("❌ 报告不存在: " + filepath)
        return None

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    print("📝 正在渲染: " + filepath)

    # Convert to HTML
    html = md_to_html(content, chart_type)
    print("  ✅ HTML生成完毕 (" + str(len(html)) + " chars)")

    # Render to PNG
    stem = Path(filepath).stem
    out_dir = Path(filepath).parent
    png_path = out_dir / (stem + "_report.png")

    ok = render_to_png(html, png_path)
    if ok:
        size_kb = png_path.stat().st_size / 1024
        print("  ✅ PNG生成: " + str(png_path) + " (" + str(int(size_kb)) + " KB)")
        return str(png_path)
    else:
        print("  ❌ PNG渲染失败")
        return None

if __name__ == '__main__':
    if len(sys.argv) > 1:
        ct = sys.argv[2] if len(sys.argv) > 2 else ''
        result = generate_report_png(sys.argv[1], ct)
        if result:
            print("\n✅ 完成: " + result)
        else:
            print("\n❌ 渲染失败")
            sys.exit(1)
    else:
        print("用法: python3 render_report.py <报告路径> [chart_type]")
        print("  chart_type: macro / metals / energy (可选)")
