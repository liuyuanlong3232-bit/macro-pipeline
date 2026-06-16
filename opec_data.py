"""欧佩克数据采集 — 两种方案
方案1(主): EIA API (STEO) → 快、可靠、已有API KEY
方案2(备): Scrapling StealthyFetcher爬OPEC MOMR → 过Cloudflare, 慢但数据新
"""
import os, sys, json
from datetime import datetime
from pathlib import Path
import requests

# 公共工具函数
sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared.utils import load_env

load_env()
EIA_KEY = os.getenv("EIA_API_KEY")

def fetch_eia_opec():
    """方案1: EIA API获取OPEC产量数据（主用）"""
    if not EIA_KEY:
        return None
    
    try:
        url = (f"https://api.eia.gov/v2/steo/data/"
               f"?api_key={EIA_KEY}"
               f"&frequency=monthly"
               f"&data[0]=value"
               f"&facets[seriesId][]=PAPR_OPEC"
               f"&sort[0][column]=period&sort[0][direction]=desc"
               f"&length=3")
        r = requests.get(url, timeout=15)
        data = r.json()
        if data.get("response") and data["response"].get("data"):
            items = data["response"]["data"]
            return {
                "source": "EIA STEO预测",
                "series": "OPEC总石油供应",
                "unit": "百万桶/日",
                "latest": round(float(items[0]["value"]), 2),
                "prev": round(float(items[1]["value"]), 2) if len(items) > 1 else None,
                "period": items[0]["period"],
                "change": round(float(items[0]["value"]) - float(items[1]["value"]), 2) if len(items) > 1 else None,
            }
    except Exception as e:
        print(f"EIA OPEC获取失败: {e}")
    return None

def fetch_opec_momr():
    """方案2: Scrapling爬OPEC月报（备用）"""
    try:
        from scrapling.fetchers import StealthyFetcher
        page = StealthyFetcher.fetch(
            "https://momr.opec.org/pdf-download/",
            headless=True,
            solve_cloudflare=True,
            block_webrtc=True,
        )
        # 找数据表(如果有)
        tables = page.css("table")
        if tables:
            rows = tables[0].css("tr")
            data = []
            for r in rows[:5]:
                cells = r.css("td::text").getall()
                if cells:
                    data.append(cells)
            return {"source": "OPEC MOMR (Scrapling)", "data": data}
        return {"source": "OPEC MOMR", "note": "页面无表格数据，建议下载PDF"}
    except Exception as e:
        return {"source": "OPEC MOMR", "error": str(e)}

if __name__ == "__main__":
    print("=== 方案1: EIA API ===")
    eia = fetch_eia_opec()
    if eia:
        print(f"  {eia['series']}: {eia['latest']} {eia['unit']} ({eia['period']})")
        print(f"  月环比: {eia['change']:+.2f}")
    
    print("\n=== 方案2: Scrapling OPEC MOMR ===")
    omr = fetch_opec_momr()
    print(f"  {omr}")
