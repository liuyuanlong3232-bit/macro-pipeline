# Hermes 工具箱 — 安装清单 & 使用指南

> 安装日期：2026-06-13
> 本地：Windows 10 + Hermes Desktop
> VPS：45.77.126.71:58234 (Ubuntu 22.04)

---

## 一、总览

| 编号 | 工具/技能 | 分类 | 自动/手动 | 已装在哪 |
|------|----------|------|----------|---------|
| 1 | Superpowers | 流程纪律 | 🔵 自动 | 本地 |
| 2 | Scrapling | 网页抓取 | 🟢 手动 | 本地+VPS |
| 3 | scrapling-finance-scraper | 金融抓取技能 | 🟢 手动 | 本地 |
| 4 | Repomix | 仓库打包 | 🟢 手动 | 本地+VPS |
| 5 | TokScale | Token监控 | 🟢 手动 | 本地+VPS |
| 6 | gbrain | 知识脑 | 🟢 手动 | 本地 |
| 7 | Mission Control | Agent仪表盘 | 🟢 手动(后台) | 本地 |
| 8 | gstack CLI | 无头浏览器+PDF | 🟢 手动 | 本地 |
| 9 | hermes-dojo | 自学自修 | 🟢 手动 | 本地 |
| 10 | oh-my-hermes | 多代理编排 | 🟢 手动 | 本地 |
| 11 | wondelai/skills | 跨领域技能库 | 🟢 手动 | 本地 |
| 12 | hermes-agent-self-evolution | 进化引擎 | 🟢 手动 | 本地 |
| 13 | macro-futures-pipeline | 宏光流水线技能 | 🟢 手动 | 本地 |

**图例：**
- 🔵 **自动** = 装好就生效，不需要你专门喊它
- 🟢 **手动** = 需要你说"帮我xxx"我才会调用

---

## 二、自动生效（不用你管）

### 1. Superpowers — 流程纪律

**功能：** 让我做复杂任务时先规划、多任务时并行、完成前先验证、做完后记录。
**你不需要做任何事** — 装好后新会话自动生效。你会注意到：
- 我开始做复杂事之前会先停下来写计划
- 多件事我会并行处理而不是一件件来
- 我说"做好了"时会先运行验证再确认

---

## 三、手动调用（需要你下指令）

### 2. Scrapling — 网页抓取

**功能：** 自适应爬虫，能绕过Cloudflare等反爬，自动伪装浏览器指纹。
**怎么叫我：** 说"抓XX网站的数据"即可，我会自动用Scrapling。
**示例：**
```
抓EIA的周度石油数据
抓CFTC的COT持仓
抓USDA的WASDE报告
```
**特性：**
- 本地自动走v2rayN代理(:10808)，VPS直连
- 静态页用`Fetcher`（快），Cloudflare页用`StealthyFetcher`（慢但能过）
- 三种模式：HTTP静态 / JS动态 / Cloudflare隐身

---

### 3. scrapling-finance-scraper — 金融抓取技能

**功能：** Scrapling的金融专用版，内置常见数据源URL、代理配置、CSS选择器模板。
**怎么叫我：** 说"用金融抓取技能 抓XXX"。
**内置数据源：** EIA、CFTC COT、USDA WASDE、NOAA ENSO、CME持仓

---

### 4. Repomix — 仓库打包

**功能：** 把整个项目文件夹打包成一个文件，方便喂给AI分析。
**怎么叫我：** 说"打包仓库"或"repomix"。
**示例：**
```
打包宏光流水线仓库
把macro-pipeline打包成markdown
```
**输出：** 生成 `repomix-output.md`（38个文件→~50K tokens）
**远程仓库（不用克隆）：** `npx repomix --remote liuyuanlong3232-bit/macro-pipeline`

---

### 5. TokScale — Token用量&费用监控

**功能：** 查看今天/本周/本月Hermes的token消耗和费用，支持全屏酷炫仪表盘。
**怎么叫我：** 说"看我的token用量"或"费用报告"。
**示例：**
```
今日token用量
本周AI费用
tokscale查看
```
**常用命令：**
```
tokscale models --client hermes --today    # 今日各模型用量
tokscale models --client hermes --week     # 本周
tokscale tui                                # 全屏仪表盘（按q退出）
```
**今天的数据（参考）：** 2,134条消息，133M tokens，$5.90

---

### 6. gbrain — 知识脑

**功能：** 结构化知识图谱（实体+关系+时间线），已用PGLite初始化（零依赖）。
**怎么叫我：** 说"查gbrain"或"存到脑里"。
**示例：**
```
把这份报告存到gbrain
查一下gbrain里关于黄金持仓的记录
```
**常用命令：**
```
gbrain put <标题> < 文件     # 存入知识
gbrain query "黄金COT持仓"   # 搜索
gbrain search "美元指数"     # 关键词搜索
gbrain list                   # 列出所有页
```
**当前状态：** 刚初始化（0页），还没往里存东西。

---

### 7. Mission Control — Agent仪表盘

**功能：** 浏览器打开的Agent管理面板，32个面板管理任务/agent/技能/日志/费用/cron。
**怎么叫我：** 说"打开Mission Control"。
**访问方式：** 浏览器打开 `http://localhost:3000/setup` 创建管理员账号。
**当前状态：** 已安装构建完成，`pnpm start` 后台运行中。
**功能：**
- 看所有agent状态、发任务、监控费用
- 浏览+安装社区技能
- 查看cron任务历史
- 角色权限管理

---

### 8. gstack CLI — 无头浏览器 & PDF生成

**功能：** 两个命令行工具。
**怎么叫我：** 叫我"打开浏览器测XX页面"或"转成PDF"。
**示例：**
```
用gstack浏览器打开example.com看看
把这个markdown转成PDF
```
**命令：**
```
gstack-browse goto https://example.com    # 打开页面
gstack-make-pdf report.md report.pdf       # Markdown→PDF
```

---

### 9. hermes-dojo — 自学自修系统

**功能：** 监控我的表现→找出弱技能→自动修复→生成改进报告。让我越用越好。
**怎么叫我：** 说"dojo分析"或"dojo报告"。
**支持命令：**
```
dojo analyze     # 分析近期的失败模式
dojo improve     # 修复最弱的技能
dojo report      # 生成改进报告
dojo history     # 学习曲线
dojo auto        # 设置每晚自动改进cron
```
**当前状态：** 已安装，但需要 `python3 scripts/seed_demo_data.py` 给它一些历史数据才能开始分析。

---

### 10. oh-my-hermes — 多代理编排（10个技能）

**功能：** 把你的想法变成多代理协作流程。
**怎么叫我：** 说"oh-my-hermes"加具体需求。
**技能清单：**

| 你说 | 实际调用 |
|------|---------|
| `做深度研究 XX主题` | omh-deep-research：多阶段搜索→综合→验证引用 |
| `帮我规划 XX` | omh-ralplan：多角色共识规划（规划师+架构师+批评家讨论到一致） |
| `帮我执行这个计划` | omh-ralph：按计划实现→验证→迭代到通过 |
| `访谈我了解需求` | omh-deep-interview：苏格拉底式需求梳理 |
| `全自动跑一遍 XX` | omh-autopilot：深度研究→访谈→规划→执行完整管道 |

---

### 11. wondelai/skills — 跨领域技能库（50+技能）

**功能：** 50多个基于经典著作的技能，覆盖产品/设计/营销/编程等。
**怎么叫我：** 说出对应关键词即可。

**常用技能速查：**

| 你说 | 背后调用的知识体系 |
|------|-------------------|
| `用JTBD分析` | 待办任务框架（创新） |
| `做CRO分析` | 转化率优化 |
| `UI设计评审` | Refactoring UI |
| `做谈判方案` |  Never Split the Difference |
| `精益画布` | Lean Startup |
| `设计冲刺` | Google Design Sprint |
| `做品牌故事` | Building a StoryBrand |
| `清洁代码审查` | Clean Code |
| `做系统设计` | DDIA / System Design Interview |
| `写个JTBD脚本` | Jobs-to-be-Done |
| `做A/B测试方案` | CRO方法论 |

---

### 12. hermes-agent-self-evolution — 进化引擎

**功能：** DSPy+GEPA遗传算法自动优化我的技能、提示词、代码。
**怎么叫我：** 说"进化XXX技能"或"自进化"。
**示例：**
```
进化我的scrapling技能
优化图表生成技能
```
**成本：** 每次进化跑约$2-10（10轮迭代，合成数据）。
**命令：**
```bash
cd ~/AppData/Local/hermes/hermes-agent-self-evolution
export HERMES_AGENT_REPO="$HOME/AppData/Local/hermes"
python3 -m evolution.skills.evolve_skill --skill scrapling --iterations 10 --eval-source synthetic
```

---

### 13. macro-futures-pipeline — 宏光数据流水线技能

**功能：** 封装了整套期货研究流水线，你喊一声我就去VPS跑报告。
**怎么叫我：**

| 你说 | 我执行 |
|------|--------|
| `生成宏观周报` | SSH到VPS → run_report.py macro → 发邮件 |
| `生成能源周报` | SSH到VPS → run_report.py energy → 发邮件 |
| `生成贵金属周报` | SSH到VPS → run_report.py metals → 发邮件 |
| `生成国际农业报告` | SSH到VPS → run_report.py agri → 发邮件 |
| `生成中国农业报告` | SSH到VPS → agri_weekly.py china → 发邮件 |
| `发送所有报告` | 上面5个全部跑一遍 |
| `检查cron` | SSH到VPS查 /etc/cron.d/hermes-reports |
| `看看今天的数据` | SSH到VPS查看最新CSV数据 |
| `COT报警检查` | 查monitor.py的输出 |

---

## 四、GitHub上已有的金融类技能（社区缺口）

**结论：没有期货/商品/交易专用技能。**

唯一相关的：
- **itgoyo/hermes-skills** 有8个通用财务技能（financial-analyst、investment-researcher等）——但这些是"角色扮演"类的，不是数据驱动的期货研究
- **我们刚做的 `macro-futures-pipeline` 是第一个**真正的期货商品研究技能

---

## 五、最佳实践：一日流程参考

| 时间 | 流程 |
|------|------|
| 早上 | 说"检查cron" → 看昨晚的报告有没有正常发 |
| 盘中 | 说"看今日token费用" → 监控AI成本 |
| 研究 | 说"做深度研究 黄金COT持仓变化" → oh-my-hermes跑研究 |
| 写报告 | 说"生成贵金属周报" → 自动发送到QQ邮箱 |
| 晚上 | (可选) 说"dojo auto" → 让dojo夜间自我改进 |
