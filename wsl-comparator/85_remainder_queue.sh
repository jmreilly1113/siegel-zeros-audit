#!/usr/bin/env bash
# Remainder replay with a prebuild queue (Joe 2026-10-13, option 3: finish as early as possible after 15:00 is missed).
# Same run policy and outputs as 77/83. Differences from 83: within a batch, a background worker builds every pending
# config in order, one lake build at a time with LEAN_NUM_THREADS=10, without waiting for comparator runs; the main loop
# runs config j's comparator runs as soon as config j's prebuild has finished. Only one lake build runs at a time, so
# no two builds can write the same module. Comparator run j only reads config j's closure, which is fully built before
# it starts; later prebuilds write only modules not yet built, hence outside it (Lake has no build lock:
# Lake/Util/Lock.lean). The prune runs after the worker and every run of the batch have finished.
# Run as root, detached. Resumable like 77/83. Usage: 85_remainder_queue.sh <schedule json> <results dir> <sample.txt>
set -u
SCHED=$1; OUT=$2; SAMPLE=$3; THREADS=10
W=/mnt/c/Users/Work/dev/siegel/wsl-comparator
L=/home/checker/math/lean; C=/home/checker/corpus/configs
CORE=/home/checker/.elan/toolchains/leanprover--lean4---v4.34.1/src/lean
mkdir -p $OUT
rm -f /home/checker/corpus/GUARD_STOPPED
nohup bash $W/69_corpus_guard.sh 65 1500 2 >/dev/null 2>&1 &
GD=$!
stopped() { [ -f /home/checker/corpus/GUARD_STOPPED ]; }
log() { echo "$(date '+%F %T') $*" >> $OUT/run.log; }
log "start (85_remainder_queue.sh, schedule $(basename $SCHED), prebuild queue with LEAN_NUM_THREADS=$THREADS); clone HEAD $(sudo -u checker git -C /home/checker/math rev-parse HEAD); status [$(sudo -u checker git -C /home/checker/math status --short | tr '\n' ' ')]; disk used $(df -BG --output=used / | tail -1 | tr -d ' ')"
log "guard: 69_corpus_guard.sh 65 1500 2"
[ -f $OUT/keep-configs.txt ] || { echo "no keep-configs.txt; run 77_remainder.sh first"; exit 1; }
NB=$(python3 -c "import json; print(len(json.load(open('$SCHED'))['batches']))")
prebuild() { # prebuild <dir> <name> <targets> <timeout>
  { echo "== prebuild $2: lake build $3 with LEAN_NUM_THREADS=$THREADS (prebuild queue, 85)  $(date '+%F %T')"; T0=$(date +%s)
    bash $W/75_sbx.sh $4 $THREADS "lake build $3" </dev/null
    echo "PREBUILD_SECONDS: $(( $(date +%s) - T0 ))"; echo "disk used: $(df -BG --output=used / | tail -1 | tr -d ' ')"
  } 2>&1 | cat > $1/$2.prebuild.log
}
aside() { # partial logs of a stopped run are kept, not overwritten
  for f in $1/$2.prebuild.log $1/$2-nanoda.log $1/$2-shipped.log; do
    [ -f $f ] && mv $f ${f%.log}.stopped-$(date +%Y%m%d%H%M%S).log
  done
}
for k in $(seq 1 $NB); do
  stopped && break
  B=$OUT/batch-$(printf %02d $k)
  [ -f $B/BATCH_DONE ] && continue
  mkdir -p $B
  if [ ! -f $B/plan.tsv ]; then
    python3 -I - "$SCHED" "$k" "$L" "$C" "$SAMPLE" > $B/plan.tsv <<'EOF'
import json, os, sys
sched, k, L, C, sample = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5]
samp = {l.split('\t')[0] for l in open(sample) if not l.startswith('#')}
print('config\tprebuild_targets\tin_sample')
for r in json.load(open(sched))['batches'][k - 1]:
    n = r.split('/')[-1][:-5]
    c = json.load(open(os.path.join(L, r), encoding='utf-8'))
    c2 = dict(c); c2['enable_nanoda'] = True
    json.dump(c2, open(os.path.join(C, n + '-nanoda.json'), 'w'), indent=2)
    print(f'{n}\t{" ".join([c["solution_module"], c["challenge_module"]] + c.get("solution_imports", []))}\t{r in samp}')
EOF
    chown checker:checker $C/*-nanoda.json
  fi
  log "batch $k of $NB: $(($(wc -l < $B/plan.tsv) - 1)) configs"
  NS=(); TS=(); IS=()
  while IFS=$'\t' read -r N TG INS; do
    [ -f $B/$N.done ] && continue
    NS+=("$N"); TS+=("$TG"); IS+=("$INS")
  done < <(tail -n +2 $B/plan.tsv)
  m=${#NS[@]}
  MK=/home/checker/corpus/pb-done/batch-$(printf %02d $k); rm -rf $MK; mkdir -p $MK
  ( for ((i=0; i<m; i++)); do
      stopped && break
      aside $B ${NS[$i]}; log "${NS[$i]}: prebuild (queue)"; prebuild $B ${NS[$i]} "${TS[$i]}" 14400; touch $MK/${NS[$i]}
    done ) &
  WPID=$!
  for ((j=0; j<m; j++)); do
    stopped && break
    N=${NS[$j]}; INS=${IS[$j]}
    while [ ! -f $MK/$N ] && kill -0 $WPID 2>/dev/null; do sleep 5; done
    [ -f $MK/$N ] || break
    if grep -q 'SANDBOX EXIT CODE: 12[4-9]\|SANDBOX EXIT CODE: 137' $B/$N.prebuild.log; then
      log "$N: prebuild timed out; comparator runs skipped"; touch $B/$N.done
    elif ! grep -q 'SANDBOX EXIT CODE' $B/$N.prebuild.log; then
      log "$N: prebuild log has no exit code (stopped); not run"
    else
      log "$N: nanoda run"
      bash $W/67_corpus_run.sh $N $C/$N-nanoda.json 7200 $B/$N-nanoda.log </dev/null
      if ! stopped; then
        ok=no; grep -q 'nanoda kernel accepts the solution' $B/$N-nanoda.log && grep -q 'Lean default kernel accepts the solution' $B/$N-nanoda.log           && grep -q 'Your solution is okay!' $B/$N-nanoda.log && grep -q 'COMPARATOR EXIT CODE: 0' $B/$N-nanoda.log && ok=yes
        if [ $ok = no ] || [ "$INS" = True ]; then
          log "$N: shipped-config run (nanoda ACCEPT_BOTH: $ok; in sample: $INS)"
          bash $W/67_corpus_run.sh $N $L/ComparatorChallenges/$N.json 7200 $B/$N-shipped.log </dev/null
        fi
        stopped || touch $B/$N.done
      fi
    fi
  done
  wait $WPID
  # a config whose comparator run was not reached (worker or main loop stopped) has no .done and is redone on resume
  for N in "${NS[@]}"; do [ -f $B/$N.done ] || { stopped || log "$N: not done at batch end (not classified as a result)"; }; done
  stopped && break
  python3 -I $W/75_classify.py $B > $B/outcomes.tsv 2>> $OUT/run.log
  awk -F'\t' 'NR>1 && $6!="ACCEPT_BOTH" {print "ComparatorChallenges/" $1 ".json"}' $B/outcomes.tsv >> $OUT/keep-configs.txt
  log "batch $k outcomes: $(awk -F'\t' 'NR>1 {print $6}' $B/outcomes.tsv | sort | uniq -c | tr '\n' ' ')"
  python3 -I $W/76_prune.py $L $CORE $SCHED $k $OUT/keep-configs.txt --apply > $B/prune.log 2>&1
  log "batch $k pruned: $(head -1 $B/prune.log); disk used $(df -BG --output=used / | tail -1 | tr -d ' ')"
  touch $B/BATCH_DONE
done
kill $GD 2>/dev/null
log "end; clone status [$(sudo -u checker git -C /home/checker/math status --short | tr '\n' ' ')]; disk used $(df -BG --output=used / | tail -1 | tr -d ' ')"
if stopped; then echo "GUARD STOPPED $(date '+%F %T')" > $OUT/GUARD_STOPPED.txt; else echo "REMAINDER DONE $(date '+%F %T')" > $OUT/DONE.txt; fi
sync
