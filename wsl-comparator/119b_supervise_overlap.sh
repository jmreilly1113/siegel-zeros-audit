#!/usr/bin/env bash
# Extended replay supervisor for 114c (2026-10-21). After a guard stop, restarts 114c (at most 15 times) when the stop
# was a MEMORY stop; otherwise (disk limit, C: free < 20 GB, STOP.txt, DONE.txt) it does not restart.
# Source of the stop: the WSL guard (69) if guard.log's last LIMIT line is within 180 s of the stop marker; otherwise the
# Windows-side monitor (78: Windows free RAM < 3000 MB or C: free < 15 GB; C: free is checked here).
# Attribution uses 114c's markers: active-run.txt (comparator/queries) and active-build.txt (prebuild):
#   both set  -> the run's config goes to serial-once.txt (redone with no concurrent build); nothing deferred
#   run only  -> the run's config is deferred (deferred.txt), as with 119
#   build only-> the build's config is deferred
# Run as root, detached. Usage: 119b_supervise_overlap.sh <plan tsv> <out dir>
set -u
PLAN=$1; OUT=$2; W=/mnt/c/Users/Work/dev/siegel/wsl-comparator; G=/home/checker/corpus/guard.log; M=/home/checker/corpus/GUARD_STOPPED
log() { echo "$(date '+%F %T') $*" >> $OUT/run.log; }
k=$(ls $OUT/GUARD_STOPPED-*.txt 2>/dev/null | wc -l)
for attempt in $(seq 1 16); do
  log "119b: start 114c (attempt $attempt; deferred: $(tr '\n' ' ' < $OUT/deferred.txt 2>/dev/null); serial-once: $(tr '\n' ' ' < $OUT/serial-once.txt 2>/dev/null))"
  bash $W/114c_extended_replay_overlap.sh $PLAN $OUT
  [ -f $OUT/DONE.txt ] && { log "119b: DONE"; exit 0; }
  [ -f $OUT/runs/STOP.txt ] && { log "119b: STOP.txt present; not restarting"; exit 0; }
  [ -f $OUT/GUARD_STOPPED.txt ] || { log "119b: 114c ended without DONE, STOP or guard stop; not restarting"; exit 0; }
  RUNC=$(cat $OUT/active-run.txt 2>/dev/null); BLDC=$(cat $OUT/active-build.txt 2>/dev/null)
  ST=$(stat -c %Y $M 2>/dev/null || date +%s)
  LL=$(grep 'LIMIT:' $G | tail -1); LT=$(date -d "$(echo "$LL" | cut -c1-19)" +%s 2>/dev/null || echo 0)
  CF=$(df -BG --output=avail /mnt/c | tail -1 | tr -dc 0-9)
  if [ $((ST - LT)) -le 180 ] && [ $((ST - LT)) -ge -60 ]; then
    SRC="WSL guard: $LL"
    DISK=$(echo "$LL" | sed -n 's/.*disk \([0-9]*\)G.*/\1/p')
    [ "${DISK:-0}" -gt 85 ] && { log "119b: WSL guard disk-limit stop ($LL); not restarting"; exit 0; }
  else
    SRC="Windows-side monitor (78; no WSL guard LIMIT line within 180 s; C: free ${CF} GB)"
    [ "${CF:-0}" -lt 20 ] && { log "119b: stop with C: free ${CF} GB; not restarting"; exit 0; }
  fi
  [ $attempt -ge 16 ] && { log "119b: 15 restarts reached; not restarting"; exit 0; }
  if [ -n "$RUNC" ] && [ -n "$BLDC" ]; then echo "$RUNC" >> $OUT/serial-once.txt; ACT="run $RUNC and build $BLDC were both active: $RUNC goes to serial-once.txt (redone without a concurrent build); nothing deferred"
  elif [ -n "$RUNC" ]; then echo "$RUNC" >> $OUT/deferred.txt; ACT="only run $RUNC active: deferred"
  elif [ -n "$BLDC" ]; then echo "$BLDC" >> $OUT/deferred.txt; ACT="only build $BLDC active: deferred"
  else log "119b: memory stop with no active run or build ($SRC); not restarting"; exit 0; fi
  k=$((k+1)); mv $OUT/GUARD_STOPPED.txt $OUT/GUARD_STOPPED-$k.txt
  log "119b: memory stop, source $SRC; $ACT; record GUARD_STOPPED-$k.txt; restarting in 60 s"
  sleep 60
done
