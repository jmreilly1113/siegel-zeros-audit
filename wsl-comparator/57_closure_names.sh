#!/usr/bin/env bash
# Task 8.7, step 4a (read-only): name lists and the #find_deps reproduction for each lean4export dump.
set -u
cd /home/checker/l3k
O=/home/checker/l3k/names; mkdir -p $O
echo "script sha256: $(sha256sum /mnt/c/Users/Work/dev/siegel/wsl-comparator/56_closure_names.py | cut -c1-64)"
for f in closure-exists_absolute_real_zero_gap.ndjson closure-dirichletRealZeroBound_proof.ndjson closure-rerouted-dirichletRealZeroBound_proof.ndjson export-main.ndjson export.ndjson; do echo "$f sha256 $(sha256sum $f | cut -c1-64)"; done
P=OAI.SiegelZeros.WeightedTorusJets
run() { /usr/bin/time -f "  (%e s, %M KB)" python3 -I /mnt/c/Users/Work/dev/siegel/wsl-comparator/56_closure_names.py "$@"; }
run closure-exists_absolute_real_zero_gap.ndjson $P.exists_absolute_real_zero_gap route1 $O
run closure-dirichletRealZeroBound_proof.ndjson $P.dirichletRealZeroBound_proof route2-original $O
run closure-rerouted-dirichletRealZeroBound_proof.ndjson $P.dirichletRealZeroBound_proof route2-rerouted $O
run export-main.ndjson challenge_dirichletRealZeroBound_proof mainrerouted-challenge $O
run export.ndjson Lemma3.actual_biquadratic_rectangle_span_via_lemma3 lemma3-bridge $O
ls -la $O
