R=/mnt/c/Users/Work/dev/siegel/results; OUT=$R/2026-10-12-corpus-remainder
echo "$(date '+%F %T') 85 was not running after the switch (its detached launch from 86 did not survive the WSL session ending); starting it directly" >> $OUT/run.log
setsid nohup bash /mnt/c/Users/Work/dev/siegel/wsl-comparator/85_remainder_queue.sh $R/2026-10-13-corpus-remainder-schedule-merged.json $OUT \
  $R/2026-10-11-corpus-headline/sample.txt >> /home/checker/corpus/remainder.out 2>&1 < /dev/null & disown
sleep 20; tail -6 $OUT/run.log; pgrep -fa 85_remainder | grep -v pgrep | cut -c1-80
