---
name: macro-futures-pipeline
version: 1.3.0
description: |
  宏光期货研究数据流水线 — 自动采集Yahoo/FRED/CFTC/Tushare数据，
  生成5份周度研究报告（宏观/能源/贵金属/国际农业/中国农业），
  配图表、发QQ邮箱。部署在VPS（45.77.126.71）上24/7运行。
  数据全部真实可验证，无预测无建议。
triggers:
  - "生成宏观周报"
  - "生成能源周报"
  - "生成贵金属周报"
  - "生成农业周报"
  - "生成国际农业报告"
  - "生成中国农业报告"
  - "发送所有报告"
  - "跑报告"
  - "更新报告"
  - "macro report"
  - "energy report"
  - "metals report"
  - "agri report"
  - "补数据空缺"
  - "检查报告空缺"
  - "接入新数据源"
tools:
  - terminal
  - write_file
  - read_file
  - cronjob
mutating: true
---

# 宏光期货研究数据流水线

## Data-First 原则

所有数据必须真实可验证。不编造任何数据。每个数据标注日期和来源。
英文指标名全部使用中文（布伦特原油、亨利港、欧佩克+、COT指数、Z分数）。
无预测、无交易建议、无多空观点。

## 数据空缺填补流程（2026-06-13 重构）

当用户要求补数据时，按以下流程操作：

### Step 1: 扫描所有报告的空缺
```bash
ssh -p 58234 -i C:\\Users\\Administrator\\.ssh\\id_rsa root@45.77.126.71 '
cd /root/hermes-macro-data/reports
for f in macro_weekly energy_weekly metals_weekly agri_global agri_china; do
  echo "=== $f ==="
  grep -n "—\|待更新\|待接入\|无数据\|数据待" ${f}_*.md 2>/dev/null | head -15
done
'
```

### Step 2: 对每个空缺，尝试数据源（按优先级）
1. **已有API的**（FRED/EIA/Yahoo/Tushare）→ 改采集脚本加新系列
2. **免费API**（Open-Meteo天气）→ 直接requests，无需Key
3. **CSV/Excel文件下载** → 政府/交易所官网提供CSV/Excel的，直接用文件对接，比爬虫稳定
4. **Scrapling爬公开网页**（Fetcher/StealthyFetcher）
5. **curl绕过Cloudflare**（比requests更可能通过）
6. **标记无法获取** → 留占位符，告知用户原因

**⚠️ 新增数据源必须先查官方文档确认参数，不猜。**

### Step 3: 部署后必须跑两遍
第一次部署后数据可能仍显示"待更新"（缓存）。
```bash
export HERMES_HOME=/root/hermes-pipeline
rm -f /root/hermes-macro-data/reports/*_$(date +%Y-%m-%d).md
python3 run_report.py <类型>
```
注意：`HERMES_HOME` 环境变量必须在运行前 export，否则 .env 加载不到密钥。

### Step 4: 验证填充效果
```bash
grep -E "原油库存|战略石油|优良率|降水" <报告文件>
```

## 🔴 CRITICAL: 环境变量

**VPS上必须执行 `export HERMES_HOME=/root/hermes-pipeline` 才能正确加载.env。**
否则 `load_dotenv()` 找不到密钥 → EIA/FRED/Tushare全部回退，报告所有数据变成"待更新"。

检查方法：
```bash
echo $HERMES_HOME   # 应为 /root/hermes-pipeline
```

已在 `/root/.bashrc` 和 `/etc/environment` 中写入，如果通过SSH交互登录会自动加载。
**通过cron运行的**也会加载 /etc/environment。
**但如果SSH后手动 `python3 xxx.py` 而不export**，就会读不到Key。务必注意。

## 🔴 CRITICAL: .env文件篡改陷阱

.env在VPS上通过echo/heredoc多次写入后会被截断——API Key变成`***`（3字符）。**症状：** 
- FRED返回400 "api_key is not a 32 character alpha-numeric lower-case string"
- MiMo返回401 "Invalid API Key"

**唯一安全修复方式：**
1. 在本地写干净.env文件
2. scp上传覆盖：`scp tmp_env root@vps:/root/hermes-pipeline/.env`
3. 绝不能通过SSH的echo/heredoc追加 .env 内容

**已发生的截断事件（备忘）：**
- FRED_API_KEY被截断到3字符 → 修复：Python write_file + scp上传
- XIAOMI_API_KEY被截断到3字符 → 修复：从/root/.hermes/.env复制正确Key
- EMAIL_PASS等邮箱配置丢失 → 修复：重新获取授权码+Python写入
- QQ_CLIENT_SECRET被截断 → 已从.env移除（由config.yaml管理）

## 🔴 本地Hermes cron陷阱

**Hermes cron必须gateway运行才能触发。** 本地Windows网关常关闭，本地cron绝不会执行。
所有定时任务必须部署到VPS系统cron（`/etc/cron.d/hermes-reports`），不依赖Hermes cron。

## 🔴 Cron语法：5个时间字段

**标准系统cron格式：** `分 时 日 月 星期`
- ✅ 正确：`30 8 * * *`（每天08:30）
- ❌ 错误：`0 30 8 * * *`（6个字段 → 语法错误 → 整个cron文件被忽略）

**症状：** `/var/log/syslog` 中 `Error: bad hour; while reading /etc/cron.d/hermes-reports`
**影响：** 一个字段数错误会导致整个配置文件的所有任务（11个）全部失效。

**修复：** `sed -i 's/0 30 8 \* \* \*/30 8 * * */' /etc/cron.d/hermes-reports`

## 🔴 不要重复cron（浪费钱！）

**Hermes本地cron 和 VPS系统cron 不能同时跑报告。** VPS系统cron已用Python脚本免费生成+发送，Hermes本地cron走LLM（每周烧$3-5 V4 Pro）是重复浪费。

症状：TokScale显示V4 Pro有使用量但没做复杂对话 → 立刻查 `hermes cron list` 并删除周报类任务。只保留数据采集cron（走DeepSeek Flash，便宜）。

## 报告成本结构

**周报完全不花模型钱。** `run_report.py` → Python脚本填数据→Markdown→发邮件，零LLM调用。V4 Flash / V4 Pro / MiMo 2.5 Pro只影响聊天质量，不影响报告。

## 接新数据源协议

1. **先查官方文档**确认正确系列ID/参数（不猜，不假设）
2. 本地测试确认数据结构
3. **CSV/Excel下载也是合法数据源**，不一定要走API/爬虫
4. 集成后全报告测试

**三类数据获取方式：API / 爬虫 / CSV文件下载**

## 数据填补流程（用户指令型任务）

**Step 0: 用户说"补数据"时，先扫描全部5份报告的空缺再列清单。**
不要只改用户提到的某一项而不看其他报告的整体空缺。

**关键陷阱：数据已被计算但不一定被显示**
最常见原因是代码中计算了变量但输出行仍硬编码为"—"。调试方法：
```python
# 错误（常见bug）:
lines.append(f"| 黄金现货 | ${price} | — | — | Alpha Vantage |")
# 正确:
lines.append(f"| 黄金现货 | ${price} | {wow} | {avg} | Alpha Vantage |")
```
诊断命令：搜索报告中"—"出现的位置，再检查对应代码行是否引用了计算变量。

```bash
ssh -p 58234 -i C:\\Users\\Administrator\\.ssh\\id_rsa root@45.77.126.71 '
cd /root/hermes-macro-data/reports
for f in macro_weekly energy_weekly metals_weekly agri_global agri_china; do
  echo "=== $f ==="
  grep -n "—\|待更新\|待接入\|无数据\|数据待" ${f}_*.md 2>/dev/null | head -20
  echo ""
done
'
```

**Step 1: 对每个空缺，尝试数据源（按优先级）**
1. **已有API直接加**（FRED/EIA/Yahoo/Tushare）→ 改采集脚本加新系列名
2. **免费开放API**（Open-Meteo天气、AKShare中国宏观）→ 无需Key，直接requests
3. **Scrapling爬公开网页**（Fetcher/StealthyFetcher）
4. **curl绕过Cloudflare**（Baker Hughes→curl可能通过而requests不行）
5. **都失败时** → 必须如实标注原因（如"Baker Hughes: curl TLS阻断"），不得编造数据

**Step 2: 改完代码后必须跑两遍**
第一遍可能读缓存CSV显示旧值。删掉报告文件再跑才是真正结果：
```bash
export HERMES_HOME=/root/hermes-pipeline
rm -f /root/hermes-macro-data/reports/*_$(date +%Y-%m-%d).md
python3 run_report.py <类型>
```

**Step 3: 验证**
直接远程查最新报告确认数据填入：
```bash
grep "原油库存\|大豆\|DR007" /root/hermes-macro-data/reports/*.md
```

## 修改规范（用户硬性要求）

任何时候修改代码都必须遵守：
1. **用 `patch` 做最小修改**，禁止整篇重写
2. **改完必须逐条列出改动**（增/删/改，格式：位置+改了什么+为什么）
3. **提示词模板（`prompts/` 目录）绝对不改**
4. **能源周报不修改**
5. **报告英文术语全部改用中文**（见下方术语映射表）

## 数据合规发布规则

See `references/data-compliance-rules.md` for green/yellow/red compliance classification:
- 🟢 API数据：可直接用
- 🟡 爬取数据：需转化后呈现（不贴原文）
- 🔴 付费数据：不可用

当生成可公开发布的内容时，必须遵守数据合规规则。

## 数据源可用性速查（2026-06-14 更新）

| 数据 | 数据源 | 方式 | 状态 |
|------|--------|------|------|
| 美债收益率 | FRED (DGS1/2/5/10/30) | API | ✅ 稳定 |
| 美元指数 | FRED (DTWEXBGS) | API | ✅ 稳定 |
| 欧元/美元/日元/人民币 | Yahoo (EURUSD=X/USDJPY=X/CNH=X) | API | ✅ 稳定 |
| VIX恐慌指数 | Yahoo (^VIX) | API | ✅ 稳定 |
| 黄金/白银期货 | Yahoo (GC=F/SI=F) | API | ✅ 稳定 |
| WTI/Brent/亨利港 | Yahoo (CL=F/BZ=F/NG=F) | API | ✅ 稳定 |
| 商业原油/SPR/库欣 | EIA API v2 | API | ✅ 实时 |
| 美国原油产量/炼厂开工率 | EIA API v2 | API | ✅ 实时 |
| 天然气库存 | EIA API v2 | API | ✅ 实时 |
| OPEC总石油供应 | EIA STEO (PAPR_OPEC) | API | ✅ 预测数据 |
| 美产区降水/温度 | Open-Meteo免费API | API | ✅ 无需Key |
| USDA优良率 | usda.library.cornell.edu PDF | pdfplumber | ✅ 稳定 |
| CFTC COT持仓 | cotdata.net | API | ✅ 稳定 |
| 中国期货(Tushare) | Tushare API | API | ✅ 仅工作日 |
| DR007/SHIBOR/LPR/存准率 | AKShare | 本地库 | ✅ 免费无需Key |
| 中国CPI/PPI/GDP/M2 | Tushare Pro (cn_cpi/cn_gdp/cn_ppi) | API | ✅ 需Token |
| 社会融资规模 | Tushare Pro sf_month | API | ✅ 已接入（需2000积分） |
| 新闻 | Finnhub | API | ✅ 稳定 |
| **Baker Hughes钻机数** | **AOGR网站静态HTML** | **requests+BS4** | **✅ 已接入（无Cloudflare）** |
| **BDI海运运价** | **TradingEconomics** | **requests+BS4** | **✅ 已接入（无需代理）** |
| **美湾粮食检验** | **USDA TXT文件** | **requests+正则** | **✅ 已接入（VPS有403）** |
| 美湾库存/南美库存/压榨率 | 无免费API | CSV下载 | ⏳ 待接入（需手动注册） |
| 油厂压榨率/生猪存栏 | 卓创/钢联 | — | ❌ 付费数据 |
### 数据源替代方案经验
当首选数据源失败时：
- **Baker Hughes**: rigcount.bakerhughes.com有Cloudflare → 改用**AOGR网站**(aogr.com)静态HTML，同一数据，无反爬
- **BDI**: investing.com有Cloudflare → 改用**TradingEconomics**(tradingeconomics.com/commodity/baltic)，无需代理
- **美湾粮食检验**: USDA AMS有403 → 改用**USDA TXT文件**(ams.usda.gov/mnreports/wa_gr101.txt)，直接正则解析
- **社融**: AKShare SSL握手失败 → 改用**Tushare sf_month**（需2000积分）
- **NOAA降水**: CPC网站404 → 改用**Open-Meteo**免费API
- FRED无Baker Hughes钻机系列
- Trading Economics guest账号已关停(410)
- Baker Hughes官网：requests被403，VPS上curl也被TLS阻断
- 同源数据也尝试EIA钻探生产率报告(DPR)路径→不通
- 最终无法获取的如实告知用户，提供原因

**用户提醒：CSV/Excel下载也是合法数据源，不一定要走API/爬虫。三类数据获取方式：API / 爬虫 / CSV文件下载。**

## 英文→中文术语映射

| 英文 | 中文 |
|------|------|
| Brent原油 | 布伦特原油 |
| Henry Hub | 亨利港 |
| SPR战略储备 | 战略石油储备(SPR) |
| OPEC+ | 欧佩克+ |
| OPEC MOMR | 欧佩克月报(MOMR) |
| COT Index | COT指数 |
| Z-Score | Z分数 |
| Baker Hughes | 贝克休斯 |
| LNG | 液化天然气(LNG) |
| Y/Y | 同比 |
| M/M | 环比 |
| WTI-Brent spread | 布伦特-WTI价差 |

## 环境

- **VPS**: 45.77.126.71:58234
- **SSH密钥**: `C:\Users\Administrator\.ssh\id_rsa`（**不是** id_ed25519）
- **SSH别名**: `ssh vps`（已配置在 ~/.ssh/config）
- **VPS时区**: Asia/Shanghai (UTC+8)（已从Etc/UTC修改）
- **项目目录**: /root/hermes-pipeline/（VPS），/c/Users/Administrator/hermes-macro-pipeline/（本地）
- **数据目录**: /root/hermes-macro-data/（VPS）
- **数据库**: /root/hermes-macro-data/hermes.db（SQLite） — 表结构见 `references/db-schema-hermes-db.md`
- **图表**: /root/hermes-macro-data/charts/（生成的PNG）
- **报告**: /root/hermes-macro-data/reports/
- **.env**: /root/hermes-pipeline/.env（VPS）← 易被截断，见CRITICAL节
- **config.yaml**: /root/hermes-pipeline/config.yaml（VPS，不是 /root/.hermes/config.yaml）
- **skills**: /root/hermes-pipeline/skills/（VPS，不是 /root/.hermes/skills/）
- **Gateway日志**: /root/hermes-pipeline/logs/gateway.log
- **系统cron**: /etc/cron.d/hermes-reports（VPS）
- ⚠️ **关键**: VPS上必须 export HERMES_HOME=/root/hermes-pipeline 才能正确加载.env
- **GitHub**: liuyuanlong3232-bit/macro-pipeline
- **邮箱**: 452731778@qq.com（发件+收件同一地址，SMTP QQ）
- **VPS Hermes**: v0.16.0 + MiMo 2.5 Pro，QQ Bot已连接

## 🔴 VPS vs 本地工作流

**VPS环境远优于本地（root权限，无中断，直连国际API，7×24在线）。**
代码修改全部在VPS上完成，本地只做同步和Git推送。

**修改流程：**
1. SSH到VPS → 在VPS上改代码
2. 本地scp同步：`scp root@vps:/root/hermes-pipeline/<file> <local_path>`
3. 本地git add/commit/push到GitHub
4. VPS上验证运行

**绝不：** 在本地Windows上改代码然后scp到VPS（本地权限/路径/代理经常出问题）

## 5份周报

| 报告 | 脚本 | cron时间（中国时间） | 数据源发布时间 | 图表 |
|------|------|----------|--------|------|
| 宏观 | macro_weekly.py | **周一09:00** | FRED每日更新 | FRED走势图 |
| 能源 | energy_weekly.py | **周四09:00** | EIA周三22:30发布→周三23:00采集 | COT净持仓+COT Index |
| 国际农业 | agri_weekly(global) | **周五09:00** | USDA周五发布 | 无图 |
| 中国农业 | agri_weekly(china) | **周五20:00** | Tushare收盘后 | 无图 |
| 贵金属 | metals_weekly.py | **周六09:00** | COT周五03:30发布→周五04:00采集 | 6张图 |

## 完整Cron Schedule（VPS `/etc/cron.d/hermes-reports`）

VPS时区已改为 **Asia/Shanghai (UTC+8)**，原为Etc/UTC。

### 每日任务
| 时间 | 任务 | 脚本 |
|------|------|------|
| **08:00** | FRED + Yahoo期货采集 | `macro_pipeline.py --source fred` + `--source yahoo` |
| **08:30** | 📧 每日数据速览发邮箱 | `scripts/daily_report.py` |
| 周二 06:00 | USDA数据过期检查 | `scripts/check_usda.py` |

### 周度定点采集
| 时间 | 数据源 | 脚本 |
|------|--------|------|
| **周三 23:00** | EIA能源（发布后30分钟） | `macro_pipeline.py --source eia` |
| **周五 04:00** | COT持仓（发布后30分钟） | `macro_pipeline.py --source cot` |

### 周报生成+发送
| 时间 | 报告 | 脚本 |
|------|------|------|
| 周一 09:00 | 宏观 | `run_report.py macro` |
| 周四 09:00 | 能源 | `run_report.py energy` |
| 周五 09:00 | 国际农业 | `run_report.py agri` |
| 周五 20:00 | 中国农业 | `run_report.py agri_cn` |
| 周六 09:00 | 贵金属 | `run_report.py metals` |
| 周日 10:00 | 资产配置 | `run_report.py allocation` |

### 数据源发布时间（北京时间）
| 数据源 | 发布时间 | 采集时间 |
|--------|---------|---------|
| FRED | 每日不定时 | 每日 08:00 |
| Yahoo期货 | 实时（交易日） | 每日 08:00 |
| EIA | 周三 22:30 | 周三 23:00 |
| COT | 周五 03:30 | 周五 04:00 |
| USDA | 周二 05:00/00:00 | 手动采集（VPS IP被屏蔽） |

## 数据时效性说明

**数据不是实时的。** 采集数据滞后1-2天（正常）：
- Yahoo期货：当日采集，显示前一日收盘价
- FRED宏观：每日更新，滞后1天
- EIA能源：周三发布，数据覆盖前一周
- COT持仓：周五发布，数据覆盖前周二

**monitor.py已移除。** 因为数据非实时，4小时检查无意义，报告已覆盖所有阈值判断。如需预警，直接看周报。

## QQ Bot配置（关键格式！）

**正确格式（已测试可通过）：**
```yaml
platforms:
  qq:                        # ❗ 注意是 qq 不是 qqbot
    enabled: true
    extra:
      app_id: "你的AppID"
      client_secret: "你...*   # ❗ 字段名是 client_secret 不是 secret
      markdown_support: true
      dm_policy: "open"
      group_policy: "open"
```

**错误格式（网关不识别）：**
```yaml
platforms:
  qqbot:              # ❌ 平台名应为 qq
    enabled: true
    secret: "..."     # ❌ 应为 client_secret
```

**环境变量：**
```bash
# .env 文件
QQ_APP_ID=你的AppID
QQ_CLIENT_SECRET=你...- **主动消息**：每月4条（给同一用户）
- **被动消息**：无限制（用户问，Bot答）
- **支持**：Markdown、图片、文件、语音

**注意事项：**
- 配置在 `/root/hermes-pipeline/config.yaml`（不是 `/root/.hermes/config.yaml`）
- 网关读的是 `HERMES_HOME` 指向的目录

### MiMo Token Plan消耗详解

**Credit不是1:1对应Token。** 不同模型有不同消耗倍数：
| 模型 | 上下文 | 消耗倍数 |
|------|-------|---------|
| MiMo-V2.5 | 256k | 1x（1 Token = 1 Credit） |
| MiMo-V2.5-Pro | 256k以内 | 2x |
| MiMo-V2.5-Pro | 256k~1M | 4x |

⚠️ `mimo-v2.5-pro` 的1M上下文意味着复杂长对话可能按4x计费，**而非按2x**。这意味着同样的token消耗，Credit消耗可能是2倍。

**Lite套餐（¥39/月）：** 41亿Credits
- 按最坏4x算：约10亿tokens的等效量
- 以每天75万Token的典型使用量，41亿≈136天
- 缓存命中率约92%，实际消耗更低
- 实际上用户400万Token/天的消耗，41亿≈100天

**查看剩余：** https://platform.xiaomimimo.com → 控制台 → 套餐使用情况

**41亿Credits能用多久？** 以每天75万Token的典型使用量，按最坏4x算≈300万Credits/天，41亿≈136天。实际缓存命中率92%，实际消耗更低。

## 每日数据速览日报

`scripts/daily_report.py` — 每天早上08:30自动生成并发邮箱。

**模板来源：** `generate_report.py`（本地最早日报模板，195行）

**内容结构：**
```
📅 贵金属日报 | YYYY-MM-DD
📊 关键数据速览 — 黄金/白银/原油/VIX/美元/美债/TIPS/CPI/FOMC
🏛️ 宏观经济环境 — 13个FRED指标含日期
🥇 黄金分析 — 价格/TIPS逻辑/COT情绪/VIX恐慌
🥈 白银分析 — 价格/金银比/COT
📋 宏观一览表 — Markdown表格
```

**CRITICAL DB查询注意（见 references/db-schema-hermes-db.md）：**
- FRED: `WHERE 系列ID = ?` ← 不是 `WHERE 系列 = ?`
- Yahoo: `"日漲跌幅%"` ← 列名含%需引号包裹
- COT: `"COT Index(26W)"` ← 列名含括号需引号包裹
- 品種: COT用简体（`黄金`），Yahoo用繁体（`黃金`）

**Cron:** 每天08:30（数据采集08:00完成后）

⚠️ **数据采集→日报的数据流完整性：** `macro_pipeline.py` 的Yahoo采集只写CSV，不导入SQLite数据库。日报生成 (`daily_report.py`) 读的是SQLite。因此必须在 `daily_collect.py` 中同时做CSV→DB导入，否则日报会显示3天前的过期数据。详见 `references/yahoo-csv-db-gap.md`。

使用独立Y轴（不要共用Y轴），每张图一个指标：
```python
# charts.py 中的 chart_fred_trends() 已改为4张独立图
fred_fed_rate.png — 联邦基金利率
fred_cpi.png — 美国CPI
fred_10y.png — 10年国债收益率
fred_tips.png — 10年TIPS收益率
```

标准标注：左下角`tag_start()`起始值 + 右下角`tag_end()`最新值（白底框）。

## PNG长图附件（邮箱友好）

用户需要在邮箱里方便下载完整报告。`render_report.py` 使用 `wkhtmltoimage` 把 markdown+图表 渲染成1张PNG长图。

```bash
# 安装（VPS上）
apt-get install -y wkhtmltopdf  # 提供 wkhtmltoimage

# 生成PNG
python3 /root/hermes-pipeline/render_report.py /path/to/report.md macro
# 输出: /path/to/report_report.png
```

`send_email.py` 自动附加PNG长图到邮件（Content-Disposition: attachment）。

⚠️ **用户明确要求：报告要能以单张长图形式下载，不要分开多张图。**

## VPS上的Hermes

VPS已部署Hermes Agent v0.16.0 + MiMo 2.5 Pro，可用于辅助分析和修改报告。

### 连接方式
```bash
# SSH连接（用别名）
ssh vps

# 启动对话
hermes chat

# 直接问问题
hermes chat -q "分析本周黄金走势"
```

### QQ Bot（手机端，推荐）
用户手机无法使用Telegram（国内被墙，且Telegram注册需要会员才能收验证码）。
Hermes支持QQ Bot（官方API，安全不封号）。

**注册流程：**
1. 打开 https://q.qq.com
2. 扫码登录（用现有QQ号）
3. 创建机器人 → 获取 AppID + AppSecret
4. 配置到VPS Hermes

**限制：**
- 主动消息：每月4条（给同一用户）
- 被动消息：无限制（用户问，Bot答）
- 支持Markdown、图片、文件
- 结论：日常对话完全够用，定时报告用邮箱

**VPS部署要求：**
- 需要公网IP（已有：45.77.126.71）
- 需要配置IP白名单
- 可能需要域名+SSL证书（Webhook方式）

### 记忆同步
本地和VPS的Hermes是独立实例，聊天记录不互通。
但可以手动同步记忆文件：
```bash
# VPS → 本地
scp -P 58234 -i C:\Users\Administrator\.ssh\id_rsa \
  root@45.77.126.71:/root/.hermes/memories/*.md \
  /c/Users/Administrator/AppData/Local/hermes/memories/

# 本地 → VPS
scp -P 58234 -i C:\Users\Administrator\.ssh\id_rsa \
  /c/Users/Administrator/AppData/Local/hermes/memories/*.md \
  root@45.77.126.71:/root/.hermes/memories/
```

### 模型切换
- **命令行**：`/model` 然后选择模型
- **Hermes Desktop**：右下角点击切换
- **注意**：切换后需要新开会话才生效

### SOUL.md
VPS上 `/root/.hermes/SOUL.md` 定义了数据优先原则：
- 所有分析必须基于 /root/hermes-macro-data/csv/ 下的官方采集数据
- 不编造数据，没有数据支撑的结论标注"数据暂缺"
- LLM只负责分析和写文字

### 模型配置
当前默认：`xiaomi/mimo-v2.5-pro`（MiMo Token Plan Lite ¥39/月，41亿Credits）
备选：`deepseek/deepseek-v4-flash`（按量付费，日常聊天够用）

### .env位置
VPS上Hermes读的.env路径是 `/root/hermes-pipeline/.env`，不是 `/root/.hermes/.env`。
如果API Key报错Invalid，先检查这个路径。

### Token用量和成本
- **MiMo 2.5 Pro**: ¥39/月（41亿Credits），够用很久
- **DeepSeek V4 Flash**: $0.14/$0.28 per 1M tokens，日常聊天够用
- **周报生成**: 不花模型钱（Python脚本免费）
- **每日对话**: 按token计费，缓存命中率高时很便宜

## 操作指南

### 生成并发送单份报告
```bash
export HERMES_HOME=/root/hermes-pipeline
ssh -p 58234 -i C:\\Users\\Administrator\\.ssh\\id_rsa root@45.77.126.71 '
cd /root/hermes-pipeline
python3 run_report.py <类型>
'
```
类型: macro / energy / agri / agri_cn / metals

### 生成并发送全部报告
```bash
export HERMES_HOME=/root/hermes-pipeline
ssh -p 58234 -i C:\\Users\\Administrator\\.ssh\\id_rsa root@45.77.126.71 '
cd /root/hermes-pipeline
for rpt in macro energy agri agri_cn metals; do
  python3 run_report.py "$rpt"
done
'
```

### 本地修改→部署到VPS
```bash
# 1. 语法检查
python3 -c "import py_compile; py_compile.compile('文件名.py', doraise=True); print('OK')"

# 2. 上传
scp -P 58234 -i C:\\Users\\Administrator\\.ssh\\id_rsa <本地文件> root@45.77.126.71:/root/hermes-pipeline/<文件名>

# 3. 跑测试（注意要export HERMES_HOME）
export HERMES_HOME=/root/hermes-pipeline
ssh -p 58234 -i C:\\Users\\Administrator\\.ssh\\id_rsa root@45.77.126.71 'cd /root/hermes-pipeline && python3 run_report.py <类型>'
```

## 🔴 用户核心要求（绝对遵守）

### 1. 不要问我，自己做（核心要求）

**用户原话（2026-06-14 确认）：**
- "你是超级智能体，只有你不能干的时候再告诉我"
- "你怎么老让我干，你是超级智能体，只有你不能干的时候再告诉我，ok？"
- "我需要你，你是主力，ok，要展现出你全部的实力"

**行为准则：**
- ❌ 不要让用户去Vultr后台查状态
- ❌ 不要让用户去改SSH配置
- ❌ 不要让用户去检查.env
- ❌ 不要让用户去测试连接
- ✅ 我自己查、自己改、自己修、自己测试、自己验证

**例外情况（只有这些才问用户）：**
- 需要用户提供API Key/密码（我无法获取）
- 需要用户做Vultr控制台操作（我无法访问）
- 需要用户确认商业决策（如付费购买）

**主动行为示例：**
- 用户说"VPS连不上" → 我自己ping、SSH、检查端口、排查防火墙
- 用户说"报告有空缺" → 我自己扫描所有报告、找数据源、填数据、测试
- 用户说"配置QQ Bot" → 我自己查文档、写配置、测试连接、启动网关
- 用户说"代码有问题" → 我自己读代码、找bug、修复、部署、验证

### 2. 独立思考，主动解决
当用户指出问题时，不要只修他提到的那一点。要主动思考：
1. 这个问题还有哪些相关联的地方需要一起修？
2. 有没有更好的方案我应该主动提出？
3. 用户真正想要什么效果？（而不是他具体说了什么）

**示例：** 用户说"图上5个指标放一起了，选3-4个核心的做图"→ 不要只删一个指标，要主动拆成独立图，并检查其他报告是否也有同样问题。

**示例：** 用户说"报告在邮箱里下载不方便"→ 主动想到把整个报告渲染成1张PNG长图附件，而不是等用户说"你能不能把报告生成一张图"。

**示例：** 用户说"QQ Bot配置有问题"→ 主动查文档、检查config.yaml格式、检查.env文件、检查环境变量冲突、测试连接，而不是让用户一个个排查。

**示例：** 用户说"VPS连不上"→ 主动ping、SSH、检查端口、检查防火墙、检查SSH密钥，而不是让用户去Vultr后台。

### 3. 混合模式：数据优先，LLM辅助
**用户要求：** 每日数据采集用固定Python脚本（不调LLM），周报生成用数据+LLM混合，深度分析用LLM+官方数据。

**核心原则：** 数据永远来自我们采集的官方数据，LLM只负责分析和写文字，不编造数据。

### 4. 用词严谨
用户要求命名严谨、用标准市场名称。英文术语全部中文化：
- Brent → 布伦特
- Henry Hub → 亨利港
- OPEC+ → 欧佩克+
- COT Index → COT指数
- Z-Score → Z分数
- Baker Hughes → 贝克休斯

## 模型配置

当前默认：`xiaomi/mimo-v2.5-pro`（MiMo Token Plan Lite ¥39/月，41亿Credits）
备选：`deepseek/deepseek-v4-flash`（按量付费，日常聊天够用）
切换命令见 `references/mimo-token-plan.md`

### 模型对比（2026-06-14 更新）

| 模型 | Input价格 | Output价格 | 聪明程度 | 适合场景 |
|------|----------|-----------|---------|---------|
| MiMo 2.5 Pro | $0.435/M | $0.87/M | 86分 | 深度分析、写报告、复杂推理 |
| DeepSeek V4 Flash | $0.14/M | $0.28/M | 57分 | 日常聊天、简单查询、数据采集 |
| DeepSeek V4 Pro | $0.435/M | $0.87/M | 51分 | ❌ 不推荐（同价但比MiMo弱） |

**MiMo 2.5 Pro 和 DeepSeek V4 Pro 同价，但MiMo更聪明（86 vs 51分）。**
**周报生成不花模型钱（Python脚本免费），模型只影响聊天质量。**

## ⚠️ 新会话才生效

模型切换后需要**新开会话**，当前会话不会变。这是 Hermes 的设计：会话启动时读一次模型配置，中途不改。

## 源代码文件说明

| 文件 | 功能 | 注意事项 |
|------|------|----------|
| macro_pipeline.py | 主数据采集（FRED+Yahoo+CFTC+News+EIA+OPEC） | 1000+行，15+数据源 |
| macro_weekly.py | 宏观周报生成器 | 读fred_indicators+yahoo_futures |
| energy_weekly.py | 能源周报生成器 | 内置fetch_eia_energy()实时拉EIA |
| metals_weekly.py | 贵金属周报生成器 | 有week_stats()计算周均价/环比；Yahoo实时不读过期CSV |
| agri_weekly.py | 全球+中国农业周报生成器 | global_agri()+china_agri()双函数；引用data_scrapers |
| charts.py | 图表生成（8个） | 读SQLite hermes.db |
| send_email.py | 邮件发送（HTML表格+图表） | QQ SMTP，base64嵌入图片 |
| run_report.py | 统一报告入口 | 按类型选择脚本+图表+发送 |
| scripts/daily_report.py | 日报生成器 | 每天早上08:30，读hermes.db生成贵金属日报并发邮箱 |
| scripts/check_usda.py | USDA数据过期检查 | 周二06:00检查，>3天未更新则提醒手动采集 |
| data_scrapers.py | 联合爬虫模块 | Baker Hughes(保留)/USDA PDF/BDI/Open-Meteo/NOAA |
| opec_data.py | OPEC数据采集模块 | EIA STEO主+Scrapling备 |
| render_report.py | PNG长图渲染 | wkhtmltoimage，邮箱附件 |
| prompts/ | 4份固定提示词模板 | **不可修改** |
| monitor.py | COT极端报警（已移除：数据非实时，无意义） | 不需要 |
| references/eia-api-endpoints.md | EIA API v2各端点速查+参数示例 | 能源报告数据采集参考 |
| references/open-meteo-api.md | Open-Meteo免费天气API+美农产区坐标 | 国际农业降水数据参考 |
| references/akshare-api.md | AKShare中国宏观数据函数速查 | DR007/SHIBOR/LPR等利率数据 |
| references/usda-crop-pdf.md | USDA Crop Progress PDF解析方法 | 玉米大豆优良率提取 |
| references/baker-hughes-debug.md | Baker Hughes钻机数调试记录 | 为什么不可用+替代方案 |
| references/change-log-format.md | 修改记录格式规范 | 每次改代码后必须遵守 |
| references/qq-bot-setup.md | QQ Bot配置指南 | 手机端交互方案 |
| references/vps-timezone-cron.md | VPS时区设置和中国时间cron配置 | 数据采集时间优化 |
| references/vps-config-pitfalls.md | VPS配置陷阱汇总（SSH/HERMES_HOME/时区/skills目录） | 避免常见错误 |
| references/qq-bot-config-format.md | QQ Bot正确配置格式和常见错误 | 网关配置参考 |
| references/vps-config-pitfalls.md | VPS配置陷阱汇总 | SSH密钥/路径/环境变量问题 |

## Python Scrapling 抓取语法
```python
from scrapling import Fetcher
f = Fetcher()
resp = f.get("https://example.com",
    proxies={"http": "http://127.0.0.1:10808", "https": "http://127.0.0.1:10808"})
# 取文本
resp.css("选择器").first.text
# 取全部
resp.css("选择器").getall()
# 取属性
resp.css("选择器::attr(href)").getall()
```

从Fetcher切换到StealthyFetcher绕过Cloudflare：
```python
from scrapling.fetchers import StealthyFetcher
page = StealthyFetcher.fetch("https://example.com",
    headless=True, solve_cloudflare=True, block_webrtc=True, hide_canvas=True)
```

## 注意事项

1. **提示词模板不可修改** — 位于 `prompts/` 目录，固定格式
2. **每次修改先列出改动清单** — 改了什么逐条告知用户
3. **数据验证三保险** — safe_price范围校验+Yahoo实时不读过期CSV+报告自动核验
4. **Tushare仅工作日有数据** — 周末返回"未获取"
5. **Alpha Vantage已完全移除** — 所有价格走Yahoo实时
6. **DXY用Yahoo** — 代码 `DX-Y.NYB`，非FRED贸易加权指数

## 报告空白审计流程

当用户反馈"报告很多空白"时：
1. SSH到VPS，在reports目录下 `grep -c "—" 各报告.md` 统计空白数
2. 排除表格分隔线（`grep -v "\|---"`）后的真实空白
3. 逐项分析：有API没接入？有爬虫没跑通？无免费数据源？
4. 能补的立即补，不能补的明确告知原因
5. 修复后重新生成全部5份报告+发送邮件

## 数据源爬取文件

- `data_scrapers.py` — 4个爬虫函数(USDA优良率/BDI/Baker Hughes/Open-Meteo)
- `opec_data.py` — OPEC数据(EIA STEO主+Scrapling备)
- 详见 `references/data-sources.md` 和 `references/scraper-techniques.md`
7. **VPS.env加载** — 必须 export HERMES_HOME=/root/hermes-pipeline，否则读不到
8. **改完跑两遍** — 第一遍可能读旧缓存，rm旧报告再跑才是真结果
9. **报告英文全改中文** — 见上方术语映射表
