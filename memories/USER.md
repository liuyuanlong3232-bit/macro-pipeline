Works on Chinese financial macro report pipeline (hermes-macro-data). Scripts: macro_weekly.py, energy_weekly.py, metals_weekly.py. Prefers thorough audit-first workflow with severity-ranked issues, then systematic fix-by-fix. Communication in Chinese.
§
User maintains a weekly financial report pipeline at ~/hermes-pipeline/ generating 5 reports: macro_weekly, energy_weekly, metals_weekly, agri_global, agri_china. Scripts use FRED API, Yahoo Finance, AKShare, Tushare, CFTC COT, EIA, and oddpool.com for data. Reports output to ~/hermes-macro-data/reports/. Data collection runs via macro_pipeline.py saving CSVs to ~/hermes-macro-data/csv/{date}/.
§
用户要求称呼：叫用户"老大"，自称"臭宝"。
§
用户偏好本地开发再上传的工作流：在自己电脑上写好脚本/工具，再传到服务器上运行，而不是让Hermes直接在服务器上从零构建。原因是服务器端网络请求容易超时/被阻断。用户的本地Hermes曾帮忙部署服务器端实例。