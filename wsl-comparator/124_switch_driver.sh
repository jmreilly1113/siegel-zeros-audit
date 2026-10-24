#!/usr/bin/env bash
# One-shot switch of the live extended replay from 114d to 114e (2026-10-24). A running bash script cannot be edited
# safely, so 114e needs a restart of 119c/114d. To lose little work, wait until every active config (active-run.txt,
# active-slow.txt) has only just started its current step (its latest run.log line < FRESH s old), then: stop the keeper,
# 119c, 114d and its jobs; install the prepared 119c (default driver 114e) and 122 (also matches 114e) with mv; start
# the keeper, which starts 119c -> 114e. 114e moves the killed steps' partial files aside and redoes those steps.
# Gives up (no action) after MAXWAIT s, or if HALT/DONE/STOP/GUARD_STOPPED appears. Run as root, detached.
# Usage: 124_switch_driver.sh <plan tsv> <out dir> <new 119c file> <new 122 file>   (DRY=1: evaluate once, act on nothing)
# 2026-10-24 (114e -> 114f): OLD = the running driver's file name (default 114d_extended_replay_lanes.sh); CHECK = the
# marker files whose configs must be fresh (default "run slow"; "run build" when the slow-lane jobs may be stopped).
set -u
PLAN=$1; OUT=$2; N119=$3; N122=$4; W=/mnt/c/Users/Work/dev/siegel/wsl-comparator; C=/home/checker/corpus
OLD=${OLD:-114d_extended_replay_lanes.sh}; CHECK=${CHECK:-run slow}; FRESH=${FRESH:-180}; MAXWAIT=${MAXWAIT:-14400}; DRY=${DRY:-0}
APP=/sys/fs/cgroup/unified/user.slice/user-1000.slice/user@1000.service/app.slice
log() { echo "$(date '+%F %T') $*" >> $OUT/run.log; }
age() { # age <config>: seconds since its latest run.log line
  local t; t=$(grep -E "^[0-9-]+ [0-9:]+ $1[: ]" $OUT/run.log | tail -1 | cut -c1-19)
  [ -n "$t" ] && echo $(( $(date +%s) - $(date -d "$t" +%s) )) || echo 999999; }
ready() { local n a ok=0; WHY=
  for n in $(for m in $CHECK; do cat $OUT/active-$m.txt; done 2>/dev/null); do a=$(age $n); WHY="$WHY $n:${a}s"; [ $a -lt $FRESH ] || ok=1; done
  return $ok; }
T0=$(date +%s)
while :; do
  for f in HALT.txt DONE.txt runs/STOP.txt GUARD_STOPPED.txt; do [ -f $OUT/$f ] && { log "124: $f present; switch to 114e not done"; exit 1; }; done
  if ready; then break; fi
  [ $DRY = 1 ] && { echo "not ready:$WHY"; exit 0; }
  [ $(( $(date +%s) - T0 )) -ge $MAXWAIT ] && { log "124: no moment with all active steps < $FRESH s old within $MAXWAIT s ($WHY); switch to 114e not done"; exit 1; }
  sleep 5
done
[ $DRY = 1 ] && { echo "ready:$WHY"; exit 0; }
log "124: switching $OLD -> the 119c default driver (checked: $CHECK; active steps:${WHY:- none}; their partial files are moved aside and the steps redone by 114e)"
KP=$(pgrep -f '122_keeper.sh' | tr '\n' ' ')
for p in $KP; do pkill -P $p; kill $p; done 2>/dev/null
for p in $(pgrep -f 119c_supervise_selfheal.sh); do pkill -P $p; kill $p; done 2>/dev/null; pkill -f $OLD
pkill -f '67_corpus_run.sh|111_memsample.py|75_sbx.sh|113_nanoda_direct.sh'
for d in $APP/run-*.service; do [ -d $d ] && echo 1 > $d/cgroup.kill; done 2>/dev/null
pkill -f 69c_lane_guard.py
for i in $(seq 1 30); do pgrep -u checker -f 'comparator|lake|lean' >/dev/null || break; sleep 2; done
pkill -KILL -u checker -f 'comparator|lake|lean'
mv $N119 $W/119c_supervise_selfheal.sh; mv $N122 $W/122_keeper.sh
log "124: stopped (left: $(pgrep -f "$OLD|119c_|122_|69c_" | wc -l) pipeline, $(pgrep -u checker | wc -l) checker processes); new 119c and 122 installed; starting the keeper"
setsid nohup bash $W/122_keeper.sh $PLAN $OUT >> $C/xr-122.out 2>&1 < /dev/null &
