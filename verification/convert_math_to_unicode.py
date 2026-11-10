#!/usr/bin/env python3
"""Convert the LaTeX math in a Markdown file to Unicode/code formatting.

The local Markdown preview does not render MathJax/KaTeX, so ``\\(\\eta\\)``
and ``\\[ ... \\]`` appear as raw text.  This script turns inline math into
backtick code spans and display math into fenced ``text`` blocks, using
Unicode for Greek letters and symbols.  Existing fenced code blocks are left
alone.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

GREEK = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε",
    "zeta": "ζ", "eta": "η", "theta": "θ", "iota": "ι", "kappa": "κ",
    "lambda": "λ", "mu": "μ", "nu": "ν", "xi": "ξ", "pi": "π", "rho": "ρ",
    "sigma": "σ", "tau": "τ", "upsilon": "υ", "phi": "φ", "chi": "χ",
    "psi": "ψ", "omega": "ω",
    "Gamma": "Γ", "Delta": "Δ", "Theta": "Θ", "Lambda": "Λ", "Xi": "Ξ",
    "Pi": "Π", "Sigma": "Σ", "Upsilon": "Υ", "Phi": "Φ", "Psi": "Ψ",
    "Omega": "Ω",
}

SYMBOLS = {
    "pm": "±", "mp": "∓", "times": "×", "cdot": "·", "to": "→",
    "rightarrow": "→", "leftarrow": "←", "Rightarrow": "⇒",
    "leftrightarrow": "↔", "approx": "≈", "sim": "∼", "simeq": "≃",
    "equiv": "≡", "le": "≤", "leq": "≤", "ge": "≥", "geq": "≥",
    "neq": "≠", "ne": "≠", "in": "∈", "notin": "∉", "subset": "⊂",
    "supset": "⊃", "sum": "Σ", "prod": "Π", "int": "∫", "oint": "∮",
    "infty": "∞", "partial": "∂", "nabla": "∇", "ell": "ℓ",
    "ldots": "…", "dots": "…", "cdots": "⋯", "langle": "⟨",
    "rangle": "⟩", "mid": "∣", "vert": "∣", "Vert": "‖",
    "ln": "ln ", "log": "log ", "exp": "exp ", "sin": "sin ", "cos": "cos ",
    "tan": "tan ", "det": "det ", "max": "max ", "min": "min ", "lim": "lim ",
    "quad": "  ", "qquad": "    ", " ": " ", ",": " ", ";": " ",
    ":": " ", "!": "", "%": "%", "&": "&", "#": "#", "_": "_",
    "{": "{", "}": "}", "|": "∣", "\\": "\n",
}

BRACE_COMMANDS = {
    "sqrt", "frac", "hat", "bar", "overline", "tilde", "vec", "mathrm",
    "text", "mathbf", "mathit", "mathcal", "operatorname", "textrm",
    "textbf", "boxed",
}


def read_group(s: str, i: int) -> tuple[str, int]:
    """Read a balanced brace group starting at s[i] == '{'."""
    assert s[i] == "{"
    depth = 1
    j = i + 1
    chars = []
    while j < len(s):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return "".join(chars), j + 1
        chars.append(s[j])
        j += 1
    return "".join(chars), j


def read_token(s: str, i: int) -> tuple[str, int]:
    """Read the next token after a command: a group, a command, or a char."""
    while i < len(s) and s[i] in " \t":
        i += 1
    if i >= len(s):
        return "", i
    if s[i] == "{":
        return read_group(s, i)
    if s[i] == "\\":
        j = i + 1
        if j < len(s) and s[j].isalpha():
            while j < len(s) and s[j].isalpha():
                j += 1
            return s[i:j], j
        return s[i:j + 1], j + 1
    return s[i], i + 1


def is_simple(text: str) -> bool:
    """True when a sqrt group can be written without extra parentheses."""
    if not text:
        return False
    return re.search(r"[\s+\-*/=(),^_]", text) is None


def is_atomic(text: str) -> bool:
    """True for a fraction/subscript token that needs no parentheses."""
    if not text:
        return False
    return re.search(r"[\s+\-*/=(),∣]", text) is None


def convert(s: str) -> str:
    out = []
    i = 0
    while i < len(s):
        c = s[i]
        if c == "\\":
            j = i + 1
            if j >= len(s):
                i += 1
                continue
            if s[j].isalpha():
                k = j
                while k < len(s) and s[k].isalpha():
                    k += 1
                cmd = s[j:k]
                i = k
            else:
                cmd = s[j]
                i = j + 1

            if cmd in GREEK:
                out.append(GREEK[cmd])
                continue
            if cmd in SYMBOLS:
                out.append(SYMBOLS[cmd])
                continue
            if cmd in ("left", "right", "big", "Big", "bigl", "bigr",
                       "Bigl", "Bigr", "displaystyle", "textstyle"):
                continue
            if cmd in BRACE_COMMANDS:
                if cmd == "sqrt":
                    arg, i = read_token(s, i)
                    arg = convert(arg)
                    out.append("√" + arg if is_simple(arg) else "√(" + arg + ")")
                elif cmd == "frac":
                    a, i = read_token(s, i)
                    b, i = read_token(s, i)
                    a = convert(a)
                    b = convert(b)
                    if is_atomic(a) and is_atomic(b):
                        out.append(f"{a}/{b}")
                    else:
                        out.append(f"({a})/({b})")
                    if i < len(s) and s[i] not in ")],.;:∣":
                        out.append(" ")
                elif cmd in ("hat", "bar", "overline", "tilde", "vec"):
                    arg, i = read_token(s, i)
                    arg = convert(arg)
                    if cmd == "hat" and arg == "s":
                        out.append("ŝ")
                        continue
                    mark = {"hat": "̂", "bar": "̄",
                            "overline": "̄", "tilde": "̃",
                            "vec": "⃗"}[cmd]
                    out.append(arg + mark)
                else:
                    arg, i = read_token(s, i)
                    out.append(convert(arg))
                continue
            if cmd == "rm":
                while i < len(s) and s[i] in " \t":
                    i += 1
                continue
            # Unknown command: drop the backslash, keep the name.
            out.append(cmd)
            continue

        if c in "_^":
            i += 1
            arg, i = read_token(s, i)
            arg = convert(arg)
            base = arg[1:] if arg[:1] in "+-" else arg
            out.append(c + (arg if is_atomic(base) else "(" + arg + ")"))
            continue
        if c == "{":
            arg, i = read_group(s, i)
            out.append(convert(arg))
            continue
        if c == "|":
            out.append("∣")
            i += 1
            continue
        out.append(c)
        i += 1

    res = "".join(out)
    res = res.replace("{,}", ",")
    res = res.replace("→ ", "→")
    res = re.sub(r"[ \t]+", " ", res).strip()
    return res


def convert_markdown(text: str) -> str:
    lines = text.splitlines(keepends=True)
    out = []
    in_fence = False
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            out.append(line)
            i += 1
            continue
        if in_fence:
            out.append(line)
            i += 1
            continue

        # Display math on its own line: \[ ... \]
        if stripped == "\\[":
            block = []
            i += 1
            while i < len(lines) and lines[i].strip() != "\\]":
                block.append(lines[i].rstrip("\n"))
                i += 1
            if i < len(lines):
                i += 1
            converted = convert("\n".join(block))
            out.append("```text\n" + converted + "\n```\n")
            continue

        # One-line display math.
        line = re.sub(
            r"\\\[(.*?)\\\]",
            lambda m: "`" + convert(m.group(1)) + "`",
            line,
            flags=re.DOTALL,
        )
        # Inline math.
        line = re.sub(
            r"\\\((.*?)\\\)",
            lambda m: "`" + convert(m.group(1)) + "`",
            line,
            flags=re.DOTALL,
        )
        out.append(line)
        i += 1
    return "".join(out)


def main() -> None:
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    converted = convert_markdown(text)
    out = path.with_name(path.stem + "_unicode.md")
    out.write_text(converted, encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
