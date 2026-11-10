#!/usr/bin/env python3
"""Plot the divergent endpoints: native and partonic cross section at pT=0."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"


def main() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 4.4))

    # Native: ptj = 20, 10, 5, 2, 1, 0 (0 is grid-dependent)
    ax = axes[0]
    x = [5, 4, 3, 2, 1, 0]
    y = [11913, 23692, 40116, 68856, 95661, 1484700]
    ax.plot(x[:5], y[:5], color="#2a78d6", marker="o", ms=6, lw=1.8,
            label="converged")
    ax.plot(x[4:], y[4:], color="#2a78d6", ls="--", lw=1.2)
    ax.plot([x[5]], [y[5]], marker="o", ms=8, mfc="white", mec="#eb6834",
            mew=1.8, ls="none", label="pT=0, grid-dependent")
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(["20", "10", "5", "2", "1", "0"])
    ax.set_xlim(5.5, -0.5)
    ax.set_ylim(8e3, 3e6)
    ax.set_xlabel(r"jet $p_T$ regulator (GeV)")
    ax.set_ylabel("total cross section (pb)")
    ax.set_title("Native MadEvent: no eta cut")
    ax.grid(True, which="both", color="black", alpha=0.10, lw=0.6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for xi, yi in zip(x[:5], y[:5]):
        ax.annotate(f"{yi/1000:.0f}k", xy=(xi, yi), xytext=(4, 4),
                    textcoords="offset points", fontsize=7, color="#333333")
    ax.annotate("1.49e6 pb\nnot converged", xy=(0, 1.48e6), xytext=(0.6, 2.5e5),
                fontsize=8, color="#eb6834",
                arrowprops=dict(arrowstyle="->", color="#eb6834", lw=0.8))
    ax.legend(fontsize=7, frameon=False, loc="upper left")

    # Partonic at 200 GeV: ptj = 20, 10, 5, 2, 0 (0 is config sum)
    ax = axes[1]
    x = [4, 3, 2, 1, 0]
    y = [303.11, 416.13, 527.96, 675.71, 1268.76]
    ax.plot(x[:4], y[:4], color="#eb6834", marker="o", ms=6, lw=1.8,
            label="converged")
    ax.plot(x[3:], y[3:], color="#eb6834", ls="--", lw=1.2)
    ax.plot([x[4]], [y[4]], marker="o", ms=8, mfc="white", mec="#2a78d6",
            mew=1.8, ls="none", label="pT=0, config sum")
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(["20", "10", "5", "2", "0"])
    ax.set_xlim(4.5, -0.5)
    ax.set_ylim(220, 2200)
    ax.set_xlabel(r"jet $p_T$ regulator (GeV)")
    ax.set_ylabel(r"partonic $\sigma$ at $\sqrt{\hat{s}}=200$ GeV (pb)")
    ax.set_title("Partonic MadEvent: no eta cut")
    ax.grid(True, which="both", color="black", alpha=0.10, lw=0.6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for xi, yi in zip(x[:4], y[:4]):
        ax.annotate(f"{yi:.0f}", xy=(xi, yi), xytext=(4, 4),
                    textcoords="offset points", fontsize=7, color="#333333")
    ax.annotate("1,269 pb (sum of grids)\ncombined result = 0", xy=(0, 1268.76),
                xytext=(0.7, 360), fontsize=8, color="#2a78d6")
    ax.legend(fontsize=7, frameon=False, loc="upper left")

    fig.suptitle(r"The $p_T\to0$ endpoint is not a converged cross section", fontsize=10)
    fig.tight_layout()
    for suffix in ("png", "pdf"):
        fig.savefig(RESULTS / f"divergence_endpoint.{suffix}", dpi=180)
    plt.close(fig)
    print("wrote divergence_endpoint.png/pdf")


if __name__ == "__main__":
    main()
