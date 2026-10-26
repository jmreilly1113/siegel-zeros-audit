#!/bin/bash
# 132 (2026-10-25): record copy of the chain launcher run from the scratchpad at 20:3x as chain129.sh (stub-tested:
# t16_chain.sh). Chains 129b side builds of large configs whose unbuilt closures share no module with the cheap configs.
# Usage: 132_chain_side_builds.sh <running config> <next config>...
# chain 129b side builds: after <prev> logs "closure built" or "attempts used", start 129b on the next target.
# Only while 114f runs, no HALT/STOP/GUARD_STOPPED, and WSL used < DISK_MAX G. DRY=1: report and exit.
O=${XR_O:-/mnt/c/Users/Work/dev/siegel/results/2026-10-21-extended-replay}; W=${XR_W:-/mnt/c/Users/Work/dev/siegel/wsl-comparator}; C=${XR_C:-/home/checker/corpus}
PREV=$1; shift; DISK_MAX=${DISK_MAX:-80}; DRY=${DRY:-0}
log() { echo "$(date '+%F %T') $*" >> $O/run.log; }
bad() { [ -f $C/GUARD_STOPPED ] || [ -f $O/runs/STOP.txt ] || [ -f $O/HALT.txt ] || ! pgrep -f ${XR_PG:-114f_extended_replay_reruns_last.sh} >/dev/null; }
used() { df -BG --output=used / | tail -1 | tr -dc 0-9; }
fin() { grep -qE "129b: $1 (closure built|reached by 114f|side build attempt 6 (done|not finished))" $O/run.log; }
for T in "$@"; do
  [ $DRY = 1 ] && { echo "prev $PREV finished: $(fin $PREV && echo yes || echo no); next $T; disk $(used)G; bad: $(bad && echo yes || echo no)"; exit 0; }
  until fin $PREV; do bad && { log "chain129: stop/HALT or 114f gone; chain ends before $T"; exit 0; }; sleep ${XR_ST:-60}; done
  [ -f $O/runs/$T.result.json ] && { PREV=$T; continue; }
  [ $(used) -ge $DISK_MAX ] && { log "chain129: WSL used $(used)G >= ${DISK_MAX}G; chain ends before $T"; exit 0; }
  bad && { log "chain129: stop/HALT or 114f gone; chain ends before $T"; exit 0; }
  log "chain129: $PREV side build finished; starting 129b for $T (disk $(used)G)"
  setsid nohup bash $W/129b_side_build_one.sh $T $O 3 >> $C/xr-129b.out 2>&1 < /dev/null &
  PREV=$T; sleep ${XR_GAP:-120}
done
log "chain129: last target ($PREV) started; chain done"
