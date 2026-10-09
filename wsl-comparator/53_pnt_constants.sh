#!/usr/bin/env bash
# Task 2 supplement (read-only, exploratory heuristic): constants from the patched PNT SiegelZeros files in the
# existing lean4export dumps of 2026-10-08 (/home/checker/l3k; produced by 41_main_closure_export.sh,
# 39_main_rerouted.sh and 36_nanoda_lemma3.sh).
set -u
echo "script sha256: $(sha256sum /mnt/c/Users/Work/dev/siegel/wsl-comparator/52_pnt_constants_in_exports.py | cut -c1-64)"
cd /home/checker/l3k
python3 -I /mnt/c/Users/Work/dev/siegel/wsl-comparator/52_pnt_constants_in_exports.py /home/checker/math/lean/.lake/packages/PrimeNumberTheoremAnd \
  closure-dirichletRealZeroBound_proof.ndjson closure-exists_absolute_real_zero_gap.ndjson export-main.ndjson export.ndjson
