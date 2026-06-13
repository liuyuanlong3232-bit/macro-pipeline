#!/usr/bin/env python3
"""
data_scrapers.py — 四个数据爬虫
Baker Hughes / NOAA / USDA / BDI
"""
import re, io, json
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
import pdfplumber

# ── 代理配置（自动检测：VPS直连，本地走代理）──
def get_proxy():
    """VPS上无代理，本地有v2rayN"""
    try:
        r = requests.get("http://127.0.0.1:10808", timeout=1)
        return {"http": "http://127.0.0.1:10808", "https": "http://127.0.0.1:10808"}
    except:
        return None
PROXY = None  # 延迟到调用时设置
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# ═══════════════════════════════════════════════════════════
# 1. Baker Hughes 钻机数
# ═══════════════════════════════════════════════════════════
def fetch_baker_hughes(use_proxy=True):
    """
    从 Baker Hughes 首页爬取北美钻机总数。
    VPS上直接用curl（Python requests被Cloudflare拦截，curl能过）
    """
    try:
        import subprocess
        cmd = [
            "curl", "-s", "https://rigcount.bakerhughes.com/",
            "-H", "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "--max-time", "15"
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        if r.returncode != 0 or not r.stdout:
            return None
        soup = BeautifulSoup(r.stdout, "lxml")
        table = soup.find("table")
        if not table:
            return None
        result = {"source": "Baker Hughes (curl)"}
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) >= 6:
                area = cells[0].get_text(strip=True)
                date_raw = cells[1].get_text(strip=True)
                count = cells[2].get_text(strip=True).replace(",", "")
                chg = cells[3].get_text(strip=True)
                if "U.S." in area or area.upper() == "US":
                    result["us_count"] = int(count)
                    result["us_change"] = chg
                elif "Canada" in area:
                    result["canada_count"] = int(count)
                    result["canada_change"] = chg
                # 解析日期
                m = re.match(r'(\d+)\s*(\w+)(\d{4})', date_raw)
                if m:
                    day, mon_str, year = m.groups()
                    month_map = {"January":1,"February":2,"March":3,"April":4,"May":5,"June":6,
                                 "July":7,"August":8,"September":9,"October":10,"November":11,"December":12}
                    month = month_map.get(mon_str, 1)
                    result["date"] = f"{year}-{month:02d}-{int(day):02d}"
        if "us_count" in result and "canada_count" in result:
            result["na_total"] = result["us_count"] + result["canada_count"]
        return result
    except Exception as e:
        print(f"[Baker Hughes] Error: {e}")
        return None


# ═══════════════════════════════════════════════════════════
# 1b. Open-Meteo 农业区降水（替代NOAA，免费无Key）
# ═══════════════════════════════════════════════════════════
AGRI_REGIONS = [
    ("玉米带(IL)", 40.0, -89.0),
    ("小麦带(KS)", 38.0, -98.0),
    ("棉花带(MS)", 33.0, -90.0),
    ("大平原(NE)", 41.5, -100.0),
    ("三角洲(AR)", 34.5, -91.0),
]

def fetch_openmeteo_precip():
    """Open-Meteo API获取美国农业区7天降水/温度（免费，无需Key）"""
    try:
        total_mm = 0
        details = []
        for name, lat, lon in AGRI_REGIONS:
            r = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat, "longitude": lon,
                    "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min",
                    "timezone": "America/Chicago",
                    "forecast_days": 7,
                },
                timeout=10,
            )
            if r.status_code != 200:
                continue
            d = r.json().get("daily", {})
            psum = d.get("precipitation_sum", [])
            if psum and any(p for p in psum):
                total = sum(float(p) for p in psum if p)
                total_mm += total
                tmin = d["temperature_2m_min"][0]
                tmax = d["temperature_2m_max"][0]
                details.append(f"{name} {total:.0f}mm")
        if details:
            return {
                "summary": ", ".join(details),
                "total_avg_mm": round(total_mm / max(len(details), 1), 1),
                "source": "Open-Meteo",
            }
    except Exception as e:
        print(f"[Open-Meteo] Error: {e}")
    return None

# ═══════════════════════════════════════════════════════════
# 2. NOAA 美国产区降水
# ═══════════════════════════════════════════════════════════
def fetch_noaa_precip(use_proxy=True):
    """
    从 NOAA CPC 爬取美国农业产区降水概览。
    URL: https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/regional_monitoring/
    注意： NOAA 网站近期结构调整，原定 URL 返回 404，
    尝试替代来源 drought.gov / CPC 土壤湿度监测。
    返回 dict 或 None。
    """
    proxies = get_proxy() if use_proxy else None
    # 尝试土壤湿度监测页（与降水相关）
    urls = [
        "https://www.cpc.ncep.noaa.gov/products/Soilmst_Monitoring/US/Soilmst/Soilmst.shtml",
        "https://www.drought.gov/",
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=20, proxies=proxies, headers=UA)
            if r.status_code == 200:
                text = r.text
                # 尝试提取降水相关摘要
                soup = BeautifulSoup(text, "lxml")
                body_text = soup.get_text()
                # 找降水关键词
                precip_info = ""
                for line in body_text.split("\n"):
                    if any(kw in line.lower() for kw in ["precip", "降水", "rainfall", "moisture"]):
                        if len(line.strip()) > 10:
                            precip_info += line.strip()[:200] + "\n"
                if precip_info:
                    return {
                        "source": url,
                        "precip_summary": precip_info[:500],
                        "note": "数据来源: " + url
                    }
        except Exception:
            continue
    # 所有尝试失败
    return None


# ═══════════════════════════════════════════════════════════
# 3. USDA 作物优良率
# ═══════════════════════════════════════════════════════════
def fetch_usda_crop_condition(use_proxy=True):
    """
    从 USDA NASS Crop Progress PDF 爬取最新玉米、大豆优良率。
    PDF 托管在 esmis.nal.usda.gov，通过 Cornell 图书馆页面获取下载链接。
    返回 dict:
      {
        "date": "2026-06-07",
        "corn": {"very_poor": 1, "poor": 5, "fair": 27, "good": 55, "excellent": 12, "good_excellent": 67},
        "soybeans": {"very_poor": ..., "good_excellent": ...},
        "source": "USDA NASS Crop Progress"
      }
    失败返回 None
    """
    proxies = get_proxy() if use_proxy else None
    try:
        # Step 1: 获取 Cornell 图书馆页面的最新报告 ID
        r = requests.get(
            "https://usda.library.cornell.edu/concern/publications/8336h188j",
            timeout=20, proxies=proxies, headers=UA
        )
        if r.status_code != 200:
            return None

        soup = BeautifulSoup(r.text, "lxml")
        pdf_link = None
        for a in soup.find_all("a"):
            href = a.get("href", "")
            if "prog" in href and href.endswith(".pdf"):
                pdf_link = href
                break
        if not pdf_link:
            return None

        # Step 2: 下载PDF
        pdf_url = "https://usda.library.cornell.edu" + pdf_link
        r2 = requests.get(pdf_url, timeout=30, proxies=proxies, headers=UA)
        if r2.status_code != 200:
            return None

        # Step 3: 解析PDF提取作物条件数据
        result = {"source": "USDA NASS Crop Progress"}
        with pdfplumber.open(io.BytesIO(r2.content)) as pdf:
            full_text = ""
            for page in pdf.pages:
                full_text += (page.extract_text() or "") + "\n"

            # 提取报告日期 - 从封面页
            date_match = re.search(r'Released\s+(\w+\s+\d+,\s+\d{4})', full_text)
            if date_match:
                try:
                    dt = datetime.strptime(date_match.group(1), "%B %d, %Y")
                    result["date"] = dt.strftime("%Y-%m-%d")
                except:
                    result["date"] = date_match.group(1)

            # 解析 Corn Condition 表
            # 查找 "Corn Condition" 段落后面的 18 States 汇总行
            corn_pattern = r'Corn\s+Condition.*?18 States\s+\.+\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)'
            corn_m = re.search(corn_pattern, full_text, re.DOTALL)
            if corn_m:
                result["corn"] = {
                    "very_poor": int(corn_m.group(1)),
                    "poor": int(corn_m.group(2)),
                    "fair": int(corn_m.group(3)),
                    "good": int(corn_m.group(4)),
                    "excellent": int(corn_m.group(5)),
                    "good_excellent": int(corn_m.group(4)) + int(corn_m.group(5))
                }

            # 解析 Soybean Condition 表
            soypattern = r'Soybean\s+Condition.*?18 States\s+\.+\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)'
            soy_m = re.search(soypattern, full_text, re.DOTALL)
            if soy_m:
                result["soybeans"] = {
                    "very_poor": int(soy_m.group(1)),
                    "poor": int(soy_m.group(2)),
                    "fair": int(soy_m.group(3)),
                    "good": int(soy_m.group(4)),
                    "excellent": int(soy_m.group(5)),
                    "good_excellent": int(soy_m.group(4)) + int(soy_m.group(5))
                }

        if "corn" in result or "soybeans" in result:
            return result
        return None

    except Exception as e:
        print(f"[USDA] Error: {e}")
        return None


# ═══════════════════════════════════════════════════════════
# 4. BDI 波罗的海干散货运价指数
# ═══════════════════════════════════════════════════════════
def fetch_bdi(use_proxy=True):
    """
    从 Investing.com 爬取波罗的海干散货运价指数 (BDI / BADI)。
    URL: https://www.investing.com/indices/baltic-dry
    返回 dict:
      {
        "price": 2818.00,
        "change": -98.00,
        "change_pct": -3.36,
        "prev_close": 1602,
        "open": 2818,
        "date": "2026-06-09",
        "source": "Investing.com (BADI)",
        "ticker": "BADI"
      }
    失败返回 None
    """
    proxies = get_proxy() if use_proxy else None
    try:
        r = requests.get("https://www.investing.com/indices/baltic-dry",
                         timeout=25, proxies=proxies, headers={
                             **UA,
                             "Accept-Language": "en-US,en;q=0.5",
                         })
        if r.status_code != 200:
            return None

        soup = BeautifulSoup(r.text, "lxml")
        result = {"source": "Investing.com (BADI)", "ticker": "BADI"}

        # 从 data-test 属性提取
        price_el = soup.find(attrs={"data-test": "instrument-price-last"})
        if price_el:
            try:
                result["price"] = float(price_el.get_text(strip=True).replace(",", ""))
            except:
                pass

        chg_el = soup.find(attrs={"data-test": "instrument-price-change"})
        if chg_el:
            try:
                result["change"] = float(chg_el.get_text(strip=True).replace(",", ""))
            except:
                pass

        pct_el = soup.find(attrs={"data-test": "instrument-price-change-percent"})
        if pct_el:
            try:
                pct_str = pct_el.get_text(strip=True).replace("(", "").replace(")", "").replace("%", "")
                result["change_pct"] = float(pct_str)
            except:
                pass

        # prevClose and open
        for attr in ["prevClose", "open"]:
            el = soup.find(attrs={"data-test": attr})
            if el:
                try:
                    result[attr] = float(el.get_text(strip=True).replace(",", ""))
                except:
                    pass

        # 日期从 trading-state-label 或 time label
        date_el = soup.find(attrs={"data-test": "trading-time-label"})
        if date_el:
            date_str = date_el.get_text(strip=True)
            # Format: "09/06" -> interpret as DD/MM
            m = re.match(r'(\d+)/(\d+)', date_str)
            if m:
                day, month = m.groups()
                year = datetime.now().year
                result["date"] = f"{year}-{int(month):02d}-{int(day):02d}"

        if "price" in result:
            return result
        return None

    except Exception as e:
        print(f"[BDI] Error: {e}")
        return None


# ═══════════════════════════════════════════════════════════
# 5. USDA Export Grain Inspections — 美湾出口数据
# ═══════════════════════════════════════════════════════════
def fetch_usda_export_inspections(use_proxy=True):
    """
    从 USDA AMS 获取周度出口谷物检验报告 (wa_gr101.txt)。
    返回 dict:
      {
        "date": "2026-06-04",
        "week_ending": "Jun 04, 2026",
        "gulf_total_mt": 1473562,
        "gulf_corn_mt": 1126896,
        "gulf_soybeans_mt": 214484,
        "gulf_wheat_mt": 132182,
        "us_total_mt": 2651639,
        "source": "USDA FGIS Export Grain Inspections"
      }
    失败返回 None
    """
    try:
        r = requests.get(
            "https://www.ams.usda.gov/mnreports/wa_gr101.txt",
            timeout=20,
            headers=UA,
        )
        if r.status_code != 200:
            return None

        text = r.text

        # 提取报告日期: look for "WEEK ENDING" line
        date_match = re.search(r'WEEK ENDING\s+(\w+\s+\d+,\s+\d{4})', text)
        week_ending = date_match.group(1) if date_match else ""

        # 提取谷物总量行 (first summary table): "Total" row
        # Pattern: Total       2,640,163   2,839,235
        total_match = re.search(r'Total\s+([\d,]+)\s+([\d,]+)', text)
        us_total = int(total_match.group(1).replace(",", "")) if total_match else 0

        # 提取 BY REGION AND PORT AREA 表格中 GULF 区域 subtotal
        # 寻找 "GULF" 区域 + SUBTOTAL 行
        # Format: GULF      ... SUBTOTAL    132,182  1,025,897  100,999       0   214,484        0  1,473,562
        # The GULF subtotal row has columns: WHEAT, CORN YELLOW, CORN WHITE, SORGHUM, SOYBEANS, CANOLA, TOTALS
        gulf_pattern = r'GULF\s+.*?SUBTOTAL\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)'
        gulf_m = re.search(gulf_pattern, text, re.DOTALL)
        if gulf_m:
            gulf_wheat = int(gulf_m.group(1).replace(",", ""))
            gulf_corn_yellow = int(gulf_m.group(2).replace(",", ""))
            gulf_corn_white = int(gulf_m.group(3).replace(",", ""))
            gulf_corn = gulf_corn_yellow + gulf_corn_white
            gulf_soybeans = int(gulf_m.group(5).replace(",", ""))
            gulf_total = int(gulf_m.group(7).replace(",", ""))
        else:
            # fallback: sum individual port areas under GULF
            gulf_total = 0
            gulf_corn = 0
            gulf_soybeans = 0
            gulf_wheat = 0
            # Try to find GULF section and parse sub-port rows
            gulf_section = re.search(
                r'GULF\s+(.+?)SUBTOTAL',
                text, re.DOTALL
            )
            if gulf_section:
                gulf_text = gulf_section.group(1)
                # Each line: port_name  numbers...
                for line in gulf_text.split("\n"):
                    line = line.strip()
                    if not line or line.startswith("GULF"):
                        continue
                    nums = re.findall(r'[\d,]+', line)
                    if len(nums) >= 7:
                        gulf_wheat += int(nums[0].replace(",", ""))
                        gulf_corn += int(nums[1].replace(",", "")) + int(nums[2].replace(",", ""))
                        gulf_soybeans += int(nums[4].replace(",", ""))
                        gulf_total += int(nums[6].replace(",", ""))

        result = {
            "date": week_ending,
            "gulf_total_mt": gulf_total,
            "gulf_corn_mt": gulf_corn,
            "gulf_soybeans_mt": gulf_soybeans,
            "gulf_wheat_mt": gulf_wheat,
            "us_total_mt": us_total,
            "source": "USDA FGIS Export Grain Inspections",
        }
        return result

    except Exception as e:
        print(f"[USDA Export Inspections] Error: {e}")
        return None


# ═══════════════════════════════════════════════════════════
# 测试入口
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=== Baker Hughes ===")
    bh = fetch_baker_hughes()
    print(bh)

    print("\n=== NOAA ===")
    noaa = fetch_noaa_precip()
    if noaa:
        print(f"Found: {noaa['precip_summary'][:200]}")
    else:
        print("NOAA: 待手动查")

    print("\n=== USDA ===")
    usda = fetch_usda_crop_condition()
    if usda:
        print(f"Date: {usda.get('date')}")
        print(f"Corn: {usda.get('corn')}")
        print(f"Soybeans: {usda.get('soybeans')}")
    else:
        print("USDA: 待手动查")

    print("\n=== BDI ===")
    bdi = fetch_bdi()
    print(bdi)
