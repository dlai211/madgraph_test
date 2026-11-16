# Z + 2 jets: run plan and commands

**Date:** 2026-11-15  
**Scope:** conditional-NF pilot for `g g > Z u u~` and MadGraph
`p p > Z j j` / fixed-√ŝ partonic runs.  
**No NF training was run on the local Windows machine.** The MadGraph
native test and the phase-space threshold scan below were run locally.

---

## 0. What already exists

| item | status |
|---|---|
| 5-D NF code (`ThreeBodyPhaseSpace`, dimension 5) | exists |
| `configs/processes/gg_zjj.json` | exists: `g g > z u u~ @1`, `√ŝ` 200–2000 GeV, `alpha_s=0.130` (fixed 2026-11-15) |
| `generated/gg_zjj_standalone` | exists locally, but the matrix library is a Windows `.pyd` |
| balanced `gg_zjj` training | **paused**, no final checkpoint |
| smoke `gg_zjj` checkpoint / validation | exists locally, not a production result |
| LHAPDF integration for a 3-body channel | **does not exist yet** |
| MadGraph `p p > z j j` baseline | exists in `madgraph_baselines/z_2jet` |

### 0.1 What `gg_zjj` covers

`gg_zjj` is the **gluon-fusion up-type pilot**:

```text
g g > Z u u~
```

It is **not** the full `p p > Z j j` process. The full process has four
MadGraph subprocess groups:

| group | content | native fixed-scale share (this test) |
|---|---|---:|
| `P1_gq_zgq` | `g q > Z g q`, q = u,c,d,s and antiquarks | 2541.4 pb (76.7%) |
| `P1_qq_zqq` | 20 subprocesses, `q q / q q~ / q~ q~ > Z q q` | 376.5 pb (11.4%) |
| `P1_qq_zgg` | `q q~ > Z g g` | 202.7 pb (6.1%) |
| `P1_gg_zqq` | `g g > Z q q~` | 191.1 pb (5.8%) |
| **total** | | **3311.6 pb** |

The `gg_zjj` pilot is therefore about 5.8% of the full `pp -> Zjj` rate. A
full NF prediction needs the other three groups (and, within `gg_zqq`, both
up-type and down-type Z couplings).

---

## 1. Energy range

The 5-D phase-space map has

```text
minimum_energy = M_Z + m_jj_min = 91.188 + 20 = 111.188 GeV.
```

That is only the algebraic minimum. With the actual cuts
(`pT_j > 20`, `|eta_j| < 2.5`, `DeltaR_jj > 0.4`, `m_jj > 20`), the cut-pass
fraction for `g g > Z u u~` is zero below about 131 GeV and turns on as:

| sqrt(s-hat) (GeV) | cut-pass fraction |
|---:|---:|
| 130 | 0.00000 |
| 132 | 0.0011 |
| 134 | 0.0122 |
| 136 | 0.0313 |
| 138 | 0.0552 |
| 140 | 0.0812 |
| 150 | 0.225 |
| 175 | 0.495 |
| 200 | 0.652 |
| 250 | 0.806 |

These numbers come from 50k–200k uniform 5-D phase-space points mapped
through `ThreeBodyPhaseSpace` and the cut mask; the matrix element is nonzero
on the passing points starting at 140 GeV.

### Recommendation

- **Pilot (existing config):** keep `gg_zjj` at **200–2000 GeV**. It is safe,
  already configured, and has a smoke checkpoint.
- **Production low range:** add `gg_zjj_low` at **140–250 GeV** (or 150–250)
  and keep the high model at 200–2000. Integrate low `[140,250]`, high
  `[250,2000]`, so the 200–250 overlap is not double-counted. Training below
  140 GeV is possible but the cut-pass fraction is below 8%, so ESS and
  training will be harder.
- **Upper range:** 2000 GeV is a reasonable start, matching the Z+1 jet
  campaign. The `[2000,13000]` tail must be measured (do not reuse the Z+1
  jet 0.1389 pb blindly).

---

## 2. Environment: orthus / odyssey

The user-facing entry point is orthus; the GPU partition is odyssey. The
repository and software are on the shared filesystem.

```bash
ssh dlai@orthus.nic.uoregon.edu
sinfo
srun --partition=odyssey --pty /bin/bash
rocm-smi
```

### 2.1 Common environment (on orthus and inside the srun shell)

```bash
source /storage/users/dlai/mango-linux/env_linux.sh

export REPO=/home/users/dlai/conditional-nf-integration
export PY=python3
export MG5=/storage/users/dlai/mango-linux/bin/mg5_aMC
export LHAPDF_DATA_PATH=/storage/users/dlai/lhapdf-env/share/LHAPDF
export PYTHONPATH="$REPO:$REPO/experiments"

ls -d "$REPO" "$MG5" "$LHAPDF_DATA_PATH"
```

If the repo lives elsewhere, change `REPO`; the rest of the commands use it.
Every new shell (including the `srun` shell and the batch script) must set
`REPO`, `PY`, `MG5`, `LHAPDF_DATA_PATH` and `PYTHONPATH` again.

### 2.2 GPU preflight

```bash
srun --partition=odyssey --gres=gpu:1 --cpus-per-task=48 --mem=64G \
  --time=24:00:00 --pty /bin/bash

source /storage/users/dlai/mango-linux/env_linux.sh
export PY=python3
rocm-smi
$PY - <<'PY'
import torch
print("torch", torch.__version__)
print("cuda/rocm available", torch.cuda.is_available())
if torch.cuda.is_available():
    print(torch.cuda.get_device_name(0))
PY
```

If `torch.cuda.is_available()` is false, fall back to `--device cpu`; the
matrix element is CPU-bound anyway. Do not use the shared orthus login node
for long training.

### 2.3 Linux matrix-element library

The local `generated/gg_zjj_standalone` contains a Windows
`matrix2py.cp310-win_amd64.pyd`. Check for a Linux build:

```bash
find "$REPO/generated/gg_zjj_standalone/SubProcesses" \
  \( -name 'matrix2py*.so' -o -name 'matrix2py*.pyd' \) -print
```

If only `.pyd` exists, regenerate a Linux standalone **into a separate
directory** so the Windows tree is preserved:

```bash
cd "$REPO"
$PY - <<'PY'
import json
from pathlib import Path
src = Path("configs/processes/gg_zjj.json")
dst = Path("configs/processes/gg_zjj_linux.json")
d = json.loads(src.read_text())
d["standalone"] = "generated/gg_zjj_standalone_linux"
dst.write_text(json.dumps(d, indent=2) + "\n")
print(dst)
PY

$PY experiments/setup_madgraph_process.py \
  --config configs/processes/gg_zjj_linux.json \
  --mg5 "$MG5"
```

Use `configs/processes/gg_zjj_linux.json` in all NF commands below. The
training output name remains `gg_zjj`; only the standalone path changes.

---

## 3. NF training (pilot)

The matrix element resolves `Cards/` relative to the CWD, so always run from
the standalone directory.

**Alpha_s check:** `gg_zjj.json` now sets `alpha_s = 0.130`, matching the
Z+1 jet and native baseline. The existing smoke checkpoint was trained with
the old default 0.118 and **must not** be used for production. At 250 GeV the
exact partonic cross section changes from 0.2914 pb (0.118) to 0.3537 pb
(0.130), a factor 1.214 ≈ (0.130/0.118)^2. Retrain from scratch after the
config fix.

```bash
cd "$REPO/generated/gg_zjj_standalone_linux"   # or gg_zjj_standalone if .so exists
PYTHONPATH="$REPO:$REPO/experiments" \
$PY -u "$REPO/experiments/run_madgraph_process_conditional_copula.py" \
  --config "$REPO/configs/processes/gg_zjj_linux.json" \
  --speed-profile balanced --device cuda \
  --batch-size 30000 --is-points 128 --me-chunk 512 --me-workers 48 \
  --output "$REPO/results/gg_zjj_copula_balanced_gpu"
```

Expected output:

```text
results/gg_zjj_copula_balanced_gpu/
  madgraph_gg_zjj_5_final_model.pt
  madgraph_gg_zjj_5_final_summary.csv
```

The earlier synchronized Windows run reached KL step 3200 in ~2 h 10 min and
was stopped before writing a checkpoint. Budget **6–16 h** for the full
two-round + chi-squared run; measure the first 400 steps to extrapolate.
Check `std_logw` is finite in the final summary.

### 3.1 Optional low-range model (140–250 GeV)

```bash
cd "$REPO"
$PY - <<'PY'
import json
from pathlib import Path
d = json.loads(Path("configs/processes/gg_zjj.json").read_text())
d["name"] = "gg_zjj_low"
d["standalone"] = "generated/gg_zjj_standalone_linux"
d["condition"]["minimum"] = 140.0
d["condition"]["maximum"] = 250.0
d["condition"]["held_out"] = [150.0, 175.0, 200.0, 225.0, 240.0]
Path("configs/processes/gg_zjj_low.json").write_text(json.dumps(d, indent=2) + "\n")
PY

cd "$REPO/generated/gg_zjj_standalone_linux"
PYTHONPATH="$REPO:$REPO/experiments" \
$PY -u "$REPO/experiments/run_madgraph_process_conditional_copula.py" \
  --config "$REPO/configs/processes/gg_zjj_low.json" \
  --speed-profile balanced --device cuda \
  --batch-size 30000 --is-points 128 --me-chunk 512 --me-workers 48 \
  --output "$REPO/results/gg_zjj_low_copula_balanced_gpu"
```

The low model output checkpoint is
`madgraph_gg_zjj_low_5_final_model.pt`. Validate it against exact MadEvent at
150, 175, 200, 225 and 240 GeV using the same
`validate_madgraph_process_with_madevent.py` command with
`--config configs/processes/gg_zjj_low.json`.

### 3.2 Slurm batch form

Create `zjj_nf.sbatch` on orthus:

```bash
#!/usr/bin/env bash
#SBATCH --job-name=zjj-nf
#SBATCH --partition=odyssey
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=48
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --output=logs/zjj-nf-%j.log

set -euo pipefail
source /storage/users/dlai/mango-linux/env_linux.sh
export REPO=/home/users/dlai/conditional-nf-integration
export PY=python3
export PYTHONPATH="$REPO:$REPO/experiments"
cd "$REPO/generated/gg_zjj_standalone_linux"
$PY -u "$REPO/experiments/run_madgraph_process_conditional_copula.py" \
  --config "$REPO/configs/processes/gg_zjj_linux.json" \
  --speed-profile balanced --device cuda \
  --batch-size 30000 --is-points 128 --me-chunk 512 --me-workers 48 \
  --output "$REPO/results/gg_zjj_copula_balanced_gpu"
```

Submit from orthus:

```bash
mkdir -p "$REPO/logs"
sbatch zjj_nf.sbatch
squeue -u dlai
```

---

## 4. NF validation

### 4.1 NF vs uniform Monte Carlo

Run this **after** the balanced training has written
`madgraph_gg_zjj_5_final_model.pt`.

```bash
cd "$REPO/generated/gg_zjj_standalone_linux"
PYTHONPATH="$REPO:$REPO/experiments" \
$PY -u "$REPO/experiments/validate_madgraph_process_integral.py" \
  --config "$REPO/configs/processes/gg_zjj_linux.json" \
  --checkpoint "$REPO/results/gg_zjj_copula_balanced_gpu/madgraph_gg_zjj_5_final_model.pt" \
  --nf-evals 200000 --gpu-chunk 20000 \
  --no-sobol --compare-uniform --device cuda \
  --output "$REPO/results/gg_zjj_validation_balanced_gpu"
```

Expected: per-energy NF estimate, stderr, ESS, pull, ESS ratio and variance
reduction against uniform MC.

### 4.2 NF vs exact partonic MadEvent

This is the important absolute-normalization check. The config condition
starts at 200 GeV; use only in-range energies for the NF comparison. The
driver now sets `drjj` and `mmjj` from the config cuts (patched 2026-11-15),
so the MadEvent cuts match the NF.

```bash
cd "$REPO/generated/gg_zjj_standalone_linux"
PYTHONPATH="$REPO:$REPO/experiments" \
$PY -u "$REPO/experiments/validate_madgraph_process_with_madevent.py" \
  --config "$REPO/configs/processes/gg_zjj_linux.json" \
  --mg5 "$MG5" \
  --energies 200 250 400 650 1000 1500 1950 \
  --refine-accuracy 0.0002 \
  --output "$REPO/results/gg_zjj_madevent_interpolation"
```

This generates a fixed-√ŝ MadEvent directory (default name
`generated/zj_hadronic_madevent_gg_zjj`) with `lpp1=lpp2=0`,
`ebeam=√ŝ/2`, fixed scale 91.188, `alpha_s=0.130`, `ptj=20`, `etaj=2.5`,
`drjj=0.4`, `mmjj=20`.

On Windows, the driver's direct `bin/madevent` call fails because the file is
a Python script; run `madgraph_baselines/prepare_run.py` on the generated
directory once and invoke `$PY bin/madevent <commands>` manually.

Local reference point (after the `drjj/mmjj` patch):
**250 GeV, `alpha_s=0.130`: 0.35373 ± 0.000996 pb** for
`g g > Z u u~`. At the old 0.118 this was 0.29144 pb; do not mix the two.
The independent 100k-point uniform phase-space integral of the same matrix
element gives 0.35364 pb (0.130) and 0.29136 pb (0.118), i.e. 0.03% agreement
with MadEvent. This validates the 5-D phase space, the cuts, and the
`alpha_s` argument.

For the threshold region below 200 GeV, run **exact MadEvent only**:

```bash
PYTHONPATH="$REPO:$REPO/experiments" \
$PY -u "$REPO/experiments/validate_madgraph_process_with_madevent.py" \
  --config "$REPO/configs/processes/gg_zjj_linux.json" \
  --mg5 "$MG5" \
  --energies 132 134 136 138 140 150 175 200 \
  --allow-outside-condition \
  --refine-accuracy -1 --survey-points 2000 --survey-iterations 4 \
  --output "$REPO/results/gg_zjj_madevent_threshold"
```

Do not compare the NF outside its training range.

---

## 5. NF total integrated cross section

**Blocker:** the existing
`experiments/integrate_hadronic_process.py` is hard-coded to the six
two-body Z+1 jet channels and the low/high Z+1 configs. It cannot integrate
a 3-body `gg_zjj` model.

A 3-body driver is needed. It should:

1. load the `gg_zjj` config and checkpoint;
2. evaluate `nf_estimate` on a log-spaced √ŝ grid in `[200,2000]` (or
   `[140,250]` + `[250,2000]` for the low/high setup);
3. multiply by the `g g` luminosity `dL/d√ŝ` with LHAPDF 247000, 200-point
   Gauss–Legendre;
4. trapezoid-integrate and add the measured `[2000,13000]` tail;
5. write `summary.json` and `per_channel.csv`.

Intended command (after the driver exists):

```bash
cd "$REPO/generated/gg_zjj_standalone_linux"
export LHAPDF_DATA_PATH=/storage/users/dlai/lhapdf-env/share/LHAPDF
export LD_LIBRARY_PATH=/storage/users/dlai/lhapdf-env/lib:${LD_LIBRARY_PATH:-}
export LD_PRELOAD=/storage/users/dlai/lhapdf-env/lib/libstdc++.so.6
PYTHONPATH="$REPO:$REPO/experiments" \
$PY -u "$REPO/experiments/integrate_gg_zjj.py" \
  --config "$REPO/configs/processes/gg_zjj_linux.json" \
  --checkpoint "$REPO/results/gg_zjj_copula_balanced_gpu/madgraph_gg_zjj_5_final_model.pt" \
  --device cuda --nf-evals 200000 \
  --pdf NNPDF23_lo_as_0130_qed --lhaid 247000 \
  --output "$REPO/results/gg_zjj_integral"
```

This is the next code step; it is not yet runnable.

---

## 6. MadGraph native `p p > Z j j`

### 6.1 Local Windows test (already run)

The existing `madgraph_baselines/z_2jet` directory was rerun with:

```text
lpp1 = lpp2 = 1
ebeam1 = ebeam2 = 6500
pdlabel = nn23lo1
lhaid = 247000
fixed_ren_scale = True
fixed_fac_scale = True
scale = 91.188
dsqrt_q2fact1 = dsqrt_q2fact2 = 91.188
ptj = 20
etaj = 2.5
drjj = 0.4
mmjj = 20
maxjetflavor = 4
use_syst = False
```

Command:

```bash
cd /c/Users/laiji/test/madgraph_baselines/z_2jet
PY="/c/Users/laiji/.conda/envs/workspace/python.exe"
$PY bin/madevent z2j_fixed_commands.txt
```

with `z2j_fixed_commands.txt`:

```text
survey z2j_fixed --points=5000 --iterations=6 --accuracy=0.002
```

On Windows, `bin/madevent` is a Python script, so run it as
`$PY bin/madevent ...`; the generated tree also needs
`madgraph_baselines/prepare_run.py` once. On Linux/orthus it is directly
executable.

Result (5000 × 6, not final):

```text
total = 3312 ± 3.75 pb
P1_gg_zqq = 191.05 pb
P1_gq_zgq = 2541.40 pb
P1_qq_zgg = 202.69 pb
P1_qq_zqq = 376.51 pb
```

For production use `--points=20000 --iterations=8` (expect ~30–60 min) and
quote the final `SubProcesses/results.dat`.

### 6.2 Generate and run on orthus/Linux

```bash
cd "$REPO"
cat > /tmp/zjj_native.mg5 <<'EOF'
set automatic_html_opening False
import model sm
generate p p > z j j
output zjj_native -noclean --nojpeg
EOF
$MG5 /tmp/zjj_native.mg5
```

Set the run card. This Python snippet handles both the old `pdlabel` and the
new `pdlabel1/2` card spellings:

```bash
cd "$REPO/zjj_native"
$PY - <<'PY'
import re
from pathlib import Path
p = Path("Cards/run_card.dat")
text = p.read_text(encoding="utf-8", errors="replace")
settings = {
    "lpp1": "1", "lpp2": "1",
    "ebeam1": "6500.0", "ebeam2": "6500.0",
    "pdlabel": "nn23lo1", "lhaid": "247000",
    "fixed_ren_scale": "True", "fixed_fac_scale": "True",
    "scale": "91.188",
    "dsqrt_q2fact1": "91.188", "dsqrt_q2fact2": "91.188",
    "ptj": "20.0", "etaj": "2.5", "drjj": "0.4", "mmjj": "20.0",
    "maxjetflavor": "4", "use_syst": "False",
    "dsqrt_shat": "0.0", "dsqrt_shatmax": "-1",
}
for name, value in settings.items():
    pat = re.compile(rf"^(\s*)(\S+)(\s*=\s*{re.escape(name)}\b)", re.MULTILINE)
    text, count = pat.subn(lambda m: f"{m.group(1)}{value}{m.group(3)}", text, count=1)
    if count == 0 and name in ("pdlabel", "fixed_fac_scale"):
        # Newer cards use pdlabel1/2 and fixed_fac_scale1/2.
        for suffix in ("1", "2"):
            pat = re.compile(rf"^(\s*)(\S+)(\s*=\s*{re.escape(name+suffix)}\b)", re.MULTILINE)
            text, count = pat.subn(lambda m: f"{m.group(1)}{value}{m.group(3)}", text, count=1)
            print(name+suffix, count)
    else:
        print(name, count)
p.write_text(text, encoding="utf-8")
PY

printf "survey z2j_fixed --points=20000 --iterations=8 --accuracy=0.002\n" \
  > z2j_fixed_commands.txt
$PY bin/madevent z2j_fixed_commands.txt
head -1 SubProcesses/results.dat
```

---

## 7. MadGraph fixed-√ŝ partonic scans

### 7.1 Pilot `g g > Z u u~`

Use `validate_madgraph_process_with_madevent.py` as in §4.2; it sets
`lpp=0`, `ebeam=√ŝ/2`, fixed scale, and the NF cuts. Individual energies are
the `--energies` list. Output `comparison.csv` has one row per energy.

### 7.2 Full `p p > Z j j` at fixed √ŝ

Use the full `z_2jet`/`zjj_native` directory with `lpp=0`,
`pdlabel=none` (or `pdlabel1/2=none`), `ebeam=√ŝ/2`, fixed scale, and the
same cuts. One run returns the sum over all four P1 groups; read each
`SubProcesses/P1_*/G*/results.dat` for the per-group breakdown.

Card edits per energy:

```text
lpp1 = lpp2 = 0
ebeam1 = ebeam2 = sqrt(s-hat)/2
pdlabel = none
fixed_ren_scale = True
fixed_fac_scale = True
scale = 91.188
dsqrt_q2fact1 = dsqrt_q2fact2 = 91.188
ptj = 20
etaj = 2.5
drjj = 0.4
mmjj = 20
maxjetflavor = 4
use_syst = False
dsqrt_shat = 0
```

Then:

```bash
printf "survey zjj_${E} --points=2000 --iterations=4 --accuracy=0.005\n" \
  > "zjj_${E}_commands.txt"
$PY bin/madevent "zjj_${E}_commands.txt"
```

Run energies in separate copies of the directory, or serially, because the
run card is shared state.

---

## 8. Procedure check

Run in this order:

1. **Preflight**: SSH to orthus, source `env_linux.sh`, check `REPO`, `MG5`,
   LHAPDF, `rocm-smi`, `torch.cuda.is_available()`.
2. **Standalone**: verify a Linux `matrix2py*.so`; if absent, generate
   `gg_zjj_standalone_linux` from `gg_zjj_linux.json`.
3. **Energy range**: confirm the 5-D threshold and cut turn-on; choose 200–2000
   (pilot) or 140–250 + 200–2000 (production).
4. **Train**: `run_madgraph_process_conditional_copula.py` on odyssey GPU with
   `--me-workers 48`.
5. **Validate**: NF vs uniform MC, then NF vs exact MadEvent with matching
   `ptj/etaj/drjj/mmjj`.
6. **Integrate**: after adding the 3-body LHAPDF driver, produce the NF total.
7. **Native compare**: `p p > Z j j` fixed-scale/eta 2.5 total; compare per
   group and total.
8. **Only then** extend to the other three P1 groups for a full `pp -> Zjj`
   NF prediction.

### Open items / caveats

- `gg_zjj` is **up-type only**. The full `gg -> Z q q~` group needs a
  down-type model (different Z coupling), and the full `pp -> Zjj` process
  needs `gq_zgq`, `qq_zgg`, `qq_zqq` as well.
- The 3-body LHAPDF integration driver is missing.
- The `gg_zjj` balanced run has no final checkpoint; restart from scratch.
- The current config minimum 200 GeV is conservative; the cut turn-on is
  ~132 GeV.
- The native 3312 ± 3.75 pb test is 5000 × 6; use 20k × 8 for production.
- The `[2000,13000]` tail must be measured for Z+2 jets.
- The MadEvent validation now includes `drjj` and `mmjj`; verify the generated
  run card after the first validation run.
