#!/usr/bin/env bash
# Plan step 3d: install our two modules into the fresh clone and make the one-term swap.
# New files: lean/OAI/NumberTheory/SiegelZeros/PaperLemma3/{Lemma3,Bridge}.lean (from lean-checks/comparator-copy/).
# Existing file changed: Characters/CharacterGlobalGreedyDeterminantMasterBounds.lean, one import line added and the
# single reference to OAI's Corollary 4 (line 138) replaced by our theorem. Nothing else.
set -eu
R=/home/checker/math-rerouted
L=$R/lean/OAI/NumberTheory/SiegelZeros
SRC=/mnt/c/Users/Work/dev/siegel/lean-checks/comparator-copy/PaperLemma3
[ -d $L/PaperLemma3 ] && { echo "PaperLemma3 already present; stopping"; exit 1; }
install -d -o checker -g checker $L/PaperLemma3
for f in Lemma3 Bridge; do install -o checker -g checker -m 644 $SRC/$f.lean $L/PaperLemma3/$f.lean; done
F=$L/Characters/CharacterGlobalGreedyDeterminantMasterBounds.lean
sudo -u checker python3 -I - "$F" <<'PY'
import sys
p = sys.argv[1]
lines = open(p, encoding='utf-8').read().split('\n')
imp_old = 'import OAI.NumberTheory.SiegelZeros.Structure.InvariantJetLinearMap'
assert lines[5] == imp_old, lines[5]
old = '  have hspan := actual_biquadratic_rectangle_span a\' b\' v hv σ τ'
new = '  have hspan := Lemma3.actual_biquadratic_rectangle_span_via_lemma3 a\' b\' v hv σ τ'
assert lines[137] == old, lines[137]
assert sum('actual_biquadratic_rectangle_span' in l for l in lines) == 1
lines[137] = new
lines.insert(6, 'import OAI.NumberTheory.SiegelZeros.PaperLemma3.Bridge')
open(p, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
print('edited', p)
PY
cd $R
echo "HEAD: $(sudo -u checker git rev-parse HEAD)"
echo "== git status --short"; sudo -u checker git status --short
echo "== new files (untracked), sha256"; sha256sum $L/PaperLemma3/*.lean | sed "s#$R/##"
echo "== git diff --stat"; sudo -u checker git diff --stat
echo "== git diff --numstat"; sudo -u checker git diff --numstat
echo "== git diff"; sudo -u checker git diff
N=$(sudo -u checker git diff --numstat | awk '{a+=$1; d+=$2; n++} END {print n" "a" "d}')
echo "== check: files changed, lines added, lines removed = $N (expected: 1 2 1)"
[ "$N" = "1 2 1" ] && echo "DIFF CHECK PASSED" || echo "DIFF CHECK FAILED"
sync
