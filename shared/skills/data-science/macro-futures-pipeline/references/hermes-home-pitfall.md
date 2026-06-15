# HERMES_HOME 环境变量：最重要的陷阱

## 问题

VPS上所有周报脚本依赖 `.env` 文件加载API密钥：
- EIA_API_KEY
- FRED_API_KEY  
- TUSHARE_TOKEN

代码中 `load_dotenv()` 的默认路径是：
```python
load_dotenv(Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))) / ".env")
```

当 `HERMES_HOME` **未设置**时，默认找 `~/.hermes/.env`。
但VPS上的 `.env` 实际在 `/root/hermes-pipeline/.env`。

## 症状

- EIA数据全部显示"待更新"
- OPEC数据显示"待更新"
- FRED数据可能正常（因为已缓存到CSV）
- **但手动跑 `python3 energy_weekly.py` 却正常**（交互登录加载了.bashrc）

## 根因

- `.bashrc` 已写入 `export HERMES_HOME=/root/hermes-pipeline`
- 但 `cron` 环境不加载 `.bashrc`
- 已写入 `/etc/environment` 解决cron问题
- 但手动SSH登录后如果不先 `source ~/.bashrc` 或显式 `export`，仍然读不到

## 正确做法

任何时候在VPS上手动跑报告，先用：
```bash
export HERMES_HOME=/root/hermes-pipeline
# 然后才 python3 xxx.py
```

## 验证方法

```bash
# 跑脚本时加一行测试
python3 -c "
import os
print('HERMES_HOME=', os.environ.get('HERMES_HOME'))
"
```
