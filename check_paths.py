#!/usr/bin/env python3
import subprocess, sys
result = subprocess.run(["which", "python"], capture_output=True, text=True)
print("which python:", result.stdout.strip())
result2 = subprocess.run(["python", "--version"], capture_output=True, text=True)
print("version:", result2.stdout.strip() + result2.stderr.strip())
result3 = subprocess.run(["python", "-c", "import sys; print(sys.path)"], capture_output=True, text=True)
print("sys.path:", result3.stdout.strip())
