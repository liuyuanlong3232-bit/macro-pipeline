# hermes.db 数据库表结构速查

## yahoo_futures (Yahoo期货行情)
| 列名 | 类型 | 示例 |
|------|------|------|
| 來源 | TEXT | "Yahoo Finance" |
| 品種 | TEXT | "COMEX黃金期貨" ← 繁体 |
| 代碼 | TEXT | "GC=F" |
| 日期 | TEXT | "2026-06-12" |
| 最新價 | REAL | 4212.1 |
| 前收盤 | REAL | 4335.9 |
| 日變化 | REAL | -123.8 |
| 日漲跌幅% | REAL | -2.855 ← 列名含%！用引号包裹 |
| 5日最高 | REAL | — |
| 5日最低 | REAL | — |
| 抓取日 | TEXT | — |

**查询关键列：** `最新價`, `"日漲跌幅%"`（必须双引号包围因为含%）

## fred_indicators (FRED宏观指标)
| 列名 | 类型 | 示例 |
|------|------|------|
| 日期 | TEXT | "2026-05-01" |
| 指標 | TEXT | "聯邦基金利率" ← 繁体 |
| 系列ID | TEXT | "FEDFUNDS" ← 用这个查！不是"系列" |
| 數值 | REAL | 3.63 |
| 抓取日 | TEXT | "2026-06-12" |

**查询模式：** `WHERE 系列ID = ?` ← 不是 `WHERE 系列 = ?`

## cotdata (CFTC COT持仓)
| 列名 | 类型 | 示例 |
|------|------|------|
| 來源 | TEXT | "cotdata.net" |
| 品種 | TEXT | "黄金" ← 简体！ |
| 交易所 | TEXT | "COMEX" |
| 報告日期 | TEXT | "2026-06-02" |
| 投機淨持倉 | INTEGER | 176020 |
| COT Index(26W) | REAL | 100.0 ← 特殊列名，用双引号 |
| Z-Score | REAL | 1.73 |
| 抓取日 | TEXT | — |

**查询模式：** `SELECT "COT Index(26W)" FROM cotdata WHERE 品種 LIKE ?`
**注意：** 品種是简体 `黄金` / `白银`，不是繁体 `黃金` / `白銀`

## 关键陷阱
1. ⚠️ FRED列名是 `系列ID` 不是 `系列`
2. ⚠️ Yahoo列 `日漲跌幅%` 含特殊字符，SQL中必须 `"日漲跌幅%"` 包裹
3. ⚠️ COT列 `COT Index(26W)` 含括号，SQL中必须 `"COT Index(26W)"` 包裹
4. ⚠️ COT数据用简体中文品種名（`黄金`），Yahoo用繁体（`黃金`）
5. ⚠️ DGS5 可能为空（FRED 5Y国债系列在DB中无数据），用DGS10兜底
