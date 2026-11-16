# Z + 2 jets NF — local run log (2026-11-16)

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
