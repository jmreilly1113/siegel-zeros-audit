#!/bin/bash
# 2026-10-25 04:2x: CycleCliqueRamsey's 2-thread prebuild (225 of 444 modules unbuilt, ~5 per 15 min) blocks the main
# lane for ~11 h. Use 114f's own preempt path twice (marker + unit kill, as 69c does) so tries reaches 4 and 114f
# leaves the config for the next attempt and the main lane goes on. Finished .olean files are kept by lake.
# APPLY=1 to act; otherwise only show the unit.
O=/mnt/c/Users/Work/dev/siegel/results/2026-10-21-extended-replay
APP=/sys/fs/cgroup/unified/user.slice/user-1000.slice/user@1000.service/app.slice
log() { echo "$(date '+%F %T') $*" >> $O/run.log; }
unit() { for d in $APP/run-*.service; do for p in $(cat $d/cgroup.procs 2>/dev/null); do
  tr '\0' ' ' < /proc/$p/cmdline 2>/dev/null | grep -q '^/usr/bin/timeout .*lake build OAI.Combinatorics.Ramsey.CycleClique' && { echo $d; break 2; }; done; done; }
d=$(unit); echo "unit: $d"; [ -n "$d" ] || exit 1
[ "$(cat $O/active-build.txt)" = CycleCliqueRamsey ] || { echo "active build is not CycleCliqueRamsey"; exit 1; }
[ "$APPLY" = 1 ] || exit 0
log "CycleCliqueRamsey: manual preempt (Claude, standing authority): 2-thread prebuild has 225 of 444 modules left (~11 h) and blocks the main lane; preempted twice via 114f's preempt path so it is left for the next attempt (built .olean files kept)"
for i in 1 2; do
  d=$(unit); [ -n "$d" ] || { echo "no unit at kill $i"; exit 1; }
  echo "$(date '+%F %T') manual preempt $i (Claude): 2-thread build would block the main lane ~11 h" >> $O/preempt/CycleCliqueRamsey.build
  echo 1 > $d/cgroup.kill; echo "killed $(basename $d) ($i)"
  if [ $i = 1 ]; then
    for t in $(seq 60); do sleep 5; n=$(unit); [ -n "$n" ] && [ "$n" != "$d" ] && break; done
    sleep 20
  fi
done
sleep 30; tail -5 $O/run.log | cut -c1-200; echo "build marker: [$(cat $O/active-build.txt)]"
