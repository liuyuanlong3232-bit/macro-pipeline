#!/usr/bin/env python3
"""Save GitHub token properly"""
p = r"C:\Users\Administrator\AppData\Local\hermes\.env"
with open(p, "r") as f:
    lines = f.readlines()
clean = [l for l in lines if "GITHUB_TOKEN" not in l]
clean.append('GITHUB_TOKEN=ghp_Pn...YU5K\n')
with open(p, "w") as f:
    f.writelines(clean)
print("Token saved")
