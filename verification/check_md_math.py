#!/usr/bin/env python3
"""Report residual LaTeX outside fenced code blocks and inline code spans."""
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
lines = path.read_text(encoding="utf-8").splitlines()
in_fence = False
for n, line in enumerate(lines, 1):
    if line.strip().startswith("```"):
        in_fence = not in_fence
        continue
    if in_fence:
        continue
    # Remove inline code spans.
    stripped = re.sub(r"`[^`]*`", "", line)
    if "\\" in stripped or "\\(" in line or "\\[" in line:
        print(f"{n}: {line}")
print("done")
