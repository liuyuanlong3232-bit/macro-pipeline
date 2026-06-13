#!/usr/bin/env python3
import sys
sys.path.insert(0, r"C:\Users\Administrator\AppData\Local\hermes\hermes-agent\venv\Lib\site-packages")
try:
    import pandas as pd
    print(f"OK: pandas {pd.__version__}")
except ImportError as e:
    print(f"FAIL: {e}")
