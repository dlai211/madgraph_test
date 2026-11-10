#!/usr/bin/env python3
"""Check Markdown table column counts after the math conversion."""
import sys
from pathlib import Path

path = Path(sys.argv[1])
lines = path.read_text(encoding="utf-8").splitlines()
blocks = []
cur = []
in_table = False
for n, line in enumerate(lines, 1):
    if line.strip().startswith("|"):
        cur.append((n, line))
        in_table = True
    else:
        if in_table and cur:
            blocks.append(cur)
            cur = []
        in_table = False
if cur:
    blocks.append(cur)
for block in blocks:
    counts = [line.count("|") for _, line in block]
    if len(set(counts)) > 1:
        print(f"BLOCK {block[0][0]}-{block[-1][0]} counts={counts[:12]}")
        for n, line in block[:5]:
            print(n, line)
print(f"table blocks: {len(blocks)}")
