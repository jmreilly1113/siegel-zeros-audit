#!/usr/bin/env bash
# Gentle switch from 83_remainder_pipelined.sh to 85_remainder_queue.sh at a batch boundary (Joe 2026-10-13, option 3).
# Run as root. Waits for "batch <K> outcomes" in run.log: at that point every run of batch K has finished and 83 is
# pruning. The stop marker is set then, so 83 finishes the prune, marks the batch done and halts at the top of its next
# batch: no comparator run is cut short. Nothing is killed. Then 85 starts on the same merged schedule.
# Usage: 86_switch_at_batch_end.sh <K>
K=$1
R=/mnt/c/Users/Work/dev/siegel/results; OUT=$R/2026-10-12-corpus-remainder
# The match is anchored to the driver's own line format ("<date> <time> batch K outcomes: ..."); this script's log lines
# never contain that text (the first version matched its own "armed" line and set the marker early; see docs/log.md).
echo "$(date '+%F %T') planned switch to 85_remainder_queue.sh armed (re-armed): marker to be set at the end of batch $K" >> $OUT/run.log
until grep -q -E "^[0-9-]{10} [0-9:]{8} batch $K outcomes:" $OUT/run.log; do
  pgrep -f 83_remainder_pipelined.sh >/dev/null || { echo "$(date '+%F %T') 83 exited before batch $K ended; switch not made" >> $OUT/run.log; exit 1; }
  sleep 2
done
touch /home/checker/corpus/GUARD_STOPPED
echo "$(date '+%F %T') planned switch: stop marker set during the batch $K prune" >> $OUT/run.log
while pgrep -f 83_remainder_pipelined.sh >/dev/null; do sleep 5; done
sleep 3
pgrep -u checker -fa 'comparator|lake|lean' && { echo "$(date '+%F %T') checker processes still running after 83 exited; 85 not started" >> $OUT/run.log; exit 1; }
[ -f $OUT/GUARD_STOPPED.txt ] && mv $OUT/GUARD_STOPPED.txt $OUT/SWITCH_STOPPED-83.txt
echo "$(date '+%F %T') 83_remainder_pipelined.sh exited (stop file kept as SWITCH_STOPPED-83.txt); starting 85_remainder_queue.sh" >> $OUT/run.log
setsid nohup bash /mnt/c/Users/Work/dev/siegel/wsl-comparator/85_remainder_queue.sh $R/2026-10-13-corpus-remainder-schedule-merged.json $OUT \
  $R/2026-10-11-corpus-headline/sample.txt >> /home/checker/corpus/remainder.out 2>&1 < /dev/null & disown
