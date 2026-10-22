#!/usr/bin/env bash
# Switch the running 114c to the slow-lane version (2026-10-22) at the next config boundary: wait for a new "outcome"
# line, then stop 114c and its children only (119c stays and restarts the new 114c after 60 s; the config whose run had
# just started is redone). Does nothing if STOP, HALT, a guard stop or DONE appears first. Run as root, detached.
# Usage: 120b_switch_slowlane.sh <out dir>
set -u
OUT=$1; log() { echo "$(date '+%F %T') $*" >> $OUT/run.log; }
n0=$(grep -c ': outcome ' $OUT/run.log)
log "120b: waiting for the next config boundary to switch 114c to the slow-lane version"
while [ "$(grep -c ': outcome ' $OUT/run.log)" -le "$n0" ]; do
  { [ -f $OUT/runs/STOP.txt ] || [ -f $OUT/HALT.txt ] || [ -f $OUT/GUARD_STOPPED.txt ] || [ -f $OUT/DONE.txt ]; } && { log "120b: STOP/HALT/guard/DONE first; no switch"; exit 0; }
  sleep 2
done
pkill -f 114c_extended_replay_overlap.sh; pkill -f 111_memsample.py
pkill -TERM -u checker -f 'comparator|lake|lean'; sleep 20; pkill -KILL -u checker -f 'comparator|lake|lean'; sync
log "120b: boundary reached ($(grep ': outcome ' $OUT/run.log | tail -1 | cut -c1-90)); 114c stopped; 119c restarts the slow-lane version"
