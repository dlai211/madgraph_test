check_PROGRAMS = testalphas testgrid testindex testinfo testpaths testperf testsetperf testnsetperf

dist_check_SCRIPTS = testunc.py

AM_CPPFLAGS += -I$(top_srcdir)/include
AM_LDFLAGS += -L$(top_builddir)/src
LIBS = -lLHAPDF

if USING_MPI
  AM_CPPFLAGS += -DHAVE_MPI=1
endif

testalphas_SOURCES = testalphas.cc
testgrid_SOURCES = testgrid.cc
testindex_SOURCES = testindex.cc
testinfo_SOURCES = testinfo.cc
testpaths_SOURCES = testpaths.cc
testperf_SOURCES = testperf.cc
testsetperf_SOURCES = testsetperf.cc
testnsetperf_SOURCES = testnsetperf.cc

TESTS_ENVIRONMENT = mkdir -p SETS && \
  for p in CT10nlo MSTW2008nlo68cl NNPDF31_lo_as_0130; do \
    test -d SETS/$$p || (wget https://lhapdfsets.web.cern.ch/current/$$p.tar.gz -q -O- | tar xz -C SETS/); done && \
  LHAPDF_DATA_PATH=$$PWD/SETS/

TESTS = testalphas testgrid testindex testinfo testpaths testperf testsetperf testnsetperf testunc.py

installcheck-local: check
	$(bindir)/lhapdf install CT10nlo
	$(bindir)/lhapdf list
	./testalphas
	./testgrid
	./testindex

uninstall-local:
	rm -rf $(pkgdatadir)/CT10nlo

CLEANFILES = alphas_ct10nlo.dat alphas_ipol.dat pdf.dat alphas_ana.dat alphas_ode.dat
