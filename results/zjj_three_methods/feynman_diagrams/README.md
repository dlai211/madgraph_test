# Feynman diagrams

The diagrams are the MadGraph PostScript files written when the process was
generated.  There is one file per matrix element (subprocess amplitude):

## Native full-process output

Originals: `C:/Users/laiji/test/madgraph_baselines/z_2jet/SubProcesses/P1_*/matrix*.ps`
(28 files).  Viewable copies: `native/P1_*_matrix*.pdf` in this folder.

### P1_gg_zqq

| file | process(es) |
|---|---|
| `matrix1.ps` / `native/P1_gg_zqq_matrix1.pdf` | g g > z u u~,g g > z c c~ |
| `matrix2.ps` / `native/P1_gg_zqq_matrix2.pdf` | g g > z d d~,g g > z s s~ |

### P1_gq_zgq

| file | process(es) |
|---|---|
| `matrix1.ps` / `native/P1_gq_zgq_matrix1.pdf` | g u > z g u,g c > z g c |
| `matrix2.ps` / `native/P1_gq_zgq_matrix2.pdf` | g d > z g d,g s > z g s |
| `matrix3.ps` / `native/P1_gq_zgq_matrix3.pdf` | g u~ > z g u~,g c~ > z g c~ |
| `matrix4.ps` / `native/P1_gq_zgq_matrix4.pdf` | g d~ > z g d~,g s~ > z g s~ |

### P1_qq_zgg

| file | process(es) |
|---|---|
| `matrix1.ps` / `native/P1_qq_zgg_matrix1.pdf` | u u~ > z g g,c c~ > z g g |
| `matrix2.ps` / `native/P1_qq_zgg_matrix2.pdf` | d d~ > z g g,s s~ > z g g |

### P1_qq_zqq

| file | process(es) |
|---|---|
| `matrix1.ps` / `native/P1_qq_zqq_matrix1.pdf` | u u > z u u,c c > z c c |
| `matrix2.ps` / `native/P1_qq_zqq_matrix2.pdf` | u u~ > z u u~,c c~ > z c c~ |
| `matrix3.ps` / `native/P1_qq_zqq_matrix3.pdf` | d d > z d d,s s > z s s |
| `matrix4.ps` / `native/P1_qq_zqq_matrix4.pdf` | d d~ > z d d~,s s~ > z s s~ |
| `matrix5.ps` / `native/P1_qq_zqq_matrix5.pdf` | u~ u~ > z u~ u~,c~ c~ > z c~ c~ |
| `matrix6.ps` / `native/P1_qq_zqq_matrix6.pdf` | d~ d~ > z d~ d~,s~ s~ > z s~ s~ |
| `matrix7.ps` / `native/P1_qq_zqq_matrix7.pdf` | u c > z u c |
| `matrix8.ps` / `native/P1_qq_zqq_matrix8.pdf` | u d > z u d,u s > z u s,c d > z c d,c s > z c s |
| `matrix9.ps` / `native/P1_qq_zqq_matrix9.pdf` | u u~ > z c c~,c c~ > z u u~ |
| `matrix10.ps` / `native/P1_qq_zqq_matrix10.pdf` | u u~ > z d d~,u u~ > z s s~,c c~ > z d d~,c c~ > z s s~ |
| `matrix11.ps` / `native/P1_qq_zqq_matrix11.pdf` | u c~ > z u c~,c u~ > z c u~ |
| `matrix12.ps` / `native/P1_qq_zqq_matrix12.pdf` | u d~ > z u d~,u s~ > z u s~,c d~ > z c d~,c s~ > z c s~ |
| `matrix13.ps` / `native/P1_qq_zqq_matrix13.pdf` | d s > z d s |
| `matrix14.ps` / `native/P1_qq_zqq_matrix14.pdf` | d u~ > z d u~,d c~ > z d c~,s u~ > z s u~,s c~ > z s c~ |
| `matrix15.ps` / `native/P1_qq_zqq_matrix15.pdf` | d d~ > z u u~,d d~ > z c c~,s s~ > z u u~,s s~ > z c c~ |
| `matrix16.ps` / `native/P1_qq_zqq_matrix16.pdf` | d d~ > z s s~,s s~ > z d d~ |
| `matrix17.ps` / `native/P1_qq_zqq_matrix17.pdf` | d s~ > z d s~,s d~ > z s d~ |
| `matrix18.ps` / `native/P1_qq_zqq_matrix18.pdf` | u~ c~ > z u~ c~ |
| `matrix19.ps` / `native/P1_qq_zqq_matrix19.pdf` | u~ d~ > z u~ d~,u~ s~ > z u~ s~,c~ d~ > z c~ d~,c~ s~ > z c~ s~ |
| `matrix20.ps` / `native/P1_qq_zqq_matrix20.pdf` | d~ s~ > z d~ s~ |

## One representative per P1 group

`representatives/<channel>/` contains the diagrams for the channel used in
the three-method comparison, as a multi-page PDF and as PNG pages:

| channel | matrix file | process |
|---|---|---|
| `gg_zjj` | `P1_gg_zqq/matrix1.ps` | g g > z u u~ (+ c c~) |
| `gu_zug` | `P1_gq_zgq/matrix1.ps` | g u > z g u (+ g c) |
| `qqbar_zgg` | `P1_qq_zgg/matrix1.ps` | u u~ > z g g (+ c c~) |
| `uu_zuu` | `P1_qq_zqq/matrix1.ps` | u u > z u u (+ c c) |

Each standalone in `conditional-nf-integration/generated/<channel>_standalone/`
also has the same diagrams at `SubProcesses/P1_*/matrix.ps`.

## Regenerating / displaying

```text
MG5_aMC> import model sm
MG5_aMC> generate p p > z j j
MG5_aMC> display diagrams
```
This opens the PostScript diagrams (and `output <dir>` writes the `matrix*.ps`
files into the output).  Any PS viewer works (Ghostscript/GSview, Evince,
Okular); `ps2pdf matrix1.ps matrix1.pdf` also works.
