# LOCAL MEMORY EXPORT
> Auto-synced from `%LOCALAPPDATA%/hermes/memories/MEMORY.md`

QQ Bot已关(6/16)AppID:1904159904。通信：QQ邮箱(452731778)6份/周。Telegram暂不使用(被墙)。VPS纯数据采集无AI。

VPS timezone已改为UTC(2026-06-16)。cron时间全部从CST+8换算为UTC(-8h)。双保险：hermes-reports(/etc/cron.d/)+root crontab各一套。改完后必须systemctl restart cron。日常采集UTC 00:00(=CST 08:00)。

用户偏好：极简回答+"给我答案就行"。交易哲学：关注共识度概念(命中率高=无超额收益，命中率低+正确=Alpha)。三因子模型价值在于发现市场未定价的东西。每次修改后要求检查代码/数据源/调用正确性。

农业项目：底层基建已完成(天气9城+期货5品种+全球6产区)，稳定运行3-5天后再启动报告开发。产品孵化三方案已写入agri-data-plan-complete.md：🥇价格参照助手(1-2周)→🥈病害预警(3-4周)→🥉论文助手。4060 8GB够跑8B RAG+Tushare/和风天气数据。司农/神农不适用(不是MCP，部署¥1681+/月)。

项目已迁移：D:\hermes\pipeline\（C盘只留.hermes/config）。VPS Hermes已停(6/16)，纯数据采集。本地DeepSeek V4 Pro。和风天气认证：Header X-QW-Api-Key+Host(pg7dnaywrf.re.qweatherapi.com)，不是?key=。

系统架构(6/22)：本地DeepSeek+VPS(45.77.126.71:58234)。D:\hermes\pipeline\。日报v2.0(三因子双层架构+天气+金十+COT)。Git 8ac468e。133表26.8万行。三因子：USD_macro(CPI/NFP/Fed,0.6权重)+USD_market(TIP/DXY/金十,0.4权重)。

用户已能独立做安全修复(SQL注入/硬编码/裸except/API泄露)——16文件368行改动，远超"小白"阶段。可直接分配后端开发任务，不需逐行教。代码功底通过实战迅速成长。

MCP已部署：OpenWebSearch(本地+VPS)免费百度搜索+**金十数据MCP**(E区财经日历+F区实时快讯,6/19接入)。和风天气(日报D区9城)+Tushare(日报D区5品种)。Brave Search未装(需信用卡)。

邮件已解决(6/22)：VPS cron每天00:35 CST自动发送日报到QQ邮箱(452731778@qq.com)。日志/var/log/hermes_email.log。之前问题：cron只生成报告不发送邮件，现已修复。

部署文件位置：deploy/hermes-cron(cron定义), deploy/HERMES_RULES.md(工作纪律), deploy/hermes-cron部署到VPS:/etc/cron.d/hermes-reports。常用路径：.hermes/plans/(计划文档), D:\hermes\pipeline\(代码仓库), shared/(Git同步)

数据采集风控调度器(Orchestrator)：NORMAL/THROTTLED/BLOCKED三态检测+自动冷却+状态持久化(6/16实现)。详见shared/orchestrator.py。连续3次429→BLOCKED冷却10-30分钟。状态文件meta/orchestrator_state.json。

时区规则：VPS=UTC，本地=UTC+8(CST)。所有cron必须用UTC时间。转换公式：CST-8=UTC。例如08:00 CST=00:00 UTC，20:00 CST=12:00 UTC。

数据准确性铁律：MiMo 2.5 Pro定价是¥39/人民币（非USD）。与老大讨论任何成本/价格时，必须标注币种（RMB/USD）。2026-06-17纠正。

配置注意：OpenRouter未配置API Key。会话中切换模型到deepseek/openrouter会断连报"不能使用"。保持默认mimo-v2-omni(xiaomi)即可。如需多模型需先配providers。

金十MCP已接入日报(6/22更新)：黄金/白银/WTI/布伦特优先用金十，Yahoo备用。金十代码：XAUUSD/XAGUSD/USOIL/UKOIL/COPPER+外汇(共13个)，不支持DXY/VIX/10Y/TIPS/锡/农产品。质检阈值：COT 15天(含假期)，EIA月度100天，EIA周度10天。TIP ETF代理TIPS已接入日报①区。伦锡采集已加入daily_collect.py。邮件发送cron已修复(35 0 * * *)。

COT采集：每周六04UTC(紧跟CFTC周五15:30ET发布)。数据源cotdata.net+CFTC官方，当前最新2026-06-09。
