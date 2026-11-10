#!/usr/bin/env python3
"""Compare the native and fine-partonic differential cross sections in sqrt(s-hat).

Native bin weights come from the LHE events (25 GeV bins, etaj=5 sample).
Partonic bin integrals come from the fine no-eta scan and the LHAPDF
luminosity. A uniform ratio points to a normalization difference; a
low-energy shape difference points to the native phase-space grid.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

import integrate_and_plot as ip

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"


def main() -> None:
    scan = ip.read_scan(RESULTS / "scan_noeta_fine.csv")
    energies = np.array([e for e, _, _ in scan[ip.CHANNELS[0]]])
    pdf = ip.lhapdf.mkPDF("NNPDF23_lo_as_0130_qed", 0)
    q2 = 91.188 ** 2
    sqrts = 13000.0
    y_nodes, y_weights = np.polynomial.legendre.leggauss(200)

    integrand = np.zeros_like(energies)
    for ch in ip.CHANNELS:
        sigma = np.array([s for _, s, _ in scan[ch]])
        lum = np.array([
            ip.luminosity(pdf, e, sqrts, q2, ip.PAIRS[ch], y_nodes, y_weights)
            for e in energies
        ])
        integrand += lum * sigma

    rows = []
    native_total = 0.0
    partonic_total = 0.0
    with (RESULTS / "eta_frame_events.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            center = float(row["shat_gev"])
            native = float(row["weight"])
            lo, hi = center - 12.5, center + 12.5
            if hi <= 114.0 or lo >= 2000.0:
                continue
            grid = np.linspace(max(lo, 114.0), min(hi, 2000.0), 21)
            partonic = float(np.trapz(np.interp(grid, energies, integrand), grid))
            if partonic <= 0:
                continue
            native_total += native
            partonic_total += partonic
            rows.append({
                "shat_center_gev": center,
                "shat_low_gev": lo,
                "shat_high_gev": hi,
                "native_pb": native,
                "partonic_pb": partonic,
                "ratio_native_over_partonic": native / partonic,
            })

    out = RESULTS / "differential_compare.csv"
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "native_total_pb": native_total,
        "partonic_total_pb": partonic_total,
        "ratio": native_total / partonic_total,
        "note": "native etaj=5 sample vs fine no-eta partonic scan",
    }
    (RESULTS / "differential_compare.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(f"bins: {len(rows)}")
    print(f"native total:   {native_total:10.2f} pb")
    print(f"partonic total: {partonic_total:10.2f} pb")
    print(f"ratio:          {native_total/partonic_total:.4f}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
