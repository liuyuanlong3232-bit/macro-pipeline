# 项目全局扫描报告
> 2026-06-16 11:30

---

## 一、文件结构总览

### 1. 本地 `D:\hermes\pipeline\`

```
D:\hermes\pipeline\
├── shared/                        ← 🔄 Git同步
│   ├── __init__.py                ← 包初始化
│   ├── utils.py                   ← ⭐ 公共工具(load_csv/fetch_fedwatch/yahoo_quote)
│   ├── agri-data-plan-complete.md ← 农业全案(含产品孵化)
│   ├── database-architecture.md   ← 数据库架构文档
│   ├── knowledge/                 ← 14个文件(5板块)
│   │   ├── README.md + 模板.md + 待补清单.md
│   │   ├── 宏观/  贵金属/  能源/  农业/  天气/  (各含数据字典+分析框架)
│   └── memories/                  ← LOCAL_MEMORY.md + VPS_MEMORY.md
│
├── scripts/                       ← 🟢 活跃脚本(日报链路)
│   ├── daily_collect.py           ← 08:00 FRED+Yahoo采集
│   ├── daily_report.py            ← 08:30 日报生成+邮件
│   ├── fetch_cn_weather.py        ← 08:03 和风天气9城
│   ├── fetch_cn_futures.py        ← 08:04 Tushare中国期货
│   ├── fetch_weather.py           ← 08:05 Open-Meteo全球天气
│   ├── quality_check.py           ← 08:10 数据质检
│   ├── weekly_summary.py          ← 周五16:00周报摘要
│   ├── fix_eia_collect.py         ← 周三23:00 EIA库存
│   ├── import_history.py          ← 历史Excel导入(一次性)
│   ├── sync_memory.py + .bat      ← 记忆同步
│   └── usda_sync.bat              ← USDA同步
│
├── memories/                      ← LOCAL_MEMORY.md
├── prompts/                       ← 4个提示词模板(不改)
├── CODE_REVIEW_FIXES.md           ← 安全修复说明文档
│
├── macro_pipeline.py              ← 🟡 核心采集引擎(含16个数据源函数)
├── send_email.py                  ← 🟡 邮件发送模块
├── monitor.py                     ← 🟡 价格预警(2h周期)
│
├── 🟠 旧周报(已停用,保留备用)
│   ├── run_report.py              ← 旧周报调度器
│   ├── agri_weekly.py             ← 旧农业周报
│   ├── energy_weekly.py           ← 旧能源周报
│   ├── metals_weekly.py           ← 旧贵金属周报
│   └── macro_weekly.py            ← 旧宏观周报
│
├── 🟠 旧功能(已停用,保留备用)
│   ├── build_db.py                ← 旧建库脚本
│   ├── clean_data.py              ← 旧数据清洗
│   ├── data_scrapers.py           ← 旧爬虫模块
│   ├── charts.py                  ← 旧图表生成
│   ├── render_report.py           ← 旧报告渲染
│   ├── generate_report.py         ← 旧日报生成器
│   ├── ecb_config.py              ← ECB配置
│   ├── opec_data.py               ← OPEC数据
│   ├── create_repo.py             ← Git仓库创建
│   ├── save_gh.py                 ← GitHub保存
│   ├── write_keys.py              ← 密钥写入
│   └── verify_structure.py        ← 结构验证
│
└── 🔴 调试/test文件(开发残留,约89个)
    ├── check_*.py (8个)           ← 旧检查脚本
    ├── debug_*.py (5个)           ← 旧调试脚本
    ├── test_*.py (19个)           ← 旧测试脚本
    ├── _test_*.py (14个)          ← 带下划线旧测试
    ├── _debug_*.py (5个)          ← 带下划线旧调试
    ├── _check_*.py (4个)          ← 带下划线旧检查
    ├── _vps_*.py (6个)            ← VPS调试脚本
    └── _bh_*.py (1个)             ← 旧爬虫调试
```

### 2. VPS `/root/hermes-pipeline/`

```
/root/hermes-pipeline/
├── scripts/                       ← 🟢 活跃脚本(比本地多7个)
│   ├── (本地有的12个全部有)
│   ├── check_usda.py              ← VPS独有: USDA检查
│   ├── import_memory.py           ← VPS独有: Git记忆导入
│   ├── import_usda.py             ← VPS独有: USDA数据导入
│   ├── import_yahoo.py            ← VPS独有: Yahoo数据导入
│   ├── reminder_monthly.py        ← VPS独有: 月度提醒
│   ├── reminder_weather.py        ← VPS独有: 天气提醒
│   ├── reminder_weekly.py         ← VPS独有: 知识库周检
│   ├── sync_shared.py             ← VPS独有: shared同步
│   └── vps_memory_push.py         ← VPS独有: 记忆推GitHub
│
├── config.yaml                    ← VPS Hermes配置(已停用)
├── .env                           ← API密钥
└── (根目录文件同本地,含89个调试文件)
```

### 3. VPS 数据 `/root/hermes-macro-data/`

```
/root/hermes-macro-data/
├── hermes.db                      ← 🟢 23MB SQLite(100+表/15万行)
├── hermes.db.bak                  ← 备份
├── alert_log.json                 ← 预警日志
├── reports/                       ← 🟢 报告输出
│   ├── daily_2026-06-15.md        ← 最新日报
│   ├── daily_2026-06-16.md
│   ├── daily_snapshot_2026-06-15.md
│   ├── macro_weekly_*.md (3个)    ← 旧宏观周报(已停)
│   ├── metals_weekly_*.md (3个)   ← 旧贵金属周报(已停)
│   ├── energy_weekly_*.md (3个)   ← 旧能源周报(已停)
│   ├── agri_global_*.md (3个)     ← 旧国际农业周报(已停)
│   └── agri_china_*.md (3个)      ← 旧中国农业周报(已停)
├── signals/                       ← 🟢 每日信号(周报用)
├── csv/                           ← 🟢 每日原始CSV
├── charts/                        ← 🟢 图表PNG
├── history/                       ← 旧Excel备份
├── logs/                          ← 日志
└── meta/                          ← 元数据
```

---

## 二、文件用途分类

### 🟢 活跃(每日/每周在跑)

| 文件 | 用途 | 调度 |
|------|------|------|
| scripts/daily_collect.py | FRED+Yahoo采集入库 | cron 08:00 |
| scripts/fetch_cn_weather.py | 和风天气9城 | cron 08:03 |
| scripts/fetch_cn_futures.py | Tushare中国期货 | cron 08:04 |
| scripts/fetch_weather.py | Open-Meteo全球天气 | cron 08:05 |
| scripts/quality_check.py | 数据质检 | cron 08:10 |
| scripts/daily_report.py | 日报生成+发邮件 | cron 08:30 |
| scripts/weekly_summary.py | 周报摘要 | cron 周五16:00 |
| macro_pipeline.py | 核心采集引擎 | daily_collect调用 |
| send_email.py | 邮件发送 | daily_report调用 |
| monitor.py | 价格预警 | cron 每2h |

### 🟡 间歇性(特定时间)

| 文件 | 用途 | 调度 |
|------|------|------|
| scripts/fix_eia_collect.py | EIA库存采集 | cron 周三23:00 |
| scripts/vps_memory_push.py | 记忆推GitHub | cron 每天04:00 |
| scripts/import_memory.py | 记忆从GitHub导入 | cron 每天05:00 |
| scripts/reminder_weekly.py | 知识库自检提醒 | cron 周日20:00 |
| scripts/reminder_monthly.py | 月度里程碑检查 | cron 每月15日 |
| scripts/reminder_weather.py | 天气启动提醒 | cron 周三/周五10:00 |
| scripts/check_usda.py | USDA过期检查 | cron 周二06:00 |
| scripts/import_usda.py | USDA数据导入 | 手动 |
| scripts/import_yahoo.py | Yahoo数据导入 | 手动 |
| scripts/sync_shared.py | shared目录同步 | 手动 |
| scripts/import_history.py | 历史Excel导入 | 一次性 |

### 🟠 旧功能(已停用，保留备用)

| 文件 | 原用途 | 替代品 |
|------|--------|--------|
| run_report.py | 周报调度器 | weekly_summary.py |
| agri_weekly.py | 农业周报 | weekly_summary.py |
| energy_weekly.py | 能源周报 | weekly_summary.py |
| metals_weekly.py | 贵金属周报 | weekly_summary.py |
| macro_weekly.py | 宏观周报 | weekly_summary.py |
| build_db.py | 建库脚本 | 一次性用过 |
| clean_data.py | 数据清洗 | 一次性用过 |
| data_scrapers.py | 旧爬虫 | macro_pipeline替代 |
| charts.py | 旧图表 | daily_report内嵌 |
| render_report.py | 旧报告渲染 | daily_report直接出 |
| generate_report.py | 旧日报生成 | daily_report替代 |

### 🔴 调试/test文件(开发残留)

| 前缀 | 数量 | 用途 |
|------|------|------|
| `_test_*` | 14个 | 旧测试(带下划线) |
| `test_*` | 19个 | 旧测试 |
| `_debug_*` | 5个 | 旧调试(带下划线) |
| `debug_*` | 5个 | 旧调试 |
| `_check_*` | 4个 | 旧检查(带下划线) |
| `check_*` | 8个 | 旧检查 |
| `_vps_*` | 6个 | VPS调试 |
| `_bh_*` | 1个 | 旧爬虫调试 |
| 其他 | 27个 | 杂项调试 |
| **合计** | **~89个** | **全部可清理** |

---

## 三、重复/冲突文件

### ⚠️ 重复文件(同一功能,两份拷贝)

| 功能 | 本地 | VPS | 状态 |
|------|------|-----|------|
| daily_collect.py | ✅ scripts/ | ✅ scripts/ | ✅ 同步,无冲突 |
| daily_report.py | ✅ scripts/ | ✅ scripts/ | ✅ 同步,无冲突 |
| send_email.py | ✅ 根目录 | ✅ 根目录 | ✅ 同步 |
| macro_pipeline.py | ✅ 根目录 | ✅ 根目录 | ✅ 同步 |
| agri_weekly.py | ✅ 根目录 | ✅ 根目录 | ⚠️ 两处都有,都停用 |
| energy_weekly.py | ✅ 根目录 | ✅ 根目录 | ⚠️ 两处都有,都停用 |
| metals_weekly.py | ✅ 根目录 | ✅ 根目录 | ⚠️ 两处都有,都停用 |
| macro_weekly.py | ✅ 根目录 | ✅ 根目录 | ⚠️ 两处都有,都停用 |
| import_history.py | ✅ scripts/ | ✅ scripts/ + 根目录 | ⚠️ 根目录也有一份 |
| build_db.py | ✅ 根目录 | ✅ 根目录 | ⚠️ 都停用 |
| clean_data.py | ✅ 根目录 | ✅ 根目录 | ⚠️ 都停用 |
| data_scrapers.py | ✅ 根目录 | ✅ 根目录 | ⚠️ 都停用 |
| charts.py | ✅ 根目录 | ✅ 根目录 | ⚠️ 都停用 |
| render_report.py | ✅ 根目录 | ✅ 根目录 | ⚠️ 都停用 |
| generate_report.py | ✅ 根目录 | ✅ 根目录 | ⚠️ 都停用 |
| monitor.py | ✅ 根目录 | ✅ 根目录 | ✅ 同步 |

### ⚠️ VPS独有文件(不在Git中)

| 文件 | 用途 | 需要同步吗 |
|------|------|-----------|
| check_usda.py | USDA检查 | 🔵 是(已加cron) |
| import_memory.py | 记忆导入 | 🔵 是(已加cron) |
| import_usda.py | USDA导入 | ⚪ 手动用 |
| import_yahoo.py | Yahoo导入 | ⚪ 手动用 |
| reminder_monthly.py | 月度提醒 | 🔵 是(已加cron) |
| reminder_weather.py | 天气提醒 | 🔵 是(已加cron) |
| reminder_weekly.py | 知识库自检 | 🔵 是(已加cron) |
| sync_shared.py | shared同步 | ⚪ 手动用 |
| vps_memory_push.py | 记忆推送 | 🔵 是(已加cron) |

### ⚠️ 潜在冲突

| 问题 | 位置 | 影响 |
|------|------|------|
| import_history.py 在两处 | scripts/ + 根目录 | 根目录那份未用 |
| build_db.py 在两处 | 根目录(本地+VPS) | 都停用,无影响 |
| cron.d 和 crontab 重复 | /etc/cron.d/hermes-reports + crontab | 双保险,无害 |
| weekly报告在reports/ | VPS reports/ 有旧周报文件 | 只是历史文件,不影响 |

---

## 四、清理建议(待执行)

### 可立即清理(89个调试文件)
```
根目录: _*.py, check_*.py, test_*.py, debug_*.py
scripts/: sync_memory.bat, usda_sync.bat (已被.py替代)
```

### 可保留但标注停用
```
run_report.py, agri_weekly.py, energy_weekly.py, metals_weekly.py, macro_weekly.py
build_db.py, clean_data.py, data_scrapers.py, charts.py, render_report.py, generate_report.py
```

### 建议同步到Git(VPS独有7个脚本)
```
check_usda.py, import_memory.py, reminder_monthly.py, reminder_weather.py, reminder_weekly.py, vps_memory_push.py, sync_shared.py
```
