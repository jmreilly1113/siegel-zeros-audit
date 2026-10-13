#!/usr/bin/env bash
# Resume after the 2026-10-13 13:33 Windows-guard stop with 93_remainder_serial_v4.sh. Run as root; sleeps 20 s after launch.
R=/mnt/c/Users/Work/dev/siegel/results; OUT=$R/2026-10-12-corpus-remainder; B=$OUT/batch-06
pgrep -u checker -fa 'comparator|lake|lean' && { echo "checker processes running; not resumed"; exit 1; }
pgrep -fa '_remainder' | grep -v pgrep && { echo "a driver is running; not resumed"; exit 1; }
[ -f $OUT/GUARD_STOPPED.txt ] && mv $OUT/GUARD_STOPPED.txt $OUT/GUARD_STOPPED-4.txt
echo "$(date '+%F %T') resume after Windows-guard stop at 13:33:45 (Windows free RAM 2635 MB < 3000 MB; stop file kept as GUARD_STOPPED-4.txt); starting 93_remainder_serial_v4.sh (serial, LEAN_NUM_THREADS=4)" >> $OUT/run.log
setsid nohup bash /mnt/c/Users/Work/dev/siegel/wsl-comparator/93_remainder_serial_v4.sh $R/2026-10-13-corpus-remainder-schedule-merged.json $OUT \
  $R/2026-10-11-corpus-headline/sample.txt >> /home/checker/corpus/remainder.out 2>&1 < /dev/null & disown
sleep 20; tail -6 $OUT/run.log; pgrep -fa 93_remainder | grep -v pgrep | cut -c1-80
