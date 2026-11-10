#!/usr/bin/env python3
"""Fit a smooth acceptance function per channel and integrate."""
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


def binned(sh, lab, w, edges):
    x, f, sig = [], [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (sh >= lo) & (sh < hi)
        if m.sum() < 2:
            continue
        ww = w[m]
        sw = ww.sum()
        sw2 = (ww * ww).sum()
        neff = sw * sw / sw2
        ff = float(np.average(lab[m], weights=ww))
        if neff < 20:
            continue
        x.append(0.5 * (lo + hi))
        f.append(ff)
        sig.append(max(np.sqrt(max(ff * (1 - ff), 1e-6) / neff), 1e-4))
    return np.array(x), np.array(f), np.array(sig)


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

    for width in (25, 50):
        edges = np.arange(112.5, 2025.0 + width, width)
        print(f"\nbin width {width} GeV")
        for deg in (2, 3, 4, 5):
            total = 0.0
            for c in CHANNELS:
                m = ch == c
                x, f, sig = binned(sh[m], lab[m], w[m], edges)
                if len(x) <= deg:
                    print("  too few bins", c, len(x))
                    continue
                coef = np.polyfit(np.log(x), f, deg, w=1.0 / sig)
                fe = np.clip(np.polyval(coef, np.log(energies)), 0.0, 1.0)
                total += float(np.sum(wgrid * integrands[c] * fe))
            print(f"  deg={deg}: channel-dependent total = {total:.2f} pb "
                  f"({(total/10599.2645-1)*100:+.2f}% vs official)")

        # all-channel polynomial for comparison
        for deg in (2, 3, 4, 5):
            x, f, sig = binned(sh, lab, w, edges)
            coef = np.polyfit(np.log(x), f, deg, w=1.0 / sig)
            fe = np.clip(np.polyval(coef, np.log(energies)), 0.0, 1.0)
            total = float(np.sum(wgrid * isum * fe))
            print(f"  all-channel deg={deg}: {total:.2f} pb "
                  f"({(total/10599.2645-1)*100:+.2f}% vs official)")


if __name__ == "__main__":
    main()
