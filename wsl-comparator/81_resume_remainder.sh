#!/usr/bin/env bash
# Resume the remainder driver after a guard stop (run as root). Keeps the stop marker under a numbered name, checks
# that no checker build processes are left, then relaunches 77_remainder.sh detached (it skips finished configs/batches).
R=/mnt/c/Users/Work/dev/siegel/results
OUT=$R/2026-10-12-corpus-remainder
pgrep -u checker -fa 'comparator|lake|lean' && { echo "checker processes still running; not resuming"; exit 1; }
if [ -f $OUT/GUARD_STOPPED.txt ]; then
  i=1; while [ -f $OUT/GUARD_STOPPED-$i.txt ]; do i=$((i+1)); done
  mv $OUT/GUARD_STOPPED.txt $OUT/GUARD_STOPPED-$i.txt; echo "stop marker kept as GUARD_STOPPED-$i.txt"
fi
echo "$(date '+%F %T') resume after guard stop ($*)" >> $OUT/run.log
setsid nohup bash /mnt/c/Users/Work/dev/siegel/wsl-comparator/77_remainder.sh $R/2026-10-12-corpus-remainder-schedule.json $OUT \
  $R/2026-10-11-corpus-headline/sample.txt >> /home/checker/corpus/remainder.out 2>&1 < /dev/null & disown
sleep 5; tail -3 $OUT/run.log; df -BG --output=used / | tail -1
