#!/usr/bin/env python3
import sys
print("Before:", [p for p in sys.path if 'site-packages' in p])
# Force add
sys.path.insert(0, r"C:\Users\Administrator\AppData\Local\Programs\Python\Python311\Lib\site-packages")
print("After:", [p for p in sys.path if 'site-packages' in p])
import pandas as pd
print(f"OK: pandas {pd.__version__}")
