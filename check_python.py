#!/usr/bin/env python3
"""Find which python has pandas"""
import sys
print(f"Python: {sys.executable}")
print(f"Version: {sys.version}")
try:
    import pandas as pd
    print(f"Pandas: {pd.__file__}")
except ImportError:
    print("Pandas: NOT FOUND")
