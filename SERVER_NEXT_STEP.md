# Native LHAPDF cross-check — status and server alternative

> **Correction 2026-11-10.** The conclusion below that “the native grid
> remains” is **wrong**. The ~14% gap was the `xfxQ`/`xfxQ2` PDF-scale bug in
> our Python convolution; native MadEvent was correct. See
> [`FINDINGS.md`](FINDINGS.md) for the corrected record. The LHAPDF path fix
> and the native 11,914.0 pb cross-check in this file are still valid.

## Status: done locally on Windows

The native `p p > Z j` run with external **LHAPDF 247000** now works locally.
Result:

| native component | LHAPDF 247000 (pb) |
|---|---:|
| `P1_gq_zq` | 8,540.6 |
| `P1_qq_zg` | 3,373.4 |
| **total** | **11,914.0 ± 10.9** |

This is identical to the internal `nn23lo1` native total **11,913 ± 10.9 pb**.
The ~14% deficit against the old fine partonic **13,866.59 pb** was therefore
**not the native PDF**. It was also not the native grid: the deficit was the
`xfxQ`/`xfxQ2` bug in the Python convolution. The corrected partonic no-eta
total is **11,876.96 pb**, matching native **11,913 ± 10.9 pb**.

## Why it failed before, and the fix

The local static LHAPDF library embeds a POSIX path:

```text
/c/Users/laiji/test/lhapdf-local/share
```

The native `madevent.exe` is a Windows PE and cannot use that path, so it
threw `LHAPDF::ReadError: Could not find any pdfsets.index files`.  The fix is
a same-length byte replacement in the native binaries:

```text
/c/Users/laiji/test/lhapdf-local/share
→
C:/Users/laiji/test/lhapdf-local/share
```

The patched binaries are in
`native_zj_lhapdf/SubProcesses/P*/madevent.exe`.  They load LHAPDF 6.5.6 and
`NNPDF23_lo_as_0130_qed` (247000).

## Local reproduction

The patched binaries can be run directly (the `madevent` driver may recompile
and overwrite the patch):

```bash
cd native_zj_lhapdf/SubProcesses
for p in P1_gq_zq P1_qq_zg; do
  for g in G1 G2; do
    cd "$p/$g"
    cfg=${g#G}
    printf "20000 8 3\n0.002\n2\n1\n0\n${cfg}\n" > input_app.txt
    ../madevent.exe < input_app.txt > direct_lhapdf.log 2>&1
    cd ../..
  done
done

for f in P1_gq_zq/G1/results.dat P1_gq_zq/G2/results.dat \
         P1_qq_zg/G1/results.dat P1_qq_zg/G2/results.dat; do
  head -1 "$f"
done
```

The first column of each `results.dat` is the cross section in pb; sum the
four numbers.  The result is **11,914.0 ± 10.9 pb**.

## Server alternative (optional)

If you want an independent check on orthus (or need to rebuild rather than
patch), the portable script is still available:

```bash
export LHAPDF_CONFIG=/path/to/lhapdf-config
bash run_native_lhapdf_server.sh native_zj_lhapdf /path/to/mg5_aMC 20000 8
```

The orthus SSH key is not authorized from this Windows session, so that path
has to be launched by you.  The local patched result is the decisive test that
the native PDF is correct; the remaining gap was our convolution's PDF scale,
not the native grid.  See [`FINDINGS.md`](FINDINGS.md).
