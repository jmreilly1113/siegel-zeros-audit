#!/bin/bash
# 133 (2026-10-26): record copy of the waiter run from the scratchpad at 01:3x as w125.sh (stub-tested: t17_w125.sh, 8 cases).
# Start each 28800 s rerun beside the pass as soon as 114f queues it in rerun-end.txt (as done by hand for GeneralMahler
# at 18:18), instead of after the pass. Pre-checks 125b's own conditions (slow lane < SIDE_SLOW_MAX lines, A >= SIDE_MIN_MB,
# kept export, no result, not already running) so 125b is only called when it will start. Ends on HALT/STOP/GUARD_STOPPED,
# when 114f is gone (XR_PG), or when 114f logs "pass done" (its end phase then runs what is left). DRY=1: report once.
O=${XR_O:-/mnt/c/Users/Work/dev/siegel/results/2026-10-21-extended-replay}; C=${XR_C:-/home/checker/corpus}
W=/mnt/c/Users/Work/dev/siegel/wsl-comparator; PG=${XR_PG:-114f_extended_replay_reruns_last.sh}; ST=${XR_ST:-60}
SSM=${SIDE_SLOW_MAX:-2}; SMB=${SIDE_MIN_MB:-12000}; RQ=$O/rerun-end.txt; DRY=${DRY:-0}
log() { echo "$(date '+%F %T') $*" >> $O/run.log; }
memA() { awk '/^MemAvailable:|^SwapFree:/ {s+=$2} END {print int(s/1024)}' ${XR_MI:-/proc/meminfo}; }
bad() { [ -f $C/GUARD_STOPPED ] || [ -f $O/runs/STOP.txt ] || [ -f $O/HALT.txt ] || ! pgrep -f "$PG" > /dev/null; }
launch() { if [ -n "${XR_LAUNCH:-}" ]; then $XR_LAUNCH "$1"; return; fi
  local P; P=$(ps -eo args | grep -o "$PG [^ ]*" | grep -v grep | head -1 | awk '{print $2}'); [ -f "$P" ] || return 1
  SIDE_SLOW_MAX=$SSM SIDE_MIN_MB=$SMB setsid nohup bash $W/125b_side_rerun.sh $P $O $1 >> $C/xr-125b.out 2>&1 < /dev/null & }
T0=$(wc -l < $O/run.log)
while :; do
  bad && { [ $DRY = 1 ] || log "w125: stop/HALT or 114f gone; waiter ends"; exit 0; }
  tail -n +$((T0+1)) $O/run.log | grep -q '114f: pass done' && { log "w125: 114f pass done; its end phase runs what is left; waiter ends"; exit 0; }
  for N in $(awk '!s[$0]++' $RQ 2>/dev/null); do
    s=$(grep -c . $O/active-slow.txt 2>/dev/null); a=$(memA)
    why=; grep -qx "$N" $O/active-slow.txt 2>/dev/null && why="already in the slow lane"
    [ -z "$why" ] && [ -f $O/runs/$N.result.json ] && why="has a result"
    [ -z "$why" ] && [ ! -f $C/xr/exp/$N.export ] && why="no kept export yet"
    [ -z "$why" ] && [ "$s" -ge $SSM ] && why="slow lane has $s"
    [ -z "$why" ] && [ "$a" -lt $SMB ] && why="A $a MB < $SMB"
    [ $DRY = 1 ] && { echo "$N: ${why:-would start}"; continue; }
    [ -n "$why" ] && continue
    log "w125: $N queued in rerun-end.txt; starting its 28800 s rerun beside the pass (slow lane $s, A $a MB)"
    launch $N; sleep ${XR_GAP:-30}
  done
  [ $DRY = 1 ] && { echo "dry: slow $(grep -c . $O/active-slow.txt) A $(memA) rq [$(tr '\n' ' ' < $RQ 2>/dev/null)]"; exit 0; }
  sleep $ST
done
