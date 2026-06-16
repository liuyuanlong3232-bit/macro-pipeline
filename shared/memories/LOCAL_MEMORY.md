QQ Bot已关(2026-06-16)。AppID: 1904159904。如需重新启用需重启VPS Hermes gateway。
§
通信渠道：QQ邮箱(452731778)发送周报日报(6份/周)，QQ Bot已关(2026-06-16)。Telegram暂不使用(被墙)。VPS纯数据采集，无AI。
§
两个技能已部署到VPS：知识扩充技能(knowledge-expansion)和毛主席语录(mao-quotes)。位置：/root/hermes-pipeline/skills/。使用方式：输入关键词→极简框架，深挖指令→定点展开。
§
VPS cron(每天): 08:00采集→08:03和风天气→08:04Tushare期货→08:05全球天气→08:10质检→08:30日报。周三23:00 EIA。周五04:00 COT+16:00周报摘要。/etc/cron.d/改完后必须systemctl restart cron。双保险：hermes-reports+root crontab各一套。
§
变现方案已调整：知识星球新规无资质不可发布，报告仅供自己学习使用。系统优化方向：提升数据质量、分析深度、学习效率。
§
VPS：cron(08:0015步)+数据源(FRED31+Yahoo16+天气全球6产区33K+中国9城+Tushare5+COT+EIA+质检)。日报ABCD四板。周报摘要替代旧6份。和风天气Key=p8g.../Host=pg7d.../Key=f8d7。MCP只装OpenWebSearch(百度免费搜)。旧系统全停(代码保留)。农业项目等稳定后启动。
§
用户偏好：极简回答，不要解释分析过程，直接给答案。"给我答案就行"就是这个风格。数据交叉验证概念已加入data-pipeline技能参考文件。
§
农业项目：底层基建已完成(天气9城+期货5品种+全球6产区)，稳定运行3-5天后再启动报告开发。产品孵化三方案已写入agri-data-plan-complete.md：🥇价格参照助手(1-2周)→🥈病害预警(3-4周)→🥉论文助手。4060 8GB够跑8B RAG+Tushare/和风天气数据。司农/神农不适用(不是MCP，部署¥1681+/月)。
§
项目已迁移：D:\hermes\pipeline\（C盘只留.hermes/config）。VPS Hermes已停(6/16)，纯数据采集。本地DeepSeek V4 Pro。和风天气认证：Header X-QW-Api-Key+Host(pg7dnaywrf.re.qweatherapi.com)，不是?key=。
§
macro-futures-pipeline技能已更新v2.0.0：新增旧系统关停协议、天气重复行修复、QWeather obsTime陷阱。precious-metals-reporting已更新v3.0.0(ABCD格式)。macro-financial-pipeline标记为superseded v1.0.1。
§
2026-06-15关键教训：①cron 6字段语法错误→全部11项任务停止(as df.daily/draw.py)②.env被截断→邮箱/XRED Key丢失③Yahoo CSV不入库→日报显示3天旧数据。技能已更新：vps-hermes-deployment(+memory-sync/+collab-example)，macro-futures-pipeline(+yahoo-csv-db-gap)
§
用户想提升Python后端能力。学习方式：以改代学（改现有流水线代码），不看理论书。当前阶段：能读懂简单代码，下一步是能独立改daily_report.py。学习计划：一阶段读懂→二阶段能改→三阶段能写。我承诺改代码时解释每行，留小bug让他修，新任务让他先试。
§
系统模型分工：本地DeepSeek V4 Pro（自行切换），VPS已停Hermes(2026-06-16)，纯数据采集服务器。SSH: ssh -p 58234 -i C:\Users\Administrator\.ssh\id_rsa root@45.77.126.71。cron全在root crontab(17条)。三层知识体系：plans(内置)+memory(内置)+shared(自建GitHub双向同步)。QQ Bot已关。
§
模型方案：本地DeepSeek V4 Pro（用户自行切换），VPS MiMo已停(6/16)。月费¥39已省掉。
§
用户已能独立做安全修复(SQL注入/硬编码/裸except/API泄露)——16文件368行改动，远超"小白"阶段。可直接分配后端开发任务，不需逐行教。代码功底通过实战迅速成长。
