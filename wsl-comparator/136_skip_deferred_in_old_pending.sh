#!/usr/bin/env bash
# 136 (2026-10-26 09:2x): keep 114f from building/running the 10 large configs deferred at 2026-10-25 ~20:40 (Joe: don't
# run them). 114f's PEND list was made at its start (2026-10-25 17:18:54, 94 configs), before that deferral, and its main
# loop does not re-read deferred.txt, so after BenjaminiSchramm it began prebuilding OrdinaryTwoPointCorrelations (09:13).
# (1) For every deferred config other than the active build: write 'retry' to pb-114d/<config>.built. 114f's main loop
#     then skips its build ("[ ! -f $PB/$N.built ]") and logs "build gave way to other jobs; left for the next attempt".
#     pb-114d is wiped at the next 114f start (line 41), whose PEND skips deferred configs.
# (2) The active build (a deferred config): 69c's starved-build preempt by hand (preempt/<config>.build + cgroup.kill of
#     the unit running 'lake build ... ComparatorChallenges.<config>') until 114f logs "preempted 4 times" (as 134).
# DRY=1: print what would be done.
set -u
O=/mnt/c/Users/Work/dev/siegel/results/2026-10-21-extended-replay; PB=/home/checker/corpus/xr/pb-114d
APP=/sys/fs/cgroup/unified/user.slice/user-1000.slice/user@1000.service/app.slice
DRY=${DRY:-0}; N=$(cat $O/active-build.txt)
log() { echo "$(date '+%F %T') $*" >> $O/run.log; }
grep -qx "$N" $O/deferred.txt || { echo "active build [$N] is not deferred; nothing to do"; exit 1; }
unit() { local d p a; for d in $APP/run-*.service; do for p in $(cat $d/cgroup.procs 2>/dev/null); do
    a=$(tr '\0' ' ' < /proc/$p/cmdline 2>/dev/null)
    case "$a" in */timeout\ *"bash -c lake build"*" ComparatorChallenges.$N"|*/timeout\ *"bash -c lake build"*" ComparatorChallenges.$N "*) echo "$d"; return;; esac; done; done; }
SK=
for D in $(grep -v '^#' $O/deferred.txt); do
  [ "$D" = "$N" ] && continue; [ -f $O/runs/$D.result.json ] && continue
  [ "$(cat $PB/$D.built 2>/dev/null)" = retry ] && continue
  SK="$SK$D "; [ $DRY = 1 ] || echo retry > $PB/$D.built
done
if [ $DRY = 1 ]; then echo "active build $N; would mark retry: $SK"; U=$(unit); echo "unit [$U]"; [ -n "$U" ] && for p in $(cat $U/cgroup.procs); do tr '\0' ' ' < /proc/$p/cmdline | cut -c1-160; echo; done | grep timeout; exit 0; fi
log "136: by hand (Claude): 114f's pending list (made 2026-10-25 17:18) predates the large-10 deferral; marked retry in pb-114d so 114f skips them: $SK"
for k in 1 2 3 4 5 6; do
  [ "$(cat $PB/$N.built 2>/dev/null)" = retry ] && break
  U=; for i in $(seq 1 240); do U=$(unit); [ -n "$U" ] && break; [ "$(cat $PB/$N.built 2>/dev/null)" = retry ] && break; sleep 5; done
  [ -n "$U" ] || break
  L0=$(wc -l < $O/run.log)
  echo "$(date '+%F %T') by hand (Claude, 136): deferred config (large-10 decision) in 114f's old pending list" >> $O/preempt/$N.build
  echo 1 > $U/cgroup.kill
  log "136: $N prebuild preempted by hand (Claude) the way 69c does ($(basename $U)), kill $k: deferred 2026-10-25 (large-10 decision), still in 114f's 17:18 pending list"
  for i in $(seq 1 120); do tail -n +$((L0+1)) $O/run.log | grep -q "$N: prebuild preempted" && break; sleep 5; done
  sleep 10
done
sleep 20
log "136: done; $N.built [$(cat $PB/$N.built 2>/dev/null)]; active build [$(cat $O/active-build.txt)], run [$(cat $O/active-run.txt)]"
