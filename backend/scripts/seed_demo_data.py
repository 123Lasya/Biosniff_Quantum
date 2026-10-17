import os
import sys

# Delegate to scripts/seed_demo_data.py
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
PARENT_ROOT = os.path.dirname(PROJECT_ROOT)

target_script = os.path.join(PARENT_ROOT, "scripts", "seed_demo_data.py")
if not os.path.exists(target_script):
    target_script = os.path.join(PROJECT_ROOT, "scripts", "seed_demo_data.py")

if os.path.exists(target_script):
    with open(target_script, "r") as f:
        code = compile(f.read(), target_script, "exec")
        exec(code, globals())
else:
    raise FileNotFoundError(f"Cannot locate seed_demo_data.py at {target_script}")
