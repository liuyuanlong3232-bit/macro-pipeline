# Chart Generation for Weekly Reports

## Matplotlib Setup (VPS)

```python
import matplotlib
matplotlib.use("Agg")  # Required for headless (VPS)
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# Chinese font
zh_fonts = [f.name for f in fm.fontManager.ttflist if "Noto Sans CJK" in f.name]
zh = zh_fonts[0] if zh_fonts else "DejaVu Sans"
plt.rcParams["font.family"] = zh
plt.rcParams["axes.unicode_minus"] = False
```

## Style Utilities

```python
C = {
    "gold": "#E67E22", "silver": "#7F8C8D", "red": "#E74C3C",
    "green": "#27AE60", "blue": "#2980B9", "purple": "#8E44AD",
    "orange": "#F39C12", "dark": "#2C3E50", "gray": "#95A5A6",
}

def clean_spines(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#DDD")
    ax.spines["bottom"].set_color("#DDD")

def setup_grid(ax):
    ax.grid(True, alpha=0.2, color="#CCC")
    ax.set_axisbelow(True)
```

## Labeling Convention

```python
# Start value: bottom-left, gray
def tag_start(ax, x, y, txt):
    ax.text(x, y, txt, fontsize=9, ha="left", va="bottom",
            color="#7F8C8D")

# End value: upper-right, bold, white background box
def tag_end(ax, x, y, txt, color="#2C3E50"):
    ax.text(x, y, txt, fontsize=11, ha="right", va="top",
            color=color, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor=color, alpha=0.85))
```

## Data Cleaning

```python
# Gold outlier filter
cleaned = [(date, float(close)) for date, close in rows
           if 1000 < float(close) < 6000]
# Silver outlier filter
cleaned = [(date, float(close)) for date, close in rows
           if 5 < float(close) < 200]
```

## Chart Inventory

| Chart | Function | File Pattern | Source Table | Query Filter |
|-------|----------|-------------|-------------|-------------|
| FRED Trends | chart_fred_trends() | fred_trends.png | macro_history | indicator IN (联邦基金利率,美国CPI,...) ORDER BY date DESC LIMIT 1100 |
| Gold Price | chart_gold_price() | gold_price.png | price_history | variety='gold', 1000<close<6000, spans 15yr+3yr+1yr subplots |
| Silver Price | chart_silver_price() | silver_price.png | price_history | variety='silver', 5<close<200, with 50/200MA |
| Gold-Silver Ratio | chart_gold_silver_ratio() | gold_silver_ratio.png | price_history | gold close / silver close, merged by date |
| COT Net Positions | chart_cot_net() | cot_net.png | cotdata | current snapshot, bar chart |
| COT Index | chart_cot_index() | cot_index.png | cotdata | current snapshot, bar chart with threshold zones |
| COT Long-Short | chart_cot_long_short() | cot_long_short.png | cotdata | current snapshot, grouped bar chart |
| COT Net History | chart_cot_net_history() | cot_net_history.png | cot_history | commodity='gold', noncomm_net time series |

## Email Embedding

Charts are base64-encoded and embedded inline in HTML email:

```python
def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()
```

Each report type controls which charts it includes via `chart_type` parameter passed to `send_report()`:
- `macro` → fred_trends.png only
- `metals` → gold_price, silver_price, gold_silver_ratio, cot_net_history, cot_net, cot_index
- `energy` → cot_net, cot_index
- `agri` / `agri_cn` → none
