#!/bin/bash
# 126 (2026-10-25): start 125 for TriangularEnergy once ErdosReciprocal's run is over (result, queued rerun or deferred), 114f has been up
# for >= 5 min (not mid-restart), and ErdosReciprocal is not the active run. 125 checks its own preconditions again.
O=${XR_O:-/mnt/c/Users/Work/dev/siegel/results/2026-10-21-extended-replay}; W=${XR_W:-/mnt/c/Users/Work/dev/siegel/wsl-comparator}; PG=${XR_PG:-114f_extended_replay_reruns_last.sh}; MINUP=${XR_MINUP:-300}; ST=${XR_ST:-30}
log() { echo "$(date '+%F %T') $*" >> $O/run.log; }
log "wait125: armed (TriangularEnergy side rerun after ErdosReciprocal's run)"
while :; do
  sleep $ST
  [ -f $O/HALT.txt ] && { log "wait125: HALT present; not started"; exit 1; }
  done_e=0
  [ -f $O/runs/ErdosReciprocal.result.json ] && done_e=1
  grep -qx ErdosReciprocal $O/rerun-end.txt 2>/dev/null && done_e=1
  grep -qx ErdosReciprocal $O/deferred.txt 2>/dev/null && done_e=1
  [ $done_e = 1 ] || continue
  grep -qx ErdosReciprocal $O/active-run.txt && continue
  p=$(pgrep -of "$PG") || continue
  [ "$(ps -o etimes= -p $p | tr -d ' ')" -ge $MINUP ] || continue
  [ -s $O/active-slow.txt ] && continue
  break
done
P=$O/phase3-order.tsv
log "wait125: conditions met; starting 125 TriangularEnergy"
exec bash $W/125_side_rerun.sh $P $O TriangularEnergy
