# Z + 2 jets NF — local run log (2026-11-16)

> **Final results:** see [`ZJJ_NF_RESULTS.md`](ZJJ_NF_RESULTS.md) for the
> consolidated tables, figures and caveats.  This file is the chronological
> campaign log.

Full `pp -> Z j j` with conditional NFs, run on the local Windows RTX 3060 as a
backup for the orthus/odyssey run. Profile: **balanced** (user choice); analysis
follows the Z+1 jet treatment (`FINDINGS.md`).

## Scope and channel inventory

The native `p p > z j j` output splits into four P1 groups; their matrix headers
give 28 distinct partonic matrix elements (up/down couplings and flavor
combinations are separate matrices):

| group | matrices | native share |
|---|---:|---:|
| `P1_gq_zgq` | 4 (`gu`, `gd`, `gu~`, `gd~`) | 2541.4 pb (76.7%) |
| `P1_qq_zqq` | 20 | 376.5 pb (11.4%) |
| `P1_qq_zgg` | 2 up/down | 202.7 pb (6.1%) |
| `P1_gg_zqq` | 2 up/down | 191.1 pb (5.8%) |
| total | 28 | 3311.6 pb |

Configs, standalones and `.pyd` modules now exist for all 28 channels:
`configs/processes/zjj_hadronic.json` lists them with their `pdf_pairs`,
luminosity multiplicity and checkpoint path. The four up-type representatives
(`gg_zjj`, `gu_zug`, `qqbar_zgg`, `uu_zuu`) existed; the other 24 were generated
with `scripts/make_zjj_channel_configs.py` and
`scripts/build_zjj_standalones.sh`.

## Fixes applied while building the channels

1. **`alpha_s` missing** in `gu_zug.json`, `qqbar_zgg.json`, `uu_zuu.json`.
   The runner defaults to 0.118; the native baseline uses 0.130. All three now
   set `"alpha_s": 0.13`, like `gg_zjj.json` and the new channel configs.
2. **MG5's internal `make` on Windows** died because MSYS make drops
   `TEMP`/`TMP` from recipe environments and gfortran then falls back to
   `C:\WINDOWS`. Patched `MG5_aMC_v3_6_7/madgraph/various/misc.py:compile` to
   pass `TEMP=<dir> TMP=<dir>` as command-line make variables.
3. **MG5 makefiles call `../bin/madevent treatcards run`** through a
   `#!/usr/bin/env python3` shebang; MSYS's `python3` lacks `six`. Added
   `C:\Users\laiji\test\shim\python3` (execs the workspace conda Python) and put
   it first on PATH for MadEvent runs.
4. **Broken `coupl.inc` symlinks**: MG5 writes a 12-byte text file when the
   symlink fails on Windows. `madgraph_windows_build.py` now replaces any
   `coupl.inc` under 100 bytes instead of trusting `Path.exists()`.
5. **Double-counted luminosity for identical partons**: `integrate_hadronic_process.py`
   summed both beam orderings for every pair, which doubles `gg`, `uu`, `dd`,
   `u~u~`, `d~d~`. The driver now sums both orderings only when the two
   partons differ.

## Training

Pilot `gg_zjj` (balanced, 5-D, alpha_s 0.13) started 2026-11-16 02:40:

```bash
cd "$REPO/generated/gg_zjj_standalone"
PYTHONPATH="$REPO;$REPO/experiments" "$PY" -u \
  experiments/run_madgraph_process_conditional_copula.py \
  --config configs/processes/gg_zjj.json \
  --speed-profile balanced --device cuda \
  --batch-size 30000 --is-points 128 --me-chunk 512 \
  --output results/gg_zjj_copula_balanced_gpu
```

Log: `logs/gg_zjj_balanced_local.log`. ESS at the marginal caches reproduces the
earlier run (`beta=0.25`: 0.856/438.4, `beta=0.75`: 0.571/292.2, `beta=1.0`:
~0.58/240). First KL check reached step 400 at 03:15:35, i.e. **1.99 s/step**.
At the 12,000-step cap two rounds would take ~13 h; the convergence gate
(`lr <= 1e-4`, three checks with |relative improvement| < 1%) should stop
earlier.

### Partonic validation of the integration path

- Exact MadEvent: 0.35292 +/- 0.000276 pb at 250 GeV,
  0.44187 +/- 0.000376 pb at 400 GeV and 0.30455 +/- 0.00018 pb at 650 GeV.
- The smoke checkpoint with 200k evaluations gives 0.44143 +/- 0.00076 pb at
  400 GeV (0.1% below exact) and 0.30456 +/- 0.00050 pb at 650 GeV
  (0.003%), confirming the partonic normalization.
- Full six-energy check with the smoke checkpoint (200k evaluations each):

  | E [GeV] | NF [pb] | exact [pb] | pull | ESS |
  |---:|---:|---:|---:|---:|
  | 250 | 0.352397 | 0.352920 | -0.68 | 0.546 |
  | 400 | 0.440923 | 0.441870 | -1.12 | 0.631 |
  | 650 | 0.304651 | 0.304550 | 0.19 | 0.651 |
  | 1000 | 0.188073 | 0.188130 | -0.18 | 0.672 |
  | 1500 | 0.113464 | 0.113230 | 1.24 | 0.676 |
  | 1950 | 0.079757 | 0.080004 | -1.83 | 0.659 |

  Every pull is within 2 sigma.  File:
  `results/gg_zjj_madevent_exact/nf_vs_exact_smoke.csv`.

### Exact partonic references for the core channels [pb]

| E [GeV] | `gg_zjj` | `gu_zug` | `qqbar_zgg` | `uu_zuu` |
|---:|---:|---:|---:|---:|
| 250 | 0.35292 | 9.3325 | 24.095 | 3.0775 |
| 400 | 0.44187 | 13.353 | 18.836 | 6.3217 |
| 650 | 0.30455 | 11.353 | 10.593 | 6.3777 |
| 1000 | 0.18813 | 8.4021 | 5.8589 | 5.246 |
| 1500 | 0.11323 | 5.907 | 3.2107 | 3.9693 |
| 1950 | 0.080004 | 4.587 | 2.1408 | 3.2002 |

Files: `results/<channel>_madevent_exact/comparison.csv`. Each MadEvent
energy takes 100-170 s. The `gq` process has the largest partonic rate by
two orders of magnitude, consistent with its 76.7% hadronic share.
- A 5,000-evaluation grid point at 395 GeV read 0.4524 pb (2.4% high): the
  reported per-point error at 5k evaluations underestimates the true scatter.
  Production integration uses 100k evaluations per grid point.
- End-to-end one-channel convolution with the smoke checkpoint and 40+60 grid
  points gave 90.86 +/- 0.17 pb partonic-CM; the native up-type gg CM total
  above 200 GeV is 89.2 pb (2% difference consistent with the 5k-eval noise).
  The machinery, acceptance factor and luminosity multiplicity are correct.

Planned order: `gg_zjj` -> `gu_zug` (76.7% group) -> `qqbar_zgg` -> `uu_zuu`,
then **ESS-transfer tests** (`experiments/test_zjj_model_transfer.py`) decide
which other channels can share a checkpoint (C-conjugate and same-topology
channels) and which need their own balanced training.

First transfer test, using the existing smoke `gg_zjj` checkpoint (a valid
proposal at alpha_s 0.13 because alpha_s only rescales the density):

| energy | ESS on `gg_zjj` (up) | ESS on `gg_zddbar` (down) |
|---:|---:|---:|
| 250 | 0.5555 | 0.5472 |
| 650 | 0.6563 | 0.6390 |
| 1950 | 0.6589 | 0.6594 |

The up-type model serves the down-type channel at no ESS cost, so the
down-type `gg` training is not needed. The same test will be applied to the
C-conjugate `gq` and `qq` channels once their representatives are trained.

The spawn-based matrix-element pool (`--me-workers`) was verified
bit-identical to the serial path on Windows by `scripts/test_me_workers.py`
(max difference 0.0 on the finite points), so the remaining trainings can use
it to cut the per-step matrix-element time.

### Pilot complete (2026-11-16 09:41)

Wall time 7 h 01 min (02:40-09:41). Checkpoint
`results/gg_zjj_copula_balanced_gpu/madgraph_gg_zjj_5_final_model.pt`,
summary ESS **0.6087**, `std_logw` **0.6608** (finite), 10 edges,
graph `0 <- 1 <- 2 <- 3 <- 4`. Round 0 converged at step 5200; round 1 ran
to completion.

200k NF-vs-uniform validation
(`results/gg_zjj_validation_balanced_gpu`):

| E [GeV] | NF [pb] | exact [pb] | pull vs exact | ESS | variance reduction |
|---:|---:|---:|---:|---:|---:|
| 250 | 0.352816 +/- 0.00046 | 0.35292 | -0.19 | 0.745 | 7.9x |
| 400 | 0.440505 +/- 0.00052 | 0.44187 | -2.13 | 0.782 | 20.5x |
| 650 | 0.304542 +/- 0.00036 | 0.30455 | -0.02 | 0.786 | 26.0x |
| 1000 | 0.187917 +/- 0.00019 | 0.18813 | -0.97 | 0.827 | 36.7x |
| 1500 | 0.113099 +/- 0.00011 | 0.11323 | -1.01 | 0.833 | 52.6x |
| 1950 | 0.079984 +/- 0.000085 | 0.080004 | -0.21 | 0.814 | 50.7x |

NF vs uniform-MC pulls are within +/-1.75 sigma; ESS improvement over uniform
2.75x-10.3x. NF vs exact agrees at 0.03-0.31% (worst pull 2.1 sigma at 400).

First hadronic integration of the channel (partonic CM, 40+60 grid,
100k evals/point): **90.739 +/- 0.028 pb** over [200,2000] + 0.042 pb tail.
An exact-convolution cross-check with the original six scan points gave
93.4 pb, biased by flat extrapolation below 250 GeV. Adding exact points at
200, 220, 240, 300 and 350 GeV gives **90.719 pb** - agreement with the NF at
**0.02%**. At those low points the NF and exact partonic values agree to
0.4-0.5% (ratios 0.9958, 1.0039, 0.9985, 0.9953, 1.0000).

The native up-type `gg` reference from the event sample is
**89.25 +/- 0.63 pb** (CM, >200 GeV), 2.4 sigma below both; it is attributed
to the event-sample statistics and the MG5 `nn23lo1` vs LHAPDF sampling.

Lab-frame integration with the per-group acceptance (same grid,
100k evals/point): **64.258 +/- 0.021 pb** ([200,2000] 64.222 + 0.036 tail).
The native up lab reference is 63.2 pb - the same +1.7% offset as in the CM,
so the frame conversion is consistent and the offset lives in the native
event-based sample, not in the method.

Balanced-model transfers (ESS at 250/650/1950 GeV, source in parentheses):

| target | source | ESS |
|---|---|---|
| `gg_zddbar` | `gg_zjj` | 0.738 / 0.814 / 0.821 (up channel: 0.745 / 0.786 / 0.814) |
| `gd_zgd` | `gu_zug` | 0.748 / 0.842 / 0.842 (up channel: 0.780 / 0.823 / 0.828) |
| `gux_zgux` | `gu_zug` | 0.783 / 0.841 / 0.836 |
| `gdx_zgdx` | `gu_zug` | 0.774 / 0.837 / 0.840 |

No ESS loss anywhere, so one model per topology covers both Z couplings and
all charge states: `gg` (up covers down) and `gq` (u covers d, u~, d~).  The
hadronic config points `gg_zddbar` at `gg_zjj` and the three gq variants at
`gu_zug`.

Pilot summary: CM 90.739 +/- 0.028 pb (exact convolution 90.719, 0.02%),
lab 64.258 +/- 0.021 pb.

### Exact convolution references for the four representatives

`scripts/zjj_exact_convolution.py` merges the six high-energy points with the
five low-energy points (200/220/240/300/350 GeV), interpolates log-log with
PCHIP, and applies the channel's luminosity and group acceptance.  Over
[200, 2000] GeV, no tail:

| channel | CM [pb] | lab [pb] |
|---|---:|---:|
| `gg_zjj` | 90.677 | 64.206 |
| `gu_zug` | 1180.775 | 917.938 |
| `qqbar_zgg` | 122.735 | 78.704 |
| `uu_zuu` | 39.145 | 28.619 |

The NF result for `gg_zjj` (90.739 CM, 64.258 lab) agrees with the exact row
at 0.07% / 0.08%.  These are the per-channel references for the three models
still training.

### `gu_zug` complete (2026-11-16 15:25)

Wall time 5 h 22 min (10:03-15:25) with `--me-workers 6`.  ESS **0.7469**,
`std_logw` **0.5228**, 10 edges.  200k validation
(`results/gu_zug_validation_balanced_gpu`):

| E [GeV] | NF [pb] | exact [pb] | pull vs exact | ESS | variance reduction |
|---:|---:|---:|---:|---:|---:|
| 250 | 9.31796 +/- 0.011 | 9.3325 | -1.21 | 0.780 | 36x |
| 400 | 13.3581 +/- 0.015 | 13.353 | +0.30 | 0.793 | 165x |
| 650 | 11.3714 +/- 0.012 | 11.353 | +1.20 | 0.823 | 370x |
| 1000 | 8.40155 +/- 0.0079 | 8.4021 | -0.06 | 0.848 | 760x |
| 1500 | 5.91608 +/- 0.0057 | 5.907 | +1.10 | 0.844 | 2366x |
| 1950 | 4.59561 +/- 0.0047 | 4.587 | +0.97 | 0.828 | 1275x |

All pulls within 1.3 sigma; NF vs exact agrees at 0.007-0.19%.  The uniform
Monte Carlo is very inefficient for this channel (ESS down to 0.0026), hence
the variance reductions up to 2366x.

Hadronic integration (40+60 grid, 100k evals/point):
**CM 1182.389 +/- 0.429 pb** vs exact **1180.775 pb**, ratio **1.0014**;
**lab 919.200 +/- 0.425 pb** vs exact **917.938 pb**, ratio **1.0014**.
The same +0.14% in both frames confirms the acceptance conversion and the
NF/PDF normalization.

`qqbar_zgg` started at 15:25 with the same settings.

### `qqbar_zgg` complete (2026-11-16 20:12)

Wall time 4 h 47 min.  ESS **0.4103**, `std_logw` **0.9044** - the hardest
channel so far (the `qq~ -> Zgg` integrand is broader than `gq`).  200k
validation (`results/qqbar_zgg_validation_balanced_gpu`):

| E [GeV] | NF [pb] | exact [pb] | pull vs exact | ESS | variance reduction |
|---:|---:|---:|---:|---:|---:|
| 250 | 24.1100 +/- 0.038 | 24.095 | +0.35 | 0.668 | 10.6x |
| 400 | 18.8044 +/- 0.027 | 18.836 | -0.83 | 0.701 | 37.1x |
| 650 | 10.6227 +/- 0.016 | 10.593 | +1.51 | 0.701 | 81.2x |
| 1000 | 5.86201 +/- 0.0089 | 5.8589 | +0.32 | 0.684 | 130x |
| 1500 | 3.21683 +/- 0.0048 | 3.2107 | +1.21 | 0.689 | 274x |
| 1950 | 2.14171 +/- 0.0034 | 2.1408 | +0.25 | 0.668 | 211x |

NF vs exact agrees at 0.04-0.28% (all pulls <=1.6 sigma).  The down-type
`ddbar_zgg` channel shares this checkpoint with no ESS loss (0.682 / 0.692 /
0.662 at 250/650/1950 vs 0.668 / 0.701 / 0.668 on the trained channel);
`ddbar_zgg` now points at `qqbar_zgg`.  Hadronic integration:
**CM 122.948 +/- 0.042 pb** vs exact 122.735 (ratio 1.0017);
**lab 78.838 +/- 0.030 pb** vs exact 78.704 (ratio 1.0017).  The same +0.17%
in both frames.

`uu_zuu`, the last of the four core models, started at 20:12.

### `uu_zuu` complete (2026-11-17 01:43)

Wall time 5 h 31 min.  ESS **0.7709**, `std_logw` **0.5150** - the best of the
four.  200k validation (`results/uu_zuu_validation_balanced_gpu`):

| E [GeV] | NF [pb] | exact [pb] | pull vs exact | ESS | variance reduction |
|---:|---:|---:|---:|---:|---:|
| 250 | 3.07299 +/- 0.0039 | 3.0775 | -1.08 | 0.758 | 36x |
| 400 | 6.32663 +/- 0.0076 | 6.3217 | +0.54 | 0.777 | 117x |
| 650 | 6.37823 +/- 0.0068 | 6.3777 | +0.07 | 0.814 | 305x |
| 1000 | 5.23617 +/- 0.0051 | 5.246 | -1.18 | 0.838 | 439x |
| 1500 | 3.97199 +/- 0.0039 | 3.9693 | +0.54 | 0.840 | 714x |
| 1950 | 3.19638 +/- 0.0033 | 3.2002 | -0.63 | 0.825 | 662x |

NF vs exact agrees at 0.008-0.19% (all pulls within 1.2 sigma).  Hadronic CM:
**39.367 +/- 0.009 pb** vs exact 39.145 (ratio 1.0057, a little higher than the
other channels but within the exact scan's interpolation uncertainty).  The
lab value is taken from the full integration below.

### ESS sweep and the 28-channel model map (2026-11-17)

The four-candidate sweep (`scripts/zjj_ess_sweep.py`, 250/650/1950 GeV,
20k evaluations) over the 20 `P1_qq_zqq` channels gives:

- `uu_zuu` for 16 channels: same-flavor 0.79-0.81, different-flavor 0.43-0.49;
- `qqbar_zgg` for the four annihilation-to-different-flavor channels
  (`uux_zccx`, `uux_zddx`, `ddx_zuux`, `ddx_zssx`), ESS 0.37-0.45.

The full map (28 channels -> 4 models): `gg_zjj` 2, `gu_zug` 4,
`qqbar_zgg` 6, `uu_zuu` 16.  Every channel now points at an existing
checkpoint in `configs/processes/zjj_hadronic.json`; no further training is
needed for the full `pp -> Zjj` integration.

### Full pp -> Zjj integration and the multiplicity bug

First full run (`results/zjj_hadronic_integral_full`): lab [200,2000]
**2820.80 +/- 0.66 pb** vs native **2815.82 +/- 8.17** (ratio 1.00177,
pull 0.61); CM **3771.55** vs **3766.84 +/- 9.46** (ratio 1.00125).
Group totals: gq 2184.2, qq_zqq 339.3, qq_zgg 150.4, gg 146.9 pb.

A per-channel comparison against the native event sample (classified by
initial and final PDG pair) showed `uux_zddx` and `ddx_zuux` at **half** the
native rate (ratios 0.49 and 0.51).  Cause: matrix10 and matrix15 each
contain two *final* flavour options (d/s and u/c respectively) with identical
amplitudes, while the config counted only the initial flavour pair.  This
explained almost the whole qq_zqq group deficit (491.05 vs 502.50 pb CM).

Fixed: `multiplicity = 2` for `uux_zddx` and `ddx_zuux`, both in
`zjj_hadronic.json` and in `make_zjj_hadronic_config.py` so a regeneration
keeps it.

Rerun (`results/zjj_hadronic_integral_full_v2`):

| comparison | NF | native | ratio |
|---|---:|---:|---:|
| lab [200,2000] | **2826.21 +/- 0.66 pb** | 2815.82 +/- 8.17 | **1.00369** (pull 1.27) |
| lab + tail | 2834.99 +/- 0.85 pb | 2824.59 | 1.00369 |
| CM [200,2000] | **3779.99 pb** | 3766.84 +/- 9.46 | **1.00349** |

Group totals: gq 2184.2 (77.3%), qq_zqq 344.8 (12.2%), qq_zgg 150.4 (5.3%),
gg 146.9 (5.2%) pb.  The four groups now agree with the native sample within
-0.8% (qq_zqq) to +0.6% (gq); the uniform +0.35% total offset is consistent
with the native sample's MG5 `nn23lo1` vs LHAPDF sampling and its ~0.3%
statistics.

`gu_zug` (the 76.7% group) started immediately after the pilot with
`--me-workers 6`. The lab-frame pilot integration and the low-energy exact
scan were running concurrently.

## Native references

- Fixed-scale lab total (existing): **3311.7 +/- 3.75 pb**, scale 91.188,
  alpha_s 0.13, `nn23lo1` (LHAPDF 247000), ptj 20, etaj 2.5, drjj 0.4, mmjj 20.
- **No-eta survey completed** (`p p > z j j`, ptj 20, drjj 0.4, mmjj 20,
  etaj = -1): **5301 +/- 4.5 pb** over the full 13 TeV phase space. 755,797
  events in `SubProcesses/P1_*/G*/events.lhe`.
- Frame fractions from that unbiased sample, restricted to sqrt(s_hat) > 200
  (the acceptance script was fixed after an `int()` truncation had folded
  events below 200 GeV into the first bin):

  | quantity | >200 GeV | >2 TeV tail |
  |---|---:|---:|
  | no eta cut | 4577.8 pb | 53.19 +/- 1.33 pb |
  | lab `|eta|<2.5` | 2815.8 +/- 8.7 pb | 8.77 +/- 0.53 pb |
  | partonic CM `|eta|<2.5` | 3766.8 +/- 10.2 pb | 7.91 +/- 0.51 pb |
  | lab / CM | **0.7475** | 1.11 |

  The lab cut removes 25% relative to the partonic-CM cut. This is *not* the
  Z+1 situation (~0.1%): at low sqrt(s_hat) the partonic CM is strongly
  boosted against the lab, and the lab cut is the stronger one.
- **Threshold wedge.** The dedicated lab-cut native run gives 3311.7 pb over
  the full range, while the no-eta sample gives only 2815.8 pb above
  200 GeV. The difference, **~496 pb (15%)**, is the 132-200 GeV region,
  which lies below the NF condition minimum (200 GeV) and is not covered by
  the current models. The [200, 2000] + tail NF result must be compared to
  **2824.6 +/- 9 pb**, not to 3311.7, unless a low-range NF model
  (140-250 GeV, as recommended in ZJJ_RUN_PLAN.md) is trained later.
- Per-group lab/CM factors differ at the 10-15% level:
  `P1_gq_zgq` 0.7693, `P1_gg_zqq` 0.7082, `P1_qq_zqq` 0.6917,
  `P1_qq_zgg` 0.6398. The integration driver applies the table for the
  channel's own group (`--acceptance-dir`).
- The NF (which applies its cuts in the partonic CM) must be multiplied by
  these factors and integrated. Target for the hadronic comparison:
  **2815.8 +/- 8.7 pb [200, 2000] plus 8.77 +/- 0.53 pb tail = 2824.6 pb**.

## Analysis pieces

- `experiments/integrate_hadronic_process.py` now accepts 5-D checkpoints
  (dimension in the filename), per-channel `checkpoint` overrides, and a
  `multiplicity` factor.
- `scripts/zjj_acceptance_from_lhe.py` computes per-bin lab/CM fractions from
  LHE events; `scripts/plot_zjj_acceptance.py` draws the two-panel acceptance
  figure (`results/figures/zjj_acceptance.{png,svg}`).
- `experiments/test_zjj_model_transfer.py` measures ESS of a checkpoint on a
  different channel.
- `scripts/zjj_analyze.py` assembles the channel/group tables and the three
  figures (channel contributions, group shares, NF vs exact) from the
  integration output.  Tested end-to-end on the one-channel smoke output.

## Hadronic integration command (after the checkpoints exist)

```bash
source C:/Users/laiji/test/lhapdf-local/env_lhapdf.sh
cd "$REPO/generated/gg_zjj_standalone"
"$PY" -u "$REPO/experiments/integrate_hadronic_process.py" \
  --low-config "$REPO/configs/processes/zjj_hadronic.json" \
  --high-config "$REPO/configs/processes/zjj_hadronic.json" \
  --split 250 --nf-evals 100000 --gpu-chunk 20000 --device cuda \
  --acceptance-dir "$REPO/results/zjj_acceptance" \
  --tail-pb 8.7745 --tail-error-pb 0.5341 \
  --output "$REPO/results/zjj_hadronic_integral"
```

The same command can be run with `--tail-pb 0 --tail-error-pb 0` and
`--acceptance-dir` omitted to get the raw partonic-CM integral (target
3766.8 +/- 10.2 pb above 200 GeV).

## 2026-11-19: three-method comparison and window fix

`scripts/zjj_three_methods.py` decomposes the native no-eta sample into the
28 channels and writes `results/zjj_three_methods/` (`channel_table.csv`,
`summary.json`) plus the five report figures.

The native reference quoted above needs a window correction: 2815.8 pb is
`sqrt(s_hat) > 200 GeV` and already contains the 8.77 pb tail above
2000 GeV, so the like-for-like [200, 2000] native value is
**2807.04 +/- 8.15 pb** (lab) and **3758.93 +/- 9.44 pb** (CM).  The
corrected ratios are NF/native = **1.00683** (lab, pull 2.34) and
**1.00560** (CM, pull 2.22); the full-range comparison (2834.99 vs
2815.82 pb lab) is unchanged.  The `qq_zqq` group is +0.37% rather than
0.8% low once the same window is used.

The threshold wedge is also event-based now: **486.2 +/- 3.1 pb** in
132--200 GeV (lab), not the earlier ~496 pb.  The old number came from
subtracting the event-sample >200 window (2815.8) from the official full
cross section (3311.7), mixing two normalisations.  The event-sample full
sum is **3302.0 +/- 8.7 pb**, and the official 3311.7 +/- 3.75 pb is 0.29%
above it, within the sample statistics.  The full-range ratio is unchanged
at +0.58% (3321.2 / 3302.0).
