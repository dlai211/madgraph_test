#!/usr/bin/env python3
"""One full-range interpolation figure: 114 -> 2000 GeV.

Combines the low-range and high-range interpolation CSVs into a single curve
and a single NF/MadEvent ratio panel.  The x-axis is logarithmic so both the
low-energy peak and the high-energy tail are visible.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

UPSTREAM = Path("C:/Users/laiji/test/conditional-nf-integration")
sys.path.insert(0, str(UPSTREAM / "scripts"))
import plot_nf_diagnostics as pnd  # noqa: E402

INTEGRAL_DIR = UPSTREAM / "results/zj_hadronic_integral"
EXACT_DIR = UPSTREAM / "results/zj_hadronic_madevent_interpolation"
OUTPUT_DIR = INTEGRAL_DIR / "plots"


def main() -> None:
    nf_low = pnd.read_nf_interpolation(INTEGRAL_DIR / "interpolation_low.csv")
    nf_high = pnd.read_nf_interpolation(INTEGRAL_DIR / "interpolation_high.csv")
    exact_low = pnd.read_exact_interpolation(EXACT_DIR, nf_low[0])
    exact_high = pnd.read_exact_interpolation(EXACT_DIR, nf_high[0])

    # Use the low scan through 250 GeV and the high scan above it.  The two
    # scans overlap in [200, 250]; keeping one avoids double points.
    low_mask = nf_low[0] <= 250.0
    high_mask = nf_high[0] > 250.0
    energies = np.concatenate([nf_low[0][low_mask], nf_high[0][high_mask]])
    values = np.concatenate([nf_low[1][low_mask], nf_high[1][high_mask]])
    errors = np.concatenate([nf_low[2][low_mask], nf_high[2][high_mask]])

    e_low_mask = exact_low[0] <= 250.0
    e_high_mask = exact_high[0] > 250.0
    e_energy = np.concatenate([exact_low[0][e_low_mask],
                               exact_high[0][e_high_mask]])
    e_value = np.concatenate([exact_low[1][e_low_mask],
                              exact_high[1][e_high_mask]])
    e_error = np.concatenate([exact_low[2][e_low_mask],
                              exact_high[2][e_high_mask]])

    fig, (ax, ratio_ax) = plt.subplots(
        2, 1, figsize=(8.2, 6.0), sharex=True,
        gridspec_kw={"height_ratios": [3.0, 1.15]},
    )
    ax.plot(energies, values, color=pnd.NF_COLOR, lw=1.8,
            label="conditional NF (six-channel sum)")
    ax.fill_between(energies, values - errors, values + errors,
                    color=pnd.NF_COLOR, alpha=0.16, linewidth=0)
    ax.errorbar(e_energy, e_value, yerr=e_error,
                fmt="o", color=pnd.EXACT_COLOR, ms=4.0, lw=0.9,
                capsize=2.0, label="MadEvent (partonic, six-channel sum)")

    nf_at_e = np.interp(e_energy, energies, values)
    nf_err_at_e = np.interp(e_energy, energies, errors)
    ratio = nf_at_e / e_value
    ratio_err = ratio * np.sqrt(
        (nf_err_at_e / nf_at_e) ** 2 + (e_error / e_value) ** 2
    )
    ratio_ax.errorbar(e_energy, ratio, yerr=ratio_err,
                      fmt="o", color=pnd.EXACT_COLOR, ms=3.4, lw=0.8,
                      capsize=1.8)
    ratio_ax.axhline(1.0, color="0.35", lw=0.8, linestyle=":")
    ratio_ax.set_ylim(0.98, 1.02)
    ratio_ax.set_ylabel("NF / MadEvent")
    ratio_ax.set_xlabel(r"$\sqrt{\hat s}$ (GeV)")
    ratio_ax.grid(True, color="#000000", alpha=0.10, linewidth=0.6)
    ratio_ax.spines["top"].set_visible(False)
    ratio_ax.spines["right"].set_visible(False)

    ax.set_xscale("log")
    ax.set_xlim(114.0, 2000.0)
    ax.set_yscale("log")
    ax.set_ylabel(r"six-channel summed partonic $\sigma$ (pb)")
    ax.set_title(
        "Six-channel summed partonic cross section — full range [114, 2000] GeV",
        fontsize=11,
    )
    ax.grid(True, which="both", color="#000000", alpha=0.10, linewidth=0.6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(fontsize=8, frameon=False, loc="best")

    ticks = [114, 150, 200, 300, 500, 700, 1000, 1500, 2000]
    ax.set_xticks(ticks)
    ax.set_xticklabels([str(t) for t in ticks])

    fig.tight_layout()
    for suffix in ("png", "pdf"):
        fig.savefig(OUTPUT_DIR / f"interpolation_combined.{suffix}", dpi=170,
                    bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {OUTPUT_DIR / 'interpolation_combined.png'}")


if __name__ == "__main__":
    main()
