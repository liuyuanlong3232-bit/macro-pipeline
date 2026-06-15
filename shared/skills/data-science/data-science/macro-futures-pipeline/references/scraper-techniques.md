# 爬虫技术选型

## requests + BeautifulSoup
- **适用**: 无反爬的静态页面
- **示例**: USDA出口TXT, BDI(本地有代理)
- **失败时**: 换curl或Scrapling
- **代码**:
```python
import requests
from bs4 import BeautifulSoup
r = requests.get(url, timeout=20, headers={"User-Agent": "..."})
soup = BeautifulSoup(r.text, "lxml")
value = soup.find(attrs={"data-test": "xxx"}).get_text(strip=True)
```

## Tailwind CSS div表格解析（AOGR风格）
- **适用**: 非标准HTML表格，使用Tailwind CSS div布局的页面
- **示例**: Baker Hughes钻机数(aogr.com)
- **陷阱**: `get_text(strip=True)` 会合并相邻span的文本（如 `-1` + `562` → `-1562`）
- **正确做法**: DOM导航找到目标span的直接文本子节点
```python
# 错误：
text = cell.get_text(strip=True)  # 可能合并相邻span
# 正确：
target = cell.find("span", class_="tc-tot-curr")
if target:
    # 只取直接文本子节点，忽略子span
    value = "".join(t.strip() for t in target.find_all(text=True, recursive=False))
```

## curl subprocess + BeautifulSoup
- **适用**: Cloudflare拦截requests但放过curl
- **注意**: VPS上curl也可能被TLS阻断(exit code 92)，此时换方案
- **代码**:
```python
import subprocess
r = subprocess.run(["curl", "-s", url, "-H", "User-Agent: ...", "--max-time", "15"],
                   capture_output=True, text=True, timeout=20)
soup = BeautifulSoup(r.stdout, "lxml")
```

## PDF下载 + pdfplumber解析
- **适用**: USDA/Cornell托管PDF中提取表格
- **示例**: USDA作物优良率
- **依赖**: `pip install pdfplumber`
- **代码**:
```python
import pdfplumber, io, re
with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
    text = ""
    for page in pdf.pages:
        text += (page.extract_text() or "") + "\n"
    # 正则提取表格
    match = re.search(r'Corn\s+Condition.*?18 States\s+\.+\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', text, re.DOTALL)
```

## Scrapling StealthyFetcher
- **适用**: Cloudflare turnstile高强度反爬
- **示例**: OPEC MOMR月报下载
- **依赖**: `pip install scrapling`，需浏览器(约20s)
- **代码**:
```python
from scrapling.fetchers import StealthyFetcher
page = StealthyFetcher.fetch(url, headless=True, solve_cloudflare=True, block_webrtc=True, hide_canvas=True)
```

## 自动代理检测
VPS直连无代理，本地需v2rayN(:10808):
```python
def get_proxy():
    try:
        requests.get("http://127.0.0.1:10808", timeout=1)
        return {"http": "http://127.0.0.1:10808", "https": "http://127.0.0.1:10808"}
    except:
        return None
```
