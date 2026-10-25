#!/usr/bin/env bash
# 131 (2026-10-25): one-shot restart of the live extended replay on a new plan file (130_smallfirst_plan.py output).
# 114f reads its plan once at start, so the new order needs a restart of 122/119c/114f. Stop sequence copied from
# 124_switch_driver.sh (used twice on 2026-10-24), without installing any script. To lose little work, wait until the
# slow lane is empty and the main-lane run (if any) has only just started its step (latest run.log line < FRESH s
# old); the build in progress is killed (lake keeps the modules it finished; 114f redoes the rest). 128b is stopped by
# its PID first and started again on the new plan after the keeper. Gives up (no action) after MAXWAIT s, or if
# HALT/DONE/STOP/GUARD_STOPPED appears. Run as root, detached.
# Usage: 131_switch_plan.sh <new plan tsv> <out dir>   (DRY=1: evaluate once, act on nothing)
set -u
PLAN=$1; OUT=$2; W=/mnt/c/Users/Work/dev/siegel/wsl-comparator; C=/home/checker/corpus
FRESH=${FRESH:-180}; MAXWAIT=${MAXWAIT:-10800}; DRY=${DRY:-0}
APP=/sys/fs/cgroup/unified/user.slice/user-1000.slice/user@1000.service/app.slice
log() { echo "$(date '+%F %T') $*" >> $OUT/run.log; }
age() { local t; t=$(grep -E "^[0-9-]+ [0-9:]+ $1[: ]" $OUT/run.log | tail -1 | cut -c1-19)
  [ -n "$t" ] && echo $(( $(date +%s) - $(date -d "$t" +%s) )) || echo 999999; }
ready() { local n a; WHY="slow [$(tr '\n' ' ' < $OUT/active-slow.txt 2>/dev/null)]"
  [ -s $OUT/active-slow.txt ] && return 1
  n=$(cat $OUT/active-run.txt 2>/dev/null); [ -z "$n" ] && { WHY="$WHY run none"; return 0; }
  a=$(age $n); WHY="$WHY run $n:${a}s"; [ $a -lt $FRESH ]; }
[ -f "$PLAN" ] || { echo "no plan $PLAN"; exit 1; }
T0=$(date +%s)
while :; do
  for f in HALT.txt DONE.txt runs/STOP.txt GUARD_STOPPED.txt; do [ -f $OUT/$f ] && { log "131: $f present; plan switch not done"; exit 1; }; done
  if ready; then break; fi
  [ $DRY = 1 ] && { echo "not ready: $WHY"; exit 0; }
  [ $(( $(date +%s) - T0 )) -ge $MAXWAIT ] && { log "131: no moment with the slow lane empty and a fresh run within $MAXWAIT s ($WHY); plan switch not done"; exit 1; }
  sleep 5
done
[ $DRY = 1 ] && { echo "ready: $WHY"; exit 0; }
log "131: switching the replay to plan $(basename $PLAN) ($WHY; build in progress: $(cat $OUT/active-build.txt 2>/dev/null); killed steps are redone)"
SB=$(pgrep -f 'bash /mnt/c/Users/Work/dev/siegel/wsl-comparator/128b_side_prebuild.sh' | tr '\n' ' '); [ -n "$SB" ] && kill $SB
KP=$(pgrep -f '122_keeper.sh' | tr '\n' ' ')
for p in $KP; do pkill -P $p; kill $p; done 2>/dev/null
for p in $(pgrep -f 119c_supervise_selfheal.sh); do pkill -P $p; kill $p; done 2>/dev/null; pkill -f 114f_extended_replay_reruns_last.sh
pkill -f '67_corpus_run.sh|111_memsample.py|75_sbx.sh|113_nanoda_direct.sh'
for d in $APP/run-*.service; do [ -d $d ] && echo 1 > $d/cgroup.kill; done 2>/dev/null
pkill -f 69c_lane_guard.py
for i in $(seq 1 30); do pgrep -u checker -f 'comparator|lake|lean' >/dev/null || break; sleep 2; done
pkill -KILL -u checker -f 'comparator|lake|lean'
log "131: stopped (128b pids [$SB]; left: $(pgrep -f '114f_|119c_|122_|69c_|128b_' | wc -l) pipeline, $(pgrep -u checker | wc -l) checker processes); starting the keeper on $(basename $PLAN)"
setsid nohup bash $W/122_keeper.sh $PLAN $OUT >> $C/xr-122.out 2>&1 < /dev/null &
sleep 60
setsid nohup bash $W/128b_side_prebuild.sh $PLAN $OUT 3 >> $C/xr-128b.out 2>&1 < /dev/null &
log "131: 128b started on $(basename $PLAN)"
