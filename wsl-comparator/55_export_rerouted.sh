#!/usr/bin/env bash
# Task 8.7: lean4export closure of dirichletRealZeroBound_proof in the rerouted clone (/home/checker/math-rerouted),
# exactly as 41_main_closure_export.sh does for the unmodified clone. Reads existing .olean files; must not build.
# Pre-checks: clone state, PaperLemma3 hashes, .olean mtime vs the 2026-10-09 comparator run (09:07-09:32 EDT).
set -u
R=/home/checker/math-rerouted
echo "== pre-checks"
echo "HEAD: $(sudo -u checker git -C $R rev-parse HEAD)"
echo "git status --short:"; sudo -u checker git -C $R status --short
sha256sum $R/lean/OAI/NumberTheory/SiegelZeros/PaperLemma3/Lemma3.lean $R/lean/OAI/NumberTheory/SiegelZeros/PaperLemma3/Bridge.lean
O=$R/lean/.lake/build/lib/lean/OAI/NumberTheory/SiegelZeros/Characters/DirichletRealZeroBoundProof.olean
echo "olean mtime: $(stat -c '%y' $O)  ($O)"
echo "newest .olean under OAI/NumberTheory/SiegelZeros: $(find $R/lean/.lake/build/lib/lean/OAI/NumberTheory/SiegelZeros -name '*.olean' -printf '%TY-%Tm-%Td %TH:%TM:%TS %p\n' | sort | tail -1)"
echo "comparator run window (results/2026-10-09-lean-comparator-rerouted-nanoda.txt): 2026-10-09 09:07-09:32 EDT; now: $(date)"
echo
echo "== export (same command as 41_main_closure_export.sh, in the rerouted clone)"
M=/home/checker/l3k/.marker-55; sudo -u checker touch $M
sudo -u checker -H bash -lc '
set -u
export PATH="$HOME/.elan/bin:$PATH"; D=/home/checker/l3k; cd $HOME/math-rerouted/lean
LP="$(lake env printenv LEAN_PATH 2>/dev/null)"
P=OAI.SiegelZeros.WeightedTorusJets
t=dirichletRealZeroBound_proof
echo "command: LEAN_PATH=\"\$(lake env printenv LEAN_PATH)\" /usr/local/bin/lean4export OAI.NumberTheory.SiegelZeros.Main -- $P.$t > $D/closure-rerouted-$t.ndjson  (cwd $HOME/math-rerouted/lean)"
LEAN_PATH="$LP" /usr/local/bin/lean4export OAI.NumberTheory.SiegelZeros.Main -- $P.$t > $D/closure-rerouted-$t.ndjson; echo "lean4export exit $?"
'
F=/home/checker/l3k/closure-rerouted-dirichletRealZeroBound_proof.ndjson
echo "files under $R/lean/.lake/build changed during the export: $(find $R/lean/.lake/build -newer $M -type f | wc -l)"
echo "output: $F, $(stat -c %s $F) bytes, sha256 $(sha256sum $F | cut -c1-64)"
python3 -I /mnt/c/Users/Work/dev/siegel/wsl-comparator/54_export_name_counts.py $F
sync
