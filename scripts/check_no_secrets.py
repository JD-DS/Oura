#!/usr/bin/env python3
"""Pre-commit hook: block .env, tokens.json, data/, *.sqlite, *.db from being committed."""
import subprocess
import sys
from pathlib import Path

try:
    staged = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        check=True,
    )
except subprocess.CalledProcessError as e:
    print("ERROR: Failed to list staged files via git:", file=sys.stderr)
    if e.stderr:
        print(e.stderr, file=sys.stderr)
    sys.exit(1)

files = [f for f in staged.stdout.strip().split("\n") if f]
blocked_names = {".env", "tokens.json"}
for f in files:
    name = Path(f).name
    parts = Path(f).parts
    if name in blocked_names or "data" in parts or f.endswith(".sqlite") or f.endswith(".db"):
        print(f"ERROR: Do not commit {f} (secrets or personal data)")
        sys.exit(1)
sys.exit(0)
