#!/usr/bin/env bash
# Corpus checks, phase 4 pilot: SiegelZeros (known good), its two negative controls, QuasiRiemannHypothesis,
# EditApproximation; all with enable_nanoda true in config copies. Stops if SiegelZeros fails or a control is accepted.
set -u
W=/mnt/c/Users/Work/dev/siegel/wsl-comparator
OUT=/mnt/c/Users/Work/dev/siegel/results/2026-10-11-corpus-pilot
L=/home/checker/math/lean
C=/home/checker/corpus/configs
mkdir -p $OUT; install -d -o checker -g checker /home/checker/corpus $C
nohup bash $W/66_disk_watchdog.sh 42 >/dev/null 2>&1 &
WD=$!
mk() { # mk <shipped name> <out name> <python edit expression on dict d>
  sudo -u checker python3 -c "
import json; d=json.load(open('$L/ComparatorChallenges/$1.json')); $3
json.dump(d, open('$C/$2.json','w'), indent=2)"; }
mk SiegelZeros SiegelZeros-nanoda "d['enable_nanoda']=True"
mk SiegelZeros SiegelZeros-control-noChoice "d['enable_nanoda']=True; d['permitted_axioms']=[a for a in d['permitted_axioms'] if a!='Classical.choice']"
mk SiegelZeros SiegelZeros-control-altered "d['enable_nanoda']=True; d['challenge_module']='ComparatorChallenges.SiegelZerosAlteredControl'"
mk QuasiRiemannHypothesis QuasiRiemannHypothesis-nanoda "d['enable_nanoda']=True"
mk EditApproximation EditApproximation-nanoda "d['enable_nanoda']=True"
ok() { grep -q "Your solution is okay!" "$1"; }

bash $W/67_corpus_run.sh SiegelZeros $C/SiegelZeros-nanoda.json 7200 $OUT/SiegelZeros-nanoda.log
if ! ok $OUT/SiegelZeros-nanoda.log; then echo "STOP: SiegelZeros pilot did not reproduce the accept" | tee $OUT/STOP.txt; kill $WD; exit 1; fi

bash $W/67_corpus_run.sh SiegelZeros-control-noChoice $C/SiegelZeros-control-noChoice.json 7200 $OUT/SiegelZeros-control-noChoice.log
if ok $OUT/SiegelZeros-control-noChoice.log; then echo "STOP: control (a) accepted" | tee $OUT/STOP.txt; kill $WD; exit 1; fi

# control (b): a copied challenge file with one hypothesis changed, added as a NEW untracked file (no upstream file edited)
A=$L/ComparatorChallenges/SiegelZerosAlteredControl.lean
sudo -u checker python3 -c "
s=open('$L/ComparatorChallenges/SiegelZeros.lean',encoding='utf-8').read()
old='3 ≤ q →'; assert s.count(old)==2
open('$A','w',encoding='utf-8').write(s.replace(old,'2 ≤ q →',1))"
{ echo "== control (b) challenge copy: diff SiegelZeros.lean SiegelZerosAlteredControl.lean"; diff $L/ComparatorChallenges/SiegelZeros.lean $A; } > $OUT/SiegelZeros-control-altered.challenge-diff.txt
bash $W/67_corpus_run.sh SiegelZeros-control-altered $C/SiegelZeros-control-altered.json 7200 $OUT/SiegelZeros-control-altered.log
rm -f $A; rm -f $L/.lake/build/lib/lean/ComparatorChallenges/SiegelZerosAlteredControl.* $L/.lake/build/ir/ComparatorChallenges/SiegelZerosAlteredControl.* 2>/dev/null
echo "clone status after removing the control file: '$(sudo -u checker git -C /home/checker/math status --short | tr '\n' ' ')'" >> $OUT/SiegelZeros-control-altered.challenge-diff.txt
if ok $OUT/SiegelZeros-control-altered.log; then echo "STOP: control (b) accepted" | tee $OUT/STOP.txt; kill $WD; exit 1; fi

bash $W/67_corpus_run.sh QuasiRiemannHypothesis $C/QuasiRiemannHypothesis-nanoda.json 43200 $OUT/QuasiRiemannHypothesis-nanoda.log
bash $W/67_corpus_run.sh EditApproximation $C/EditApproximation-nanoda.json 28800 $OUT/EditApproximation-nanoda.log
kill $WD 2>/dev/null
echo "PILOT DONE $(date '+%F %T')" > $OUT/DONE.txt
sync
