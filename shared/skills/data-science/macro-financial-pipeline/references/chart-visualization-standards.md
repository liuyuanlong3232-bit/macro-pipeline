# Chart Visualization Standards (Session-Verified)

Consolidated chart rendering rules for weekly reports sent to QQ mobile email.
These rules were debugged and verified across multiple iterations on 2026-06-13.

## 1. Data Cleaning (Before Every Chart)

Historical data from `D:\commodity_research_platform\export\merged\商品价格.xlsx`
contains occasional outlier rows where Yahoo returned decimal-shifted values.

**Always filter before plotting:**

```python
# Gold: range $1,000-$6,000
cleaned = [(r[0], float(r[1])) for r in rows if 1000 < float(r[1]) < 6000]

# Silver: range $5-$200  
cleaned = [(r[0], float(r[1])) for r in rows if 5 < float(r[1]) < 200]
```

Without this, the 15-year Y-axis gets compressed to $0-$5000 and shows as a flat
heartbeat line. Test: gold should have ~3,740 rows (2011-2026) after cleaning.

## 2. Multi-Panel Charts — Independent Y-Axes

When plotting "all time / 3yr / 1yr" in subplots (e.g. gold_price chart),
matplotlib's auto-scale uses the global min/max across all panels, crushing
near-term detail.

**Fix — per-subplot padding:**

```python
ymin, ymax = min(y), max(y)
padding = (ymax - ymin) * 0.15    # 15% headroom
ax.set_ylim(ymin - padding, ymax + padding)
```

Result after cleaning (gold):
| Panel | Y-range | Usefulness |
|-------|---------|------------|
| 15yr  | $1,000-$4,200 | Full context |
| 3yr   | $1,986-$4,200 | Medium zoom |
| 1yr   | $3,100-$4,200 | Near-term detail visible |

## 3. Label Positioning — Start vs Latest Value

The user noticed labels appearing "有些在大数字后，有些在大数据前"
(labels behind vs in front of data points).

**Fixed convention — three label types:**

```python
def tag_start(ax, x, y, txt):
    """Starting value: bottom-left of line, no bbox, gray text"""
    ax.text(x, y, txt, fontsize=9, ha="left", va="bottom",
            color="#7F8C8D", fontweight="normal")

def tag_end(ax, x, y, txt, color="#2C3E50"):
    """Latest value: right side with white bbox for legibility"""
    ax.text(x, y, txt, fontsize=11, ha="right", va="top",
            color=color, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor=color, alpha=0.85))
```

Apply consistently to ALL line charts: FRED indicators, gold, silver, ratio, COT history.

## 4. Email Table Rendering — HTML `<table>` (Final, After 3 Iterations)

The user went through 3 attempts before settling on the FINAL correct approach on 2026-06-13.

**Do NOT strip pipes to text.** The user explicitly rejected that: "还是需要表格版的，数据应该生成表格".

**FINALLY CORRECT approach — render as HTML `<table>`:**

1. **Intercept separator rows FIRST** — before any table detection:
   ```python
   stripped_no_pipe = stripped.replace("|","").replace("-","").replace(":","").strip()
   if not stripped_no_pipe and "|" in stripped:
       continue  # |------|------| — skip silently
   ```

2. **Detect table rows** (handles both `| 品种 | 价格 |` and `品种 | 价格` formats):
   ```python
   if "|" in stripped:
       real_cells = [c for c in stripped.split("|") 
                     if c.strip() and not set(c.strip()) <= set("-: ")]
       if len(real_cells) >= 2:
           is_table_row = True
   ```

3. **Extract cells** from either format:
   ```python
   cells = [c.strip() for c in stripped.split("|")]
   if stripped.startswith("|") and stripped.endswith("|"):
       cells = cells[1:-1]  # strip leading empty from Format A
   cells = [c for c in cells if c.strip()]
   ```

4. **Render as proper HTML `<table>`:**
   ```python
   html = '<table style="border-collapse:collapse;width:100%;font-size:12px;">\n'
   for is_header, cell_list in rows:
       tag = "th" if is_header else "td"
       bg = "#f8f9fa" if is_header else "#fff"
       row = "<tr>"
       for c in cell_list:
           row += f'<{tag} style="border:1px solid #ddd;padding:6px 8px;background:{bg};...">{c}</{tag}>'
       row += "</tr>\n"
       html += row
   html += "</table>\n"
   ```

**Critical:** QQ Mobile mail renders HTML `<table>` correctly. The earlier assumption that CSS stripping would break tables was WRONG — the real problem was the separator `|------|` lines rendering as visible garbage. Once those are stripped, HTML tables work fine.

## 5. Chart Size vs Email Reliability

QQ SMTP can timeout with 6+ base64 charts (~500KB total).

| Setting | Value | Notes |
|---------|-------|-------|
| DPI | 150 | 120 if timeout persists |
| Max charts per email | 6 (metals) | 1-2 for others |
| Max file size | ~70KB/chart | Check with `ls -lh` |

If timeout occurs:
- Reduce DPI to 120 in `plt.savefig(dpi=120)`
- Or split: email 1 (gold/silver/ratio), email 2 (COT data)
- Or increase SMTP timeout in send_email.py

## 6. Chart Type Mappings (run_report.py → send_email.py)

| report_type | Charts sent | Count |
|------------|-------------|-------|
| `macro` | fred_fed_rate, fred_cpi, fred_10y, fred_tips | 4 |
| `metals` | gold_price, silver_price, gold_silver_ratio, cot_net_history, cot_net, cot_index | 6 |
| `energy` | cot_net, cot_index | 2 |
| `agri` | (none) | 0 |
| `agri_cn` | (none) | 0 |
| `allocation` | (none) | 0 |

## 7. FRED Macro Chart — Use 3 Years, Not 15

The user explicitly said: "宏观数据图不需要十五年的" — macro indicator charts don't need 15 years of history. The macro chart should only show ~3 years.

Implementation in `charts.py`:
```python
# Query with DESC LIMIT 1100 days (~3 years), then reverse
rows = db.execute(
    "SELECT date, value FROM macro_history WHERE indicator=? "
    "AND value IS NOT NULL ORDER BY date DESC LIMIT 1100",
    (name,)
).fetchall()
rows = list(reversed(rows))
```

The 15-year data in `macro_history` still exists for calculations, but the chart only visualizes the recent 3 years.

## 8. Scrapling — New Data Source Scraping Tool

Installed 2026-06-13. Use for scraping data sources that are behind Cloudflare, anti-bot, or require stealth headers.

```python
from scrapling import Fetcher
f = Fetcher()
resp = f.get(url, proxies={"http": "http://127.0.0.1:10808",
                           "https": "http://127.0.0.1:10808"})
resp.css("title").first.text
```

See `references/scrapling-web-scraping.md` for full API reference and pitfall list.

## 9. Common Chart Config

```python
zh = "Noto Sans CJK JP"      # Chinese font
plt.rcParams["font.family"] = zh
plt.rcParams["axes.unicode_minus"] = False

# Standard styling
ax.set_title("...", fontsize=13, fontweight="bold", color="#2C3E50")
ax.set_ylabel("...", fontsize=9, color="#666")
ax.grid(True, alpha=0.2, color="#CCC")
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
```

## 10. Outlier Audit After Import

After importing Excel data, always check min/max per year:

```sql
SELECT substr(日期,1,4) as yr,
       MIN(收盘), AVG(收盘), MAX(收盘), COUNT(*)
FROM price_history WHERE 品种='gold'
GROUP BY yr ORDER BY yr;
```

Gold should never dip below $1,000 (even COVID-era was $1,475 min).
If 2026 shows values ~$397-444, those are decimal-shifted Yahoo errors (~31 rows).

Same check for silver: should never go below $10 or above $115 (15-year history).
