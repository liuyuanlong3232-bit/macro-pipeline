# QQ Mail Mobile Legibility — Table Formatting

## Problem

QQ Mail's mobile HTML renderer makes `|` pipe characters in markdown tables VISIBLE. An email like:

```
黄金 | $4212 | +0.3%  →  renders as "黄金 | $4212 | +0.3%" with literal pipes
```

Also, separator rows `|------|------|------|` render as visible garbage lines on mobile.

## Fix History (Iterated 3 Times)

### v1 — Table rows only (BROKEN)
Only handled `| `-prefixed table rows. Missed edge cases: table rows without trailing space, inline pipes in non-table text, mixed markdown formats.

### v2 — Strip pipes to Chinese full-width spaces (REJECTED)

The user agreed for one iteration but came back and rejected it. The stripped-pipe approach loses table structure.

### v3 — Full HTML `<table>` with separator stripping (CORRECT — FINAL 2026-06-13)

The user explicitly said "数据应该生成表格". Final approach:

```python
# Step 1: Intercept separator rows FIRST, before any table detection
stripped_no_pipe = stripped.replace("|", "").replace("-", "").replace(":", "").strip()
if not stripped_no_pipe and "|" in stripped:
    continue  # pure separator like |------|------| — skip silently

# Step 2: Check if this line is a table row
is_table_row = False
if "|" in stripped:
    cells_raw = [c.strip() for c in stripped.split("|")]
    real_cells = [c for c in cells_raw if c.strip() and not set(c.strip()) <= set("-: ")]
    if len(real_cells) >= 2:
        is_table_row = True

# Step 3: Extract cells — handle both formats
cells = [c.strip() for c in stripped.split("|")]
if stripped.startswith("|") and stripped.endswith("|"):
    cells = cells[1:-1]  # Format A: strip leading/trailing empties
cells = [c for c in cells if c.strip()]

# Step 4: Accumulate, then flush as <table>
def flush_table():
    html = '<table style="border-collapse:collapse;width:100%;margin:10px 0;font-size:12px;">'
    for is_header, cell_list in table_rows:
        tag = "th" if is_header else "td"
        bg = "#f8f9fa" if is_header else "#fff"
        fw = "bold" if is_header else "normal"
        row = "<tr>"
        for c in cell_list:
            row += f'<{tag} style="border:1px solid #ddd;padding:6px 8px;background:{bg};font-weight:{fw};text-align:center;">{c}</{tag}>'
        row += "</tr>\n"
        html += row
    html += "</table>"
    return html
```

### Key Rules

1. **Always strip separator rows first** — before any table detection
2. **Handle both formats** — with and without leading `|`
3. **Render as HTML `<table>`** — the user wants visible tabular structure
4. **Charts supplement but do NOT replace tables** — the user rejected removing tables when charts are present