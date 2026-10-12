#!/usr/bin/env bash
# Non-official diagnostic: rerun the three nanoda stack-overflow configs with the larger-stack nanoda copy. Run as root.
set -u
W=/mnt/c/Users/Work/dev/siegel/wsl-comparator; OUT=/mnt/c/Users/Work/dev/siegel/results/2026-10-12-nanoda-bigstack-diag
C=/home/checker/corpus/configs; mkdir -p $OUT
rm -f /home/checker/corpus/GUARD_STOPPED
nohup bash $W/69_corpus_guard.sh 60 1500 2 >/dev/null 2>&1 & GD=$!
for N in OptimalMaxCut UniqueGamesTheorem VertexCover; do
  [ -f /home/checker/corpus/GUARD_STOPPED ] && break
  bash $W/79_corpus_run_bigstack.sh $N $C/$N-nanoda.json 7200 $OUT/$N-bigstack.log </dev/null
done
kill $GD 2>/dev/null
[ -f /home/checker/corpus/GUARD_STOPPED ] && echo "GUARD STOPPED $(date '+%F %T')" > $OUT/GUARD_STOPPED.txt || echo "DIAG DONE $(date '+%F %T')" > $OUT/DONE.txt
