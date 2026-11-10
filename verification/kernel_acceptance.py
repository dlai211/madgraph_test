#!/usr/bin/env python3
"""Kernel-smoothed, channel-dependent lab acceptance."""
from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
CHANNELS = ["gu_zu", "gd_zd", "gux_zux", "gdx_zdx", "uux_zg", "ddx_zg"]


def load_integrands():
    data = defaultdict(dict)
    with (HERE / "channel_integrands.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            data[row["channel"]][float(row["energy_gev"])] = float(row["integrand_pb_per_gev"])
    energies = np.array(sorted(data[CHANNELS[0]]))
    return energies, {ch: np.array([data[ch][e] for e in energies]) for ch in CHANNELS}


def load_events():
    rows = list(csv.DictReader((HERE / "events_flat.csv").open()))
    w = np.array([float(r["weight"]) for r in rows])
    sh = np.array([float(r["shat"]) for r in rows])
    lab = np.abs(np.array([float(r["y_lab"]) for r in rows])) < 2.5
    ch = np.array([r["channel"] for r in rows])
    return w, sh, lab, ch


def kernel_f(xeval, sh, lab, w, bandwidth):
    """Weighted Gaussian kernel regression of a 0/1 acceptance."""
    # chunk to keep memory bounded
    out = np.empty_like(xeval, dtype=float)
    for i, x in enumerate(xeval):
        h = bandwidth(x) if callable(bandwidth) else bandwidth
        k = np.exp(-0.5 * ((sh - x) / h) ** 2)
        den = np.sum(k * w)
        out[i] = np.sum(k * w * lab) / den if den > 0 else np.nan
    return out


def main() -> None:
    energies, integrands = load_integrands()
    w, sh, lab, ch = load_events()
    wgrid = np.zeros_like(energies)
    wgrid[1:-1] = 0.5 * (energies[2:] - energies[:-2])
    wgrid[0] = 0.5 * (energies[1] - energies[0])
    wgrid[-1] = 0.5 * (energies[-1] - energies[-2])
    isum = sum(integrands[c] for c in CHANNELS)
    t_noeta = float(np.sum(wgrid * isum))
    print(f"no-eta total: {t_noeta:.4f} pb")

    for label, bandwidth in [
        ("h=15 GeV", 15.0),
        ("h=25 GeV", 25.0),
        ("h=50 GeV", 50.0),
        ("h=100 GeV", 100.0),
        ("h=max(25,0.1E)", lambda x: max(25.0, 0.10 * x)),
        ("h=max(40,0.15E)", lambda x: max(40.0, 0.15 * x)),
    ]:
        total_chan = 0.0
        total_single = 0.0
        f_all = kernel_f(energies, sh, lab, w, bandwidth)
        for c in CHANNELS:
            m = ch == c
            fc = kernel_f(energies, sh[m], lab[m], w[m], bandwidth)
            total_chan += float(np.sum(wgrid * integrands[c] * fc))
            total_single += float(np.sum(wgrid * integrands[c] * f_all))
        print(f"{label:20s} single={total_single:9.2f}  channel={total_chan:9.2f}  "
              f"diff={total_chan-total_single:+8.2f} pb ({(total_chan/total_single-1)*100:+.2f}%)")


if __name__ == "__main__":
    main()
