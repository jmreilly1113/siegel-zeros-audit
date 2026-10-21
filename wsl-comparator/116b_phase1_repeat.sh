#!/usr/bin/env bash
# Extended replay, Phase 1 repeat (2026-10-21): the first test gave 29 s plain vs 40 s instrumented on
# TalagrandDiscreteConvexity. Rebuild, then alternate: plain, instr (hash + copy), plain, instr-hashonly, plain, instr,
# instr-hashonly, to separate the export copy's cost from run-to-run variation. Same config, wrapper and guard as 116.
# Run as root, detached. Usage: 116b_phase1_repeat.sh <out dir>
set -u
OUT=$1; W=/mnt/c/Users/Work/dev/siegel/wsl-comparator; L=/home/checker/math/lean; X=/home/checker/corpus/xr
N=TalagrandDiscreteConvexity; CFG=/home/checker/corpus/configs/$N-nanoda.json
mkdir -p $OUT; log() { echo "$(date '+%F %T') $*" >> $OUT/run.log; }
rm -f /home/checker/corpus/GUARD_STOPPED
nohup bash $W/69_corpus_guard.sh 85 1500 2 >/dev/null 2>&1 & GD=$!
TG=$(python3 -I -c "import json,sys; c=json.load(open(sys.argv[1])); print(' '.join([c['solution_module'], c['challenge_module']] + c.get('solution_imports', [])))" $CFG)
{ bash $W/75_sbx.sh 14400 4 "lake build $TG" </dev/null; } > $OUT/$N.prebuild.log 2>&1
log "prebuild: $(grep -h 'SANDBOX EXIT CODE' $OUT/$N.prebuild.log)"
k=0
for V in plain instr plain hashonly plain instr hashonly; do
  k=$((k+1)); F=$OUT/$N-$k-$V.log
  case $V in
    plain) bash $W/67_corpus_run.sh $N $CFG 7200 $F </dev/null ;;
    instr) python3 -I $W/111_memsample.py $CFG $OUT/$N-$k-$V.mem.json $X/exp/$N.export & SP=$!; bash $W/67_corpus_run.sh $N $CFG 7200 $F </dev/null; wait $SP ;;
    hashonly) python3 -I $W/111_memsample.py $CFG $OUT/$N-$k-$V.mem.json & SP=$!; bash $W/67_corpus_run.sh $N $CFG 7200 $F </dev/null; wait $SP ;;
  esac
  log "$k $V: $(grep -h -E 'Your solution|COMPARATOR EXIT CODE|DURATION' $F | tr '\n' ';')"
done
rm -f $X/exp/$N.export $X/exp/$N.export.nanoda-config.json
python3 -I $W/112_prune.py $L $OUT/../phase1/empty-keep.txt --apply > $OUT/$N.prune.log 2>&1
log "pruned: $(cat $OUT/$N.prune.log)"
kill $GD 2>/dev/null; echo "DONE $(date '+%F %T')" > $OUT/DONE.txt; sync
