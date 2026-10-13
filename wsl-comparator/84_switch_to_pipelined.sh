#!/usr/bin/env bash
# Gentle switch from 77_remainder.sh to 83_remainder_pipelined.sh (Joe 2026-10-13, option 2). Run as root.
# Creates the driver's stop marker so 77 halts at the end of its current step (nothing is killed), waits for it to exit,
# keeps its stop file under a name that says it was a planned switch (not a guard stop), then starts 83 detached on the
# merged schedule. 83 resumes from the .done markers.
R=/mnt/c/Users/Work/dev/siegel/results; OUT=$R/2026-10-12-corpus-remainder
echo "$(date '+%F %T') planned switch: stop marker set so 77_remainder.sh halts after its current step (Joe 2026-10-13, finish by 15:00)" >> $OUT/run.log
touch /home/checker/corpus/GUARD_STOPPED
while pgrep -f 77_remainder.sh >/dev/null; do sleep 15; done
sleep 5
pgrep -u checker -fa 'comparator|lake|lean' && { echo "$(date '+%F %T') checker processes still running after 77 exited; 83 not started" >> $OUT/run.log; exit 1; }
[ -f $OUT/GUARD_STOPPED.txt ] && mv $OUT/GUARD_STOPPED.txt $OUT/SWITCH_STOPPED-77.txt
echo "$(date '+%F %T') 77_remainder.sh exited (stop file kept as SWITCH_STOPPED-77.txt); starting 83_remainder_pipelined.sh" >> $OUT/run.log
setsid nohup bash /mnt/c/Users/Work/dev/siegel/wsl-comparator/83_remainder_pipelined.sh $R/2026-10-13-corpus-remainder-schedule-merged.json $OUT \
  $R/2026-10-11-corpus-headline/sample.txt >> /home/checker/corpus/remainder.out 2>&1 < /dev/null & disown
