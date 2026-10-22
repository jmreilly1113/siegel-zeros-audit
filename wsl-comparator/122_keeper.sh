#!/usr/bin/env bash
# Extended replay keeper (2026-10-22). Every 60 s: if no supervisor (119b/119c) and no driver (114c) is running and none
# of DONE.txt, HALT.txt, runs/STOP.txt exists, start 119c. Inside WSL, so Claude Code's memory reaper cannot stop it.
# Exits once DONE.txt, HALT.txt or STOP.txt exists. One instance (flock). Run as root, detached.
# Usage: 122_keeper.sh <plan tsv> <out dir>
set -u
PLAN=$1; OUT=$2; W=/mnt/c/Users/Work/dev/siegel/wsl-comparator
exec 7>/home/checker/corpus/122.lock; flock -n 7 || exit 0
log() { echo "$(date '+%F %T') $*" >> $OUT/run.log; }
log "122: keeper start"
while true; do
  [ -f $OUT/DONE.txt ] && { log "122: DONE; keeper ends"; exit 0; }
  [ -f $OUT/HALT.txt ] && { log "122: HALT.txt present; keeper ends"; exit 0; }
  [ -f $OUT/runs/STOP.txt ] && { log "122: STOP.txt present; keeper ends"; exit 0; }
  if ! pgrep -f '119b_supervise_overlap.sh|119c_supervise_selfheal.sh|114c_extended_replay_overlap.sh' >/dev/null; then
    log "122: no supervisor or driver running; starting 119c"
    setsid nohup bash $W/119c_supervise_selfheal.sh $PLAN $OUT >> /home/checker/corpus/xr-119c.out 2>&1 < /dev/null 7>&- &
  fi
  sleep 60
done
