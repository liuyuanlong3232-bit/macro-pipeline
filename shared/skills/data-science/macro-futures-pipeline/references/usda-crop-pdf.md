# USDA Crop Progress PDF 解析

> 来源: usda.library.cornell.edu
> 依赖: `pip install pdfplumber` (VPS已装)

## 数据流

```
Cornell图书馆页面 → 找到最新PDF下载链接 → 下载PDF → pdfplumber解析表格 → 提取优良率
```

## 实现代码

```python
import re, requests, io, pdfplumber
from bs4 import BeautifulSoup

def fetch_usda_crop_condition():
    proxies = None  # VPS直连
    
    # Step 1: 获取Cornell页面最新报告的PDF下载链接
    r = requests.get(
        "https://usda.library.cornell.edu/concern/publications/8336h188j",
        timeout=20, proxies=proxies,
        headers=HEADERS
    )
    soup = BeautifulSoup(r.text, "lxml")
    pdf_links = soup.select("a[href$='.pdf']")
    pdf_urls = []
    for a in pdf_links:
        href = a.get("href", "")
        if "crop-progress" in href.lower():
            pdf_urls.append(href if href.startswith("http") else "https://usda.library.cornell.edu" + href)
    if not pdf_urls:
        return None
    latest_url = pdf_urls[0]  # 第一篇是最近的

    # Step 2: 下载PDF
    pdf_resp = requests.get(latest_url, timeout=30)
    
    # Step 3: 解析PDF提取Corn/Soybeans优良率
    result = {"date": "", "corn": {}, "soybeans": {}}
    with pdfplumber.open(io.BytesIO(pdf_resp.content)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            # 提取报告日期（通常在首页顶部）
            date_match = re.search(r'(?:as of|week ending)\s+(\w+\.?\s+\d+,\s+\d{4})', text, re.I)
            if date_match:
                result["date"] = date_match.group(1)
            
            # 解析表格行
            lines = text.split("\n")
            for i, line in enumerate(lines):
                if "Corn" in line and "Condition" in lines[max(0,i-1) if i>0 else 0]:
                    # 找玉米行: 通常是"Corn  5  8  19  51  17"这样的格式
                    vals = re.findall(r'\d+', line)
                    if len(vals) >= 5:
                        result["corn"] = {
                            "very_poor": int(vals[-5]),
                            "poor": int(vals[-4]),
                            "fair": int(vals[-3]),
                            "good": int(vals[-2]),
                            "excellent": int(vals[-1]),
                            "good_excellent": int(vals[-2]) + int(vals[-1]),
                        }
                if "Soybean" in line and "Condition" in lines[max(0,i-1)]:
                    vals = re.findall(r'\d+', line)
                    if len(vals) >= 5:
                        result["soybeans"] = {
                            "very_poor": int(vals[-5]),
                            "poor": int(vals[-4]),
                            "fair": int(vals[-3]),
                            "good": int(vals[-2]),
                            "excellent": int(vals[-1]),
                            "good_excellent": int(vals[-2]) + int(vals[-1]),
                        }
    return result
```

## 返回格式

```python
{
    "date": "June 8, 2026",
    "corn": {"very_poor": 3, "poor": 8, "fair": 22, "good": 53, "excellent": 14, "good_excellent": 67},
    "soybeans": {"very_poor": 2, "poor": 7, "fair": 26, "good": 52, "excellent": 13, "good_excellent": 65},
    "source": "USDA NASS Crop Progress"
}
```

## 注意事项

- PDF结构每周可能微调，正则匹配需要柔性
- "good_excellent" = good + excellent 的合并值（行业惯例）
- VPS直连Cornell（美国）速度较好(<5s)
- 本地通过代理(10808)也稳定
- PDF文件名包含日期信息，按发布时间降序取第一个
- 频率：每周一发布（USDA Crop Progress报告）
