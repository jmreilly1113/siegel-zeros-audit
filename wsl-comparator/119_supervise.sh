#!/usr/bin/env bash
# Extended replay supervisor (2026-10-21). Runs 114b_extended_replay_shared.sh on <plan>; if it ends because the WSL
# guard stopped it for MEMORY (last LIMIT line in guard.log has MemAvailable below the floor while disk is under its
# limit), the config that was in progress is appended to <out>/deferred.txt (not a result; decided later), the stop
# record is kept as GUARD_STOPPED-<k>.txt, and 114b is restarted after 60 s. It does NOT restart after a disk-limit stop,
# a STOP.txt (conditions a, b, d), DONE.txt, or more than 15 memory restarts. Run as root, detached.
# Usage: 119_supervise.sh <plan tsv> <out dir>
set -u
PLAN=$1; OUT=$2; W=/mnt/c/Users/Work/dev/siegel/wsl-comparator; G=/home/checker/corpus/guard.log
log() { echo "$(date '+%F %T') $*" >> $OUT/run.log; }
k=$(ls $OUT/GUARD_STOPPED-*.txt 2>/dev/null | wc -l)
for attempt in $(seq 1 16); do
  log "119: start 114b (attempt $attempt; deferred so far: $(tr '\n' ' ' < $OUT/deferred.txt 2>/dev/null))"
  bash $W/114b_extended_replay_shared.sh $PLAN $OUT
  [ -f $OUT/DONE.txt ] && { log "119: DONE"; exit 0; }
  [ -f $OUT/runs/STOP.txt ] && { log "119: STOP.txt present; not restarting"; exit 0; }
  [ -f $OUT/GUARD_STOPPED.txt ] || { log "119: 114b ended without DONE, STOP or guard stop; not restarting"; exit 0; }
  L=$(grep 'LIMIT:' $G | tail -1)
  DISK=$(echo "$L" | sed -n 's/.*disk \([0-9]*\)G.*/\1/p'); MEM=$(echo "$L" | sed -n 's/.*MemAvailable \([0-9]*\)MB.*/\1/p')
  if [ -z "$MEM" ] || [ "$MEM" -ge 1500 ] || [ "${DISK:-999}" -gt 85 ]; then log "119: guard stop is not a memory stop ($L); not restarting"; exit 0; fi
  N=$(grep -E '^[0-9-]+ [0-9:]+ [A-Za-z0-9]+ \([0-9]+, group ' $OUT/run.log | tail -1 | awk '{print $3}')
  [ -f $OUT/runs/$N.result.json ] && { log "119: last config $N already has a result; memory stop not attributable; not restarting"; exit 0; }
  [ $attempt -ge 16 ] && { log "119: 15 memory restarts reached; not restarting"; exit 0; }
  k=$((k+1)); mv $OUT/GUARD_STOPPED.txt $OUT/GUARD_STOPPED-$k.txt
  echo "$N" >> $OUT/deferred.txt
  log "119: memory guard stop during $N ($L); $N deferred; record kept as GUARD_STOPPED-$k.txt; restarting in 60 s"
  sleep 60
done
