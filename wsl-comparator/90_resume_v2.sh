#!/usr/bin/env bash
# Resume after the 2026-10-13 13:02 disk-guard stop with 89_remainder_queue_v2.sh. Run as root (not as the last command
# of a wsl.exe session's job: it sleeps 20 s after the detached launch). Keeps the stop file and the invalid .done marker.
R=/mnt/c/Users/Work/dev/siegel/results; OUT=$R/2026-10-12-corpus-remainder; B=$OUT/batch-06
pgrep -u checker -fa 'comparator|lake|lean' && { echo "checker processes running; not resumed"; exit 1; }
pgrep -fa '_remainder' | grep -v pgrep && { echo "a driver is running; not resumed"; exit 1; }
[ -f $OUT/GUARD_STOPPED.txt ] && mv $OUT/GUARD_STOPPED.txt $OUT/GUARD_STOPPED-2.txt
# MaximalSeshadriConstants.done (13:03:00) was written for runs the guard killed (no COMPARATOR EXIT CODE in either log)
[ -f $B/MaximalSeshadriConstants.done ] && mv $B/MaximalSeshadriConstants.done $B/MaximalSeshadriConstants.done.invalid-killed-by-guard
echo "$(date '+%F %T') resume after disk-guard stop at 13:02:38 (disk 66G > 65G limit; stop file kept as GUARD_STOPPED-2.txt); MaximalSeshadriConstants.done set aside as .done.invalid-killed-by-guard (both its logs lack COMPARATOR EXIT CODE); starting 89_remainder_queue_v2.sh" >> $OUT/run.log
setsid nohup bash /mnt/c/Users/Work/dev/siegel/wsl-comparator/89_remainder_queue_v2.sh $R/2026-10-13-corpus-remainder-schedule-merged.json $OUT \
  $R/2026-10-11-corpus-headline/sample.txt >> /home/checker/corpus/remainder.out 2>&1 < /dev/null & disown
sleep 20; tail -6 $OUT/run.log; pgrep -fa 89_remainder | grep -v pgrep | cut -c1-80
