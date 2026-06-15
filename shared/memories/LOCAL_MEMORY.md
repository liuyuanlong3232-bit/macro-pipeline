QQ Bot部署成功！VPS: 45.77.126.71:58234，模型MiMo 2.5 Pro。QQ Bot已连接(WebSocket正常)。AppID: 1904159904。使用方式：私聊直接发消息，群聊@机器人。每月主动消息限制4条，被动消息无限制。
§
通信渠道：邮箱(QQ邮箱452731778@qq.com)发送周报日报(6份/周)，QQ Bot用于日常对话(每月主动消息4条限制)。Telegram暂不使用(被墙)。VPS Hermes MiMo 2.5 Pro已部署，网关运行中。
§
两个技能已部署到VPS：知识扩充技能(knowledge-expansion)和毛主席语录(mao-quotes)。位置：/root/hermes-pipeline/skills/。使用方式：输入关键词→极简框架，深挖指令→定点展开。
§
VPS cron(每天): 08:00采集→08:03天气→08:04期货→08:05全球天气→08:10质检→08:30日报。周三23:00 EIA。周五04:00 COT+16:00周报摘要。旧6份周报已停。
§
变现方案已调整：知识星球新规无资质不可发布，报告仅供自己学习使用。系统优化方向：提升数据质量、分析深度、学习效率。
§
VPS：cron(08:0015步)+数据源(FRED31+Yahoo16+天气全球6产区33K+中国9城+Tushare5+COT+EIA+质检)。日报ABCD四板。周报摘要替代旧6份。和风天气Key=p8g.../Host=pg7d.../Key=f8d7。MCP只装OpenWebSearch(百度免费搜)。旧系统全停(代码保留)。农业项目等稳定后启动。
§
用户结论：本地Hermes(我)+VPS Hermes(云端)配合就够了，不需要其他软件。核心定位：本地做主力交互和分析，VPS做7x24数据工厂和定时任务。MiMo 2.5 Pro ¥39/月。VPS SSH: ssh -p 58234 -i C:\Users\Administrator\.ssh\id_rsa root@45.77.126.71。FRED_API_KEY已修复32位。
§
用户偏好：极简回答，不要解释分析过程，直接给答案。"给我答案就行"就是这个风格。数据交叉验证概念已加入data-pipeline技能参考文件。
§
农业项目：底层基建已完成(天气9城+期货5品种+全球6产区)，稳定运行3-5天后再启动报告开发。计划文件：agri-data-plan-complete.md
§
VPS环境比本地好用（root权限无中断）。代码修改直接在VPS上做，我同步到本地推GitHub。本地只做日常对话和决策分析。
§
macro-futures-pipeline技能已更新v2.0.0：新增旧系统关停协议、天气重复行修复、QWeather obsTime陷阱。precious-metals-reporting已更新v3.0.0(ABCD格式)。macro-financial-pipeline标记为superseded v1.0.1。
§
2026-06-15关键教训：①cron 6字段语法错误→全部11项任务停止(as df.daily/draw.py)②.env被截断→邮箱/XRED Key丢失③Yahoo CSV不入库→日报显示3天旧数据。技能已更新：vps-hermes-deployment(+memory-sync/+collab-example)，macro-futures-pipeline(+yahoo-csv-db-gap)
§
用户想提升Python后端能力。学习方式：以改代学（改现有流水线代码），不看理论书。当前阶段：能读懂简单代码，下一步是能独立改daily_report.py。学习计划：一阶段读懂→二阶段能改→三阶段能写。我承诺改代码时解释每行，留小bug让他修，新任务让他先试。
§
系统模型分工：本地DeepSeek V4 Pro（自行切换），VPS MiMo 2.5 Pro ¥39/月固定。SSH: ssh -p 58234 -i C:\Users\Administrator\.ssh\id_rsa root@45.77.126.71。cron：daily_collect+daily_report+6份周报。三层知识体系：plans(内置)+memory(内置)+shared(自建GitHub双向同步)。
§
模型方案定稿：本地DeepSeek V4 Pro（用户自行切换），VPS云端MiMo 2.5 Pro ¥39/月固定。MiMo月耗~120万实际token+7600万缓存，¥39刚好月均。不够再升级套餐。