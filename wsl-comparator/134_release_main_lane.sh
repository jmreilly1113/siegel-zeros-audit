#!/usr/bin/env bash
# 134 (2026-10-26 05:1x): release 114f's main lane from the UniversalTensorSquares prebuild (retry 2 at 2 threads, ~38
# modules/h, main lane idle since 03:32). Does what 69c's starved-build preempt does (69c lines 138-141): append to
# preempt/<config>.build, then write 1 to the build unit's cgroup.kill. 114f's build_one counts preempts; after the 4th
# it writes 'retry' and the main lane goes on (the config is left for the next attempt). Two preempts are needed (tries 2 -> 4).
# Only the unit whose timeout root runs 'lake build' with the UTS solution module is touched. DRY=1: print the unit only.
set -u
N=UniversalTensorSquares; MOD=OAI.RepresentationTheory.UniversalSquare
O=/mnt/c/Users/Work/dev/siegel/results/2026-10-21-extended-replay
APP=/sys/fs/cgroup/unified/user.slice/user-1000.slice/user@1000.service/app.slice
DRY=${DRY:-0}
log() { echo "$(date '+%F %T') $*" >> $O/run.log; }
unit() { local d p a; for d in $APP/run-*.service; do for p in $(cat $d/cgroup.procs 2>/dev/null); do
    a=$(tr '\0' ' ' < /proc/$p/cmdline 2>/dev/null)
    case "$a" in */timeout\ *"bash -c lake build"*"$MOD"*) echo "$d"; return;; esac; done; done; }
[ "$(cat $O/active-build.txt)" = $N ] || { echo "active build is not $N"; exit 1; }
for k in 1 2; do
  U=; for i in $(seq 1 60); do U=$(unit); [ -n "$U" ] && break; sleep 5; done
  [ -n "$U" ] || { echo "no $N build unit found"; log "134: no $N build unit found (preempt $k); nothing done"; exit 1; }
  if [ $DRY = 1 ]; then echo "unit $U procs $(wc -l < $U/cgroup.procs)"; for p in $(cat $U/cgroup.procs); do tr '\0' ' ' < /proc/$p/cmdline | cut -c1-160; echo; done | grep timeout; exit 0; fi
  L0=$(wc -l < $O/run.log)
  echo "$(date '+%F %T') by hand (Claude, 134): main lane idle since 03:32; build at 2 threads ~38 modules/h" >> $O/preempt/$N.build
  echo 1 > $U/cgroup.kill
  log "134: $N prebuild preempted by hand (Claude) the way 69c does (preempt/$N.build + cgroup.kill of $(basename $U)), $k of 2: main lane idle since 03:32, retry at 2 threads ~38 modules/h"
  for i in $(seq 1 120); do tail -n +$((L0+1)) $O/run.log | grep -q "$N: prebuild preempted\|$N (.*prebuild (LEAN\|$N: build gave way" && break; sleep 5; done
  sleep 10
  tail -n +$((L0+1)) $O/run.log | grep -q "$N: prebuild preempted [0-9]* times\|$N: build gave way" && break
done
sleep 30
log "134: done; active build [$(cat $O/active-build.txt)], run [$(cat $O/active-run.txt)]"
