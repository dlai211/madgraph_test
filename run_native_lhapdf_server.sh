#!/usr/bin/env bash
# Run the native p p > Z j integration with external LHAPDF 247000 on a Linux
# machine (e.g. orthus).  Windows build fixes are not applied here.
#
# Usage:
#   ./run_native_lhapdf_server.sh [ME_DIR] [MG5] [POINTS] [ITERATIONS]
#
#   ME_DIR      default: native_zj_lhapdf
#   MG5         default: mg5_aMC (only used if ME_DIR does not exist)
#   POINTS      default: 20000
#   ITERATIONS  default: 8
#
# If lhapdf-config is not in PATH, set LHAPDF_CONFIG=/path/to/lhapdf-config.
set -euo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
ME_DIR=${1:-native_zj_lhapdf}
MG5=${2:-mg5_aMC}
POINTS=${3:-20000}
ITER=${4:-8}
LHAPDF_CONFIG=${LHAPDF_CONFIG:-$(command -v lhapdf-config || true)}

if [ -z "$LHAPDF_CONFIG" ]; then
    echo "ERROR: lhapdf-config not found; set LHAPDF_CONFIG=/path/to/lhapdf-config" >&2
    exit 1
fi
echo "Using LHAPDF config: $LHAPDF_CONFIG"
export LHAPDF_DATA_PATH=$("$LHAPDF_CONFIG" --datadir)
echo "LHAPDF_DATA_PATH: $LHAPDF_DATA_PATH"

cd "$HERE"
if [ ! -d "$ME_DIR" ]; then
    echo "Generating $ME_DIR with $MG5"
    "$MG5" generate_native_lhapdf.mg5
fi
cd "$ME_DIR"

# Card settings: LHAPDF 247000, fixed scale, ptj=20, no eta cut.
python3 - Cards/run_card.dat <<'PY'
import re
import sys
p = sys.argv[1]
text = open(p, encoding="utf-8", errors="replace").read()
def set_value(name, value):
    global text
    pattern = re.compile(rf"^(\s*)(\S+)(\s*=\s*{re.escape(name)}\b)", re.MULTILINE)
    text, count = pattern.subn(
        lambda m: f"{m.group(1)}{value}{m.group(3)}", text, count=1
    )
    if count != 1:
        raise SystemExit(f"could not set {name} in {p}")
for name, value in [
    ("lpp1", "1"), ("lpp2", "1"),
    ("ebeam1", "6500.0"), ("ebeam2", "6500.0"),
    ("pdlabel1", "lhapdf"), ("pdlabel2", "lhapdf"),
    ("lhaid", "247000"),
    ("fixed_ren_scale", "True"),
    ("fixed_fac_scale1", "True"), ("fixed_fac_scale2", "True"),
    ("scale", "91.188"),
    ("dsqrt_q2fact1", "91.188"), ("dsqrt_q2fact2", "91.188"),
    ("ptj", "20.0"), ("etaj", "-1.0"),
    ("maxjetflavor", "4"), ("use_syst", "False"),
]:
    set_value(name, value)
open(p, "w", encoding="utf-8").write(text)
PY

# Point MG5 at the server's lhapdf-config.
python3 - Cards/me5_configuration.txt "$LHAPDF_CONFIG" <<'PY'
import re
import sys
p, cfg = sys.argv[1], sys.argv[2]
text = open(p, encoding="utf-8", errors="replace").read()
for name in ("lhapdf_py2", "lhapdf_py3"):
    pattern = re.compile(rf"^#?\s*{name}\s*=.*$", re.MULTILINE)
    if pattern.search(text):
        text = pattern.sub(f"{name} = {cfg}", text, count=1)
    else:
        text += f"\n{name} = {cfg}\n"
open(p, "w", encoding="utf-8").write(text)
PY

# Build with external LHAPDF; replace any Windows temp paths.
python3 - Source/make_opts "$LHAPDF_CONFIG" <<'PY'
import re
import sys
p, cfg = sys.argv[1], sys.argv[2]
text = open(p, encoding="utf-8", errors="replace").read()
text, count = re.subn(r"^lhapdf=.*$", f"lhapdf={cfg}", text, count=1, flags=re.MULTILINE)
if count == 0:
    text = f"lhapdf={cfg}\n" + text
for name in ("TMP", "TEMP", "TMPDIR"):
    text = re.sub(rf"^export {name} :=.*$", f"export {name} := /tmp", text,
                  flags=re.MULTILINE)
open(p, "w", encoding="utf-8").write(text)
PY

cat > survey_lhapdf.txt <<EOF
survey lhapdf_native --points=$POINTS --iterations=$ITER --accuracy=0.002
EOF

./bin/madevent survey_lhapdf.txt | tee lhapdf_native.log
echo "--- result ---"
head -1 SubProcesses/results.dat
echo
echo "Compare: internal nn23lo1 native ~11,913 pb; corrected partonic fine no-eta 11,876.96 pb."
