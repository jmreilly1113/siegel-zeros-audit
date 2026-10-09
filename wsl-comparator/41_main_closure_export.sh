#!/usr/bin/env bash
# Second method for "does OAI's main theorem use Corollary 4?": lean4export (independent of our Lean
# scan) writes the dependency closure of each theorem; we then look for names in the export.
# Control: the closure of actual_biquadratic_rectangle_span itself.
set -u
sudo -u checker -H bash -lc '
set -u
export PATH="$HOME/.elan/bin:$PATH"; D=/home/checker/l3k; cd $HOME/math/lean
LP="$(lake env printenv LEAN_PATH 2>/dev/null)"
P=OAI.SiegelZeros.WeightedTorusJets
for t in exists_absolute_real_zero_gap dirichletRealZeroBound_proof actual_biquadratic_rectangle_span; do
  LEAN_PATH="$LP" /usr/local/bin/lean4export OAI.NumberTheory.SiegelZeros.Main -- $P.$t > $D/closure-$t.ndjson; echo "$t: lean4export exit $?, $(stat -c %s $D/closure-$t.ndjson) bytes"
  python3 /mnt/c/Users/Work/dev/siegel/wsl-comparator/42_export_names.py $D/closure-$t.ndjson actual_biquadratic_rectangle_span uniform_rectangular_multiplicity source_rectangle_span_of_polynomial_zero_test
done
'
