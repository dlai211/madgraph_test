# convenience variables that must exist
prefix=C:/Users/laiji/test/madgraph_test/lhapdf-win
exec_prefix=${prefix}

export PATH="$exec_prefix/bin":$PATH
export PYTHONPATH=":$PYTHONPATH"
export LD_LIBRARY_PATH="${exec_prefix}/lib:$LD_LIBRARY_PATH"
export LHAPDF_DATA_PATH="$prefix/share/LHAPDF/"

