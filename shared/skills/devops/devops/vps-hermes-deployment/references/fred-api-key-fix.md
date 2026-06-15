# FRED API Key .env Fix Pattern

## Symptom
FRED pipeline returns 400 error for ALL series. Macro_pipeline logs show:
```
api_key=%2A%2A%2A  (three asterisks = ***)
```
Error: `400 Bad Request - api_key is not a 32 character alpha-numeric lower-case string`

## Root Cause
Writing FRED_API_KEY via bash `echo` causes truncation. The key `40fa26cf844e61f5be94820c5ded91b2` gets stored as `***` (3 chars) because:
- bash `echo` interacts with shell quoting
- Environment variable redaction interferes

## Fix (Python, not bash)

```python
key = "40fa26cf844e61f5be94820c5ded91b2"

# Read current .env
with open("/root/hermes-pipeline/.env", "r") as f:
    lines = f.readlines()

# Remove any existing FRED_API_KEY lines
lines = [l for l in lines if "FRED_API_KEY" not in l]

# Append correct key
lines.append("FRED_API_KEY=" + key + "\n")

# Write back
with open("/root/hermes-pipeline/.env", "w") as f:
    f.writelines(lines)
```

## Verification
```bash
cd /root/hermes-pipeline && python3 -c "
import sys; sys.path.insert(0, '.')
from macro_pipeline import FRED_API_KEY
print('长度:', len(FRED_API_KEY))
print('正确:', len(FRED_API_KEY) == 32)
"
```

Expected: `长度: 32, 正确: True`

## Pipeline Test
```bash
cd /root/hermes-pipeline && python3 macro_pipeline.py --source fred
```
Expected: `✅ FRED 377 行数据, 29/29 系列成功`
