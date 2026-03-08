#!/usr/bin/env python3
"""Pre-commit hook: block .env, tokens.json, data/, *.sqlite, *.db from being committed."""
import subprocess
import sys

staged = subprocess.run(
    ["git", "diff", "--cached", "--name-only"],
    capture_output=True,
    text=True,
)
files = [f for f in staged.stdout.strip().split("\n") if f]
blocked = [".env", "tokens.json"]
for f in files:
    if f in blocked or f.startswith("data/") or f.endswith(".sqlite") or f.endswith(".db"):
        print(f"ERROR: Do not commit {f} (secrets or personal data)")
        sys.exit(1)
sys.exit(0)
