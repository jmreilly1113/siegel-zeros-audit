#!/usr/bin/env bash
# Switch the extended replay from 119/114b to 119b/114c at the next config boundary (Joe, 2026-10-21 ~20:00).
# Waits for a new "outcome" line in run.log, then stops 119 and 114b (and checker's build processes; the next config's
# prebuild has just started and is redone by 114c), then starts 119b on the same plan. Does nothing if a STOP, guard
# stop or DONE appears first. Run as root, detached. Usage: 120_switch_to_114c.sh <plan tsv> <out dir>
set -u
PLAN=$1; OUT=$2; W=/mnt/c/Users/Work/dev/siegel/wsl-comparator
log() { echo "$(date '+%F %T') $*" >> $OUT/run.log; }
n0=$(grep -c ': outcome ' $OUT/run.log)
log "120: waiting for the next config boundary to switch to 119b/114c (outcome lines now: $n0)"
while [ "$(grep -c ': outcome ' $OUT/run.log)" -le "$n0" ]; do
  [ -f $OUT/runs/STOP.txt ] || [ -f $OUT/GUARD_STOPPED.txt ] || [ -f $OUT/DONE.txt ] && { log "120: STOP/guard/DONE before the boundary; no switch"; exit 0; }
  pgrep -f 119_supervise.sh >/dev/null || { log "120: 119 not running; no switch"; exit 0; }
  sleep 2
done
pkill -f 119_supervise.sh; pkill -f 114b_extended_replay_shared.sh; pkill -f 69_corpus_guard.sh; pkill -f 111_memsample.py
pkill -TERM -u checker -f 'comparator|lake|lean'; sleep 20; pkill -KILL -u checker -f 'comparator|lake|lean'; sync
log "120: boundary reached ($(grep ': outcome ' $OUT/run.log | tail -1 | cut -c1-120)); 119/114b stopped; starting 119b/114c"
exec bash $W/119b_supervise_overlap.sh $PLAN $OUT
