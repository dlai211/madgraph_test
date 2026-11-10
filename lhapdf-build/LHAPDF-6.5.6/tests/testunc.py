#! /usr/bin/env python3

import lhapdf
print("Version:", lhapdf.version())
print()

#pdfset = lhapdf.getPDFSet("CT10nlo")
pdfset = lhapdf.getPDFSet("NNPDF31_lo_as_0130")
print(pdfset)
print("m_t =", pdfset.get_entry("MTop", 123.4))
print()

pdfs = pdfset.mkPDFs()
print()

xfs_g = [pdfs[k].xfxQ(21, 1e-4, 100.) for k in range(pdfset.size)]
print("Gluon PDFs at x = 0.001, Q = 100 GeV:", xfs_g)
print()

for alt_ci_method in [True,False]:
    print(f"Using alt (asymm) CI calculation = {alt_ci_method}")
    u = pdfset.uncertainty(xfs_g, 95., alt_ci_method)
    print(u)
    print(u.central)
    print(" + ", u.errplus)
    print(" - ", u.errminus)
    print(" +-", u.errsymm)
    print()

#import numpy as np
#for cl in np.linspace(0.0, 1.0, 20):
xfmin, xfmax = min(xfs_g), max(xfs_g)
print("Range =", xfmax - xfmin)
for i in range(11):
    cl = i/10
    print(f"CL = {cl:0.2f} -> CI = {pdfset.uncertainty(xfs_g, 100*cl, True).errsymm:0.2f}")
print(f"  ... last interval should equal half-range = {(xfmax - xfmin)/2:0.2f}")
print()

e = pdfset.errorInfo
print(e)
print()

# pdf = lhapdf.mkPDF("CT10/0")
# print(pdf)
