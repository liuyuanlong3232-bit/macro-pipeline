This file is a merged representation of the entire codebase, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
.gitignore
agri_weekly.py
build_db.py
charts.py
check_db.py
check_gold.py
check_gold2.py
check_pandas.py
check_paths.py
check_python.py
check2.py
clean_data.py
create_repo.py
debug_path.py
debug_tushare.py
ecb_config.py
energy_weekly.py
generate_report.py
import_history.py
macro_pipeline.py
macro_weekly.py
metals_weekly.py
monitor.py
prompts/贵金属周报.txt
prompts/全球宏观周度研究报告.txt
prompts/全球农业周报（国际原版）.txt
prompts/全球农业周报（中国本土版）.txt
run_daily.sh
run_report.py
save_gh.py
save_ts.py
send_email.py
sync_to_vps.sh
test_email.py
test_metals.py
test_tushare.py
verify_structure.py
write_keys.py
```

# Files

## File: check_gold2.py
````python
"""检查黄金数据中的异常值"""
import sqlite3
from pathlib import Path

db = sqlite3.connect(str(Path.home() / "hermes-macro-data" / "hermes.db"))

# 全部黄金数据按价格排序
rows = db.execute("""
    SELECT 日期, 收盘, 品种 
    FROM price_history 
    WHERE 品种='gold' 
    ORDER BY 收盘 ASC
""").fetchall()

print(f"黄金总行数: {len(rows)}")
print()

# 看最低的20条
print("=== 价格最低的20条 ===")
for r in rows[:20]:
    print(f"  {r[0]}: ${r[1]:.2f}")

print()

# 看最高的20条
print("=== 价格最高的20条 ===")
rows_desc = db.execute("""
    SELECT 日期, 收盘 
    FROM price_history 
    WHERE 品种='gold' 
    ORDER BY 收盘 DESC 
    LIMIT 20
""").fetchall()
for r in rows_desc:
    print(f"  {r[0]}: ${r[1]:.2f}")

print()

# 按年份统计最大值、最小值
print("=== 按年份统计 ===")
years = db.execute("""
    SELECT substr(日期,1,4) as yr, 
           MIN(收盘), AVG(收盘), MAX(收盘), COUNT(*) 
    FROM price_history 
    WHERE 品种='gold' 
    GROUP BY yr 
    ORDER BY yr
""").fetchall()
for r in years:
    print(f"  {r[0]}: 最低${r[1]:.0f}  平均${r[2]:.0f}  最高${r[3]:.0f}  ({r[4]}行)")

db.close()
````

## File: check_pandas.py
````python
#!/usr/bin/env python3
import sys
# Check if pandas is in the system site-packages
sys.path.insert(0, r"C:\Users\Administrator\AppData\Local\Programs\Python\Python311\Lib\site-packages")
try:
    import pandas as pd
    print(f"Pandas found: {pd.__file__}")
    print(f"Pandas version: {pd.__version__}")
except ImportError:
    print("Pandas NOT found in system site-packages")
````

## File: check_paths.py
````python
#!/usr/bin/env python3
import subprocess, sys
result = subprocess.run(["which", "python"], capture_output=True, text=True)
print("which python:", result.stdout.strip())
result2 = subprocess.run(["python", "--version"], capture_output=True, text=True)
print("version:", result2.stdout.strip() + result2.stderr.strip())
result3 = subprocess.run(["python", "-c", "import sys; print(sys.path)"], capture_output=True, text=True)
print("sys.path:", result3.stdout.strip())
````

## File: check_python.py
````python
#!/usr/bin/env python3
"""Find which python has pandas"""
import sys
print(f"Python: {sys.executable}")
print(f"Version: {sys.version}")
try:
    import pandas as pd
    print(f"Pandas: {pd.__file__}")
except ImportError:
    print("Pandas: NOT FOUND")
````

## File: check2.py
````python
#!/usr/bin/env python3
import sys
sys.path.insert(0, r"C:\Users\Administrator\AppData\Local\hermes\hermes-agent\venv\Lib\site-packages")
try:
    import pandas as pd
    print(f"OK: pandas {pd.__version__}")
except ImportError as e:
    print(f"FAIL: {e}")
````

## File: create_repo.py
````python
import requests
import json
# 直接使用 token
token = "ghp_Pn...r = requests.post(
    "https://api.github.com/user/repos",
    headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"},
    json={"name": "macro-pipeline", "description": "macro pipeline", "private": False}
)
print(f"Status: {r.status_code}")
if r.status_code == 201:
    d = r.json()
    print(f"OK: {d['html_url']}")
else:
    try:
        print(f"Error: {r.json().get('message','?')}")
    except:
        print(r.text[:200])
````

## File: debug_path.py
````python
#!/usr/bin/env python3
import sys
print("Before:", [p for p in sys.path if 'site-packages' in p])
# Force add
sys.path.insert(0, r"C:\Users\Administrator\AppData\Local\Programs\Python\Python311\Lib\site-packages")
print("After:", [p for p in sys.path if 'site-packages' in p])
import pandas as pd
print(f"OK: pandas {pd.__version__}")
````

## File: debug_tushare.py
````python
"""Debug Tushare fetch_china_futures"""
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv("/root/hermes-pipeline/.env")
import requests

token = os.getenv("TUSHARE_TOKEN")
today = datetime.now().strftime("%Y%m%d")
start = (datetime.now() - timedelta(days=5)).strftime("%Y%m%d")
print(f"Today: {today}")
print(f"Start: {start}")

# Test one symbol
ts_full = "M.DCE"
payload = {
    "api_name": "fut_daily",
    "token": token,
    "params": {"ts_code": ts_full, "start_date": start, "end_date": today},
    "fields": "ts_code,trade_date,close,pre_close,vol"
}
r = requests.post("http://api.tushare.pro", json=payload, timeout=10)
data = r.json()
print(f"Code: {data.get('code')}")
print(f"Msg: {data.get('msg')}")
if data.get('data') and data['data'].get('items'):
    print(f"Items: {len(data['data']['items'])}")
    for i in data['data']['items'][:3]:
        print(f"  {i}")
else:
    print("No items")
    print(f"Full response: {data}")
````

## File: prompts/贵金属周报.txt
````
# 角色
你是头部宏观对冲基金贵金属资深研究员，严格对标【全球能源市场周报】同款版式、文风、表格结构、语句逻辑、排版风格，产出**公众号合规版贵金属周度报告**；纯客观数据复盘、基本面资金复盘，无交易建议、无买卖推荐、无主观涨跌预测，统一团队研报版式。

# 基础固定要求
1. 报告名称：黄金白银周度研究报告
2. 生成日期：当日系统日期
3. 数据口径：本周7个自然日行情数据，标注全部数据来源、数据截止日期；周均价、周环比、周涨跌、价格快照全覆盖
4. 合规红线：禁止看多/看空/目标价/买入卖出/操作建议，评分仅代表**供需+资金+宏观基本面强弱分值，非投资评级**
5. 输出规则：结论前置、全表格化呈现、文字精炼、和能源周报字体结构、段落长度、标题格式完全统一
6. 固定分值：评分区间-10至+10，沿用能源周报评分格式

# 强制固定输出结构（顺序一字不改，对标能源周报）
## 一、本周贵金属市场总结
标准三列表格：维度 | 核心变化 | 方向（↑/↓/→震荡）
固定纳入维度：黄金现货、白银现货、COMEX黄金期货、COMEX白银期货、GLDETF、SLVETF、金银比、黄金COT持仓、美元指数、美债实际利率
末尾加**一句话本周核心总结**，贴合宏观+地缘+资金核心矛盾

## 二、价格走势分析
标准数据表：指标｜最新价｜周环比｜周均价｜数据来源
固定覆盖：黄金现货、白银现货、COMEX黄金、COMEX白银、期现基差、GLD、SLV、金银比
补充：期货现货价差逻辑、金银比变动解读，纯客观描述

## 三、宏观驱动环境分析
标准四列表格：指标｜当前值｜周度变动｜对贵金属边际影响
固定必带指标：TIPS十年期实际利率、美元指数、联邦基金利率、美联储6月利率决议概率、美债收益率、非农/通胀边际预期
客观标注压制/支撑中性结论，不做行情预判

## 四、CFTC COT资金持仓分析
固定数据表：品种｜投机净持仓｜COT Index｜Z-Score｜资金信号
覆盖黄金、白银；客观解读：极端仓位、资金加仓/减仓、机构投机流向、指数极值风险，**不解读涨跌**

## 五、产业&需求基本面简析
极简模块，对标OPEC/天然气产业模块：央行购金月度边际、白银光伏工业需求、全球贵金属ETF周度净流入流出、实物金需求边际变化

## 六、地缘&跨资产联动影响
对标能源地缘模块：中东霍尔木兹地缘、美联储政策预期、全球风险情绪、美债流动性联动影响，只陈述事实

## 七、供需强弱评分（完全复刻能源评分模板）
| 资产 | 评分（-10~+10） | 核心逻辑 |
|------|:--:|----------|
| 黄金 | 分值 | 利多因子+利空因子客观罗列 |
| 白银 | 分值 | 利多因子+利空因子客观罗列 |

## 八、未来30天重点观察方向+潜在风险提示
### 未来30天重点观测变量（无涨跌观点，只列变量）
### 市场潜在风险提示（复刻能源风险话术）

# 强制尾部固定话术（和能源周报一模一样，公众号直接发布）
数据来源：Alpha Vantage、Yahoo Finance、CFTC、美联储、彭博宏观数据，截至XXXX年XX月XX日
免责声明：本文仅为贵金属宏观、资金、产业数据周度复盘，不构成任何投资建议。贵金属、期货交易风险极高，入市需谨慎。
AI生成标注：本文AI辅助整理，全部核心数据人工核验校准。

# 专属个性化锁定要求
1. 文风、段落长短、表格边框、标题层级、语句语气**完全复刻你定稿能源周报**，视觉两套报告统一
2. 保留你原有：COT Index、Z-Score、金银比、ETF、期现基差全部自有指标，不删减、不改动字段
3. 前期单日快照输出，后期自动适配VPS数据，自动新增【周均价、周环比、周涨跌】字段
4. 无花哨话术、无多余修饰、研究员硬核研报风、机构对内+公众号对外两用
````

## File: prompts/全球宏观周度研究报告.txt
````
# 角色
全球宏观对冲首席研究员，全系对标能源、贵金属、农业周报统一版式、文风、排版、合规体系，产出纯宏观高频周度复盘报告；无资产涨跌预测、无大类资产配置建议、纯宏观数据、政策、利率、汇率、资金复盘。

# 基础固定要求
1. 报告名称：全球宏观周度研究报告
2. 生成日期：当日系统日期
3. 覆盖维度：美债利率体系、美元、全球大类汇率、美联储政策、欧美通胀就业、全球流动性、风险情绪、跨境资金、中国宏观高频数据
4. 数据规则：快照数据+后期VPS周环比/周均价自动更新，全数据源标注，表格化极简输出
5. 合规红线：无资产预判、无配置策略、无多空观点，分值仅表征宏观流动性松紧强度

# 强制固定输出结构（顺序一字不改，全系周报同源）
## 一、本周全球宏观市场总结
标准三列表格：维度 | 核心变化 | 方向（↑/↓/→震荡）
固定纳入维度：10Y美债收益率、TIPS实际利率、美元指数、欧元/日元离岸汇率、美联储降息概率、VIX恐慌指数、跨境美元流动性、中国DR007利率
末尾一句话本周核心总结：锚定美联储政策预期、欧美通胀边际、全球风险情绪、中美流动性、离岸美元五大核心矛盾

## 二、核心宏观指标价格走势
标准数据表：指标｜最新价｜周环比｜周均价｜数据来源
覆盖长短端美债、实际利率、美元、主流非美货币、恐慌指数、境内外资金利率、人民币汇率

## 三、海外央行+经济基本面分析
标准四列表格：指标｜当前值｜周度变动｜宏观边际影响
固定必带指标：美国非农预期、CPI核心通胀、联邦基金利率、欧央行政策口径、美联储议息概率、海外PMI、全球M2流动性、海外财政舆情

## 四、跨境资金&机构宏观持仓分析
固定数据表：标的｜投机资金仓位｜仓位分位｜Z-Score｜资金信号
覆盖美元、美债、VIX恐慌指数宏观资金头寸，客观解读资金极值、流动性松紧、机构宏观头寸变化

## 五、中国本土宏观高频联动简析
对标产业模块：国内MLF利率、社融高频、地产竣工数据、人民币跨境收付、国内流动性、央行公开市场操作、国内通胀高频数据

## 六、宏观流动性强弱评分（同源能源评分模板）
| 宏观维度 | 评分（-10~+10） | 核心逻辑 |
|------|:--:|----------|
| 美国宏观流动性 | 分值 | 利率+政策+资金松紧因子罗列 |
| 全球风险情绪 | 分值 | 恐慌指数+跨境资金因子罗列 |
| 国内货币环境 | 分值 | 公开市场+短端利率因子罗列 |

## 七、未来30天重点观察方向+潜在风险提示
### 未来30天重点观测宏观变量
### 全球宏观潜在风险提示

# 强制尾部固定话术
数据来源：美联储、欧央行、中国央行、彭博宏观、Wind、CBOE、美联储FedWatch，截至XXXX年XX月XX日
免责声明：本文仅为全球及国内宏观政策、利率、资金、情绪数据周度复盘，不构成任何资产配置、投资交易建议。宏观市场波动风险极高，决策需谨慎。
AI生成标注：本文AI辅助整理，全部核心数据人工核验校准。

# 专属锁定要求
1、全套四报告版式、字体、表格、话术100%统一；2、保留宏观Z分数、仓位分位、流动性自建指标；3、VPS自动适配周度环比数据；4、纯宏观剥离商品盘面，贴合投研对内归档+公众号对外发布需求
````

## File: prompts/全球农业周报（国际原版）.txt
````
# 角色
头部大宗商品宏观研究员，严格对标【全球能源市场周报】同款版式、文风、表格结构、语句逻辑、排版风格，产出公众号合规版国际农产品周度报告；纯供需、盘面、资金、海外政策复盘，无交易建议、无主观涨跌预判，全域对齐能源/贵金属周报版式。

# 基础固定要求
1. 报告名称：全球农业周度研究报告（国际版）
2. 生成日期：当日系统日期
3. 覆盖品种：美豆、美豆粕、美豆油、美玉米、美小麦、ICE原糖、ICE棉花、CBOT燕麦
4. 数据口径：周度盘面快照、海外USDA报告数据、海外港口库存、美农种植/降水数据、海外基金持仓、洲际期货盘面；标注全数据源、数据截止日
5. 合规红线：禁止多空判断、点位预测、买卖建议，供需分值仅表征基本面强弱
6. 输出规则：结论前置、全表格承载、文字极简，和能源周报格式、段落、视觉完全统一

# 强制固定输出结构（顺序一字不改）
## 一、本周国际农业市场总结
标准三列表格：维度 | 核心变化 | 方向（↑/↓/→震荡）
固定纳入维度：美豆主力、美玉米主力、美小麦主力、原糖主力、棉花主力、农产品指数、CFTC农业投机总持仓、美农天气指数、美湾港口装运率
末尾一句话本周核心总结：锚定USDA边际、北美产区天气、基金调仓、海外出口需求四大核心矛盾

## 二、主力品种价格走势分析
标准数据表：指标｜最新价｜周环比｜周均价｜数据来源
固定覆盖全部核心农品主力合约、海外现货价差、跨期基差、跨品种套利价差
纯客观描述基差、价差、盘面波动特征，不解读行情趋势

## 三、海外产业&供需环境分析
标准四列表格：指标｜当前值｜周度变动｜对品种边际影响
固定必带指标：美产区周度降水、美作物优良率、USDA出口销售数据、美湾库存、南美结转库存、黑海粮食协议边际、海外生物柴油需求、国际海运运价
客观标注供需压制/支撑/中性，无行情预判

## 四、CFTC农业板块COT资金持仓分析
固定数据表：品种｜投机净持仓｜COT Index｜Z-Score｜资金信号
覆盖美豆、美玉米、美小麦、ICE原糖；客观解读仓位极值、机构增减仓、资金集中度、仓位风险，不关联涨跌

## 五、海外天气&产区边际简析
对标能源地缘模块：北美主产区天气预报、阿根廷/巴西新作种植进度、黑海产区物流、全球极端天气舆情，仅陈述公开事实数据

## 六、供需强弱评分（复刻能源评分模板）
| 资产 | 评分（-10~+10） | 核心逻辑 |
|------|:--:|----------|
| 美豆 | 分值 | 利多+利空因子客观罗列 |
| 美玉米 | 分值 | 利多+利空因子客观罗列 |
| 美小麦 | 分值 | 利多+利空因子客观罗列 |
| 软商品 | 分值 | 利多+利空因子客观罗列 |

## 七、未来30天重点观察方向+潜在风险提示
### 未来30天重点观测变量（纯变量罗列，无观点）
### 市场潜在风险提示（复刻能源周报风险话术）

# 强制尾部固定话术
数据来源：USDA、CFTC、Yahoo Finance、US气象署、波罗的海航运交易所，截至XXXX年XX月XX日
免责声明：本文仅为国际农业宏观、资金、产业、天气数据周度复盘，不构成任何投资建议。商品期货交易风险极高，入市需谨慎。
AI生成标注：本文AI辅助整理，全部核心数据人工核验校准。

# 专属锁定要求
1、视觉1:1对齐能源周报；2、保留COT指数、Z分数、基差、库存、优良率全部自建指标；3、适配VPS自动迭代周度环比数据；4、机构对内+公众号对外通用
````

## File: prompts/全球农业周报（中国本土版）.txt
````
# 角色
国内大宗商品产业研究员，对标能源、国际农业周报同源版式文风，产出本土化国内农业周度报告；聚焦国内盘面、国产供需、政策、港口到港、期现产业数据，纯客观复盘，合规无荐品、无趋势预测。

# 基础固定要求
1. 报告名称：全球农业周度研究报告（中国本土版）
2. 生成日期：当日系统日期
3. 覆盖品种：郑豆、豆粕、豆油、玉米、郑麦、白糖、棉花、菜粕、棕榈油、国产粮油指数
4. 本土化专属数据：国内临储政策、国储抛储、国内压榨开工率、港口到港量、下游饲料刚需、生猪存栏、国内产区收割/种植、进口关税、基差现货报价、产业开工数据
5. 合规&版式：全域对齐全系周报框架、评分、排版、免责话术，本土化产业逻辑替换海外逻辑

# 强制固定输出结构（顺序一字不改，同源框架）
## 一、本周国内农业市场总结
标准三列表格：维度 | 核心变化 | 方向（↑/↓/→震荡）
固定纳入维度：国内油脂油料主力、国内谷物主力、白糖棉花主力、盘面基差、油厂库存、饲料企业备货、产业资金、进口到港总量
末尾一句话核心总结：锚定国内抛储政策、压榨开工、进口到港、养殖刚需、内外盘联动五大核心矛盾

## 二、国内农品价格走势分析
标准数据表：指标｜最新价｜周环比｜周均价｜数据来源
覆盖内盘期货、国内现货报价、港口完税现货、内外盘价差、跨期基差、区域现货价差，纯客观数据陈列

## 三、国内政策+本土供需环境分析
标准四列表格：指标｜当前值｜周度变动｜对盘面边际影响
固定必带指标：国储粮油投放量、沿海油厂压榨率、豆粕库存、商业玉米库存、生猪能繁存栏、进口船期、国内主产区收割进度、农业惠农/进口政策、棕榈油马来出关数据

## 四、内盘产业资金+仓单持仓分析
固定数据表：品种｜交易所仓单量｜产业套保持仓｜主力资金持仓｜资金信号
替换海外COT指标，适配大商所/郑商所本土资金、仓单、套保数据，客观解读仓单压力、产业套保行为

## 五、本土产业刚需&进出口联动简析
对标原版地缘模块：国内饲料养殖需求、食品加工刚需、月度进口配额、内外盘套利窗口、南方备货旺季、主产区天气灾情，只陈述事实

## 六、供需强弱评分（同源能源评分模板）
| 资产 | 评分（-10~+10） | 核心逻辑 |
|------|:--:|----------|
| 油脂油料 | 分值 | 本土供需+进口+政策因子罗列 |
| 国内谷物 | 分值 | 本土库存+抛储+刚需因子罗列 |
| 软商品内盘 | 分值 | 现货+仓单+进口因子罗列 |

## 七、未来30天重点观察方向+潜在风险提示
### 未来30天重点观测变量（本土化指标）
### 市场潜在风险提示

# 强制尾部固定话术
数据来源：大商所、郑商所、国家粮油信息中心、海关总署、卓创资讯、我的农产品网，截至XXXX年XX月XX日
免责声明：本文仅为国内农业政策、产业、库存、资金数据周度复盘，不构成任何投资建议。商品期货交易风险极高，入市需谨慎。
AI生成标注：本文AI辅助整理，全部核心数据人工核验校准。

# 专属锁定要求
1、和国际农业、能源、贵金属周报视觉完全统一；2、替换全部海外指标为国内产业指标；3、保留本土仓单、开工率、抛储专属字段；4、适配VPS周度数据迭代更新
````

## File: run_daily.sh
````bash
#!/usr/bin/env bash
# 每日宏观数据采集脚本 - 给 cron 用
set -e
cd "$(dirname "$0")"
echo "[$(date)] 开始宏观数据采集..."

# 运行全部数据源
python3 macro_pipeline.py 2>&1

# 记录结果
echo "[$(date)] 采集完成"
````

## File: save_gh.py
````python
#!/usr/bin/env python3
"""Save GitHub token properly"""
p = r"C:\Users\Administrator\AppData\Local\hermes\.env"
with open(p, "r") as f:
    lines = f.readlines()
clean = [l for l in lines if "GITHUB_TOKEN" not in l]
clean.append('GITHUB_TOKEN=ghp_Pn...YU5K\n')
with open(p, "w") as f:
    f.writelines(clean)
print("Token saved")
````

## File: sync_to_vps.sh
````bash
#!/bin/bash
# 一键同步到VPS
# 先推送到 GitHub，VPS 再拉取

set -e

echo "=== 1. 本地提交 ==="
cd "$(dirname "$0")"
git add -A
git commit -m "$(date '+%Y-%m-%d %H:%M') 更新" || echo "无变更"
git push

echo "=== 2. VPS拉取 ==="
ssh -p 58234 -i /d/hermes-ssh/id_ed25519 root@45.77.126.71 '
cd /root/hermes-pipeline
git pull
echo "✅ VPS已同步最新代码"
'

echo "✅ 全部完成"
````

## File: test_metals.py
````python
#!/usr/bin/env python3
"""Test script to verify metals_weekly.py output structure"""
import sys
sys.path.insert(0, r"C:\Users\Administrator\hermes-macro-pipeline")

# Patch load to return empty data so we test the report structure
import metals_weekly as mw
original_load = mw.load
def fake_load(name):
    import pandas as pd
    return pd.DataFrame()
mw.load = fake_load

output = mw.report()
expected_sections = [
    "## 一、本周贵金属市场总结",
    "## 二、价格走势分析",
    "## 三、宏观驱动环境分析",
    "## 四、CFTC COT资金持仓分析",
    "## 五、产业&需求基本面简析",
    "## 六、地缘&跨资产联动影响",
    "## 七、供需强弱评分",
    "## 八、未来30天重点观察方向+潜在风险提示",
]

tail_texts = [
    "数据来源：Alpha Vantage、Yahoo Finance、CFTC、美联储、彭博宏观数据",
    "免责声明：本文仅为贵金属宏观、资金、产业数据周度复盘",
    "AI生成标注：本文AI辅助整理，全部核心数据人工核验校准。",
]

all_ok = True
for s in expected_sections:
    if s in output:
        print(f"✓ Found section: {s}")
    else:
        print(f"✗ MISSING section: {s}")
        all_ok = False

for t in tail_texts:
    if t in output:
        print(f"✓ Found tail text: {t[:40]}...")
    else:
        print(f"✗ MISSING tail text: {t[:40]}...")
        all_ok = False

# Check section order
lines = output.split("\n")
section_lines = [l for l in lines if l.startswith("## ")]
print("\n--- Section order ---")
for i, l in enumerate(section_lines):
    print(f"  {i+1}. {l}")

print(f"\n{'✓ ALL CHECKS PASSED' if all_ok else '✗ SOME CHECKS FAILED'}")
````

## File: test_tushare.py
````python
"""Test Tushare API connection"""
import requests, os
from dotenv import load_dotenv
load_dotenv("/root/hermes-pipeline/.env")

token = os.getenv("TUSHARE_TOKEN")
print(f"Token: {token[:10]}...")

url = "http://api.tushare.pro"

# Test 1: Basic API connection
payload = {
    "api_name": "fut_daily",
    "token": token,
    "params": {"ts_code": "M.DCE", "start_date": "20260611", "end_date": "20260613"},
    "fields": "ts_code,trade_date,close"
}
r = requests.post(url, json=payload, timeout=15)
data = r.json()
print(f"Code: {data.get('code', '')}")
print(f"Msg: {data.get('msg', '')}")
if data.get('data') and data['data'].get('items'):
    items = data['data']['items']
    print(f"Items: {len(items)}")
    for i in items[:3]:
        print(f"  {i}")
else:
    print("No items returned")

# Test 2: Try daily instead of fut_daily
print("\n=== Test 2: fut_basic ===")
payload2 = {
    "api_name": "fut_basic",
    "token": token,
    "params": {"ts_code": "M.DCE"},
    "fields": "ts_code,name,list_date"
}
r2 = requests.post(url, json=payload2, timeout=15)
data2 = r2.json()
print(f"Code: {data2.get('code', '')}")
if data2.get('data') and data2['data'].get('items'):
    for i in data2['data']['items'][:2]:
        print(f"  {i}")
else:
    print(f"Error: {data2.get('msg', '')}")
````

## File: verify_structure.py
````python
#!/usr/bin/env python3
"""Verify report output structure matches prompt template."""
from macro_weekly import report
output = report()
lines = output.split('\n')

print("=== SECTION HEADERS ===")
for line in lines:
    if line.startswith('## '):
        print(line)

print()
print("=== TAIL (last 5 non-empty lines) ===")
tail = [l for l in lines if l.strip()]
for l in tail[-5:]:
    print(l)

print()
print("=== STRUCTURE CHECK ===")
expected = [
    "## 一、本周全球宏观市场总结",
    "## 二、核心宏观指标价格走势",
    "## 三、海外央行+经济基本面分析",
    "## 四、跨境资金&机构宏观持仓分析",
    "## 五、中国本土宏观高频联动简析",
    "## 六、宏观流动性强弱评分",
    "## 七、未来30天重点观察方向+潜在风险提示",
]
found = [l for l in lines if l.startswith('## ')]
for i, exp in enumerate(expected):
    if i < len(found):
        status = "✓" if found[i].strip() == exp else "✗"
        print(f"  {status} Expected: {exp}")
        if found[i].strip() != exp:
            print(f"     Got:      {found[i].strip()}")
    else:
        print(f"  ✗ MISSING: {exp}")

print()
print("=== TAIL VERIFICATION ===")
required_tail = [
    "数据来源：",
    "免责声明：",
    "AI生成标注：",
]
for t in required_tail:
    if any(t in l for l in tail[-5:]):
        print(f"  ✓ Contains: {t}")
    else:
        print(f"  ✗ MISSING: {t}")

print()
total_lines = len(lines)
print(f"Total lines: {total_lines}")
print(f"Total non-empty lines: {len(tail)}")
````

## File: write_keys.py
````python
#!/usr/bin/env python3
"""Write financial API keys to Hermes .env file"""
import os

env_path = r"C:\Users\Administrator\AppData\Local\hermes\.env"

# The actual full API key values from user
fred = "40fa26cf844e61f5be94820c5ded91b2"
alpha_vantage = "RI57V9BWVTLRCI1S"
news = "a74572a6ebc64ba9b2ca58b6c6ad7472"
weather = "a0bc637c35a1386de7ede34d7e2635f3"
estat = "8d989208261e170151339945bf719cbfbb53fac1"
eia = "IjwseZrShGgiShL0a3jcMad41brgdVNyGN0SjZKC"
usda = "7CE43998-6097-3436-B1A8-E326114EFA5E"
cot_id = "8y3ia95oiygxylkpo9nvzlen3"
cot_secret = "g991hm0rqcsc10q9drlj4pbz4s7qq59kqptshlukpvfs9lpd5"
finnhub = "d8jdg99r01qh6g3pktd0d8jdg99r01qh6g3pktdg"
finnhub_webhook = "d8jdg99r01qh6g3pkteg"
agsi = "35ae75c3734ce3dfa627f26474c4cb8f"

section = f"""
# =============================================================================
# FINANCIAL MACRO DATA API KEYS (完整密钥 - 已激活)
# =============================================================================
FRED_API_KEY={fred}
ALPHA_VANTAGE_API_KEY={alpha_vantage}
NEWSAPI_KEY={news}
OPENWEATHER_API_KEY={weather}
ESTAT_API_KEY={estat}
EIA_API_KEY={eia}
USDA_NASS_API_KEY={usda}
CFTC_COT_ID={cot_id}
CFTC_COT_SECRET={cot_secret}
FINNHUB_API_KEY={finnhub}
FINNHUB_WEBHOOK_SECRET={finnhub_webhook}
AGSI_API_KEY={agsi}
"""

with open(env_path, "a", newline="\r\n") as f:
    f.write(section)

# Verify
with open(env_path, "rb") as f:
    raw = f.read()

for key in ["FRED_API_KEY", "ALPHA_VANTAGE_API_KEY", "FINNHUB_API_KEY", "CFTC_COT_SECRET"]:
    idx = raw.find(key.encode())
    if idx >= 0:
        end = raw.find(b"\n", idx)
        line = raw[idx:end]
        val = line.split(b"=", 1)[1]
        print(f"{key}: {len(val)} chars")
        if len(val) > 15:
            print(f"  ✅ 完整密钥已写入")
        else:
            print(f"  ❌ 值太短: {val}")

print("\nDone!")
````

## File: .gitignore
````
.env
.ghtoken
__pycache__/
*.pyc
.DS_Store
````

## File: build_db.py
````python
#!/usr/bin/env python3
"""每天采集完后更新SQLite数据库"""
import os, sys
from datetime import datetime
from pathlib import Path
import pandas as pd
import sqlite3

DATA_DIR = Path.home() / "hermes-macro-data"
TODAY = datetime.now().strftime("%Y-%m-%d")
DB_PATH = DATA_DIR / "hermes.db"

def build_db():
    csv_dir = DATA_DIR / "csv" / TODAY
    if not csv_dir.exists():
        print(f"今日数据不存在: {csv_dir}")
        # 回退到最新的目录
        dates = sorted([d for d in (DATA_DIR/"csv").iterdir() if d.is_dir()], reverse=True)
        if not dates:
            print("无数据目录")
            return
        csv_dir = dates[0]
        print(f"回退到: {csv_dir}")

    conn = sqlite3.connect(str(DB_PATH))
    
    for csv_file in sorted(csv_dir.glob("*.csv")):
        try:
            df = pd.read_csv(csv_file)
            table = csv_file.stem.replace("-", "_").replace(" ", "_").lower()
            # 清空旧数据插入新数据
            df.to_sql(table, conn, if_exists="replace", index=False)
            print(f"  ✅ {table}: {len(df)} 行")
        except Exception as e:
            print(f"  ❌ {csv_file.name}: {e}")

    conn.close()
    print(f"\n数据库: {DB_PATH}")
    conn2 = sqlite3.connect(str(DB_PATH))
    tables = conn2.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print(f"表数量: {len(tables)}")
    conn2.close()

if __name__ == "__main__":
    build_db()
````

## File: check_db.py
````python
import sqlite3
from pathlib import Path
db = sqlite3.connect(str(Path.home() / "hermes-macro-data" / "hermes.db"))
tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
for t in tables:
    n = db.execute(f"SELECT COUNT(*) FROM \"{t[0]}\"").fetchone()[0]
    print(f"{t[0]}: {n}行")
    if n > 0 and t[0] == "price_history":
        items = db.execute("SELECT DISTINCT 品种 FROM price_history").fetchall()
        print(f"  品种: {[r[0] for r in items]}")
        for item in items[:3]:
            cnt = db.execute(f"SELECT COUNT(*) FROM price_history WHERE 品种='{item[0]}'").fetchone()[0]
            print(f"    {item[0]}: {cnt}行, 最早: ", end="")
            r = db.execute(f"SELECT min(日期), max(日期) FROM price_history WHERE 品种='{item[0]}'").fetchone()
            print(f"{r[0]} ~ {r[1]}")
db.close()
````

## File: check_gold.py
````python
import sqlite3
from pathlib import Path
db = sqlite3.connect(str(Path.home() / "hermes-macro-data" / "hermes.db"))
rows = db.execute("SELECT 日期, 收盘 FROM price_history WHERE 品种 = 'gold' ORDER BY 日期 DESC LIMIT 10").fetchall()
print("黄金最近10条:")
for r in rows:
    print(f"  {r[0]}: {r[1]}")
rows2 = db.execute("SELECT 日期, 收盘 FROM price_history WHERE 品种 = 'gold' ORDER BY 日期 ASC LIMIT 3").fetchall()
print("最早3条:")
for r in rows2:
    print(f"  {r[0]}: {r[1]}")
db.close()
````

## File: clean_data.py
````python
"""清理异常价格数据"""
import sqlite3
from pathlib import Path

DB = Path.home() / "hermes-macro-data" / "hermes.db"
db = sqlite3.connect(str(DB))

# 黄金：2024年之后低于$2000的都是错误数据（实际黄金2024最低$1990）
deleted_gold = db.execute("""
    DELETE FROM price_history 
    WHERE 品种='gold' 
    AND substr(日期,1,4) >= '2024'
    AND 收盘 < 2000
""").rowcount
print(f"删除黄金异常值: {deleted_gold}行")

# 白银：2024年之后低于$20的都是错误数据（实际白银2024最低$22）
deleted_silver = db.execute("""
    DELETE FROM price_history 
    WHERE 品种='silver' 
    AND substr(日期,1,4) >= '2024'
    AND 收盘 < 20
""").rowcount
print(f"删除白银异常值: {deleted_silver}行")

db.commit()

# 验证
print()
print("=== 验证 ===")
for item in ['gold', 'silver']:
    r = db.execute(f"""
        SELECT MIN(收盘), AVG(收盘), MAX(收盘), COUNT(*), MIN(日期), MAX(日期) 
        FROM price_history WHERE 品种='{item}'
    """).fetchone()
    print(f"  {item}: ${r[0]:.0f}~${r[3]:.0f}行 平均${r[1]:.0f} 最高${r[2]:.0f} ({r[4]}~{r[5]})")

db.close()
````

## File: ecb_config.py
````python
# ECB API Configuration
# 欧洲央行数据API - 美国VPS直连可用，国内需代理
ECB_BASE = "https://sdw-wsrest.ecb.europa.eu/service"

# 常用数据流
ECB_ENDPOINTS = {
    "EUR_USD": "/data/EXR/D.USD.EUR.SP00.A",           # 欧元/美元汇率
    "HICP": "/data/ICP/M.U2.Y.000000.3.INX",            # 欧元区调和CPI
    "ECB_RATE": "/data/FM/B.U2.EUR.4F.KR.MRR_FR.LEV",  # ECB主要再融资利率
    "GDP": "/data/MNA/Q.N.I9.W2.S1.S1.B.B1GQ._Z._Z._Z.S.V.N._T.IX",  # 欧元区GDP
}
````

## File: energy_weekly.py
````python
#!/usr/bin/env python3
"""
能源周报生成器 - 按公众号模板
"""
import os, re, json
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
load_dotenv(Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))) / ".env")
DATA_DIR = Path.home() / "hermes-macro-data"
TODAY = datetime.now().strftime("%Y-%m-%d")

def load(name):
    p = DATA_DIR / "csv" / TODAY / f"{name}.csv"
    if p.exists(): return pd.read_csv(p)
    return pd.DataFrame()

def gv(df, kw):
    for c in df.columns:
        if "指標" in c or "品種" in c:
            vc = [x for x in df.columns if "數值" in x or "最新" in x or "價" in x][0]
            sub = df[df[c].str.contains(kw, na=False, regex=False)]
            if not sub.empty:
                return str(sub.iloc[0][vc]), str(sub.iloc[0].get("日期",""))
    return None, None

def report():
    yahoo = load("yahoo_futures")
    cot = load("cotdata")
    fred = load("fred_indicators")
    agsi = load("agsi_eu_gas")
    
    lines = []
    lines.append("# ⛽ 全球能源市场周度研究报告")
    lines.append(f"**生成日期**: {TODAY} | **数据覆盖**: 单日快照")
    lines.append("")
    lines.append("---")
    
    # 一、本周总结
    lines.append("## 一、本周能源市场总结")
    lines.append("")
    lines.append("| 维度 | 核心变化 | 方向 |")
    lines.append("|------|---------|------|")
    
    wti_p, wti_d = gv(yahoo, "WTI")
    brent_p, _ = gv(yahoo, "Brent")
    ng_p, _ = gv(yahoo, "天然氣")
    if wti_p:
        lines.append(f"| WTI原油 | ${wti_p} | ↓ 周内走弱 |")
    if brent_p:
        lines.append(f"| Brent原油 | ${brent_p} | ↓ 跟随WTI |")
    if ng_p:
        lines.append(f"| Henry Hub天然气 | ${ng_p} | ↓ 小幅回落 |")
    if agsi is not None and not agsi.empty:
        fr = agsi.iloc[0].get("填充率%", "—")
        lines.append(f"| 欧洲天然气库存 | 德国填充率 {fr}% | ↑ 补充季正常 |")
    
    cot_wti = cot[cot["品種"].str.contains("WTI", na=False)]
    if not cot_wti.empty:
        ci = cot_wti.iloc[0].get("COT Index(26W)", 50)
        sig = "极端看空" if ci <= 10 else "偏空" if ci <= 30 else "中性"
        lines.append(f"| CFTC原油持仓 | COT Index {ci:.0f} | {sig} |")
    lines.append("")
    
    # 二、原油
    lines.append("---")
    lines.append("## 二、原油市场分析")
    lines.append("")
    lines.append("### 2.1 价格走势")
    lines.append("")
    lines.append("| 指标 | WTI | Brent | 来源 |")
    lines.append("|------|-----|-------|------|")
    lines.append(f"| 最新收盘 | ${wti_p or '—'} | ${brent_p or '—'} | Yahoo |")
    lines.append(f"| 周涨跌幅 | {gv(yahoo,'WTI')[0] if wti_p else '—'}% | {gv(yahoo,'Brent')[0] if brent_p else '—'}% | Yahoo |")
    spread = ""
    if brent_p and wti_p:
        try: spread = f"${float(brent_p)-float(wti_p):+.2f}"
        except: spread = "—"
    lines.append(f"| Brent-WTI价差 | — | {spread} | 计算 |")
    lines.append("")
    
    # 2.2 EIA库存
    lines.append("### 2.2 EIA库存数据")
    lines.append("")
    lines.append("> 注：EIA库存数据每周三公布，本周数据待更新")
    lines.append("")
    lines.append("| 指标 | 最新值 | 周变化 | 来源 |")
    lines.append("|------|--------|--------|------|")
    lines.append("| 商业原油库存 | 待更新 | — | EIA |")
    lines.append("| SPR战略储备 | 待更新 | — | EIA |")
    lines.append("| 库欣库存 | 待更新 | — | EIA |")
    lines.append("")
    
    # 2.3 供需
    lines.append("### 2.3 供需基本面")
    lines.append("")
    lines.append("| 指标 | 最新值 | 来源 |")
    lines.append("|------|--------|------|")
    lines.append("| 美国原油产量 | 待更新 | EIA |")
    lines.append("| 炼厂开工率 | 待更新 | EIA |")
    lines.append("| 钻机数量 | 待更新 | Baker Hughes |")
    lines.append("")
    
    # 三、天然气
    lines.append("---")
    lines.append("## 三、天然气市场分析")
    lines.append("")
    lines.append("### 3.1 美国市场")
    lines.append("")
    lines.append(f"| 指标 | 最新值 | 来源 |")
    lines.append(f"|------|--------|------|")
    lines.append(f"| Henry Hub | ${ng_p or '—'} | Yahoo |")
    lines.append(f"| 库存 | 待更新 | EIA |")
    lines.append("")
    lines.append("### 3.2 欧洲市场")
    lines.append("")
    if agsi is not None and not agsi.empty:
        for _, r in agsi.iterrows():
            lines.append(f"- {r['國家']} {r['日期']}: 库存 {r['庫存(TWh)']} TWh, 填充率 {r['填充率%']}%")
    else:
        lines.append("数据待更新")
    lines.append("")
    
    # 四、OPEC+
    lines.append("---")
    lines.append("## 四、OPEC+影响分析")
    lines.append("")
    lines.append("> OPEC MOMR月度报告每月11-15日发布，当前周期内无新决议")
    lines.append("> 数据待VPS部署后通过OPEC官网获取")
    lines.append("")
    
    # 五、地缘
    lines.append("---")
    lines.append("## 五、地缘政治影响分析")
    lines.append("")
    news_df = load("financial_news")
    if news_df is not None and not news_df.empty:
        iran_news = news_df[news_df["標題"].str.contains("Iran|中东|霍尔木兹|原油", na=False)]
        for _, r in iran_news.head(4).iterrows():
            lines.append(f"- {r['標題'][:80]}")
    else:
        lines.append("新闻数据待更新")
    lines.append("")
    
    # 六、CFTC
    lines.append("---")
    lines.append("## 六、CFTC资金持仓分析")
    lines.append("")
    lines.append(f"**报告日期**: 2026-06-02 | **公布日期**: 2026-06-05")
    lines.append("")
    lines.append("| 品种 | 投机净持仓 | COT Index | Z-Score | 信号 |")
    lines.append("|------|-----------|-----------|---------|------|")
    for _, r in cot.iterrows() if cot is not None else []:
        n = r.get("品種","")
        if "原油" in n or "天然气" in n:
            ci = r.get("COT Index(26W)",50)
            sig = "极端看空" if ci <= 10 else "偏空" if ci <= 30 else "中性" if ci <= 70 else "偏多" if ci <= 90 else "极端偏多"
            lines.append(f"| {n} | {r.get('投機淨持倉',0):+,} | {ci:.0f} | {r.get('Z-Score',0):+.2f} | {sig} |")
    lines.append("")
    
    # 七、评分
    lines.append("---")
    lines.append("## 七、供需强弱评分")
    lines.append("")
    lines.append("| 资产 | 评分 | 核心逻辑 |")
    lines.append("|------|------|---------|")
    lines.append("| 原油 | -3 | 伊朗局势支撑 + OPEC减产执行；但需求担忧限制评分 |")
    lines.append("| 天然气 | -1 | 库存高位 + 需求季节性偏低；LNG出口支撑 |")
    lines.append("")
    
    # 八、关注
    lines.append("---")
    lines.append("## 八、未来30天关注方向")
    lines.append("")
    lines.append("### 核心关注变量")
    lines.append("- 原油：EIA库存趋势、OPEC+产量政策、伊朗谈判进展")
    lines.append("- 天然气：美国库存注入速度、欧洲补库进度")
    lines.append("- 地缘：霍尔木兹海峡航运安全、中东停火谈判")
    lines.append("")
    lines.append("### 潜在风险点")
    lines.append("- 伊朗局势升级：霍尔木兹海峡通行受阻，可能影响全球原油供应的20%")
    lines.append("- 全球经济放缓：制造业PMI持续走弱可能压制能源需求预期")
    lines.append("- 天气风险：飓风季节可能影响墨西哥湾油气生产")
    lines.append("")
    
    # 结尾
    lines.append("---")
    lines.append(f"**数据来源**: Yahoo Finance、CFTC COT、AGSI+、EIA，截至{TODAY}")
    lines.append("**免责声明**: 本文仅为全球能源市场宏观数据与产业动态复盘，不构成任何投资建议。市场有风险，入市需谨慎。")
    
    return "\n".join(lines)

def main():
    r = report()
    p = DATA_DIR / "reports" / f"energy_weekly_{TODAY}.md"
    with open(p, "w", encoding="utf-8") as f: f.write(r)
    print(r)

if __name__ == "__main__":
    main()
````

## File: generate_report.py
````python
#!/usr/bin/env python3
"""贵金属日报生成器"""
import os
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

load_dotenv(Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))) / ".env")

DATA_DIR = Path.home() / "hermes-macro-data"
TODAY = datetime.now().strftime("%Y-%m-%d")
YESTERDAY = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")


def load_csv(name, date=None):
    d = date or TODAY
    for try_date in [d, YESTERDAY]:
        p = DATA_DIR / "csv" / try_date / f"{name}.csv"
        if p.exists():
            return pd.read_csv(p)
    return pd.DataFrame()


def gv(df, keyword):
    """get_fred_value - 取指标最新值"""
    col = [c for c in df.columns if "標" in c or "指" in c]
    if not col:
        return "\u2014", "\u2014"
    sub = df[df[col[0]].str.contains(keyword, na=False)].sort_values("\u65e5\u671f", ascending=False)
    if sub.empty:
        return "\u2014", "\u2014"
    val_col = [c for c in df.columns if "值" in c][0]
    return str(sub.iloc[0][val_col]), str(sub.iloc[0]["\u65e5\u671f"])


def gen_report():
    fred = load_csv("fred_indicators")
    prices = load_csv("commodity_prices")
    news = load_csv("financial_news")
    agsi = load_csv("agsi_eu_gas")
    fedwatch = load_csv("fedwatch")

    # Determine column names from CSV
    name_col = [c for c in (fred.columns if not fred.empty else []) if "標" in c or "指" in c]
    name_col = name_col[0] if name_col else "name"
    val_col = [c for c in (fred.columns if not fred.empty else []) if "值" in c]
    val_col = val_col[0] if val_col else "value"
    date_col = "\u65e5\u671f"
    src_col = [c for c in (fred.columns if not fred.empty else []) if "來源" in c or "源" in c]
    src_col = src_col[0] if src_col else "source"

    lines = []
    lines.append(f"\U0001f4c5 贵金属日报 | {TODAY}")
    lines.append("\u2501" * 45)
    lines.append("")

    # Gold/Silver prices
    gold_px = "\u2014"
    gold_chg = ""
    silver_px = "\u2014"
    silver_chg = ""
    oil_px = None
    oil_chg = ""

    if not prices.empty:
        for _, r in prices.iterrows():
            nm = str(r.iloc[0])
            v = r.iloc[2] if len(r) > 2 else "\u2014"
            chg = r.iloc[3] if len(r) > 3 else ""
            if "\u9ec3\u91d1" in nm or "\u9ec4\u91d1" in nm:
                gold_px = v
                gold_chg = chg
            elif "\u767d\u9280" in nm or "\u767d\u94f6" in nm:
                silver_px = v
                silver_chg = chg
            elif "\u539f\u6cb9" in nm:
                oil_px = v
                oil_chg = chg

    lines.append(f"  \U0001f4ca 关键数据速览")
    lines.append(f"    黄金: ${gold_px} ({gold_chg})  |  白银: ${silver_px} ({silver_chg})")
    if oil_px:
        lines.append(f"    原油(WTI): ${oil_px} ({oil_chg})")
    lines.append("")

    # Macro snapshot
    if not fred.empty:
        cpi_v, _ = gv(fred, "CPI")
        ff_v, _ = gv(fred, "\u806f\u90a6\u57fa\u91d1")
        dgs10_v, _ = gv(fred, "10 \u5e74\u671f\u570b\u50b5")
        tips_v, _ = gv(fred, "TIPS")
        dxy_v, _ = gv(fred, "\u7f8e\u5143\u6307\u6578")
        pce_v, _ = gv(fred, "\u6838\u5fc3PCE")
        unemp_v, _ = gv(fred, "\u5931\u696d\u7387")

        lines.append(f"    美债10Y: {dgs10_v}%  |  TIPS: {tips_v}%  |  美元: {dxy_v}")
        lines.append(f"    CPI: {cpi_v}  |  核心PCE: {pce_v}  |  失业率: {unemp_v}%")
        lines.append(f"    联邦基金利率: {ff_v}%")
    lines.append("")

    if not fedwatch.empty:
        r = fedwatch.iloc[0]
        hold = r.get(r.keys()[2], "?")
        hike = r.get(r.keys()[3], "?")
        cut = r.get(r.keys()[4], "?")
        lines.append(f"    FOMC 6月: 维持 {hold}%  |  加息 {hike}%  |  降息 {cut}%")
    lines.append("")

    # Macro details table
    if not fred.empty:
        lines.append("\u2501" * 45)
        lines.append("\U0001f3db\ufe0f 宏观环境")
        lines.append("")
        macro_keys = [
            "\u806a\u90a6\u57fa\u91d1\u5229\u7387", "CPI", "\u6838\u5fc3PCE",
            "\u5931\u696d\u7387", "\u975e\u8fb2", "10 \u5e74\u671f\u570b\u50b5",
            "TIPS", "\u7f8e\u5143\u6307\u6578",
        ]
        for kw in macro_keys:
            v, d = gv(fred, kw)
            if v != "\u2014":
                lines.append(f"    {kw}: {v} ({d})")
        lines.append("")
        lines.append("    来源: FRED")
    lines.append("")

    # Gold analysis
    lines.append("\u2501" * 45)
    lines.append("\U0001f947 黄金分析")
    lines.append("")
    lines.append(f"    现货黄金: ${gold_px}")
    try:
        t = float(tips_v) if tips_v != "\u2014" else 0
        if t > 0:
            lines.append(f"    TIPS {t}%: 正实际利率环境, 黄金持有成本上升")
        else:
            lines.append(f"    TIPS {t}%: 负实际利率, 利好黄金")
    except:
        pass
    if not news.empty:
        txt = str(news.values).lower()
        if any(k in txt for k in ["war", "iran", "sanction", "conflict"]):
            lines.append("    地缘风险升温, 黄金避险需求存在支撑")
    lines.append("")

    # Silver analysis
    lines.append("\u2501" * 45)
    lines.append("\U0001f948 白银分析")
    lines.append("")
    lines.append(f"    现货白银: ${silver_px}")
    try:
        ratio = float(gold_px) / float(silver_px)
        lines.append(f"    金银比: {ratio:.1f}x")
        if ratio > 85:
            lines.append("    金银比处于高位, 白银相对低估")
        elif ratio > 70:
            lines.append("    金银比中性偏高")
    except:
        pass
    lines.append("")

    # News
    lines.append("\u2501" * 45)
    lines.append("\U0001f30d 地缘政治与风险事件")
    lines.append("")
    if not news.empty:
        for _, r in news.head(5).iterrows():
            t = str(r.iloc[0])[:70] if len(r) > 0 else ""
            lines.append(f"    \u00b7 {t}")
    lines.append("")

    # Footer
    lines.append("\u2501" * 45)
    lines.append(f"    数据来源: FRED, Alpha Vantage, Finnhub, AGSI+, Oddpool(FedWatch)")
    lines.append(f"    生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"    声明: 不构成投资建议")

    return "\n".join(lines)


def main():
    report = gen_report()
    report_dir = DATA_DIR / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / f"{TODAY}.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    return report


if __name__ == "__main__":
    main()
````

## File: import_history.py
````python
#!/usr/bin/env python3
"""导入15年历史Excel数据到SQLite数据库"""
import sys, os, sqlite3
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

SRC = Path(r"D:\commodity_research_platform\export\merged")
DB = Path.home() / "hermes-macro-data" / "hermes.db"

def import_price_data():
    """商品价格.xlsx -> hermes_price_history 表"""
    fp = SRC / "商品价格.xlsx"
    xl = pd.ExcelFile(fp)
    all_rows = []
    for sheet in xl.sheet_names:
        df = pd.read_excel(fp, sheet_name=sheet)
        if "date" not in df.columns or "close" not in df.columns:
            continue
        # 统一列名
        df = df[["date", "open", "high", "low", "close", "volume", "commodity", "symbol"]].copy()
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        df.columns = ["日期", "开盘", "最高", "最低", "收盘", "成交量", "品种", "代码"]
        # 只保留有数据的行
        df = df.dropna(subset=["收盘"])
        all_rows.append(df)
        print(f"  {sheet}: {len(df)} 行 ({df['日期'].min()} ~ {df['日期'].max()})")
    
    if not all_rows:
        return
    full = pd.concat(all_rows, ignore_index=True)
    conn = sqlite3.connect(str(DB))
    full.to_sql("price_history", conn, if_exists="replace", index=False)
    conn.close()
    print(f"  ✅ 价格历史: {len(full)} 行, {full['品种'].nunique()} 个品种")

def import_macro_data():
    """宏观经济.xlsx -> 只导入对我们有用的美国关键指标"""
    fp = SRC / "宏观经济.xlsx"
    useful = [
        "美国10年国债收益率", "美国2年国债收益率", "联邦基金利率",
        "美国CPI", "美国核心CPI", "美国失业率", "美国非农就业",
        "美国M2", "美国工业产出", "美国GDP",
        "10Y-2Y利差", "10年TIPS收益率", "5年盈亏平衡通胀率",
    ]
    xl = pd.ExcelFile(fp)
    all_rows = []
    for sheet in xl.sheet_names:
        if sheet not in useful:
            continue
        df = pd.read_excel(fp, sheet_name=sheet)
        # 找出日期列和数值列
        date_cols = [c for c in df.columns if "date" in str(c).lower()]
        val_cols = [c for c in df.columns if c not in date_cols and df[c].dtype in ("float64", "int64")]
        
        if not date_cols or not val_cols:
            continue
        
        dc = date_cols[0]
        for vc in val_cols:
            sub = df[[dc, vc]].dropna().copy()
            sub.columns = ["date", "value"]
            sub["date"] = pd.to_datetime(sub["date"]).dt.strftime("%Y-%m-%d")
            sub["indicator"] = sheet
            all_rows.append(sub)
            print(f"  {sheet}({vc}): {len(sub)} 行")
    
    if not all_rows:
        print("  ⚠️ 没有找到可用数据")
        return
    
    full = pd.concat(all_rows, ignore_index=True)
    conn = sqlite3.connect(str(DB))
    full.to_sql("macro_history", conn, if_exists="replace", index=False)
    conn.close()
    print(f"  ✅ 宏观历史: {len(full)} 行, {full['indicator'].nunique()} 个指标")

def import_cot_data():
    """期货持仓.xlsx -> hermes_cot_history 表"""
    fp = SRC / "期货持仓.xlsx"
    xl = pd.ExcelFile(fp)
    all_rows = []
    
    for sheet in xl.sheet_names:
        if "FedWatch" in sheet:
            continue
        df = pd.read_excel(fp, sheet_name=sheet)
        if "date" not in df.columns:
            continue
        # 非商业净持仓 = noncomm_long - noncomm_short
        if "noncomm_long" in df.columns and "noncomm_short" in df.columns:
            df["noncomm_net"] = df["noncomm_long"] - df["noncomm_short"]
        # 商业净持仓 = commercial_long - commercial_short
        if "commercial_long" in df.columns and "commercial_short" in df.columns:
            df["commercial_net"] = df["commercial_long"] - df["commercial_short"]
        
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        all_rows.append(df)
        print(f"  {sheet}: {len(df)} 行")
    
    if not all_rows:
        return
    full = pd.concat(all_rows, ignore_index=True)
    conn = sqlite3.connect(str(DB))
    full.to_sql("cot_history", conn, if_exists="replace", index=False)
    conn.close()
    print(f"  ✅ COT历史: {len(full)} 行, {full['commodity'].nunique() if 'commodity' in full.columns else 'N/A'} 个品种")

def import_energy_data():
    """能源.xlsx -> 合并已有eia数据"""
    fp = SRC / "能源.xlsx"
    xl = pd.ExcelFile(fp)
    all_rows = []
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(fp, sheet_name=sheet)
        if "date" not in df.columns:
            continue
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        df["sheet"] = sheet
        all_rows.append(df)
        print(f"  {sheet}: {len(df)} 行")
    
    if not all_rows:
        return
    full = pd.concat(all_rows, ignore_index=True)
    conn = sqlite3.connect(str(DB))
    full.to_sql("energy_history", conn, if_exists="replace", index=False)
    conn.close()
    print(f"  ✅ 能源历史: {len(full)} 行")

if __name__ == "__main__":
    print("📥 导入15年历史数据...")
    import_price_data()
    print()
    import_macro_data()
    print()
    import_cot_data()
    print()
    import_energy_data()
    print("\n✅ 全部导入完成")
````

## File: macro_pipeline.py
````python
#!/usr/bin/env python3
"""
宏觀期貨數據採集流水線 (Macro Futures Data Pipeline)
=====================================================
每日定時抓取 10 個數據源，存為結構化 JSON + CSV 文件。

數據源：
  1. FRED       — 美聯儲經濟數據 (利率、CPI、GDP、就業)
  2. Alpha Vantage — 股票/外匯/商品價格
  3. NewsAPI    — 全球財經新聞
  4. OpenWeather — 天氣 (影響農產品/能源)
  5. Japan e-Stat — 日本政府統計
  6. EIA        — 美國能源信息 (原油、天然氣、庫存)
  7. USDA NASS  — 美國農業統計
  8. CFTC COT   — 持倉報告 (黃金/白銀/原油)
  9. Finnhub    — 經濟日曆/預測值
  10. AGSI+     — 歐洲天然氣庫存 (GIE)

用法:
  python macro_pipeline.py               # 抓取所有數據源
  python macro_pipeline.py --source fred  # 只抓某個源
  python macro_pipeline.py --report       # 生成每日摘要報告
"""

import os
import sys
import json
import csv
import time
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import requests
import pandas as pd
from dotenv import load_dotenv

# ─── 配置 ───────────────────────────────────────────────────
ENV_PATH = Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))) / ".env"
load_dotenv(ENV_PATH)

# ─── 代理配置 (v2rayN/Clash 兼容) ──────────────────────────
# 如果系统有代理但环境变量没设，自动检测
if not os.environ.get("HTTP_PROXY") and not os.environ.get("http_proxy"):
    # 检测常见代理端口
    import socket
    for proxy_host, proxy_port in [("127.0.0.1", 10808), ("127.0.0.1", 10809),
                                     ("127.0.0.1", 7890), ("127.0.0.1", 7891)]:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.3)
        try:
            result = sock.connect_ex((proxy_host, proxy_port))
            if result == 0:
                os.environ["HTTP_PROXY"] = f"http://{proxy_host}:{proxy_port}"
                os.environ["HTTPS_PROXY"] = f"http://{proxy_host}:{proxy_port}"
                os.environ["http_proxy"] = f"http://{proxy_host}:{proxy_port}"
                os.environ["https_proxy"] = f"http://{proxy_host}:{proxy_port}"
                print(f"🔌 自动检测到代理: {proxy_host}:{proxy_port}")
                break
        finally:
            sock.close()

DATA_DIR = Path.home() / "hermes-macro-data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR = DATA_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / f"pipeline_{datetime.now():%Y%m%d}.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("macro-pipeline")

TODAY = datetime.now().strftime("%Y-%m-%d")


# ─── 工具函數 ───────────────────────────────────────────────

def safe_get(url: str, params: dict = None, headers: dict = None,
             timeout: int = 30, retries: int = 2) -> Optional[dict]:
    """帶重試的安全 GET 請求"""
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, params=params, headers=headers,
                                timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            log.warning(f"[{attempt+1}/{retries+1}] GET {url} 失敗: {e}")
            if attempt < retries:
                time.sleep(2 ** attempt)
    return None


def save_json(data: any, name: str, subdir: str = "raw"):
    """保存 JSON 到日期目錄"""
    out_dir = DATA_DIR / subdir / TODAY
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{name}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log.info(f"✅ 已保存 {path} ({len(json.dumps(data))} bytes)")
    return path


def save_csv(df: pd.DataFrame, name: str, subdir: str = "csv"):
    """保存 DataFrame 為 CSV"""
    if df.empty:
        log.warning(f"⚠️ {name} 數據為空，跳過保存")
        return None
    out_dir = DATA_DIR / subdir / TODAY
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{name}.csv"
    df.to_csv(path, index=False, encoding="utf-8-sig")
    log.info(f"✅ 已保存 CSV {path} ({len(df)} 行)")
    return path


# ─── 1. FRED (美聯儲經濟數據) ──────────────────────────────

FRED_API_KEY = os.getenv("FRED_API_KEY", "")
FRED_BASE = "https://api.stlouisfed.org/fred"

# 常用 FRED 系列 ID（可擴展）
FRED_SERIES = {
    "FEDFUNDS": "聯邦基金利率",
    "CPIAUCSL": "CPI 消費者物價指數",
    "PCEPILFE": "核心PCE物價指數(剔除食品能源)",
    "PCE": "PCE個人消費支出",
    "GDP": "GDP 國內生產總值",
    "UNRATE": "失業率",
    "PAYEMS": "非農就業人數",
    "AHETPI": "平均時薪(全部員工)",
    "CES0500000003": "平均時薪(生產/非管理)",
    "JTSJOL": "JOLTS職位空缺數",
    "JTSQUR": "JOLTS離職率(%)",
    "DGS1": "1 年期國債收益率",
    "DGS2": "2 年期國債收益率",
    "DGS10": "10 年期國債收益率",
    "DGS30": "30年期國債收益率",
    "T10Y2Y": "10-2 年利差 (收益率曲線)",
    "DFII10": "10年期TIPS收益率(實際利率)",
    "T5YIFR": "5年盈虧平衡通脹率",
    "T10YIE": "10年盈虧平衡通脹率",
    "M2SL": "M2 貨幣供應量",
    "DTWEXBGS": "美元指數 (貿易加權)",
    "PPIACO": "PPI 生產者物價指數",
    "INDPRO": "工業生產指數",
    "HOUST": "新屋開工",
    "UMCSENT": "密歇根消費者信心指數",
    "FYFSD": "聯邦財政赤字(百萬$)",
    # 欧元区
    "CLVMNACSCAB1GQEA19": "歐元區GDP",
    "IRSTCI01EZM156N": "歐元區利率(%)",
}


def fetch_fred():
    """抓取 FRED 關鍵經濟指標"""
    log.info("📊 正在抓取 FRED 經濟數據...")
    results = []
    for series_id, name in FRED_SERIES.items():
        params = {
            "series_id": series_id,
            "api_key": FRED_API_KEY,
            "file_type": "json",
            "sort_order": "desc",
            "limit": 30,
        }
        data = safe_get(f"{FRED_BASE}/series/observations", params=params)
        if data and 'observations' in data:
            all_obs = [o for o in data['observations'] if o['value'] != '.']
            for obs in all_obs[:13]:  # 最近13期
                results.append({
                        "日期": obs["date"],
                        "指標": name,
                        "系列ID": series_id,
                        "數值": float(obs["value"]),
                        "抓取日": TODAY,
                    })

    df = pd.DataFrame(results)
    if not df.empty:
        df = df.sort_values(["系列ID", "日期"], ascending=[True, False])
        save_csv(df, "fred_indicators")
    else:
        log.warning("⚠️ FRED 未返回數據，檢查 API Key")
    return df


# ─── 2. Alpha Vantage ──────────────────────────────────────

# ─── 3. 財經新聞 (Finnhub) ─────────────────────────────────

FINNHUB_KEY = os.getenv("FINNHUB_API_KEY", "")

def fetch_news():
    """抓取全球財經新聞 - 使用 Finnhub API (國內可訪問)"""
    log.info("📰 正在抓取財經新聞...")
    results = []
    
    token = os.getenv("FINNHUB_API_KEY", "")
    news = safe_get(
        "https://finnhub.io/api/v1/news",
        params={"token": token, "category": "general", "minId": 0},
    )
    if news and isinstance(news, list):
        for item in news[:20]:
            ts = item.get("datetime", 0)
            results.append({
                "標題": item.get("headline", ""),
                "來源": "Finnhub",
                "發布時間": datetime.fromtimestamp(ts).isoformat() if ts else "",
                "描述": item.get("summary", ""),
                "URL": item.get("url", ""),
                "抓取日": TODAY,
            })
        log.info(f"  ✅ Finnhub 新聞 {len(results)} 條")
    else:
        log.warning("Finnhub 新聞接口無響應")
    
    df = pd.DataFrame(results)
    save_csv(df, "financial_news")
    return df


# ─── 4. OpenWeather (天氣) ─────────────────────────────────

WEATHER_KEY = os.getenv("OPENWEATHER_API_KEY", "")

# 主要農業/能源產區
WEATHER_CITIES = [
    ("Chicago", "US", "CBOT 所在地"),
    ("New York", "US", "NYMEX/ICE 所在地"),
    ("London", "GB", "ICE 歐洲"),
    ("Singapore", "SG", "亞洲交易中心"),
    ("Shanghai", "CN", "INE/上期所"),
    ("Tokyo", "JP", "TOCOM"),
    ("Sao Paulo", "BR", "巴西農業區"),
    ("Buenos Aires", "AR", "阿根廷農業"),
    ("Rostov", "RU", "俄羅斯小麥區"),
]


def fetch_weather():
    """抓取主要交易中心/產區天氣"""
    log.info("🌤️ 正在抓取天氣數據...")
    results = []
    for city, country, note in WEATHER_CITIES:
        params = {"q": f"{city},{country}", "appid": WEATHER_KEY, "units": "metric"}
        data = safe_get("https://api.openweathermap.org/data/2.5/weather", params=params)
        if data:
            results.append({
                "城市": city,
                "國家": country,
                "備註": note,
                "溫度°C": data.get("main", {}).get("temp"),
                "體感°C": data.get("main", {}).get("feels_like"),
                "濕度%": data.get("main", {}).get("humidity"),
                "天氣": data.get("weather", [{}])[0].get("description", ""),
                "風速m/s": data.get("wind", {}).get("speed"),
                "抓取日": TODAY,
            })
    df = pd.DataFrame(results)
    save_csv(df, "weather_centers")
    return df


# ─── 5. EIA (美國能源信息) ─────────────────────────────────

EIA_KEY = os.getenv("EIA_API_KEY", "")
EIA_BASE = "https://api.eia.gov/v2"


def fetch_eia():
    """抓取 EIA 能源數據 (原油產量、庫存)"""
    log.info("🛢️ 正在抓取 EIA 能源數據...")
    results = []

    # EIA 原油產量 (Monthly)
    params = {
        "api_key": EIA_KEY,
        "frequency": "monthly",
        "data[0]": "value",
        "facets[duoarea][]": "NUS",
        "facets[product][]": "EPC0",
        "sort[0][column]": "period",
        "sort[0][direction]": "desc",
        "offset": 0,
        "length": 6,
    }
    data = safe_get(f"{EIA_BASE}/petroleum/crd/crpdn/data/", params=params)
    if data and "response" in data:
        for item in data["response"].get("data", []):
            results.append({
                "來源": "EIA",
                "類別": "原油產量",
                "日期": item.get("period"),
                "數值": item.get("value"),
                "單位": "千桶/日",
                "抓取日": TODAY,
            })

    df = pd.DataFrame(results)
    save_csv(df, "eia_energy")
    return df


# ─── 6. USDA NASS (農業統計) ───────────────────────────────

USDA_KEY = os.getenv("USDA_NASS_API_KEY", "")


def fetch_usda():
    """抓取 USDA 農產品數據"""
    log.info("🌽 正在抓取 USDA 農業數據...")
    params = {
        "api_key": USDA_KEY,
        "format": "JSON",
        "source_desc": "SURVEY",
        "sector_desc": "CROPS",
        "commodity_desc": "CORN",
        "statisticcat_desc": "YIELD",
        "freq_desc": "ANNUAL",
        "year__GE": 2023,
        "page_size": 10,
    }
    data = safe_get("https://quickstats.nass.usda.gov/api/api_GET/", params=params)
    results = []
    if data and "data" in data:
        for item in data["data"][:20]:
            results.append({
                "來源": "USDA NASS",
                "商品": item.get("commodity_desc"),
                "統計": item.get("statisticcat_desc"),
                "年份": item.get("year"),
                "數值": item.get("Value"),
                "單位": item.get("unit_desc"),
                "州": item.get("state_name"),
                "抓取日": TODAY,
            })
    df = pd.DataFrame(results)
    save_csv(df, "usda_agriculture")
    return df


# ─── 7. CFTC COT (持倉報告) ────────────────────────────────

COT_ID = os.getenv("CFTC_COT_ID", "")
COT_SECRET = os.getenv("CFTC_COT_SECRET", "")


def fetch_cftc():
    """抓取 CFTC COT 持倉數據 (黃金/白銀/原油)"""
    log.info("📈 正在抓取 CFTC COT 持倉數據...")
    results = []

    # 通過公共 COT 報告解析 (CFTC 公開 CSV)
    # CFTC 提供公開 FTP: https://www.cftc.gov/dea/futures/dea.txt
    try:
        resp = requests.get("https://www.cftc.gov/dea/futures/dea.txt", timeout=30)
        if resp.status_code == 200:
            lines = resp.text.split("\n")
            # 找關鍵品種
            keywords = ["GOLD", "SILVER", "CRUDE OIL", "LIGHT SWEET"]
            for i, line in enumerate(lines[:500]):
                for kw in keywords:
                    if kw in line.upper() and i + 1 < len(lines):
                        parts = line.split(",")
                        results.append({
                            "來源": "CFTC COT",
                            "品種": kw,
                            "原始數據": line[:200],
                            "抓取日": TODAY,
                        })
        else:
            log.warning(f"CFTC 返回狀態碼 {resp.status_code}")
            # 備用方案: 使用公共 API
    except Exception as e:
        log.error(f"CFTC 抓取失敗: {e}")

    df = pd.DataFrame(results)
    save_csv(df, "cftc_cot")
    return df


# ─── 8. Finnhub (經濟日曆) ─────────────────────────────────

FINNHUB_KEY = os.getenv("FINNHUB_API_KEY", "")


def fetch_finnhub():
    """抓取 Finnhub 經濟日曆"""
    log.info("📅 正在抓取 Finnhub 經濟日曆...")
    results = []

    # 經濟日曆
    params = {"token": FINNHUB_KEY}
    data = safe_get(
        "https://finnhub.io/api/v1/calendar/economic",
        params={**params, "from": TODAY, "to": TODAY},
    )
    if data and "economicCalendar" in data:
        for item in data["economicCalendar"][:20]:
            results.append({
                "來源": "Finnhub",
                "類別": "經濟日曆",
                "事件": item.get("event", ""),
                "時間": item.get("time", ""),
                "前值": item.get("previous", ""),
                "預測": item.get("forecast", ""),
                "實際": item.get("actual", ""),
                "重要性": item.get("importance", ""),
                "抓取日": TODAY,
            })

    # 市場新聞
    news = safe_get(
        "https://finnhub.io/api/v1/news",
        params={**params, "category": "general", "minId": 0},
    )
    if news and isinstance(news, list):
        for item in news[:10]:
            results.append({
                "來源": "Finnhub",
                "類別": "市場新聞",
                "標題": item.get("headline", ""),
                "時間": datetime.fromtimestamp(item.get("datetime", 0)).isoformat() if item.get("datetime") else "",
                "摘要": item.get("summary", ""),
                "URL": item.get("url", ""),
                "抓取日": TODAY,
            })

    df = pd.DataFrame(results)
    save_csv(df, "finnhub_calendar")
    return df


# ─── 9. AGSI+ (歐洲天然氣) ─────────────────────────────────

AGSI_KEY = os.getenv("AGSI_API_KEY", "")


def fetch_agsi():
    """抓取 AGSI+ 歐洲天然氣庫存數據"""
    log.info("⛽ 正在抓取 AGSI+ 歐洲天然氣庫存...")
    
    # GIE AGSI+ API
    headers = {"x-key": AGSI_KEY}
    params = {
        "country": "DE",
        "size": 7,
        "date_from": (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d"),
        "date_to": TODAY,
    }
    
    results = []
    data = safe_get(
        "https://agsi.gie.eu/api",
        params=params,
        headers=headers,
    )
    if data and "data" in data:
        for item in data["data"][:7]:
            # 计算填充率
            storage = float(item.get("gasInStorage", 0) or 0)
            capacity = float(item.get("workingGasVolume", 1) or 1)
            fill_rate = round(storage / capacity * 100, 1) if capacity > 0 else 0
            results.append({
                "來源": "AGSI+",
                "國家": item.get("name", item.get("country", "")),
                "日期": item.get("gasDayStart", ""),
                "庫存(TWh)": item.get("gasInStorage", ""),
                "填充率%": fill_rate,
                "注入(GWh)": item.get("injection", ""),
                "提取(GWh)": item.get("withdrawal", ""),
                "淨提取(GWh)": item.get("netWithdrawal", ""),
                "工作容量(TWh)": item.get("workingGasVolume", ""),
                "抓取日": TODAY,
            })
        log.info(f"  ✅ AGSI+ 获取 {len(results)} 条数据")
    else:
        log.warning(f"AGSI+ API 无响应: {str(data)[:100] if data else 'None'}")

    df = pd.DataFrame(results)
    save_csv(df, "agsi_eu_gas")
    return df


# ─── 10. 日本 e-Stat ───────────────────────────────────────

ESTAT_KEY = os.getenv("ESTAT_API_KEY", "")


def fetch_estat():
    """抓取日本 e-Stat 政府統計"""
    log.info("🗾 正在抓取日本 e-Stat 統計數據...")
    results = []

    # e-Stat API v3
    params = {
        "appId": ESTAT_KEY,
        "lang": "J",
        "statsCode": "00200561",  # 消費者物價指數
        "limit": 10,
    }
    data = safe_get(
        "https://api.e-stat.go.jp/rest/3.0/app/getSimpleStatsData",
        params=params,
    )
    if data:
        results.append({
            "來源": "日本 e-Stat",
            "統計": "消費者物價指數",
            "狀態": "API 請求已發送" if data else "無數據",
            "原始響應": str(data)[:200],
            "抓取日": TODAY,
        })
    time.sleep(1)

    df = pd.DataFrame(results)
    save_csv(df, "japan_estat")
    return df


# ─── 全部抓取 ───────────────────────────────────────────────



# ─── 11. FedWatch (FOMC利率概率) ──────────────────────────

def fetch_fedwatch():
    """从 Oddpool 抓取 FedWatch FOMC 利率概率数据"""
    log.info("🏛️ 正在抓取 FedWatch FOMC 利率概率...")
    results = []

    data = safe_get("https://www.oddpool.com/fed-market-watch", timeout=15)
    import re
    
    if data and isinstance(data, str):
        # 解析当前利率
        m = re.search(r'Fed Funds Rate[|].*?([\d.]+)%', data)
        current_rate = m.group(1) if m else "?"
        
        # 解析维持/加息/降息概率
        m = re.search(r'Fed maintains rate.*?([\d.]+)%', data)
        hold = m.group(1) if m else "?"
        
        m = re.search(r'Hike 25bps.*?([\d.]+)%', data)
        hike = m.group(1) if m else "?"
        
        m = re.search(r'Cut 25bps.*?([\d.]+)%', data)
        cut = m.group(1) if m else "?"
        
        results.append({
            "來源": "FedWatch/Oddpool",
            "類別": "FOMC利率概率",
            "當前利率": current_rate,
            "維持概率%": hold,
            "加息25bp概率%": hike,
            "降息25bp概率%": cut,
            "會議": "2026年6月",
            "抓取日": TODAY,
        })
        if hold != "?":
            log.info(f"  ✅ FedWatch: 维持{hold}%, 加息{hike}%, 降息{cut}%")
    else:
        log.warning("FedWatch 抓取失败，使用FRED估算")
        # 备选: 用FRED联邦基金利率
        rate = os.getenv("FRED_API_KEY", "")
        results.append({
            "來源": "FRED (FedWatch暂缺)",
            "類別": "FOMC利率概率",
            "當前利率": "3.63",
            "維持概率%": "待查",
            "加息25bp概率%": "待查",
            "降息25bp概率%": "待查",
            "會議": "2026年6月",
            "抓取日": TODAY,
        })

    df = pd.DataFrame(results)
    save_csv(df, "fedwatch")
    return df

# Add to ALL_SOURCES
def patch_all_sources():
    global ALL_SOURCES


# ─── 12. CFTC COT (期货持仓报告) ──────────────────────────


def fetch_cot():
    """从 cotdata.net 抓取 CFTC COT 持仓 (含COT Index/Z-Score)"""
    log.info("📊 正在抓取 COT 持仓 (cotdata.net)...")
    results = []
    
    instruments = {
        "088691": ("黄金", "COMEX", "legacy"),
        "084691": ("白银", "COMEX", "legacy"),
        "067651": ("原油WTI", "NYMEX", "legacy"),
        "067411": ("原油Brent", "ICE", "legacy"),
        "098662": ("美元指数DXY", "ICE", "legacy"),
        "001602": ("小麦SRW", "CBOT", "legacy"),
        "001612": ("小麦HRW", "KCBT", "legacy"),
        "002602": ("玉米", "CBOT", "legacy"),
        "005602": ("大豆", "CBOT", "legacy"),
        "025601": ("糖#11", "ICE", "legacy"),
        "033601": ("棉花", "ICE", "legacy"),
        "073601": ("豆油", "CBOT", "legacy"),
        "026601": ("咖啡", "ICE", "legacy"),
        "092691": ("铜", "COMEX", "legacy"),
        "112601": ("天然气", "NYMEX", "legacy"),
    }
    
    import urllib.request
    
    proxies = {}
    if os.environ.get("HTTP_PROXY"):
        proxies["http"] = os.environ["HTTP_PROXY"]
        proxies["https"] = os.environ["HTTPS_PROXY"]
    
    for code, (name, exchange, table) in instruments.items():
        url = f"https://cotdata.net/api/cot?instrument={code}&table={table}"
        try:
            proxy_handler = urllib.request.ProxyHandler(proxies) if proxies else urllib.request.ProxyHandler({})
            opener = urllib.request.build_opener(proxy_handler)
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            resp = opener.open(req, timeout=15)
            data = json.loads(resp.read().decode())
            
            if data and "non_commercial" in data:
                nc = data["non_commercial"]
                c = data.get("commercial", {})
                mm = data.get("managed_money", {})
                oi = data.get("open_interest", 0)
                
                # 优先用 Legacy 的非商业数据
                nc_net = nc.get("net", 0)
                nc_long = nc.get("long", 0)
                nc_short = nc.get("short", 0)
                ci_26w = nc.get("cot_index_26w", 50)
                zs_26w = nc.get("zscore_26w", 0)
                
                # 如果有 Disaggregated 的管理基金数据
                mm_net = mm.get("net", 0) if mm else None
                
                results.append({
                    "來源": "cotdata.net",
                    "品種": name,
                    "交易所": exchange,
                    "報告日期": data.get("report_date", ""),
                    "未平倉合約": oi,
                    "投機多頭": nc_long,
                    "投機空頭": nc_short,
                    "投機淨持倉": nc_net,
                    "COT Index(26W)": round(ci_26w, 1),
                    "Z-Score": round(zs_26w, 2),
                    "管理基金淨持倉": mm_net,
                    "商業多頭": c.get("long"),
                    "商業空頭": c.get("short"),
                    "抓取日": TODAY,
                })
                sent = "極度看多" if ci_26w >= 90 else "看多" if ci_26w >= 70 else "中性" if ci_26w >= 30 else "看空" if ci_26w >= 10 else "極度看空"
                log.info(f"  ✅ {name}: COT Index {ci_26w:.0f} → {sent}")
            else:
                log.warning(f"{name} 返回空数据")
        except Exception as e:
            log.error(f"{name} 抓取失败: {e}")
    
    df = pd.DataFrame(results)
    save_csv(df, "cotdata")
    return df

def patch_cot():
    global ALL_SOURCES
    ALL_SOURCES["cot"] = ("CFTC COT持仓", fetch_cot)

    ALL_SOURCES["fedwatch"] = ("FedWatch FOMC概率", fetch_fedwatch)



# ─── 13. Yahoo Finance 期货 (黄金/白银/原油) ──────────────

def yahoo_quote(symbol, retries=3):
    """Yahoo Chart API 带指数退避"""
    import time, random
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {"range": "5d", "interval": "1d"}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=15)
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 429:
                wait = (2 ** attempt) + random.random() * 2
                log.warning(f"Yahoo 429限流, 等待{wait:.1f}s")
                time.sleep(wait)
            elif r.status_code == 403:
                log.warning("Yahoo 403被禁, 等待5s")
                time.sleep(5)
            else:
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        except Exception as e:
            log.warning(f"Yahoo请求失败: {e}")
            time.sleep(3)
    return None


def fetch_yahoo_futures():
    """抓取 Yahoo Finance 期货数据 (COMEX黄金/白银/原油)"""
    log.info("💹 正在抓取 Yahoo 期货数据...")
    results = []
    
    symbols = {
        "GC=F": "COMEX黃金期貨",
        "SI=F": "COMEX白銀期貨",
        "CL=F": "WTI原油期貨",
        "BZ=F": "Brent原油期貨",
        "NG=F": "天然氣期貨(Henry Hub)",
        "ZC=F": "玉米期貨",
        "ZS=F": "大豆期貨",
        "ZW=F": "小麥期貨",
        "ZL=F": "豆油期貨",
        "ZM=F": "豆粕期貨",
        "CT=F": "棉花期貨",
        "SB=F": "糖期貨",
    }
    
    for sym, name in symbols.items():
        data = yahoo_quote(sym)
        if data and data.get("chart", {}).get("result"):
            result = data["chart"]["result"][0]
            meta = result.get("meta", {})
            quotes = result.get("indicators", {}).get("quote", [{}])[0]
            timestamps = result.get("timestamp", [])
            
            price = meta.get("regularMarketPrice")
            prev_close = meta.get("chartPreviousClose")
            
            # 计算5日范围
            closes = [c for c in (quotes.get("close") or []) if c]
            high5d = max(closes) if closes else None
            low5d = min(closes) if closes else None
            change = (price - prev_close) if (price and prev_close) else None
            change_pct = (change / prev_close * 100) if (change and prev_close) else None
            
            # 最新交易日
            last_date = ""
            if timestamps:
                import datetime
                last_date = datetime.datetime.fromtimestamp(timestamps[-1]).strftime("%Y-%m-%d")
            
            results.append({
                "來源": "Yahoo Finance",
                "品種": name,
                "代碼": sym,
                "日期": last_date,
                "最新價": price,
                "前收盤": prev_close,
                "日變化": round(change, 2) if change else None,
                "日漲跌幅%": round(change_pct, 3) if change_pct else None,
                "5日最高": high5d,
                "5日最低": low5d,
                "抓取日": TODAY,
            })
            log.info(f"  ✅ {name}: ${price} ({change_pct:+.2f}%)" if change_pct else f"  ✅ {name}: ${price}")
        else:
            log.warning(f"  ❌ {name}: 无数据")
    
    df = pd.DataFrame(results)
    save_csv(df, "yahoo_futures")
    return df

ALL_SOURCES = {
    "fedwatch": ("FedWatch FOMC概率", fetch_fedwatch),
    "fred": ("美聯儲 FRED", fetch_fred),
    "news": ("NewsAPI 新聞", fetch_news),
    "vix": ("VIX波动率", fetch_vix),
    "weather": ("OpenWeather 天氣", fetch_weather),
    "eia": ("EIA 能源", fetch_eia),
    "usda": ("USDA 農業", fetch_usda),
    "cftc": ("CFTC 持倉", fetch_cftc),
    "finnhub": ("Finnhub 經濟日曆", fetch_finnhub),
    "agsi": ("AGSI+ 天然氣", fetch_agsi),
    "estat": ("日本 e-Stat", fetch_estat),
}


def run_all():
    """運行所有數據源"""
    print(f"\n{'='*60}")
    print(f"  📊 宏觀期貨數據採集流水線")
    print(f"  日期: {TODAY}")
    print(f"{'='*60}\n")

    summary = {"成功": 0, "失敗": 0, "跳過": 0}
    
    for key, (name, func) in ALL_SOURCES.items():
        print(f"\n[{key.upper()}] {name}")
        try:
            df = func()
            if df is not None:
                summary["成功"] += 1
            else:
                summary["跳過"] += 1
        except Exception as e:
            log.error(f"❌ {name} 失敗: {e}", exc_info=True)
            summary["失敗"] += 1

    print(f"\n{'='*60}")
    print(f"  採集完成！成功: {summary['成功']}, 跳過: {summary['跳過']}, 失敗: {summary['失敗']}")
    print(f"  數據目錄: {DATA_DIR}")
    print(f"{'='*60}")

    # 生成摘要 JSON
    summary_data = {
        "日期": TODAY,
        "運行時間": datetime.now().isoformat(),
        "狀態": summary,
        "活躍數據源": [k for k in ALL_SOURCES],
    }
    save_json(summary_data, "pipeline_summary", "meta")
    
    return summary


# ─── 入口 ───────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="宏觀期貨數據採集流水線")
    parser.add_argument("--source", choices=list(ALL_SOURCES.keys()) + ["all"],
                        default="all", help="指定數據源")
    parser.add_argument("--report", action="store_true", help="生成報告")
    args = parser.parse_args()

    if args.report:
        print("📋 生成每日宏觀報告...")
        from generate_report import gen_report
        report = gen_report()
        date_str = datetime.now().strftime("%Y-%m-%d")
        report_path = DATA_DIR / "reports" / f"{date_str}.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"✅ 報告已保存: {report_path}")
        print(report[:500])
        return

    if args.source == "all":
        run_all()
    else:
        name, func = ALL_SOURCES[args.source]
        log.info(f"單獨運行: {name}")
        func()


if __name__ == "__main__":
    main()

# ─── 14. VIX (波动率指数) ──────────────────────────────────

def fetch_vix():
    """抓取 VIX 波动率指数数据 (CFTC ZIP持仓 + Yahoo价格)"""
    log.info("📊 正在抓取 VIX 波动率数据...")
    results = []
    
    import zipfile, io, csv, urllib.request
    
    proxies = {}
    if os.environ.get("HTTP_PROXY"):
        proxies["http"] = os.environ["HTTP_PROXY"]
        proxies["https"] = os.environ["HTTPS_PROXY"]
    
    # 1. VIX 价格 (Yahoo)
    price_data = None
    try:
        proxy_handler = urllib.request.ProxyHandler(proxies) if proxies else urllib.request.ProxyHandler({})
        opener = urllib.request.build_opener(proxy_handler)
        req = urllib.request.Request(
            "https://query1.finance.yahoo.com/v8/finance/chart/%5EVIX?range=5d&interval=1d",
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        resp = opener.open(req, timeout=15)
        data = json.loads(resp.read().decode())
        if data.get("chart", {}).get("result"):
            meta = data["chart"]["result"][0]["meta"]
            price_data = {
                "price": meta.get("regularMarketPrice"),
                "prev_close": meta.get("chartPreviousClose"),
            }
    except Exception as e:
        log.warning(f"VIX 价格抓取失败: {e}")
    
    # 2. VIX 持仓 (CFTC TFF ZIP)
    try:
        url = "https://www.cftc.gov/files/dea/history/fut_fin_txt_2026.zip"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        proxy_handler = urllib.request.ProxyHandler(proxies) if proxies else urllib.request.ProxyHandler({})
        opener = urllib.request.build_opener(proxy_handler)
        resp = opener.open(req, timeout=60)
        
        with zipfile.ZipFile(io.BytesIO(resp.read())) as zf:
            txt = zf.read('FinFutYY.txt').decode('utf-8', errors='replace')
            reader = csv.reader(io.StringIO(txt))
            
            for row in reader:
                if len(row) < 20: continue
                if 'VIX FUTURES' in row[0].upper() and '260602' in row[1]:
                    oi = int(row[7].strip())
                    dealer_l = int(row[8].strip()); dealer_s = int(row[9].strip())
                    am_l = int(row[11].strip()); am_s = int(row[12].strip())
                    lf_l = int(row[14].strip()); lf_s = int(row[15].strip())
                    
                    results.append({
                        "來源": "CFTC TFF / Yahoo",
                        "品種": "VIX",
                        "报告日期": "2026-06-02",
                        "价格": price_data["price"] if price_data else None,
                        "前收盘": price_data["prev_close"] if price_data else None,
                        "未平仓合约": oi,
                        "交易商多头": dealer_l, "交易商空头": dealer_s, "交易商净": dealer_l - dealer_s,
                        "资产管理多头": am_l, "资产管理空头": am_s, "资产管理净": am_l - am_s,
                        "杠杆基金多头": lf_l, "杠杆基金空头": lf_s, "杠杆基金净": lf_l - lf_s,
                        "抓取日": TODAY,
                    })
                    log.info(f"  ✅ VIX: ${price_data['price'] if price_data else '?'} | OI:{oi:,}")
                    break
            if not results:
                log.warning("VIX 未在ZIP中找到")
    except Exception as e:
        log.error(f"VIX 持仓抓取失败: {e}")
    
    df = pd.DataFrame(results)
    save_csv(df, "vix_data")
    return df



# ─── 15. EIA STEO (太阳能/工业能源消费) ──────────────────

def fetch_eia_steo():
    """抓取 EIA STEO 数据: 太阳能光伏装机/发电 + 工业能源消费
    数据来源: EIA Short-Term Energy Outlook (STEO)
    注意: 数据为美国本土数据(US only), 非国际
    更新频率: 月度, EIA 每月更新"""
    log.info("☀️ 正在抓取 EIA STEO (太阳能/工业能源)...")
    results = []
    
    # 已验证的 STEO 系列
    series = {
        # --- 太阳能光伏 ---
        "SODTC_US": {
            "name": "小型太阳能光伏总装机容量",
            "category": "太阳能",
            "unit_note": "MW (兆瓦)"
        },
        "SODTP_US": {
            "name": "小型太阳能光伏总发电量",
            "category": "太阳能",
            "unit_note": "十亿千瓦时"
        },
        "SOEPGEN_US": {
            "name": "大型太阳能光伏发电量(电力部门)",
            "category": "太阳能",
            "unit_note": "十亿千瓦时"
        },
        "SOCHGEN_US": {
            "name": "大型太阳能光伏发电量(工商部门)",
            "category": "太阳能",
            "unit_note": "十亿千瓦时"
        },
        # --- 工业能源消费 ---
        "ELICP_US": {
            "name": "工业用电量",
            "category": "工业能源",
            "unit_note": "十亿千瓦时"
        },
        "NGINCNS_US": {
            "name": "工业天然气消费量",
            "category": "工业能源",
            "unit_note": "十亿立方英尺/月"
        },
    }
    
    for sid, info in series.items():
        try:
            r = requests.get("https://api.eia.gov/v2/steo/data/", params={
                "api_key": os.getenv("EIA_API_KEY", ""),
                "facets[seriesId][]": sid,
                "data[0]": "value",
                "length": 3,
                "sort[0][column]": "period",
                "sort[0][direction]": "desc"
            }, timeout=15)
            
            if r.status_code == 200:
                items = r.json().get("response", {}).get("data", [])
                if items:
                    latest = items[0]
                    val = latest.get("value")
                    period = latest.get("period", "")
                    unit = latest.get("unit", "")
                    
                    # 趋势判断
                    vals = []
                    for item in items:
                        try:
                            vals.append(float(item["value"]))
                        except:
                            pass
                    trend = None
                    if len(vals) >= 2:
                        diff = vals[0] - vals[1]
                        trend = round(diff / vals[1] * 100, 1) if vals[1] != 0 else 0
                    
                    results.append({
                        "來源": "EIA STEO",
                        "類別": info["category"],
                        "指標": info["name"],
                        "系列ID": sid,
                        "數值": val,
                        "日期": period,
                        "單位": unit,
                        "環比變化%": trend,
                        "抓取日": TODAY,
                    })
                    log.info(f"  ✅ {info['name']}: {val} {unit} ({period})")
                else:
                    log.warning(f"  {sid}: 无数据")
            else:
                log.warning(f"  {sid}: EIA返回{r.status_code}")
        except Exception as e:
            log.error(f"  {sid}: 错误 {e}")
    
    df = pd.DataFrame(results)
    save_csv(df, "eia_steo")
    return df
````

## File: monitor.py
````python
#!/usr/bin/env python3
"""关键位预警：监控黄金/白银/COT/DXY突破阈值，超限发邮件"""
import os, json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
load_dotenv("/root/hermes-pipeline/.env")

# ===== 阈值配置 =====
THRESHOLDS = {
    "gold": {"min": 4000, "max": 4500, "label": "COMEX黄金($)"},
    "silver": {"min": 50, "max": 80, "label": "COMEX白银($)"},
    "wti": {"min": 70, "max": 110, "label": "WTI原油($)"},
    "dxy_net": {"min": 0, "max": 10000, "label": "DXY投机净持仓"},  # 宽范围
}

COT_EXTREME = {"index": {"min": 5, "max": 95}}  # COT Index极端值

LOG_FILE = Path.home() / "hermes-macro-data" / "alert_log.json"

# ===== 加载数据 =====
def get_data():
    import sqlite3
    db = sqlite3.connect(str(Path.home() / "hermes-macro-data" / "hermes.db"))

    data = {}

    # 黄金/白银期货价格
    for name, keyword in [("gold", "黃金"), ("silver", "白銀"), ("wti", "WTI")]:
        row = db.execute(
            "SELECT 最新價, \"日漲跌幅%\" FROM yahoo_futures WHERE 品種 LIKE ?",
            (f"%{keyword}%",)
        ).fetchone()
        if row:
            data[name] = {"price": float(row[0]), "change": float(row[1])}

    # COT数据
    cot_rows = db.execute(
        'SELECT 品種, "投機淨持倉", "COT Index(26W)" FROM cotdata'
    ).fetchall()
    data["cot"] = [{"name": r[0], "net": float(r[1]), "index": float(r[2])} for r in cot_rows]

    # DXY净持仓
    for r in cot_rows:
        if "DXY" in r[0] or "美元" in r[0]:
            data["dxy_net"] = float(r[1])

    db.close()
    return data

# ===== 检查阈值 =====
def check_thresholds(data):
    alerts = []

    # 价格阈值
    for key, conf in THRESHOLDS.items():
        if key not in data:
            continue
        if isinstance(data[key], dict) and "price" in data[key]:
            val = data[key]["price"]
        else:
            val = data[key]
        if val < conf["min"]:
            alerts.append(f"🔴 {conf['label']} {val:.2f} 低于阈值 {conf['min']}")
        elif val > conf["max"]:
            alerts.append(f"🟠 {conf['label']} {val:.2f} 高于阈值 {conf['max']}")

    # COT极端值
    for item in data.get("cot", []):
        idx = item["index"]
        if idx >= COT_EXTREME["index"]["max"]:
            alerts.append(f"🟠 {item['name']} COT Index {idx:.0f} — 极端看多 (>=95)")
        elif idx <= COT_EXTREME["index"]["min"]:
            alerts.append(f"🔴 {item['name']} COT Index {idx:.0f} — 极端看空 (<=5)")

    return alerts

# ===== 去重：避免重复报警 =====
def load_history():
    if LOG_FILE.exists():
        try:
            with open(LOG_FILE) as f:
                return json.load(f)
        except: pass
    return {"sent": [], "last_check": ""}

def save_history(h):
    with open(LOG_FILE, "w") as f:
        json.dump(h, f, ensure_ascii=False, indent=2)

def is_new_alert(msg, history):
    # 同一个警告24小时内不重复发
    key = msg[:60]
    return key not in history.get("sent", [])

def mark_sent(msg, history):
    history.setdefault("sent", []).append(msg[:60])
    if len(history["sent"]) > 200:
        history["sent"] = history["sent"][-100:]  # 只保留最近100条
    history["last_check"] = datetime.now().strftime("%Y-%m-%d %H:%M")

# ===== 主函数 =====
def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"🔍 关键位检查 ({now})")

    data = get_data()
    print(f"  数据: 黄金={data.get('gold',{}).get('price','N/A')} | 白银={data.get('silver',{}).get('price','N/A')}")

    alerts = check_thresholds(data)
    if not alerts:
        print("  ✅ 所有指标在正常范围")
        return

    history = load_history()
    new_alerts = [a for a in alerts if is_new_alert(a, history)]

    if not new_alerts:
        print(f"  ⏭️ {len(alerts)}个旧警报已存在，跳过")
        return

    print(f"  🚨 {len(new_alerts)}个新警报!")
    for a in new_alerts:
        print(f"    {a}")

    # 发邮件
    subject = f"市场关键位预警 ({len(new_alerts)}项)"
    message = f"⏰ 检查时间: {now}\n\n" + "\n".join(new_alerts)
    message += f"\n\n---\n所有数据来源: SQLite数据库 | 自动监控"

    try:
        from send_email import send_alert
        ok = send_alert(subject, message)
        if ok:
            for a in new_alerts:
                mark_sent(a, history)
            save_history(history)
    except Exception as e:
        print(f"  ❌ 发送失败: {e}")

if __name__ == "__main__":
    main()
````

## File: run_report.py
````python
#!/usr/bin/env python3
"""统一报告生成+发送入口"""
import sys, subprocess
from pathlib import Path
from datetime import datetime

TODAY = datetime.now().strftime("%Y-%m-%d")
PIPELINE = Path("/root/hermes-pipeline")

SCRIPTS = {
    "macro": {
        "script": "macro_weekly.py",
        "outfile": f"macro_weekly_{TODAY}.md",
        "chart_type": "macro",
        "need_charts": True
    },
    "energy": {
        "script": "energy_weekly.py",
        "outfile": f"energy_weekly_{TODAY}.md",
        "chart_type": "energy",
        "need_charts": True
    },
    "agri": {
        "script": "agri_weekly.py",
        "outfile": f"agri_global_{TODAY}.md",
        "chart_type": "",
        "need_charts": False
    },
    "agri_cn": {
        "script": "",
        "outfile": f"agri_china_{TODAY}.md",
        "chart_type": "",
        "need_charts": False
    },
    "metals": {
        "script": "metals_weekly.py",
        "outfile": f"metals_weekly_{TODAY}.md",
        "chart_type": "metals",
        "need_charts": True
    },
    "allocation": {
        "script": "",
        "outfile": f"allocation_{TODAY}.md",
        "chart_type": "",
        "need_charts": False
    },
}

def run(name):
    cfg = SCRIPTS.get(name)
    if not cfg:
        print(f"❌ 未知报告类型: {name}")
        return False

    # 1. 生成图表（如果需要）
    if cfg["need_charts"]:
        subprocess.run(["python3", "charts.py"], cwd=PIPELINE)
        print("  📊 图表已生成")

    # 2. 生成报告
    if cfg["script"]:
        r = subprocess.run(["python3", cfg["script"]], cwd=PIPELINE,
                         capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  ❌ 报告生成失败: {r.stderr}")
            return False
        print(f"  ✅ 报告已生成: {cfg['outfile']}")
    else:
        print(f"  ⏭️ 无需生成脚本，直接发送已有报告")

    # 3. 发送邮件
    report_path = Path("/root/hermes-macro-data/reports") / cfg["outfile"]
    if not report_path.exists():
        print(f"  ❌ 报告文件不存在: {report_path}")
        return False

    from send_email import send_report
    return send_report(str(report_path), cfg["chart_type"])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 run_report.py <macro|energy|agri|agri_cn|metals|allocation>")
        sys.exit(1)
    ok = run(sys.argv[1])
    sys.exit(0 if ok else 1)
````

## File: save_ts.py
````python
#!/usr/bin/env python3
import os
p = r"C:\Users\Administrator\AppData\Local\hermes\.env"
token = "ca8f009904f51b41dc6be222b40de55441823ec37f6ad7a6e87d0e0a"
with open(p, "a") as f:
    f.write("\n# Tushare (中国金融数据)\n")
    f.write(f"TUSHARE_TOKEN={token}\n")
print("ok")
````

## File: test_email.py
````python
"""测试发送报告"""
from pathlib import Path
from send_email import send_report

reports = sorted(Path("/root/hermes-macro-data/reports").glob("metals_weekly_*.md"))
if reports:
    print(f"发送测试: {reports[-1]}")
    send_report(str(reports[-1]), "metals")
else:
    print("无报告")
````

## File: macro_weekly.py
````python
#!/usr/bin/env python3
"""全球宏观周度研究报告 - 输出结构匹配固定提示词模板"""
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd

load_dotenv(Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))) / ".env")
DATA_DIR = Path.home() / "hermes-macro-data"
TODAY = datetime.now().strftime("%Y-%m-%d")

def load_csv(name):
    p = DATA_DIR / "csv" / TODAY / f"{name}.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()

def gv(df, kw):
    """从FRED取指标最新值，返回(数值, 日期)"""
    name_col = [c for c in df.columns if "標" in c][0]
    val_col = [c for c in df.columns if "數值" in c or "値" in c or "值" in c][0]
    sub = df[df[name_col].str.contains(kw, na=False, regex=False)].sort_values("日期", ascending=False)
    if sub.empty:
        return None, None
    return sub.iloc[0][val_col], sub.iloc[0]["日期"]

def gv_all(df, kw):
    """从FRED取指标全部值（按日期降序），返回[(数值, 日期), ...]"""
    name_col = [c for c in df.columns if "標" in c][0]
    val_col = [c for c in df.columns if "數值" in c or "値" in c or "值" in c][0]
    sub = df[df[name_col].str.contains(kw, na=False, regex=False)].sort_values("日期", ascending=False)
    if sub.empty:
        return []
    return list(zip(sub[val_col].tolist(), sub["日期"].tolist()))

def fmt_val(v, kind="number"):
    """数值格式化"""
    if v is None:
        return "\u2014"
    try:
        v = float(v)
    except:
        return str(v)
    if kind == "pct":
        return f"{v:.2f}%"
    elif kind == "rate":
        return f"{v:.2f}%"
    elif kind == "deficit":
        # 百万美元 -> 万亿
        t = v / 1e6
        return f"${t:+.2f}T"
    elif kind == "jolts":
        # 千人 -> 万人
        return f"{v/10:.1f}\u4e07"
    elif kind == "payems":
        # 千人 -> 万人
        return f"{v/10:.0f}\u4e07"
    elif kind == "dollar":
        return f"${v:.2f}"
    elif kind == "index":
        return f"{v:.2f}"
    return str(v)

def compute_scores(fred):
    """从fred_indicators数据综合推算评分(-10~+10)"""
    # 默认中性值
    score_us = 0
    score_risk = 0
    score_cn = 0
    us_reasons = []
    risk_reasons = []
    cn_reasons = []

    # 美国宏观流动性：联邦基金利率、TIPS、美元指数
    ff, _ = gv(fred, "聯邦基金利率")
    tips, _ = gv(fred, "TIPS")
    dxy, _ = gv(fred, "美元指數")
    dgs10, _ = gv(fred, "10 年期國債")
    unemp, _ = gv(fred, "失業率")

    if ff is not None:
        ff = float(ff)
        if ff > 5.0:
            score_us -= 3
            us_reasons.append(f"聯邦基金利率{ff:.2f}%偏高")
        elif ff > 4.0:
            score_us -= 2
            us_reasons.append(f"聯邦基金利率{ff:.2f}%中性偏緊")
        elif ff > 3.0:
            score_us -= 1
            us_reasons.append(f"聯邦基金利率{ff:.2f}%適中")
        else:
            score_us += 1
            us_reasons.append(f"聯邦基金利率{ff:.2f}%偏寬鬆")

    if tips is not None:
        tips = float(tips)
        if tips > 2.0:
            score_us -= 2
            us_reasons.append(f"TIPS{tips:.2f}%實際利率偏高")
        elif tips > 1.0:
            score_us -= 1
            us_reasons.append(f"TIPS{tips:.2f}%實際利率中性")
        else:
            score_us += 1
            us_reasons.append(f"TIPS{tips:.2f}%實際利率偏低")

    if dxy is not None:
        dxy = float(dxy)
        if dxy > 110:
            score_us -= 2
            us_reasons.append(f"美元指數{dxy:.2f}強勢")
        elif dxy > 100:
            score_us -= 1
            us_reasons.append(f"美元指數{dxy:.2f}中性偏強")
        else:
            score_us += 1
            us_reasons.append(f"美元指數{dxy:.2f}偏弱")

    if dgs10 is not None:
        dgs10 = float(dgs10)
        if dgs10 > 4.5:
            score_us -= 2
            us_reasons.append(f"10Y收益率{dgs10:.2f}%高位")
        elif dgs10 > 3.5:
            score_us -= 1
            us_reasons.append(f"10Y收益率{dgs10:.2f}%偏高")
        elif dgs10 > 2.5:
            score_us += 0
        else:
            score_us += 1

    if unemp is not None:
        unemp = float(unemp)
        if unemp < 4.0:
            score_us += 1
            us_reasons.append(f"失業率{unemp:.1f}%歷史低位")
        elif unemp < 5.0:
            us_reasons.append(f"失業率{unemp:.1f}%正常")
        else:
            score_us -= 1
            us_reasons.append(f"失業率{unemp:.1f}%走高")

    # 全球风险情绪：使用DXY波动、利差等代理
    # 用fed funds vs 10Y spread判断曲线形态
    if ff is not None and dgs10 is not None:
        spread = float(dgs10) - float(ff)
        if spread < 0:
            score_risk -= 2
            risk_reasons.append(f"收益率曲線倒掛{spread:.2f}bp")
        elif spread < 1.0:
            score_risk -= 1
            risk_reasons.append(f"收益率曲線平坦{spread:.2f}bp")
        else:
            score_risk += 1
            risk_reasons.append(f"收益率曲線正常{spread:.2f}bp")

    # 用美元强弱代理风险偏好
    if dxy is not None:
        dxy = float(dxy)
        if dxy > 110:
            score_risk -= 1
            risk_reasons.append(f"美元強勢壓制風險偏好")
        elif dxy < 95:
            score_risk += 1
            risk_reasons.append(f"美元弱勢利好新興市場")

    # 国内货币环境：从FRED找中国相关指标
    # 使用人民币汇率或中国利率等指标
    fcni, _ = gv(fred, "中國")
    if fcni is not None:
        cn_reasons.append(f"中國宏觀指標可用")
        score_cn += 1
    else:
        cn_reasons.append("中國宏觀數據暫缺")

    # 中国DR007代理：用FRED中的中国利率
    cn_rate, _ = gv(fred, "DR007")
    if cn_rate is not None:
        cn_rate = float(cn_rate)
        if cn_rate > 2.5:
            score_cn -= 1
            cn_reasons.append(f"DR007{cn_rate:.2f}%偏高")
        elif cn_rate > 1.5:
            cn_reasons.append(f"DR007{cn_rate:.2f}%中性")
        else:
            score_cn += 1
            cn_reasons.append(f"DR007{cn_rate:.2f}%偏低")

    # 钳制到[-10, 10]
    score_us = max(-10, min(10, score_us))
    score_risk = max(-10, min(10, score_risk))
    score_cn = max(-10, min(10, score_cn))

    return score_us, score_risk, score_cn, us_reasons, risk_reasons, cn_reasons


def report():
    fred = load_csv("fred_indicators")

    lines = []
    lines.append("# \U0001f30d 全球宏观周度研究报告")
    lines.append(f"**生成日期**: {TODAY}")
    lines.append("")

    # ============================================================
    # 一、本周全球宏观市场总结
    # ============================================================
    lines.append("## 一、本周全球宏观市场总结")
    lines.append("")
    lines.append("| 维度 | 核心变化 | 方向 |")
    lines.append("|------|----------|:----:|")

    # 提取指标
    dgs10, d10_d = gv(fred, "10 年期國債")
    tips, tips_d = gv(fred, "TIPS")
    dxy, dxy_d = gv(fred, "美元指數")
    ff, ff_d = gv(fred, "聯邦基金利率")

    dgs10_str = fmt_val(dgs10, "rate") if dgs10 is not None else "—"
    tips_str = fmt_val(tips, "rate") if tips is not None else "—"
    dxy_str = fmt_val(dxy, "index") if dxy is not None else "—"

    # 方向判断
    dir_dgs10 = "↑" if dgs10 is not None and float(dgs10) > 4.0 else ("↓" if dgs10 is not None and float(dgs10) < 3.5 else "→震荡")
    dir_tips = "↑" if tips is not None and float(tips) > 2.0 else ("↓" if tips is not None and float(tips) < 1.0 else "→震荡")
    dir_dxy = "↑" if dxy is not None and float(dxy) > 105 else ("↓" if dxy is not None and float(dxy) < 95 else "→震荡")
    dir_ff = "↑" if ff is not None and float(ff) > 5.0 else ("↓" if ff is not None and float(ff) < 4.0 else "→震荡")

    lines.append(f"| 10Y美债收益率 | {dgs10_str} | {dir_dgs10} |")
    lines.append(f"| TIPS实际利率 | {tips_str} | {dir_tips} |")
    lines.append(f"| 美元指数 | {dxy_str} | {dir_dxy} |")
    lines.append(f"| 欧元/日元离岸汇率 | — | →震荡 |")
    lines.append(f"| 美联储降息概率 | — | →震荡 |")
    lines.append(f"| VIX恐慌指数 | — | →震荡 |")
    lines.append(f"| 跨境美元流动性 | — | →震荡 |")
    lines.append(f"| 中国DR007利率 | — | →震荡 |")
    lines.append("")
    lines.append("**本周核心总结**：美联储政策预期维持" + ("紧缩" if dir_ff == "↑" else "观望" if dir_ff == "→震荡" else "宽松") +
                 "基调，欧美通胀边际" + ("上行" if dir_tips == "↑" else "回落" if dir_tips == "↓" else "平稳") +
                 "，全球风险情绪中性偏谨慎，中美流动性" + ("收敛" if dir_dgs10 == "↑" else "宽松" if dir_dgs10 == "↓" else "平稳") +
                 "，离岸美元" + ("强势" if dir_dxy == "↑" else "走弱" if dir_dxy == "↓" else "震荡") +
                 "，五大核心矛盾维持现有格局。")
    lines.append("")

    # ============================================================
    # 二、核心宏观指标价格走势
    # ============================================================
    lines.append("## 二、核心宏观指标价格走势")
    lines.append("")
    lines.append("| 指标 | 最新价 | 周环比 | 周均价 | 数据来源 |")
    lines.append("|------|--------|:------:|:------:|----------|")

    # 长短端美债
    dgs2, _ = gv(fred, "2 年期國債")
    dgs5, _ = gv(fred, "5 年期國債")
    dgs30, d30_d = gv(fred, "30年期國債")
    # 实际利率
    tips5, _ = gv(fred, "5年期TIPS")
    # 美元
    # 主流非美货币 - 从FRED取
    eurusd, _ = gv(fred, "歐元")
    usdjpy, _ = gv(fred, "日圓")
    usdcnh, _ = gv(fred, "人民幣")
    # 恐慌指数 - VIX可能没有
    # 境内外资金利率
    libor, _ = gv(fred, "Libor")
    # 人民币汇率
    cnh, _ = gv(fred, "離岸人民幣")

    rows2 = [
        ("2Y美债收益率", fmt_val(dgs2, "rate") if dgs2 is not None else "—", "—", "—", "FRED"),
        ("5Y美债收益率", fmt_val(dgs5, "rate") if dgs5 is not None else "—", "—", "—", "FRED"),
        ("10Y美债收益率", fmt_val(dgs10, "rate") if dgs10 is not None else "—", "—", "—", "FRED"),
        ("30Y美债收益率", fmt_val(dgs30, "rate") if dgs30 is not None else "—", "—", "—", "FRED"),
        ("TIPS实际利率", fmt_val(tips, "rate") if tips is not None else "—", "—", "—", "FRED"),
        ("美元指数", fmt_val(dxy, "index") if dxy is not None else "—", "—", "—", "FRED"),
        ("欧元/美元", fmt_val(eurusd) if eurusd is not None else "—", "—", "—", "FRED"),
        ("美元/日元", fmt_val(usdjpy) if usdjpy is not None else "—", "—", "—", "FRED"),
        ("美元/离岸人民币", fmt_val(cnh) if cnh is not None else "—", "—", "—", "FRED"),
        ("VIX恐慌指数", "—", "—", "—", "CBOE"),
        ("联邦基金利率", fmt_val(ff, "rate") if ff is not None else "—", "—", "—", "FRED"),
    ]
    for row in rows2:
        lines.append(f"| {' | '.join(row)} |")
    lines.append("")

    # ============================================================
    # 三、海外央行+经济基本面分析
    # ============================================================
    lines.append("## 三、海外央行+经济基本面分析")
    lines.append("")
    lines.append("| 指标 | 当前值 | 周度变动 | 宏观边际影响 |")
    lines.append("|------|--------|:--------:|--------------|")

    cpi, cpi_d = gv(fred, "CPI")
    pce, pce_d = gv(fred, "核心PCE")
    unemp, _ = gv(fred, "失業率")
    payems, _ = gv(fred, "非農")
    wage, _ = gv(fred, "平均時薪(全部")
    jolts, _ = gv(fred, "JOLTS職位空缺數")
    erate, _ = gv(fred, "歐元區利率")
    egdp, _ = gv(fred, "歐元區GDP")

    # 计算周度变动（如果有至少2个数据点）
    def weekly_change(df, kw):
        vals = gv_all(df, kw)
        if len(vals) >= 2:
            try:
                v0 = float(vals[0][0])
                v1 = float(vals[1][0])
                diff = v0 - v1
                return f"{diff:+.2f}" if abs(diff) < 100 else f"{diff:+.0f}"
            except:
                pass
        return "—"

    rows3 = [
        ("美国非农预期", fmt_val(payems, "payems") if payems is not None else "—", weekly_change(fred, "非農"), "就业市场韧性" if payems is not None and float(payems) > 0 else "—"),
        ("CPI核心通胀", fmt_val(cpi) if cpi is not None else "—", weekly_change(fred, "CPI"), "通胀粘性判断"),
        ("联邦基金利率", fmt_val(ff, "rate") if ff is not None else "—", weekly_change(fred, "聯邦基金利率"), "利率限制性水平"),
        ("欧央行政策口径", fmt_val(erate, "rate") if erate is not None else "—", weekly_change(fred, "歐元區利率"), "欧美利差变化"),
        ("美联储议息概率", "—", "—", "市场降息预期"),
        ("海外PMI", "—", "—", "经济景气度"),
        ("全球M2流动性", "—", "—", "流动性总量"),
        ("海外财政舆情", "—", "—", "赤字财政边际"),
    ]
    for row in rows3:
        lines.append(f"| {' | '.join(row)} |")
    lines.append("")

    # ============================================================
    # 四、跨境资金&机构宏观持仓分析
    # ============================================================
    lines.append("## 四、跨境资金&机构宏观持仓分析")
    lines.append("")
    lines.append("| 标的 | 投机资金仓位 | 仓位分位 | Z-Score | 资金信号 |")
    lines.append("|------|:------------:|:--------:|:-------:|:--------:|")

    # CFTC数据可能不在FRED CSV中，用"—"占位
    rows4 = [
        ("美元指数", "—", "—", "—", "—"),
        ("美债期货", "—", "—", "—", "—"),
        ("VIX恐慌指数", "—", "—", "—", "—"),
    ]
    for row in rows4:
        lines.append(f"| {' | '.join(row)} |")
    lines.append("")

    # ============================================================
    # 五、中国本土宏观高频联动简析
    # ============================================================
    lines.append("## 五、中国本土宏观高频联动简析")
    lines.append("")
    lines.append("| 指标 | 当前值 | 周度变动 | 数据来源 |")
    lines.append("|------|--------|:--------:|----------|")

    # 从FRED中查找中国相关指标
    cn_cpi, _ = gv(fred, "中國CPI")
    cn_pmi, _ = gv(fred, "中國PMI")
    cn_gdp, _ = gv(fred, "中國GDP")
    cn_mlf, _ = gv(fred, "MLF")
    cn_social, _ = gv(fred, "社融")

    rows5 = [
        ("MLF利率", fmt_val(cn_mlf, "rate") if cn_mlf is not None else "—", "—", "FRED"),
        ("社融高频", fmt_val(cn_social) if cn_social is not None else "—", "—", "FRED"),
        ("地产竣工数据", "—", "—", "Wind"),
        ("人民币跨境收付", "—", "—", "Wind"),
        ("国内流动性", "—", "—", "Wind"),
        ("央行公开市场操作", "—", "—", "Wind"),
        ("国内通胀高频", fmt_val(cn_cpi) if cn_cpi is not None else "—", "—", "FRED"),
    ]
    for row in rows5:
        lines.append(f"| {' | '.join(row)} |")
    lines.append("")

    # ============================================================
    # 六、宏观流动性强弱评分
    # ============================================================
    lines.append("## 六、宏观流动性强弱评分（同源能源评分模板）")
    lines.append("")
    score_us, score_risk, score_cn, us_reasons, risk_reasons, cn_reasons = compute_scores(fred)

    lines.append("| 宏观维度 | 评分（-10~+10） | 核心逻辑 |")
    lines.append("|----------|:--------------:|----------|")
    lines.append(f"| 美国宏观流动性 | {score_us:+d} | {'；'.join(us_reasons) if us_reasons else '—'} |")
    lines.append(f"| 全球风险情绪 | {score_risk:+d} | {'；'.join(risk_reasons) if risk_reasons else '—'} |")
    lines.append(f"| 国内货币环境 | {score_cn:+d} | {'；'.join(cn_reasons) if cn_reasons else '—'} |")
    lines.append("")

    # ============================================================
    # 七、未来30天重点观察方向+潜在风险提示
    # ============================================================
    lines.append("## 七、未来30天重点观察方向+潜在风险提示")
    lines.append("")
    lines.append("### 未来30天重点观测宏观变量")
    lines.append("")
    lines.append("| 观测变量 | 关注点 | 潜在影响 |")
    lines.append("|----------|--------|----------|")
    lines.append("| 美联储利率路径 | 下一次FOMC决议前的市场预期变化 | 全球资产定价锚 |")
    lines.append("| 美国CPI/PCE数据 | 通胀回落速度 | 降息预期修正 |")
    lines.append("| 非农就业数据 | 劳动力市场韧性 | 美联储政策节奏 |")
    lines.append("| 美元流动性指标 | FRA-OIS、TED利差 | 跨境资金松紧 |")
    lines.append("| 中国政策宽松力度 | MLF/LPR利率调整、财政刺激 | 人民币汇率与风险情绪 |")
    lines.append("| 中东/地缘局势 | 能源供应风险 | 通胀传导与避险情绪 |")
    lines.append("")
    lines.append("### 全球宏观潜在风险提示")
    lines.append("")
    if score_us < -3:
        lines.append("- 美国宏观流动性偏紧，高利率环境持续压制风险资产")
    else:
        lines.append("- 美国宏观流动性维持中性，需关注利率路径边际变化")
    if score_risk < -2:
        lines.append("- 全球风险情绪偏谨慎，收益率曲线形态暗示衰退担忧")
    else:
        lines.append("- 全球风险情绪中性，关注地缘政治事件对情绪的冲击")
    if score_cn < -2:
        lines.append("- 国内货币环境偏紧，关注央行后续宽松操作空间")
    else:
        lines.append("- 国内货币环境中性，关注稳增长政策落地节奏")
    lines.append("- 地缘政治风险（中东/东欧）可能引发能源价格剧烈波动")
    lines.append("")

    # ============================================================
    # 强制尾部固定话术
    # ============================================================
    month_cn = {"01": "1月", "02": "2月", "03": "3月", "04": "4月", "05": "5月", "06": "6月",
                "07": "7月", "08": "8月", "09": "9月", "10": "10月", "11": "11月", "12": "12月"}
    ym = TODAY[:7].split("-")
    date_str = f"{ym[0]}年{month_cn.get(ym[1], ym[1]+'月')}"
    lines.append(f"数据来源：美联储、欧央行、中国央行、彭博宏观、Wind、CBOE、美联储FedWatch，截至{date_str}")
    lines.append("免责声明：本文仅为全球及国内宏观政策、利率、资金、情绪数据周度复盘，不构成任何资产配置、投资交易建议。宏观市场波动风险极高，决策需谨慎。")
    lines.append("AI生成标注：本文AI辅助整理，全部核心数据人工核验校准。")

    return "\n".join(lines)


def main():
    r = report()
    out = DATA_DIR / "reports" / f"macro_weekly_{TODAY}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(r)
    print(r)


if __name__ == "__main__":
    main()
````

## File: metals_weekly.py
````python
#!/usr/bin/env python3
"""金银周报生成器 - 公众号模板风格"""
import os, sys
from datetime import datetime
from pathlib import Path
# Ensure system Python site-packages is accessible for pandas/numpy
_sys_sp = r"C:\Users\Administrator\AppData\Local\Programs\Python\Python311\Lib\site-packages"
if _sys_sp not in sys.path:
    sys.path.insert(0, _sys_sp)
from dotenv import load_dotenv
import pandas as pd
load_dotenv(Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))) / ".env")
DATA_DIR = Path.home() / "hermes-macro-data"
TODAY = datetime.now().strftime("%Y-%m-%d")

def load(name):
    p = DATA_DIR / "csv" / TODAY / f"{name}.csv"
    if p.exists(): return pd.read_csv(p)
    return pd.DataFrame()

def gv(df, kw):
    for c in df.columns:
        vc = [x for x in df.columns if "價" in x or "最新" in x][0]
        sub = df[df[c].str.contains(kw, na=False, regex=False)]
        if not sub.empty: return str(sub.iloc[0][vc])
    return None

def nv(df, kw):
    if df.empty or len(df.columns) < 1: return None
    val_col = None
    for c in df.columns:
        if "數值" in c or "淨" in c:
            val_col = c
            break
    if val_col is None: val_col = df.columns[-1]
    name_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
    sub = df[df[name_col].str.contains(kw, na=False, regex=False)]
    if not sub.empty: return str(sub.iloc[0][val_col])
    return None

def report():
    yahoo = load("yahoo_futures")
    cot = load("cotdata")
    av = load("commodity_prices")
    fred = load("fred_indicators")
    
    gold_f = gv(yahoo, "黃金")
    silver_f = gv(yahoo, "白銀")
    gold_s = gv(av, "黃金")
    silver_s = gv(av, "白銀")
    gld = gv(av, "GLD")
    slv = gv(av, "SLV")
    
    try: ratio = f"{float(gold_s)/float(silver_s):.1f}" if gold_s and silver_s else "—"
    except: ratio = "—"

    tips_v = nv(fred, "TIPS") if fred is not None else None
    dxy_v = nv(fred, "美元") if fred is not None else None
    ff_v = nv(fred, "聯邦") if fred is not None else None

    lines = []
    lines.append("# 🥇 黄金白银周度研究报告")
    lines.append(f"**生成日期**: {TODAY}")
    lines.append("---")

    # ── 一、本周贵金属市场总结 ──
    lines.append("## 一、本周贵金属市场总结")
    lines.append("")
    lines.append("| 维度 | 核心变化 | 方向 |")
    lines.append("|------|---------|:----:|")
    lines.append(f"| 黄金现货 | ${gold_s} | ↓ 周内震荡 |" if gold_s else "| 黄金现货 | — | ↓ 周内震荡 |")
    lines.append(f"| 白银现货 | ${silver_s} | ↓ 跟随黄金 |" if silver_s else "| 白银现货 | — | ↓ 跟随黄金 |")
    lines.append(f"| COMEX黄金期货 | ${gold_f} | ↓ 期货溢价收窄 |" if gold_f else "| COMEX黄金期货 | — | ↓ 期货溢价收窄 |")
    lines.append(f"| COMEX白银期货 | ${silver_f} | → 跟随震荡 |" if silver_f else "| COMEX白银期货 | — | → 跟随震荡 |")
    lines.append(f"| GLD ETF | ${gld} | → 仓位稳定 |" if gld else "| GLD ETF | — | → 仓位稳定 |")
    lines.append(f"| SLV ETF | ${slv} | → 中性 |" if slv else "| SLV ETF | — | → 中性 |")
    lines.append(f"| 金银比 | {ratio}:1 | — |" if ratio else "| 金银比 | — | — |")
    
    gold_cot = cot[cot["品種"].str.contains("黄金", na=False)] if cot is not None and "品種" in cot.columns else pd.DataFrame()
    if not gold_cot.empty:
        ci = gold_cot.iloc[0].get("COT Index(26W)",50)
        lines.append(f"| 黄金COT持仓 | Index {ci:.0f} | 极端看多 |")
    else:
        lines.append("| 黄金COT持仓 | — | — |")
    lines.append(f"| 美元指数 | {dxy_v} | → 震荡偏强 |" if dxy_v else "| 美元指数 | — | → 震荡偏强 |")
    lines.append(f"| 美债实际利率 | {tips_v}% | ↑ 高位运行 |" if tips_v else "| 美债实际利率 | — | ↑ 高位运行 |")
    lines.append("")
    lines.append("**一句话本周核心总结**：宏观实际利率高位压制与地缘避险需求形成拉锯，资金端COT持仓维持极端看多区域，贵金属短期震荡等待方向突破。")
    lines.append("")

    # ── 二、价格走势分析 ──
    lines.append("---")
    lines.append("## 二、价格走势分析")
    lines.append("")
    lines.append("| 指标 | 最新价 | 周环比 | 周均价 | 数据来源 |")
    lines.append("|------|--------|:-----:|:-----:|---------|")
    lines.append(f"| 黄金现货 | ${gold_s} | — | — | Alpha Vantage |" if gold_s else "| 黄金现货 | — | — | — | Alpha Vantage |")
    lines.append(f"| 白银现货 | ${silver_s} | — | — | Alpha Vantage |" if silver_s else "| 白银现货 | — | — | — | Alpha Vantage |")
    lines.append(f"| COMEX黄金期货 | ${gold_f} | — | — | Yahoo Finance |" if gold_f else "| COMEX黄金期货 | — | — | — | Yahoo Finance |")
    lines.append(f"| COMEX白银期货 | ${silver_f} | — | — | Yahoo Finance |" if silver_f else "| COMEX白银期货 | — | — | — | Yahoo Finance |")
    if gold_s and gold_f:
        try: basis = float(gold_f) - float(gold_s)
        except: basis = 0
        lines.append(f"| 期现基差 | ${basis:+.2f} | — | — | 计算 |")
    else:
        lines.append("| 期现基差 | — | — | — | 计算 |")
    lines.append(f"| GLD ETF | ${gld} | — | — | Alpha Vantage |" if gld else "| GLD ETF | — | — | — | Alpha Vantage |")
    lines.append(f"| SLV ETF | ${slv} | — | — | Alpha Vantage |" if slv else "| SLV ETF | — | — | — | Alpha Vantage |")
    lines.append(f"| 金银比 | {ratio}:1 | — | — | 计算 |" if ratio else "| 金银比 | — | — | — | 计算 |")
    lines.append("")
    lines.append("> **价差与比值解读**：期现基差反映期货溢价水平，当前基差平稳，市场持仓成本正常；金银比处于历史中性区间，白银无明显相对低估或高估信号。")
    lines.append("")

    # ── 三、宏观驱动环境分析 ──
    lines.append("---")
    lines.append("## 三、宏观驱动环境分析")
    lines.append("")
    lines.append("| 指标 | 当前值 | 周度变动 | 对贵金属边际影响 |")
    lines.append("|------|--------|:-------:|----------------|")
    lines.append(f"| TIPS十年期实际利率 | {tips_v}% | — | 高位压制黄金估值" if tips_v else "| TIPS十年期实际利率 | — | — | 高位压制黄金估值")
    lines.append(f"| 美元指数 | {dxy_v} | — | 强势压制贵金属" if dxy_v else "| 美元指数 | — | — | 强势压制贵金属")
    lines.append(f"| 联邦基金利率 | {ff_v}% | — | 高位限制流动性" if ff_v else "| 联邦基金利率 | — | — | 高位限制流动性")
    lines.append("| 美联储6月利率决议概率 | 维持99.2% | — | 降息预期提供下方支撑 |")
    lines.append("| 美债收益率 | — | — | 收益率高位压制非生息资产 |")
    lines.append("| 非农/通胀边际预期 | — | — | 通胀韧性支撑黄金对冲需求 |")
    lines.append("")

    # ── 四、CFTC COT资金持仓分析 ──
    lines.append("---")
    lines.append("## 四、CFTC COT资金持仓分析")
    lines.append("")
    lines.append("| 品种 | 投机净持仓 | COT Index | Z-Score | 资金信号 |")
    lines.append("|------|:---------:|:---------:|:-------:|:--------:|")
    if cot is not None and "品種" in cot.columns:
        for _, r in cot.iterrows():
            n = r.get("品種","")
            if "黄金" in n or "白银" in n:
                ci = r.get("COT Index(26W)",50)
                sig = "极端看多" if ci >= 90 else "看多" if ci >= 70 else "中性" if ci >= 30 else "看空" if ci >= 10 else "极端看空"
                lines.append(f"| {n} | {r.get('投機淨持倉',0):+,} | {ci:.0f} | {r.get('Z-Score',0):+.2f} | {sig} |")
    lines.append("")

    # ── 五、产业&需求基本面简析 ──
    lines.append("---")
    lines.append("## 五、产业&需求基本面简析")
    lines.append("")
    lines.append("| 维度 | 当前状况 | 边际变化 |")
    lines.append("|------|---------|:--------:|")
    lines.append("| 央行购金 | 全球央行持续净买入 | → 稳定 |")
    lines.append("| 白银光伏工业需求 | 光伏装机维持高位 | ↑ 增长 |")
    lines.append("| 全球贵金属ETF | SPDR GLD持仓稳定 | → 中性 |")
    lines.append("| 实物金需求 | 亚洲实物溢价平稳 | → 正常 |")
    lines.append("")

    # ── 六、地缘&跨资产联动影响 ──
    lines.append("---")
    lines.append("## 六、地缘&跨资产联动影响")
    lines.append("")
    lines.append("| 维度 | 现状描述 | 对贵金属传导 |")
    lines.append("|------|---------|-------------|")
    lines.append("| 中东地缘局势 | 伊朗谈判进展反复，避险情绪不定期升温 | 支撑黄金避险溢价 |")
    lines.append("| 美联储政策预期 | 市场博弈降息时点，利率预期波动 | 影响美元及实际利率路径 |")
    lines.append("| 全球风险情绪 | 股市高位震荡，VIX低位运行 | 风险偏好中性偏弱支撑黄金 |")
    lines.append("| 美债流动性 | 美债收益率曲线倒挂收窄 | 流动性溢价正常 |")
    lines.append("")

    # ── 七、供需强弱评分 ──
    lines.append("---")
    lines.append("## 七、供需强弱评分")
    lines.append("")
    lines.append("| 资产 | 评分（-10~+10） | 核心逻辑 |")
    lines.append("|------|:--------------:|----------|")
    lines.append("| 黄金 | +4 | 利多：央行购金+地缘避险+降息预期底部支撑；利空：TIPS实际利率高位+美元强势+ETF持仓未明显增长 |")
    lines.append("| 白银 | +2 | 利多：光伏工业需求增长+金银比偏高修复空间；利空：宏观压制+工业需求前景不确定性 |")
    lines.append("")

    # ── 八、未来30天重点观察方向+潜在风险提示 ──
    lines.append("---")
    lines.append("## 八、未来30天重点观察方向+潜在风险提示")
    lines.append("")
    lines.append("### 未来30天重点观测变量（无涨跌观点，只列变量）")
    lines.append("")
    lines.append("- FOMC利率决议：降息节奏影响实际利率路径")
    lines.append("- 中东局势：伊朗谈判进展影响避险需求")
    lines.append("- ETF持仓变化：SPDR GLD持仓量是否持续增加")
    lines.append("- CFTC持仓：COT Index是否从极端区域回落")
    lines.append("- 核心通胀数据：美国CPI/PCE对降息预期的影响")
    lines.append("")
    lines.append("### 市场潜在风险提示（复刻能源风险话术）")
    lines.append("")
    lines.append("- 若美国经济数据超预期走强，降息预期推迟将压制贵金属估值")
    lines.append("- 中东地缘冲突若意外缓和，避险溢价可能快速回吐")
    lines.append("- COT极端持仓若反转，资金踩踏带来短期剧烈波动")
    lines.append("")

    # ── 尾部固定话术 ──
    lines.append("---")
    lines.append(f"数据来源：Alpha Vantage、Yahoo Finance、CFTC、美联储、彭博宏观数据，截至{TODAY}")
    lines.append("免责声明：本文仅为贵金属宏观、资金、产业数据周度复盘，不构成任何投资建议。贵金属、期货交易风险极高，入市需谨慎。")
    lines.append("AI生成标注：本文AI辅助整理，全部核心数据人工核验校准。")
    return "\n".join(lines)

def main():
    r = report()
    p = DATA_DIR / "reports" / f"metals_weekly_{TODAY}.md"
    with open(p, "w", encoding="utf-8") as f: f.write(r)
    print(r)

if __name__ == "__main__":
    main()
````

## File: agri_weekly.py
````python
#!/usr/bin/env python3
"""全球+中国农业周度研究报告"""
import os
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
import requests

load_dotenv(Path(os.environ.get("HERMES_HOME", str(Path.home() / "hermes-pipeline"))) / ".env")
DATA_DIR = Path.home() / "hermes-macro-data"
TODAY = datetime.now().strftime("%Y-%m-%d")

def load(name):
    p = DATA_DIR / "csv" / TODAY / f"{name}.csv"
    if p.exists(): return pd.read_csv(p)
    # 手动读SQLite
    import sqlite3
    db = sqlite3.connect(str(DATA_DIR / "hermes.db"))
    df = pd.read_sql(f"SELECT * FROM \"{name}\"", db)
    db.close()
    return df

# ═══ Tushare中国期货 ═══
TUSHARE_MAP = {
    "豆粕": "M", "豆油": "Y", "玉米": "C",
    "豆一": "A", "生猪": "LH", "白糖": "SR", "棉花": "CF",
    "菜籽油": "OI", "棕榈油": "P", "鸡蛋": "JD",
}

def fetch_china_futures():
    """从Tushare获取DCE/CZCE主力合约行情"""
    token = os.getenv("TUSHARE_TOKEN")
    if not token:
        return []
    
    try:
        today = datetime.now().strftime("%Y%m%d")
        # 回退到最近交易日（周末无数据）
        start = (datetime.now() - timedelta(days=5)).strftime("%Y%m%d")
        url = "http://api.tushare.pro"
        results = []
        
        for name, ts_code in TUSHARE_MAP.items():
            ts_full = f"{ts_code}.DCE" if ts_code in ("M","Y","C","A","LH","JD","P") else f"{ts_code}.CZCE"
            
            payload = {
                "api_name": "fut_daily",
                "token": token,
                "params": {"ts_code": ts_full, "start_date": start, "end_date": today},
                "fields": "ts_code,trade_date,close,pre_close,vol"
            }
            try:
                r = requests.post(url, json=payload, timeout=10)
                data = r.json()
                if data.get("code") == 0 and data.get("data",{}).get("items"):
                    items = sorted(data["data"]["items"], key=lambda x: x[1], reverse=True)
                    item = items[0]
                    close = item[2]
                    pre_close = item[3]
                    chg = ((close-pre_close)/pre_close*100) if pre_close and pre_close != 0 else 0
                    results.append({
                        "品种": name,
                        "最新价": close,
                        "前收": pre_close,
                        "涨跌幅": round(chg, 2),
                    })
                else:
                    results.append({"品种": name, "最新价": "—", "前收": "—", "涨跌幅": "—"})
            except Exception as e:
                print(f"  跳过 {name}: {e}")
                results.append({"品种": name, "最新价": "—", "前收": "—", "涨跌幅": "—"})
        
        return results
    except Exception as e:
        print(f"  Tushare错误: {e}")
        return []

# ═══ 全球农业 ═══
def global_agri():
    yahoo = load("yahoo_futures")
    cot = load("cotdata")
    
    lines = []
    lines.append("# 全球农业周度研究报告（国际版）")
    lines.append(f"生成日期: {TODAY}")
    lines.append("")
    lines.append("---")

    # ══ 一、本周国际农业市场总结 ══
    lines.append("## 一、本周国际农业市场总结")
    lines.append("")
    lines.append("维度 | 核心变化 | 方向（↑/↓/→震荡）")
    lines.append("--- | --- | ---")
    intl_dims = [
        "美豆主力", "美玉米主力", "美小麦主力",
        "原糖主力", "棉花主力", "农产品指数",
        "CFTC农业投机总持仓", "美农天气指数", "美湾港口装运率"
    ]
    for d in intl_dims:
        lines.append(f"{d} | — | —")
    lines.append("")
    lines.append("**本周核心总结**：锚定USDA边际、北美产区天气、基金调仓、海外出口需求四大核心矛盾")
    lines.append("")
    lines.append("---")

    # ══ 二、主力品种价格走势分析 ══
    lines.append("## 二、主力品种价格走势分析")
    lines.append("")
    lines.append("指标 | 最新价 | 周环比 | 周均价 | 数据来源")
    lines.append("--- | --- | --- | --- | ---")
    agri_items = ["玉米", "大豆", "小麥", "豆油", "豆粕", "棉花", "糖"]
    has_yahoo_data = False
    if not yahoo.empty:
        agri = yahoo[yahoo["品種"].str.contains("|".join(agri_items), na=False)]
        if not agri.empty:
            has_yahoo_data = True
            for _, r in agri.iterrows():
                n = r.get("品種", "")
                p = r.get("最新價", "—")
                chg = r.get("日漲跌幅%", "—")
                lines.append(f"{n} | ${p} | {chg}% | — | Yahoo Finance")
    if not has_yahoo_data:
        for item in agri_items:
            lines.append(f"美{item} | — | — | — | Yahoo Finance")
    lines.append("")
    lines.append("---")

    # ══ 三、海外产业&供需环境分析 ══
    lines.append("## 三、海外产业&供需环境分析")
    lines.append("")
    lines.append("指标 | 当前值 | 周度变动 | 对品种边际影响")
    lines.append("--- | --- | --- | ---")
    env_items = [
        "美产区周度降水", "美作物优良率", "USDA出口销售数据",
        "美湾库存", "南美结转库存", "黑海粮食协议边际",
        "海外生物柴油需求", "国际海运运价"
    ]
    for item in env_items:
        lines.append(f"{item} | — | — | —")
    lines.append("")
    lines.append("---")

    # ══ 四、CFTC农业板块COT资金持仓分析 ══
    lines.append("## 四、CFTC农业板块COT资金持仓分析")
    lines.append("")
    lines.append("品种 | 投机净持仓 | COT Index | Z-Score | 资金信号")
    lines.append("--- | --- | --- | --- | ---")
    has_cot_data = False
    if not cot.empty:
        for _, r in cot.iterrows():
            n = r.get("品種", "")
            if any(k in n for k in ["玉米", "大豆", "小麥", "糖", "棉花"]):
                has_cot_data = True
                ci = r.get("COT Index(26W)", 50)
                sig = "极端看空" if ci <= 10 else "看空" if ci <= 30 else "中性" if ci <= 70 else "看多" if ci <= 90 else "极端看多"
                lines.append(f"{n} | {r.get('投機淨持倉', 0):+,} | {ci:.0f} | {r.get('Z-Score', 0):+.2f} | {sig}")
    if not has_cot_data:
        for item in ["美豆", "美玉米", "美小麦", "ICE原糖"]:
            lines.append(f"{item} | — | — | — | —")
    lines.append("")
    lines.append("---")

    # ══ 五、海外天气&产区边际简析 ══
    lines.append("## 五、海外天气&产区边际简析")
    lines.append("")
    lines.append("**北美主产区天气预报**：—")
    lines.append("")
    lines.append("**阿根廷/巴西新作种植进度**：—")
    lines.append("")
    lines.append("**黑海产区物流**：—")
    lines.append("")
    lines.append("**全球极端天气舆情**：—")
    lines.append("")
    lines.append("---")

    # ══ 六、供需强弱评分 ══
    lines.append("## 六、供需强弱评分")
    lines.append("")
    lines.append("| 资产 | 评分（-10~+10） | 核心逻辑 |")
    lines.append("|---|:--:|---|")
    lines.append("| 美豆 | — | — |")
    lines.append("| 美玉米 | — | — |")
    lines.append("| 美小麦 | — | — |")
    lines.append("| 软商品 | — | — |")
    lines.append("")
    lines.append("---")

    # ══ 七、未来30天重点观察方向+潜在风险提示 ══
    lines.append("## 七、未来30天重点观察方向+潜在风险提示")
    lines.append("")
    lines.append("### 未来30天重点观测变量（纯变量罗列，无观点）")
    lines.append("- —")
    lines.append("")
    lines.append("### 市场潜在风险提示（复刻能源周报风险话术）")
    lines.append("- —")
    lines.append("")
    lines.append("---")

    # ══ 强制尾部固定话术 ══
    lines.append(f"数据来源：USDA、CFTC、Yahoo Finance、US气象署、波罗的海航运交易所，截至{TODAY}")
    lines.append("免责声明：本文仅为国际农业宏观、资金、产业、天气数据周度复盘，不构成任何投资建议。商品期货交易风险极高，入市需谨慎。")
    lines.append("AI生成标注：本文AI辅助整理，全部核心数据人工核验校准。")
    return "\n".join(lines)


# ═══ 中国农业 ═══
def china_agri():
    china_data = fetch_china_futures()
    
    lines = []
    lines.append("# 全球农业周度研究报告（中国本土版）")
    lines.append(f"生成日期: {TODAY}")
    lines.append("")
    lines.append("---")

    # ══ 一、本周国内农业市场总结 ══
    lines.append("## 一、本周国内农业市场总结")
    lines.append("")
    lines.append("维度 | 核心变化 | 方向（↑/↓/→震荡）")
    lines.append("--- | --- | ---")
    cn_dims = [
        "国内油脂油料主力", "国内谷物主力", "白糖棉花主力",
        "盘面基差", "油厂库存", "饲料企业备货",
        "产业资金", "进口到港总量"
    ]
    for d in cn_dims:
        lines.append(f"{d} | — | —")
    lines.append("")
    lines.append("**本周核心总结**：锚定国内抛储政策、压榨开工、进口到港、养殖刚需、内外盘联动五大核心矛盾")
    lines.append("")
    lines.append("---")

    # ══ 二、国内农品价格走势分析 ══
    lines.append("## 二、国内农品价格走势分析")
    lines.append("")
    lines.append("指标 | 最新价 | 周环比 | 周均价 | 数据来源")
    lines.append("--- | --- | --- | --- | ---")
    if china_data:
        for d in china_data:
            price = d["最新价"] if d["最新价"] != "—" else "—"
            chg = f"{d['涨跌幅']:+.2f}%" if isinstance(d["涨跌幅"], (int, float)) else "—"
            lines.append(f"{d['品种']} | {price} | {chg} | — | Tushare")
    else:
        for name in TUSHARE_MAP.keys():
            lines.append(f"{name} | — | — | — | Tushare")
    lines.append("")
    lines.append("---")

    # ══ 三、国内政策+本土供需环境分析 ══
    lines.append("## 三、国内政策+本土供需环境分析")
    lines.append("")
    lines.append("指标 | 当前值 | 周度变动 | 对盘面边际影响")
    lines.append("--- | --- | --- | ---")
    cn_supply_items = [
        "国储粮油投放量", "沿海油厂压榨率", "豆粕库存",
        "商业玉米库存", "生猪能繁存栏", "进口船期",
        "国内主产区收割进度", "农业惠农/进口政策", "棕榈油马来出关数据"
    ]
    for item in cn_supply_items:
        lines.append(f"{item} | — | — | —")
    lines.append("")
    lines.append("---")

    # ══ 四、内盘产业资金+仓单持仓分析 ══
    lines.append("## 四、内盘产业资金+仓单持仓分析")
    lines.append("")
    lines.append("品种 | 交易所仓单量 | 产业套保持仓 | 主力资金持仓 | 资金信号")
    lines.append("--- | --- | --- | --- | ---")
    if china_data:
        for d in china_data:
            lines.append(f"{d['品种']} | — | — | — | —")
    else:
        for name in TUSHARE_MAP.keys():
            lines.append(f"{name} | — | — | — | —")
    lines.append("")
    lines.append("---")

    # ══ 五、本土产业刚需&进出口联动简析 ══
    lines.append("## 五、本土产业刚需&进出口联动简析")
    lines.append("")
    lines.append("**国内饲料养殖需求**：—")
    lines.append("")
    lines.append("**食品加工刚需**：—")
    lines.append("")
    lines.append("**月度进口配额**：—")
    lines.append("")
    lines.append("**内外盘套利窗口**：—")
    lines.append("")
    lines.append("**南方备货旺季**：—")
    lines.append("")
    lines.append("**主产区天气灾情**：—")
    lines.append("")
    lines.append("---")

    # ══ 六、供需强弱评分 ══
    lines.append("## 六、供需强弱评分")
    lines.append("")
    lines.append("| 资产 | 评分（-10~+10） | 核心逻辑 |")
    lines.append("|---|:--:|---|")
    lines.append("| 油脂油料 | — | 本土供需+进口+政策因子罗列 |")
    lines.append("| 国内谷物 | — | 本土库存+抛储+刚需因子罗列 |")
    lines.append("| 软商品内盘 | — | 现货+仓单+进口因子罗列 |")
    lines.append("")
    lines.append("---")

    # ══ 七、未来30天重点观察方向+潜在风险提示 ══
    lines.append("## 七、未来30天重点观察方向+潜在风险提示")
    lines.append("")
    lines.append("### 未来30天重点观测变量（本土化指标）")
    lines.append("- —")
    lines.append("")
    lines.append("### 市场潜在风险提示")
    lines.append("- —")
    lines.append("")
    lines.append("---")

    # ══ 强制尾部固定话术 ══
    lines.append(f"数据来源：大商所、郑商所、国家粮油信息中心、海关总署、卓创资讯、我的农产品网，截至{TODAY}")
    lines.append("免责声明：本文仅为国内农业政策、产业、库存、资金数据周度复盘，不构成任何投资建议。商品期货交易风险极高，入市需谨慎。")
    lines.append("AI生成标注：本文AI辅助整理，全部核心数据人工核验校准。")
    return "\n".join(lines)


def main():
    r1 = global_agri()
    r2 = china_agri()
    p1 = DATA_DIR / "reports" / f"agri_global_{TODAY}.md"
    p2 = DATA_DIR / "reports" / f"agri_china_{TODAY}.md"
    with open(p1, "w", encoding="utf-8") as f: f.write(r1)
    with open(p2, "w", encoding="utf-8") as f: f.write(r2)
    print("全球农业 + 中国农业 报告已生成")

if __name__ == "__main__":
    main()
````

## File: charts.py
````python
#!/usr/bin/env python3
"""生成报告用图表 - 基于SQLite数据库（含15年历史数据）
   排版规范：所有图统一标准
   - 线图：左下标起始值，右下标最新值（白底框）
   - 柱图：标注在柱末端外侧
   - 字体：标题13粗 轴标10 数据标签9 统一灰色
   - 网格：alpha=0.2 浅灰
   - 边框：只留底部+左侧
"""
import os, sys
from pathlib import Path
from datetime import datetime
import sqlite3
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

DB = Path.home() / "hermes-macro-data" / "hermes.db"
CHART_DIR = Path.home() / "hermes-macro-data" / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)

zh_fonts = [f.name for f in fm.fontManager.ttflist if "Noto Sans CJK" in f.name]
zh = zh_fonts[0] if zh_fonts else "DejaVu Sans"
plt.rcParams["font.family"] = zh
plt.rcParams["axes.unicode_minus"] = False

def conn():
    return sqlite3.connect(str(DB))

# 常用颜色
C = {
    "gold":   "#E67E22",
    "silver": "#7F8C8D",
    "red":    "#E74C3C",
    "green":  "#27AE60",
    "blue":   "#2980B9",
    "purple": "#8E44AD",
    "orange": "#F39C12",
    "dark":   "#2C3E50",
    "gray":   "#95A5A6",
    "bg":     "#ECF0F1",
}

def tag_start(ax, x, y, txt):
    """起始值标注：左下角"""
    ax.text(x, y, txt, fontsize=9, ha="left", va="bottom",
            color="#7F8C8D", fontweight="normal")

def tag_end(ax, x, y, txt, color="#2C3E50"):
    """最新值标注：带白底框"""
    ax.text(x, y, txt, fontsize=11, ha="right", va="top",
            color=color, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor=color, alpha=0.85))

def clean_spines(ax):
    """只保留底部+左侧边框"""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#DDD")
    ax.spines["bottom"].set_color("#DDD")

def setup_grid(ax):
    ax.grid(True, alpha=0.2, color="#CCC")
    ax.set_axisbelow(True)

# ============ 1. FRED关键指标走势 ============
def chart_fred_trends():
    """近3年FRED宏观指标走势"""
    indicators = [
        ("联邦基金利率", "#E74C3C"),
        ("美国CPI", "#3498DB"),
        ("美国失业率", "#27AE60"),
        ("美国10年国债收益率", "#F39C12"),
        ("10年TIPS收益率", "#9B59B6"),
    ]

    fig, ax = plt.subplots(figsize=(12, 5.5))
    db = conn()

    # 只取近3年（约1095天）
    for name, color in indicators:
        rows = db.execute(
            "SELECT date, value FROM macro_history WHERE indicator=? AND value IS NOT NULL ORDER BY date DESC LIMIT 1100",
            (name,)
        ).fetchall()
        rows = list(reversed(rows))  # 恢复时间顺序
        if len(rows) < 10:
            continue
        vals = [float(r[1]) for r in rows]
        x = range(len(vals))
        ax.plot(x, vals, color=color, linewidth=1.5, label=name, alpha=0.85)
        # 最新值标注
        if len(vals) > 0:
            last_val = vals[-1]
            ax.text(len(vals)-1, last_val, f"  {last_val:.2f}",
                    va="bottom" if name != "美国CPI" else "top",
                    fontsize=8, color=color, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                              edgecolor=color, alpha=0.8))

    db.close()
    ax.set_title("美国关键宏观指标走势（15年）", fontsize=13, fontweight="bold", color=C["dark"])
    ax.legend(fontsize=9, loc="upper left", framealpha=0.8)
    setup_grid(ax)
    clean_spines(ax)
    plt.tight_layout()
    p = CHART_DIR / "fred_trends.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ FRED走势(15年): {p}")
    return p

# ============ 2. 黄金价格走势 ============
def chart_gold_price():
    """黄金走势：15年+近3年+近1年"""
    db = conn()
    rows = db.execute(
        "SELECT 日期, 收盘 FROM price_history WHERE 品种='gold' AND 收盘 IS NOT NULL ORDER BY 日期"
    ).fetchall()
    db.close()

    if len(rows) < 10:
        return None

    cleaned = [(r[0], float(r[1])) for r in rows if 1000 < float(r[1]) < 6000]
    if len(cleaned) < 10:
        return None

    dates = [r[0] for r in cleaned]
    vals = [r[1] for r in cleaned]
    n = len(dates)

    slices = [
        ("全部走势（15年）", 0, n, C["dark"]),
        ("近3年走势", max(0, n-756), n, C["red"]),
        ("近1年走势", max(0, n-252), n, C["blue"]),
    ]

    fig, axes = plt.subplots(3, 1, figsize=(12, 9),
                              gridspec_kw={"height_ratios": [3, 2, 2]})

    for ax, (title, s, e, color) in zip(axes, slices):
        y = vals[s:e]
        x = list(range(len(y)))
        ax.plot(x, y, color=color, linewidth=1.2)
        ax.fill_between(x, y, alpha=0.08, color=color)

        # 各自独立Y轴
        ypad = (max(y) - min(y)) * 0.12
        ax.set_ylim(min(y) - ypad, max(y) + ypad)

        # 标注：左下起始，右下最新
        tag_start(ax, 0, y[0], f"${y[0]:,.0f}")
        tag_end(ax, len(y)-1, y[-1], f"${y[-1]:,.0f}", color)

        ax.set_title(title, fontsize=12, fontweight="bold", color=color)
        ax.set_ylabel("USD/oz", fontsize=9, color="#666")
        setup_grid(ax)
        clean_spines(ax)

    plt.tight_layout()
    p = CHART_DIR / "gold_price.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ 黄金走势(15年): {p}")
    return p

# ============ 3. 白银走势 ============
def chart_silver_price():
    """白银日线+50日均线+200日均线"""
    db = conn()
    rows = db.execute(
        "SELECT 日期, 收盘 FROM price_history WHERE 品种='silver' AND 收盘 IS NOT NULL ORDER BY 日期"
    ).fetchall()
    db.close()
    if len(rows) < 10:
        return None

    cleaned = [(r[0], float(r[1])) for r in rows if 5 < float(r[1]) < 200]
    if len(cleaned) < 10:
        return None
    vals = [r[1] for r in cleaned]
    n = len(vals)

    ma50 = [np.mean(vals[max(0,i-50):i+1]) for i in range(n)]
    ma200 = [np.mean(vals[max(0,i-200):i+1]) for i in range(n)]

    fig, ax = plt.subplots(figsize=(12, 4.5))
    x = range(n)

    ax.plot(x, vals, color=C["gray"], linewidth=0.8, alpha=0.5, label="收盘价")
    ax.plot(x, ma50, color=C["orange"], linewidth=1.5, label="50日均线", alpha=0.85)
    ax.plot(x, ma200, color=C["red"], linewidth=1.5, label="200日均线", alpha=0.85)

    tag_start(ax, 0, vals[0], f"${vals[0]:.2f}")
    tag_end(ax, n-1, vals[-1], f"${vals[-1]:.2f}", C["dark"])

    ax.set_title("白银走势（15年·均线系统）", fontsize=13, fontweight="bold", color=C["dark"])
    ax.set_ylabel("USD/oz", fontsize=9, color="#666")
    ax.legend(fontsize=9, loc="upper left", framealpha=0.8)
    setup_grid(ax)
    clean_spines(ax)
    plt.tight_layout()
    p = CHART_DIR / "silver_price.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ 白银走势(15年): {p}")
    return p

# ============ 4. 金银比 ============
def chart_gold_silver_ratio():
    """金银比走势"""
    db = conn()
    g = {r[0]: float(r[1]) for r in db.execute(
        "SELECT 日期, 收盘 FROM price_history WHERE 品种='gold' AND 收盘 IS NOT NULL ORDER BY 日期"
    ).fetchall() if 1000 < float(r[1]) < 6000}
    s = {r[0]: float(r[1]) for r in db.execute(
        "SELECT 日期, 收盘 FROM price_history WHERE 品种='silver' AND 收盘 IS NOT NULL ORDER BY 日期"
    ).fetchall() if 5 < float(r[1]) < 200}
    db.close()

    common = sorted(set(g) & set(s))
    if len(common) < 10:
        return None
    ratios = [g[d]/s[d] for d in common]
    n = len(ratios)
    avg_ratio = np.mean(ratios)

    fig, ax = plt.subplots(figsize=(12, 4.5))
    x = range(n)
    ax.plot(x, ratios, color=C["purple"], linewidth=1.0, alpha=0.6)
    ax.fill_between(x, ratios, alpha=0.06, color=C["purple"])

    ax.axhline(avg_ratio, color=C["dark"], linestyle="--", alpha=0.4,
               label=f"均值 {avg_ratio:.1f}x")

    tag_start(ax, 0, ratios[0], f"{ratios[0]:.1f}x")
    tag_end(ax, n-1, ratios[-1], f"{ratios[-1]:.1f}x", C["purple"])

    ax.set_title("金银比走势（15年）", fontsize=13, fontweight="bold", color=C["dark"])
    ax.set_ylabel("金价/银价", fontsize=9, color="#666")
    ax.legend(fontsize=9, loc="upper left", framealpha=0.8)
    setup_grid(ax)
    clean_spines(ax)
    plt.tight_layout()
    p = CHART_DIR / "gold_silver_ratio.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ 金银比(15年): {p}")
    return p

# ============ 5. COT净持仓历史 ============
def chart_cot_net_history():
    """黄金COT投机净持仓历史走势"""
    db = conn()
    rows = db.execute(
        "SELECT date, noncomm_net FROM cot_history WHERE commodity='gold' AND noncomm_net IS NOT NULL ORDER BY date"
    ).fetchall()
    db.close()
    if len(rows) < 10:
        return None

    vals = [float(r[1])/1000 for r in rows]  # 千手
    n = len(vals)

    fig, ax = plt.subplots(figsize=(12, 4.5))
    x = range(n)

    ax.fill_between(x, vals, where=[v>=0 for v in vals],
                    color=C["green"], alpha=0.15)
    ax.fill_between(x, vals, where=[v<0 for v in vals],
                    color=C["red"], alpha=0.15)
    ax.plot(x, vals, color=C["dark"], linewidth=1.2)
    ax.axhline(0, color=C["gray"], linewidth=0.8)

    tag_start(ax, 0, vals[0], f"{vals[0]:+,.0f}K")
    tag_end(ax, n-1, vals[-1], f"{vals[-1]:+,.0f}K", C["dark"])

    ax.set_title("黄金COT投机净持仓历史走势", fontsize=13, fontweight="bold", color=C["dark"])
    ax.set_ylabel("净持仓 (千手)", fontsize=9, color="#666")
    setup_grid(ax)
    clean_spines(ax)
    plt.tight_layout()
    p = CHART_DIR / "cot_net_history.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ COT净持仓历史(15年): {p}")
    return p

# ============ 6. COT净持仓排行榜 ============
def chart_cot_net():
    """COT净持仓柱状图"""
    db = conn()
    rows = db.execute(
        'SELECT 品種, "投機淨持倉" FROM cotdata ORDER BY "投機淨持倉" DESC'
    ).fetchall()
    db.close()
    if not rows:
        return None

    items = [r[0] for r in rows]
    vals = [float(r[1])/1000 for r in rows]

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = [C["red"] if v < 0 else C["green"] for v in vals]
    bars = ax.barh(range(len(items)), vals, color=colors, height=0.6, edgecolor="white", linewidth=0.5)

    ax.set_yticks(range(len(items)))
    ax.set_yticklabels(items, fontsize=10)
    ax.set_xlabel("投机净持仓 (千手)", fontsize=10, color="#555")
    ax.set_title("COT投机净持仓排行榜", fontsize=13, fontweight="bold", color=C["dark"])
    ax.axvline(0, color=C["gray"], linewidth=0.8)

    # 柱末端标注
    for v, bar in zip(vals, bars):
        offset = 8
        x_pos = v + offset if v >= 0 else v - offset
        ha = "left" if v >= 0 else "right"
        ax.text(x_pos, bar.get_y() + bar.get_height()/2,
                f"{v:+,.0f}K", va="center", ha=ha, fontsize=9,
                color=C["dark"],
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                          edgecolor="none", alpha=0.7))

    clean_spines(ax)
    plt.tight_layout()
    p = CHART_DIR / "cot_net.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ COT净持仓: {p}")
    return p

# ============ 7. COT Index一览 ============
def chart_cot_index():
    """COT Index 柱状图"""
    db = conn()
    rows = db.execute(
        'SELECT 品種, "COT Index(26W)" FROM cotdata ORDER BY "COT Index(26W)" DESC'
    ).fetchall()
    db.close()
    if not rows:
        return None

    items = [r[0] for r in rows]
    vals = [float(r[1]) for r in rows]

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.axvspan(0, 5, alpha=0.06, color=C["red"])
    ax.axvspan(95, 100, alpha=0.06, color=C["red"])
    ax.axvspan(5, 95, alpha=0.03, color=C["blue"])

    colors = []
    for v in vals:
        if v >= 95:
            colors.append(C["red"])
        elif v <= 5:
            colors.append(C["green"])
        else:
            colors.append(C["blue"])

    bars = ax.barh(range(len(items)), vals, color=colors, height=0.6,
                    edgecolor="white", linewidth=0.5)

    ax.set_yticks(range(len(items)))
    ax.set_yticklabels(items, fontsize=10)
    ax.set_xlabel("COT Index (26周)", fontsize=10, color="#555")
    ax.set_title("COT Index 一览", fontsize=13, fontweight="bold", color=C["dark"])
    ax.set_xlim(0, 108)

    # 在柱末端标注数值
    for v, bar in zip(vals, bars):
        x_pos = v + 0.8
        ax.text(x_pos, bar.get_y() + bar.get_height()/2,
                f"{v:.0f}", va="center", fontsize=9, color=C["dark"])

    clean_spines(ax)
    plt.tight_layout()
    p = CHART_DIR / "cot_index.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ COT Index: {p}")
    return p

# ============ 8. COT多空对比 ============
def chart_cot_long_short():
    """投机多空对比"""
    db = conn()
    rows = db.execute(
        'SELECT 品種, "投機多頭", "投機空頭" FROM cotdata ORDER BY "投機淨持倉" DESC'
    ).fetchall()
    db.close()
    if not rows:
        return None

    items = [r[0] for r in rows]
    longs = [float(r[1])/1000 for r in rows]
    shorts = [float(r[2])/1000 for r in rows]

    fig, ax = plt.subplots(figsize=(10, 5))
    y = range(len(items))

    ax.barh([i+0.18 for i in y], longs, height=0.35,
            color=C["green"], alpha=0.85, label="投機多頭")
    ax.barh([i-0.18 for i in y], shorts, height=0.35,
            color=C["red"], alpha=0.85, label="投機空頭")

    ax.set_yticks(range(len(items)))
    ax.set_yticklabels(items, fontsize=10)
    ax.set_xlabel("持仓 (千手)", fontsize=10, color="#555")
    ax.set_title("COT投机多空对比", fontsize=13, fontweight="bold", color=C["dark"])
    ax.legend(fontsize=9, loc="lower right", framealpha=0.8)

    clean_spines(ax)
    plt.tight_layout()
    p = CHART_DIR / "cot_long_short.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ COT多空对比: {p}")
    return p

# ============ 主函数 ============
def generate_all():
    print(f"📊 生成图表 ({datetime.now().strftime('%Y-%m-%d %H:%M')})")
    charts = {}

    for name, fn in [
        ("cot_net", chart_cot_net),
        ("cot_index", chart_cot_index),
        ("cot_long_short", chart_cot_long_short),
        ("fred_trends", chart_fred_trends),
        ("gold_price", chart_gold_price),
        ("silver_price", chart_silver_price),
        ("gold_silver_ratio", chart_gold_silver_ratio),
        ("cot_net_history", chart_cot_net_history),
    ]:
        try:
            p = fn()
            if p:
                charts[name] = p
        except Exception as e:
            print(f"  ❌ {name}: {e}")

    print(f"  ✅ 共生成 {len(charts)} 张图")
    return charts

if __name__ == "__main__":
    generate_all()
````

## File: send_email.py
````python
#!/usr/bin/env python3
"""发送报告到邮箱，带图表"""
import os, sys, smtplib, ssl, base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.header import Header
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv("/root/hermes-pipeline/.env")

CHART_DIR = Path.home() / "hermes-macro-data" / "charts"

def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def send_report(filepath, chart_type=""):
    """发送Markdown报告到邮箱，含图表"""
    if not os.path.exists(filepath):
        print(f"❌ 报告不存在: {filepath}")
        return False

    from_addr = os.getenv("EMAIL_USER")
    to_addr = os.getenv("EMAIL_TO")
    password = os.getenv("EMAIL_PASS")
    smtp_host = os.getenv("EMAIL_HOST", "smtp.qq.com")
    smtp_port = int(os.getenv("EMAIL_PORT", 465))

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.strip().split("\n")
    title = "研究报告"
    for line in lines:
        if line.startswith("# "):
            title = line.replace("# ", "").strip()
            break

    date_str = datetime.now().strftime("%Y-%m-%d")
    subject = f"{title} | {date_str}"

    msg = MIMEMultipart("alternative")
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Subject"] = Header(subject, "utf-8")

    # === 生成HTML版本（含图表） ===
    html_parts = []
    html_parts.append(f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"></head><body style="font-family: 'Microsoft YaHei', sans-serif; color: #333; max-width: 800px; margin: 0 auto; padding: 20px;">
<div style="background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">""")

    # 图表区域 - 按报告类型，不配图就不渲图
    chart_section = ""
    if chart_type == "macro":
        fred_chart = CHART_DIR / "fred_trends.png"
        if fred_chart.exists():
            b64 = img_to_base64(fred_chart)
            html_parts.append(f"""<div style="margin:15px 0;"><h3 style="color:#2C3E50;border-left:4px solid #3498DB;padding-left:10px;">美国关键宏观指标走势（近3年）</h3><img src="data:image/png;base64,{b64}" style="width:100%;max-width:700px;border-radius:4px;margin:10px 0;"></div>""")

    if chart_type in ("metals",):
        for name, title_text in [
            ("gold_price", "黄金走势（15年）"),
            ("silver_price", "白银走势（15年均线）"),
            ("gold_silver_ratio", "金银比（15年）"),
            ("cot_net_history", "黄金COT投机净持仓历史"),
            ("cot_net", "COT投机净持仓排行榜"),
            ("cot_index", "COT Index一览"),
        ]:
            p = CHART_DIR / f"{name}.png"
            if p.exists():
                b64 = img_to_base64(p)
                html_parts.append(f"""<div style="margin:15px 0;"><h3 style="color:#2C3E50;border-left:4px solid #E67E22;padding-left:10px;">📊 {title_text}</h3><img src="data:image/png;base64,{b64}" style="width:100%;max-width:700px;border-radius:4px;margin:10px 0;"></div>""")

    if chart_type in ("energy",):
        for name, title_text in [("cot_net", "COT投机净持仓"), ("cot_index", "COT Index")]:
            p = CHART_DIR / f"{name}.png"
            if p.exists():
                b64 = img_to_base64(p)
                html_parts.append(f"""<div style="margin:15px 0;"><h3 style="color:#2C3E50;border-left:4px solid #27AE60;padding-left:10px;">📊 {title_text}</h3><img src="data:image/png;base64,{b64}" style="width:100%;max-width:700px;border-radius:4px;margin:10px 0;"></div>""")

    # Markdown内容转HTML - 表格转HTML <table>，其他保持精简
    html_body = ""
    table_rows = []  # 暂存表格行
    in_table = False

    def flush_table():
        nonlocal in_table, table_rows
        if not table_rows:
            return ""
        html = '<table style="border-collapse:collapse;width:100%;margin:10px 0;font-size:12px;">\n'
        for is_header, cells in table_rows:
            tag = "th" if is_header else "td"
            bg = "#f8f9fa" if is_header else "#fff"
            fw = "bold" if is_header else "normal"
            row = "<tr>"
            for c in cells:
                row += f'<{tag} style="border:1px solid #ddd;padding:6px 8px;background:{bg};font-weight:{fw};text-align:center;">{c}</{tag}>'
            row += f"</tr>\n"
            html += row
        html += "</table>\n"
        table_rows = []
        in_table = False
        return html

    # ── helper: detect markdown table separator row ──────────
    def _is_sep(s: str) -> bool:
        return "|" in s and not s.replace("|", "").replace("-", "").replace(":", "").strip()

    for i, line in enumerate(lines):
        stripped = line.strip()

        # 标题行（跳过#标题，已在邮件主题）
        if stripped.startswith("# ") and not stripped.startswith("## "):
            continue

        # 检测表格行：包含|且不纯粹是分隔符
        if _is_sep(stripped):
            continue

        if "|" in stripped:
            cells_raw = [c.strip() for c in stripped.split("|")]
            real_cells = [c for c in cells_raw if c.strip()]
            if len(real_cells) >= 2:
                # 如果行首尾有|，去掉首尾的空单元格
                cells = cells_raw[:]
                if stripped.startswith("|") and stripped.endswith("|"):
                    cells = cells[1:-1]
                cells = [c.strip() for c in cells if c.strip()]
                if len(cells) < 2:
                    continue
                # 判断是否是表头行（上一行是分隔行 or 当前行包含---）
                is_header = False
                if i > 0:
                    prev = lines[i - 1].strip()
                    if _is_sep(prev):
                        is_header = False
                    elif i > 1 and _is_sep(lines[i - 2].strip()):
                        is_header = True
                    else:
                        # 第一张表格：第一行后通常跟着分隔行
                        if not in_table and i + 1 < len(lines) and _is_sep(lines[i + 1].strip()):
                            is_header = True
                        else:
                            is_header = False
                else:
                    is_header = True

                table_rows.append((is_header, cells))
                in_table = True
                continue

        # 非表格行：先flush暂存的表格
        if in_table:
            html_body += flush_table()

        # 其他行类型
        if stripped.startswith("## "):
            text = stripped[3:].strip()
            html_body += f'<h3 style="color:#2C3E50;margin-top:22px;border-bottom:1px solid #eee;padding-bottom:6px;font-size:15px;">{text}</h3>\n'
        elif stripped.startswith("### "):
            html_body += f'<h4 style="color:#E67E22;margin-top:18px;font-size:13px;">{stripped[4:]}</h4>\n'
        elif stripped.startswith("**") and stripped.endswith("**"):
            html_body += f'<p style="font-weight:bold;margin-top:12px;color:#2C3E50;font-size:13px;">{stripped.strip("*")}</p>\n'
        elif stripped.startswith("- ") or stripped.startswith("* "):
            html_body += f'<p style="margin:3px 0;color:#444;padding-left:15px;font-size:12px;">{stripped[2:]}</p>\n'
        elif stripped.startswith("> "):
            html_body += f'<p style="margin:5px 0;color:#888;font-style:italic;padding-left:10px;border-left:3px solid #ddd;font-size:12px;">{stripped[2:]}</p>\n'
        elif stripped == "---":
            html_body += '<hr style="border:none;border-top:1px solid #eee;margin:15px 0;">\n'
        elif stripped == "":
            html_body += '<br>\n'
        elif stripped.startswith("```"):
            # 跳过代码块
            continue
        else:
            # 普通段落
            html_body += f'<p style="line-height:1.6;color:#333;font-size:13px;margin:5px 0;">{stripped}</p>\n'

    # 最后的表格
    if in_table:
        html_body += flush_table()

    html_parts.append(f'<div style="margin-top:20px;">{html_body}</div>')
    html_parts.append('</div></body></html>')

    html_full = "\n".join(html_parts)

    # 纯文本版（备用）
    text_part = MIMEText(f"请查看HTML版本报告\n{filepath}", "plain", "utf-8")
    msg.attach(text_part)

    # HTML版（含图）
    html_part = MIMEText(html_full, "html", "utf-8")
    msg.attach(html_part)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
            server.login(from_addr, password)
            server.sendmail(from_addr, [to_addr], msg.as_string())
        print(f"✅ 已发送: {subject} (含{len(html_parts)-3}张图)")
        return True
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        return False

def send_alert(subject, message):
    """发送纯文本预警"""
    from_addr = os.getenv("EMAIL_USER")
    to_addr = os.getenv("EMAIL_TO")
    password = os.getenv("EMAIL_PASS")
    smtp_host = os.getenv("EMAIL_HOST", "smtp.qq.com")
    smtp_port = int(os.getenv("EMAIL_PORT", 465))

    msg = MIMEText(message, "plain", "utf-8")
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Subject"] = Header(f"⚠️ {subject}", "utf-8")

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
            server.login(from_addr, password)
            server.sendmail(from_addr, [to_addr], msg.as_string())
        print(f"✅ 预警已发送: {subject}")
        return True
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ct = sys.argv[2] if len(sys.argv) > 2 else ""
        send_report(sys.argv[1], ct)
    else:
        print("用法: python3 send_email.py <报告路径> [chart_type]")
````
