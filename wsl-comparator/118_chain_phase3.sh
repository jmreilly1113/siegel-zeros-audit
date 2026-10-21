#!/usr/bin/env bash
# Extended replay: start Phase 3 (114b, shared builds, phase3-order.tsv) as soon as the Phase 2 pilot (114, max 5) ends
# cleanly (<out>/PART_DONE-5.txt). If the pilot ends with STOP.txt or a guard stop, Phase 3 is NOT started.
# Run as root, detached. Usage: 118_chain_phase3.sh <out dir>
set -u
OUT=$1; W=/mnt/c/Users/Work/dev/siegel/wsl-comparator
log() { echo "$(date '+%F %T') $*" >> $OUT/run.log; }
while true; do
  [ -f $OUT/runs/STOP.txt ] && { log "118: pilot ended with STOP.txt; Phase 3 not started"; exit 0; }
  [ -f $OUT/GUARD_STOPPED.txt ] || [ -f /home/checker/corpus/GUARD_STOPPED ] && { log "118: guard stop during the pilot; Phase 3 not started"; exit 0; }
  [ -f $OUT/PART_DONE-5.txt ] && break
  sleep 30
done
sleep 5
pgrep -f 114_extended_replay.sh >/dev/null && { log "118: 114 still running after PART_DONE-5; Phase 3 not started"; exit 0; }
log "118: pilot done; starting Phase 3 with 114b_extended_replay_shared.sh on phase3-order.tsv"
exec bash $W/114b_extended_replay_shared.sh $OUT/phase3-order.tsv $OUT
