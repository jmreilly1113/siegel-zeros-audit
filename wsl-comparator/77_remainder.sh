#!/usr/bin/env bash
# Remainder replay at openai/math fd4aeeb, on C:, batch by batch with pruning (Joe 2026-10-11: run the plan without
# waiting for approval). Run as root, detached (setsid nohup). Resumable: a config with <name>.done is skipped, a batch
# with BATCH_DONE is skipped, and pruning after a batch runs only once (prune.log present).
# Usage: 77_remainder.sh <schedule json (from 74_prune_schedule.py)> <results dir> <sample.txt from the headline batch>
# Run policy per config: same as 75_headline_batch.sh (prebuild with LEAN_NUM_THREADS=4 in the network-blocking wrapper,
# nanoda run, shipped-config run if in the seeded sample or if the nanoda run is not ACCEPT_BOTH). No fixes.
set -u
SCHED=$1; OUT=$2; SAMPLE=$3
W=/mnt/c/Users/Work/dev/siegel/wsl-comparator
L=/home/checker/math/lean; C=/home/checker/corpus/configs
CORE=/home/checker/.elan/toolchains/leanprover--lean4---v4.34.1/src/lean
mkdir -p $OUT
rm -f /home/checker/corpus/GUARD_STOPPED
nohup bash $W/69_corpus_guard.sh 60 1500 2 >/dev/null 2>&1 &
GD=$!
stopped() { [ -f /home/checker/corpus/GUARD_STOPPED ]; }
log() { echo "$(date '+%F %T') $*" >> $OUT/run.log; }
log "start; clone HEAD $(sudo -u checker git -C /home/checker/math rev-parse HEAD); status [$(sudo -u checker git -C /home/checker/math status --short | tr '\n' ' ')]; disk used $(df -BG --output=used / | tail -1 | tr -d ' ')"
log "guard: 69_corpus_guard.sh 60 1500 2"
# keep list: pilot configs plus every headline config whose outcome is not ACCEPT_BOTH
if [ ! -f $OUT/keep-configs.txt ]; then
  { echo "# configs whose builds are never pruned"
    python3 -c "import json; print('\n'.join(json.load(open('$SCHED'))['kept_configs']))"
    awk -F'\t' 'NR>1 && $6!="ACCEPT_BOTH" {print "ComparatorChallenges/" $1 ".json"}' /mnt/c/Users/Work/dev/siegel/results/2026-10-11-corpus-headline/outcomes.tsv
  } > $OUT/keep-configs.txt
fi
if [ ! -f $OUT/prune-after-headline.log ] && ! stopped; then
  python3 -I $W/76_prune.py $L $CORE $SCHED 0 $OUT/keep-configs.txt --apply > $OUT/prune-after-headline.log 2>&1
  log "pruned after headline: $(head -1 $OUT/prune-after-headline.log); disk used $(df -BG --output=used / | tail -1 | tr -d ' ')"
fi
NB=$(python3 -c "import json; print(len(json.load(open('$SCHED'))['batches']))")
prebuild() { # prebuild <dir> <name> <targets> <timeout>
  { echo "== prebuild $2: lake build $3 with LEAN_NUM_THREADS=4  $(date '+%F %T')"; T0=$(date +%s)
    bash $W/75_sbx.sh $4 4 "lake build $3" </dev/null
    echo "PREBUILD_SECONDS: $(( $(date +%s) - T0 ))"; echo "disk used: $(df -BG --output=used / | tail -1 | tr -d ' ')"
  } 2>&1 | cat > $1/$2.prebuild.log
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
  while IFS=$'\t' read -r N TG INS <&3; do
    stopped && break
    [ -f $B/$N.done ] && continue
    for f in $B/$N.prebuild.log $B/$N-nanoda.log $B/$N-shipped.log; do  # partial logs of a stopped run are kept, not overwritten
      [ -f $f ] && mv $f ${f%.log}.stopped-$(date +%Y%m%d%H%M%S).log
    done
    log "$N: prebuild"
    prebuild $B $N "$TG" 14400
    stopped && break
    if grep -q 'SANDBOX EXIT CODE: 12[4-9]\|SANDBOX EXIT CODE: 137' $B/$N.prebuild.log; then
      log "$N: prebuild timed out; comparator runs skipped"; touch $B/$N.done; continue
    fi
    log "$N: nanoda run"
    bash $W/67_corpus_run.sh $N $C/$N-nanoda.json 7200 $B/$N-nanoda.log </dev/null
    stopped && break
    ok=no; grep -q 'nanoda kernel accepts the solution' $B/$N-nanoda.log && grep -q 'Lean default kernel accepts the solution' $B/$N-nanoda.log \
      && grep -q 'Your solution is okay!' $B/$N-nanoda.log && grep -q 'COMPARATOR EXIT CODE: 0' $B/$N-nanoda.log && ok=yes
    if [ $ok = no ] || [ "$INS" = True ]; then
      log "$N: shipped-config run (nanoda ACCEPT_BOTH: $ok; in sample: $INS)"
      bash $W/67_corpus_run.sh $N $L/ComparatorChallenges/$N.json 7200 $B/$N-shipped.log </dev/null
      stopped && break
    fi
    touch $B/$N.done
  done 3< <(tail -n +2 $B/plan.tsv)
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
