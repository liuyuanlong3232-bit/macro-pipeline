# VPS工作流模式

## 核心理念
代码修改直接在VPS上做，本地Hermes只做日常对话和决策分析。

## 原因
| 环境 | 优势 | 劣势 |
|------|------|------|
| **VPS** | root权限无中断、直连国际API、7×24在线 | 对话体验不如本地 |
| **本地** | 响应快、交互流畅 | 权限限制、需要代理、关机就停 |

## 工作流

### 代码修改
```
用户需求 → SSH到VPS → 在VPS上修改代码 → 测试 → 
本地同步代码 → 推GitHub
```

### 日常运营
```
本地Hermes：对话分析、决策支持
VPS Hermes：数据采集、报告生成、定时任务
QQ Bot：手机端交互
```

## 同步命令

### VPS → 本地
```bash
for f in macro_pipeline.py macro_weekly.py energy_weekly.py metals_weekly.py agri_weekly.py data_scrapers.py charts.py; do
  scp -P 58234 -i C:\\Users\\Administrator\\.ssh\\id_rsa root@45.77.126.71:/root/hermes-pipeline/$f /c/Users/Administrator/hermes-macro-pipeline/
done
```

### 提交到GitHub
```bash
cd /c/Users/Administrator/hermes-macro-pipeline
git add -u
git commit -m "描述改动"
HTTPS_PROXY=http://127.0.0.1:10808 git push
```
