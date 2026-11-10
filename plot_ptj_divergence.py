#!/usr/bin/env python3
"""Plot the no-cut divergence: cross section versus the jet pT regulator."""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"


def read(path: Path):
    rows = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if not row["sigma_pb"] or float(row["ptj_gev"]) <= 0:
                continue
            rows.append((float(row["ptj_gev"]), float(row["sigma_pb"]), float(row["error_pb"])))
    return sorted(rows)


def main() -> None:
    native = read(RESULTS / "native_ptj_sequence.csv")
    partonic = read(RESULTS / "partonic_200gev_ptj_sequence.csv")

    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.4))

    ax = axes[0]
    x = [p for p, _, _ in native]
    y = [s for _, s, _ in native]
    e = [err for _, _, err in native]
    ax.errorbar(x, y, yerr=e, color="#2a78d6", lw=1.8, marker="o", ms=6,
                capsize=3, label="native p p → Z j")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.8, 25)
    ax.set_xlabel(r"jet $p_T$ regulator (GeV)")
    ax.set_ylabel(r"total cross section (pb)")
    ax.set_title("Native MadEvent: no eta cut")
    ax.grid(True, which="both", color="black", alpha=0.10, lw=0.6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.annotate("$p_T=0$: $1.5\\times10^6$ pb,\ngrid-dependent, not converged",
                xy=(1.0, 95661), xytext=(1.5, 12000), fontsize=8, color="#555555",
                arrowprops=dict(arrowstyle="->", color="#555555", lw=0.8))
    for xi, yi in zip(x, y):
        ax.annotate(f"{yi/1000:.0f}k" if yi >= 1000 else f"{yi:.0f}",
                    xy=(xi, yi), xytext=(4, 4), textcoords="offset points",
                    fontsize=7, color="#333333")

    ax = axes[1]
    x = [p for p, _, _ in partonic]
    y = [s for _, s, _ in partonic]
    e = [err for _, _, err in partonic]
    ax.errorbar(x, y, yerr=e, color="#eb6834", lw=1.8, marker="o", ms=6,
                capsize=3, label=r"partonic $g q \to Z q$ etc.")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.8, 25)
    ax.set_ylim(350, 800)
    ax.set_xlabel(r"jet $p_T$ regulator (GeV)")
    ax.set_ylabel(r"partonic $\sigma$ at $\sqrt{\hat{s}}=200$ GeV (pb)")
    ax.set_title("Partonic MadEvent: no eta cut")
    ax.grid(True, which="both", color="black", alpha=0.10, lw=0.6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.annotate("$p_T=0$: grid fails,\nno finite result", xy=(1.0, 675.7),
                xytext=(1.5, 430), fontsize=8, color="#555555",
                arrowprops=dict(arrowstyle="->", color="#555555", lw=0.8))
    for xi, yi in zip(x, y):
        ax.annotate(f"{yi:.0f}", xy=(xi, yi), xytext=(4, 4),
                    textcoords="offset points", fontsize=7, color="#333333")

    fig.suptitle("The cut-free LO $Z+j$ cross section is divergent", fontsize=10)
    fig.tight_layout()
    for suffix in ("png", "pdf"):
        fig.savefig(RESULTS / f"nocut_divergence.{suffix}", dpi=180)
    plt.close(fig)
    print("wrote nocut_divergence.png/pdf")


if __name__ == "__main__":
    main()
