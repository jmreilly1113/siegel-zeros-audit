#!/usr/bin/env bash
# Extended replay supervisor 119c (2026-10-22, Joe: "don't lose big chunks of time again"). Replaces 119b's policy:
# it restarts 114c after ANY guard stop except a disk-limit stop, and halts only on
#   STOP.txt (conditions a, b, d) | DONE.txt | WSL guard disk limit | C: free < 22 GB | 40 restarts.
# When it halts it writes HALT.txt (so the keeper 122 does not restart it). One instance at a time (flock).
# Handling of a guard stop (also a leftover GUARD_STOPPED.txt found at start), using 114c's markers:
#   run R active (with or without a build): first stop on R -> R goes to serial-once.txt (redone with no concurrent
#     build); a second stop on R -> R deferred (deferred.txt)
#   only build B active: first stop on B -> retried; a second stop on B -> B deferred
#   nothing active -> plain restart
# Every stop is recorded in stops.tsv (time, source, run, build, action) and kept as GUARD_STOPPED-<k>.txt.
# Run as root, detached. Usage: 119c_supervise_selfheal.sh <plan tsv> <out dir>
set -u
PLAN=$1; OUT=$2; W=/mnt/c/Users/Work/dev/siegel/wsl-comparator; G=/home/checker/corpus/guard.log; M=/home/checker/corpus/GUARD_STOPPED
exec 8>/home/checker/corpus/119c.lock
flock -n 8 || { echo "$(date '+%F %T') 119c: another instance holds the lock; exiting" >> $OUT/run.log; exit 0; }
log() { echo "$(date '+%F %T') $*" >> $OUT/run.log; }
halt() { echo "HALT $(date '+%F %T'): $*" > $OUT/HALT.txt; log "119c: HALT: $*"; exit 0; }
[ -f $OUT/stops.tsv ] || printf 'time\tsource\tactive_run\tactive_build\taction\n' > $OUT/stops.tsv
nstops() { awk -F'\t' -v c="$1" 'NR>1 && ($3==c || $4==c)' $OUT/stops.tsv | wc -l; }
handle_stop() {
  local RUNC BLDC ST LL LT CF SRC DISK ACT k
  RUNC=$(cat $OUT/active-run.txt 2>/dev/null); BLDC=$(cat $OUT/active-build.txt 2>/dev/null)
  ST=$(stat -c %Y $OUT/GUARD_STOPPED.txt 2>/dev/null || date +%s)
  LL=$(grep 'LIMIT:' $G | tail -1); LT=$(date -d "$(echo "$LL" | cut -c1-19)" +%s 2>/dev/null || echo 0)
  CF=$(df -BG --output=avail /mnt/c | tail -1 | tr -dc 0-9)
  if [ $((ST - LT)) -le 300 ] && [ $((ST - LT)) -ge -60 ]; then
    SRC="WSL guard: $LL"; DISK=$(echo "$LL" | sed -n 's/.*disk \([0-9]*\)G.*/\1/p')
    [ "${DISK:-0}" -gt 85 ] && halt "WSL guard disk-limit stop ($LL)"
  else SRC="no WSL guard LIMIT line within 300 s (external stop; C: free ${CF} GB)"; fi
  [ "${CF:-99}" -lt 22 ] && halt "C: free ${CF} GB < 22 GB"
  if [ -n "$RUNC" ]; then
    if [ "$(nstops $RUNC)" -ge 1 ]; then echo "$RUNC" >> $OUT/deferred.txt; ACT="second stop on $RUNC: deferred"
    else echo "$RUNC" >> $OUT/serial-once.txt; ACT="first stop on $RUNC: serial-once (no concurrent build)"; fi
  elif [ -n "$BLDC" ]; then
    if [ "$(nstops $BLDC)" -ge 1 ]; then echo "$BLDC" >> $OUT/deferred.txt; ACT="second stop on build $BLDC: deferred"
    else ACT="first stop on build $BLDC: retried"; fi
  else ACT="nothing active: plain restart"; fi
  printf '%s\t%s\t%s\t%s\t%s\n' "$(date '+%F %T')" "$SRC" "$RUNC" "$BLDC" "$ACT" >> $OUT/stops.tsv
  k=$(( $(ls $OUT/GUARD_STOPPED-*.txt 2>/dev/null | wc -l) + 1 )); mv $OUT/GUARD_STOPPED.txt $OUT/GUARD_STOPPED-$k.txt
  log "119c: stop handled; source $SRC; $ACT; record GUARD_STOPPED-$k.txt"
}
for attempt in $(seq 1 41); do
  [ -f $OUT/DONE.txt ] && { log "119c: DONE"; exit 0; }
  [ -f $OUT/runs/STOP.txt ] && halt "STOP.txt present: $(tail -1 $OUT/runs/STOP.txt)"
  [ -f $OUT/GUARD_STOPPED.txt ] && handle_stop
  [ $attempt -ge 41 ] && halt "40 restarts reached"
  [ $attempt -gt 1 ] && sleep 60
  log "119c: start 114c (attempt $attempt; deferred: $(tr '\n' ' ' < $OUT/deferred.txt 2>/dev/null); serial-once: $(tr '\n' ' ' < $OUT/serial-once.txt 2>/dev/null))"
  bash $W/114c_extended_replay_overlap.sh $PLAN $OUT 8>&-
  [ -f $OUT/GUARD_STOPPED.txt ] || [ -f $OUT/DONE.txt ] || [ -f $OUT/runs/STOP.txt ] || log "119c: 114c ended without DONE, STOP or guard stop; restarting"
done
