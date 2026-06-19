# VPS Hermes 记忆

## 系统状态
- VPS: 45.77.126.71:58234
- 模型: MiMo 2.5 Pro
- 数据: /root/hermes-macro-data/
- 报告: /root/hermes-macro-data/reports/

## 工作原则
1. 数据优先，不编造
2. 主动解决，不问用户
3. 混合模式：数据+LLM分析
4. 最小修改：只patch不重写

## 已完成
- 重构6个报告脚本
- 修复空缺数据
- 统一格式
§
VPS Hermes已重构代码(+1063行)，本地已同步并推送到GitHub。MiMo 2.5 Pro比V4 Flash聪明29分(86 vs 57)。VPS SSH: ssh -p 58234 -i C:\Users\Administrator\.ssh\id_rsa root@45.77.126.71
§
系统状态备忘：VPS 45.77.126.71:58234，MiMo 2.5 Pro(¥39/月)，FRED API已修复。技能已更新(DB Schema/ .env陷阱/Cron 5字段)。代码修改在VPS上做，本地同步推GitHub。用户要求：不问他，自己做；数据优先；极简回答。
§
QQ Bot部署成功！VPS: 45.77.126.71:58234，模型MiMo 2.5 Pro。QQ Bot已连接(WebSocket正常)。AppID: 1904159904。使用方式：私聊直接发消息，群聊@机器人。每月主动消息限制4条，被动消息无限制。
§
通信渠道：邮箱(QQ邮箱452731778@qq.com)发送周报日报(6份/周)，QQ Bot用于日常对话(每月主动消息4条限制)。Telegram暂不使用(被墙)。VPS Hermes MiMo 2.5 Pro已部署，网关运行中。
§
两个技能已部署到VPS：知识扩充技能(knowledge-expansion)和毛主席语录(mao-quotes)。位置：/root/hermes-pipeline/skills/。使用方式：输入关键词→极简框架，深挖指令→定点展开。
§
VPS时区已改为中国时间(Asia/Shanghai UTC+8)。数据采集cron：每日08:00采集FRED/Yahoo，周三23:00采集EIA，周五04:00采集COT。报告cron：周一宏观/周四能源/周五国际农业+中国农业/周六贵金属/周日资产配置。数据源发布时间：EIA周三22:30，COT周五03:30。
§
变现方案已调整：知识星球新规无资质不可发布，报告仅供自己学习使用。系统优化方向：提升数据质量、分析深度、学习效率。
§
VPS Hermes已修复11项问题(2026-06-14)：Yahoo采集/CFTC URL/DGS5恢复/FedWatch API/FRED Key修复。代码已同步到本地并推送GitHub。FRED_API_KEY已正确写入32位。数据流水线全部恢复。
§
用户结论：本地Hermes(我)+VPS Hermes(云端)配合就够了，不需要其他软件。核心定位：本地做主力交互和分析，VPS做7x24数据工厂和定时任务。MiMo 2.5 Pro ¥39/月。VPS SSH: ssh -p 58234 -i C:\Users\Administrator\.ssh\id_rsa root@45.77.126.71。FRED_API_KEY已修复32位。
§
用户偏好：极简回答，不要解释分析过程，直接给答案。"给我答案就行"就是这个风格。数据交叉验证概念已加入data-pipeline技能参考文件。
§
农业数据业务已做全案计划(.hermes/plans/agri-data-plan-complete.md)。核心：爬取数据(USDA优良率/出口检验/美湾库存)都是政府公开数据，转化后可用。公众号个人订阅号无需金融资质。知识星球实名认证即可收费。第一阶段先把现有报告脚本里的数值转为趋势描述，加免责声明。
§
VPS环境比本地好用（root权限无中断）。代码修改直接在VPS上做，我同步到本地推GitHub。本地只做日常对话和决策分析。
§
VPS cron已规范化(2026-06-15)：用`scripts/daily_collect.py`替代内联Python -c。数据时效性修复：采集后自动CSV→SQLite导入，日报不再读3天旧数据。VPS Hermes协作模型：诊断(chat -q) + 执行(SSH root)。
§
macro-futures-pipeline技能已更新：新增DB Schema速查表、.env截断陷阱、Cron 5字段语法规则、日报生成器文档、VPS优先工作流。