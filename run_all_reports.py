#!/usr/bin/env python3
"""批量生成并发送所有报告"""
import sys
import subprocess
from pathlib import Path
from datetime import datetime

TODAY = datetime.now().strftime("%Y-%m-%d")
PIPELINE = Path("/root/hermes-pipeline")

# 报告类型列表
REPORT_TYPES = ["macro", "energy", "metals", "agri", "agri_cn"]

def run_report(report_type):
    """运行单个报告"""
    print(f"\n{'='*60}")
    print(f"📊 正在处理报告: {report_type}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            ["python3", "run_report.py", report_type],
            cwd=PIPELINE,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ {report_type} 报告生成并发送成功")
            return True
        else:
            print(f"❌ {report_type} 报告失败:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ 运行 {report_type} 时发生错误: {e}")
        return False

def main():
    """主函数"""
    print(f"🚀 开始批量生成报告 - {TODAY}")
    print(f"报告类型: {', '.join(REPORT_TYPES)}")
    
    success_count = 0
    failed_reports = []
    
    for report_type in REPORT_TYPES:
        if run_report(report_type):
            success_count += 1
        else:
            failed_reports.append(report_type)
    
    print(f"\n{'='*60}")
    print(f"📈 批量报告完成")
    print(f"成功: {success_count}/{len(REPORT_TYPES)}")
    if failed_reports:
        print(f"失败: {', '.join(failed_reports)}")
    print(f"{'='*60}")
    
    return len(failed_reports) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)