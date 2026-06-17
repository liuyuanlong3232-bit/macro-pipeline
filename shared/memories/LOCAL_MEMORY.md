QQ Bot已关(6/16)AppID:1904159904。通信：QQ邮箱(452731778)6份/周。Telegram暂不使用(被墙)。VPS纯数据采集无AI。
§
VPS timezone已改为UTC(2026-06-16)。cron时间全部从CST+8换算为UTC(-8h)。双保险：hermes-reports(/etc/cron.d/)+root crontab各一套。改完后必须systemctl restart cron。日常采集UTC 00:00(=CST 08:00)。
§
VPS状态(6/16)：时区UTC，cron已换算(00:00=CST08:00)。Hermes已停，纯数据采集。hermes.db(23MB)+19个脚本+15条cron。SSH: ssh -p 58234 root@45.77.126.71。邮件发送不依赖Hermes(smtplib)。
§
用户偏好：极简回答，不要解释分析过程，直接给答案。"给我答案就行"就是这个风格。数据交叉验证概念已加入data-pipeline技能参考文件。
§
农业项目：底层基建已完成(天气9城+期货5品种+全球6产区)，稳定运行3-5天后再启动报告开发。产品孵化三方案已写入agri-data-plan-complete.md：🥇价格参照助手(1-2周)→🥈病害预警(3-4周)→🥉论文助手。4060 8GB够跑8B RAG+Tushare/和风天气数据。司农/神农不适用(不是MCP，部署¥1681+/月)。
§
项目已迁移：D:\hermes\pipeline\（C盘只留.hermes/config）。VPS Hermes已停(6/16)，纯数据采集。本地DeepSeek V4 Pro。和风天气认证：Header X-QW-Api-Key+Host(pg7dnaywrf.re.qweatherapi.com)，不是?key=。
§
系统架构(6/16)：本地DeepSeek V4 Pro + VPS纯采集(45.77.126.71:58234)。项目D:\hermes\pipeline\。Git三方同步。硬性规则：本地改→VPS测试→推Git。cron统一用deploy/hermes-cron文件管理。
§
用户已能独立做安全修复(SQL注入/硬编码/裸except/API泄露)——16文件368行改动，远超"小白"阶段。可直接分配后端开发任务，不需逐行教。代码功底通过实战迅速成长。
§
MCP已部署：OpenWebSearch(本地+VPS)，免费百度搜索，无需API Key。和风天气已接入日报D区(9城)。Tushare已接入日报D区(5品种)。Brave Search未装(需信用卡)。其他MCP(Sequential Thinking/Context7/Obsidian等)均不需要。
§
邮件问题(6/16)：QQ邮箱拦截自动邮件。日志显示"已发送"但用户未收到。原因：连续发HTML表格被判垃圾邮件。需查垃圾箱/广告邮件文件夹。解决方向：改邮件标题+调整发送频率。
§
用户成长里程碑(6/16)：从"小白"到独立修复16文件368行安全漏洞(SQL注入/硬编码/裸except)。能直接分配后端开发任务。学习方式：以改代学，不看理论书。
§
部署文件位置：deploy/hermes-cron(cron定义), deploy/HERMES_RULES.md(工作纪律), deploy/hermes-cron部署到VPS:/etc/cron.d/hermes-reports。常用路径：.hermes/plans/(计划文档), D:\hermes\pipeline\(代码仓库), shared/(Git同步)
§
数据采集风控调度器(Orchestrator)已实现：NORMAL/THROTTLED/BLOCKED三态检测+自动冷却+状态持久化。详见shared/orchestrator.py。所有HTTP请求走safe_request()，每次记录状态。连续3次429→BLOCKED冷却10-30分钟。状态文件meta/orchestrator_state.json。
§
Orchestrator观察期(6/16-6/18)：①BLOCKED误触发②mode叠加降速③state.json偏保守。每天中午12:00 UTC自动检查VPS日志。观察3天无异常→可进PROD。
§
时区规则：VPS=UTC，本地=UTC+8(CST)。所有cron必须用UTC时间。转换公式：CST-8=UTC。例如08:00 CST=00:00 UTC，20:00 CST=12:00 UTC。