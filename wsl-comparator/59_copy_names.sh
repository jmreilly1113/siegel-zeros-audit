#!/usr/bin/env bash
# Task 8.7: copy the name lists (56_closure_names.py output) into results/, and write the PNT patch name list.
set -eu
O=/mnt/c/Users/Work/dev/siegel/results/2026-10-09-closure-names
mkdir -p $O
cp /home/checker/l3k/names/*.txt.gz $O/
python3 -I /mnt/c/Users/Work/dev/siegel/wsl-comparator/58_pnt_declared_names.py /home/checker/math/lean/.lake/packages/PrimeNumberTheoremAnd $O/pnt-patch-declared-names.txt.gz
cd $O; sha256sum *.txt.gz
