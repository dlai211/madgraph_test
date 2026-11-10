#!/usr/bin/env python3
"""Compare the native and partonic ptj=5 integrals channel by channel."""
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PATH = HERE / "results/ptj5/total_integral.csv"

GQ = ["gu_zu", "gd_zd", "gux_zux", "gdx_zdx"]
QQ = ["uux_zg", "ddx_zg"]
NATIVE = {"gq": 22141.3, "qq": 17974.3, "total": 40116.0}
NATIVE_ERR = {"gq": 40.6657, "qq": 21.3671, "total": 45.938}


def main() -> None:
    values = {}
    with PATH.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            values[row["channel"]] = float(row["integral_pb"])
    part = {
        "gq": sum(values[ch] for ch in GQ),
        "qq": sum(values[ch] for ch in QQ),
        "total": values["total"],
    }
    rows = []
    for key in ("gq", "qq", "total"):
        rows.append({
            "channel": key,
            "native_pb": NATIVE[key],
            "native_error_pb": NATIVE_ERR[key],
            "partonic_pb": part[key],
            "ratio_native_over_partonic": NATIVE[key] / part[key],
        })
    out = HERE / "results/ptj5/comparison.csv"
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "native": NATIVE,
        "partonic": part,
        "ratio": {key: NATIVE[key] / part[key] for key in NATIVE},
        "note": "partonic values use the coarse 50-point grid",
    }
    (HERE / "results/ptj5/comparison.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    for row in rows:
        print(
            f"{row['channel']:5s} native={row['native_pb']:10.2f} "
            f"partonic={row['partonic_pb']:10.2f} "
            f"ratio={row['ratio_native_over_partonic']:.3f}"
        )
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
