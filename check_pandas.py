#!/usr/bin/env python3
import sys
# Check if pandas is in the system site-packages
sys.path.insert(0, r"C:\Users\Administrator\AppData\Local\Programs\Python\Python311\Lib\site-packages")
try:
    import pandas as pd
    print(f"Pandas found: {pd.__file__}")
    print(f"Pandas version: {pd.__version__}")
except ImportError:
    print("Pandas NOT found in system site-packages")
