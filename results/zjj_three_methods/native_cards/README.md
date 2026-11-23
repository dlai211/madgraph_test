# Native MadGraph cards for `pp -> Z j j`

Source output directory: `C:\Users\laiji\test\madgraph_baselines\z_2jet`.

| file | what it is |
|---|---|
| `proc_card.dat` | process definition: `generate p p > z j j` (the `j` multiparticle = g,u,c,d,s and antiparticles) |
| `param_card.dat` | SM parameters used by the run |
| `run_card_noeta.dat` | the **actual** run card of the no-eta survey: `etaj = -1`, `nevents = 20000` per subprocess, `ptj = 20`, `drjj = 0.4`, `mmjj = 20`, fixed scales 91.188 GeV, `nn23lo1` / LHAPDF 247000 |

The no-eta card was extracted from
`z_2jet/noeta_tag_1_debug.log` (MadGraph echoes the run card it used).
The `Cards/run_card.dat` in the output directory is the template with
`etaj = 2.5`; it corresponds to the official cut run, not to the 756k-event
no-eta sample in `SubProcesses/P1_*/G*/events.lhe`.

Launch drivers:

- `madgraph_baselines/run_z2j.mg5` -- `generate p p > z j j`, output, launch
- `madgraph_baselines/launch_z2j.mg5` -- launch of the existing output
- `madgraph_baselines/z_2jet/noeta_commands.txt` -- `survey noeta ...`
