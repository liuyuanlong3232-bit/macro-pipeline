import requests
import json
# 直接使用 token
token = "ghp_Pn...r = requests.post(
    "https://api.github.com/user/repos",
    headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"},
    json={"name": "macro-pipeline", "description": "macro pipeline", "private": False}
)
print(f"Status: {r.status_code}")
if r.status_code == 201:
    d = r.json()
    print(f"OK: {d['html_url']}")
else:
    try:
        print(f"Error: {r.json().get('message','?')}")
    except:
        print(r.text[:200])
