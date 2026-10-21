#!/usr/bin/env bash
# Extended replay, Phase 5: per-kernel timing sample. For each listed config: prebuild (75_sbx.sh, as 93), then 3 rounds
# of one nanoda-off run and one nanoda-on run of 67_corpus_run.sh, order alternating (round 1 off,on; round 2 on,off;
# round 3 off,on), each with 111_memsample.py; then prune (112_prune.py with the replay's keep list). nanoda off/on =
# copies of the shipped config with "enable_nanoda": false / true (a config without the key runs with nanoda off, so the
# false copy has the same semantics as the shipped file). Sandbox, timeout (7200 s) and guard as the replay.
# Resumable: a run whose log has a COMPARATOR EXIT CODE line is skipped. Run as root, detached.
# Usage: 117_timing.sh <config list file (one name per line)> <out dir> <keep-configs file>
set -u
LIST=$1; OUT=$2; KEEP=$3
W=/mnt/c/Users/Work/dev/siegel/wsl-comparator; L=/home/checker/math/lean; X=/home/checker/corpus/xr
mkdir -p $OUT $X/configs; chown -R checker:checker $X
log() { echo "$(date '+%F %T') $*" >> $OUT/run.log; }
stopped() { [ -f /home/checker/corpus/GUARD_STOPPED ]; }
rm -f /home/checker/corpus/GUARD_STOPPED
nohup bash $W/69_corpus_guard.sh 85 1500 2 >/dev/null 2>&1 &
GD=$!
log "start 117_timing.sh; clone HEAD $(sudo -u checker git -C /home/checker/math rev-parse HEAD) status [$(sudo -u checker git -C /home/checker/math status --short | tr '\n' ' ')]; kernel $(uname -r)"
for N in $(grep -v '^#' $LIST); do
  stopped && break
  for V in off on; do
    python3 -I -c "import json,sys; c=json.load(open(sys.argv[1])); c['enable_nanoda']=(sys.argv[3]=='on'); json.dump(c, open(sys.argv[2],'w'), indent=2)" $L/ComparatorChallenges/$N.json $X/configs/$N-timing-$V.json $V
  done
  chown checker:checker $X/configs/$N-timing-*.json
  TG=$(python3 -I -c "import json,sys; c=json.load(open(sys.argv[1])); print(' '.join([c['solution_module'], c['challenge_module']] + c.get('solution_imports', [])))" $L/ComparatorChallenges/$N.json)
  if ! grep -q 'SANDBOX EXIT CODE: 0' $OUT/$N.prebuild.log 2>/dev/null; then
    log "$N: prebuild"
    { echo "== prebuild: lake build $TG with LEAN_NUM_THREADS=4 (117)  $(date '+%F %T')"; T0=$(date +%s)
      bash $W/75_sbx.sh 14400 4 "lake build $TG" </dev/null
      echo "PREBUILD_SECONDS: $(( $(date +%s) - T0 ))"; } 2>&1 | cat > $OUT/$N.prebuild.log
  fi
  grep -q 'SANDBOX EXIT CODE: 0' $OUT/$N.prebuild.log || { log "$N: prebuild failed; skipped"; continue; }
  for r in 1 2 3; do
    if [ $r -eq 2 ]; then ORDER="on off"; else ORDER="off on"; fi
    for V in $ORDER; do
      stopped && break 3
      F=$OUT/$N-$V-r$r.log
      grep -q 'COMPARATOR EXIT CODE' $F 2>/dev/null && continue
      [ -f $F ] && mv $F ${F%.log}.stopped-$(date +%Y%m%d%H%M%S).log
      python3 -I $W/111_memsample.py $X/configs/$N-timing-$V.json $OUT/$N-$V-r$r.mem.json & SP=$!
      bash $W/67_corpus_run.sh $N-$V-r$r $X/configs/$N-timing-$V.json 7200 $F </dev/null
      wait $SP
      log "$N $V r$r: $(grep -h -E 'kernel accepts|Your solution|COMPARATOR EXIT CODE|DURATION' $F | tr '\n' ';')"
    done
  done
  python3 -I $W/112_prune.py $L $KEEP --apply > $OUT/$N.prune.log 2>&1
  log "$N: pruned: $(head -1 $OUT/$N.prune.log)"
done
kill $GD 2>/dev/null
if stopped; then echo "GUARD STOPPED $(date '+%F %T')" > $OUT/GUARD_STOPPED.txt; else echo "TIMING DONE $(date '+%F %T')" > $OUT/DONE.txt; fi
sync
