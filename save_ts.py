#!/usr/bin/env python3
import os
p = r"C:\Users\Administrator\AppData\Local\hermes\.env"
token = "ca8f009904f51b41dc6be222b40de55441823ec37f6ad7a6e87d0e0a"
with open(p, "a") as f:
    f.write("\n# Tushare (中国金融数据)\n")
    f.write(f"TUSHARE_TOKEN={token}\n")
print("ok")
