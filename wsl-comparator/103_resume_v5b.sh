#!/usr/bin/env bash
# Resume after the 2026-10-20 02:59 batch-8 disk-guard stop (GUARD_STOPPED-7.txt) and the mid-batch prune (102), with 100_remainder_serial_v5.sh.
# Run as root after WSL has been started and a keep-alive (wsl.exe sleep) is running on the Windows side. Pre-flight checks first; nothing is
# started if any fails. Sleeps 20 s after launch.
R=/mnt/c/Users/Work/dev/siegel/results; OUT=$R/2026-10-12-corpus-remainder; M=/home/checker/math
fail() { echo "PRE-FLIGHT FAIL: $*"; exit 1; }
pgrep -u checker -fa 'comparator|lake|lean' && fail "checker processes running"
pgrep -fa '_remainder' | grep -v pgrep && fail "a driver is running"
[ -f $OUT/GUARD_STOPPED.txt ] && fail "unexpected GUARD_STOPPED.txt (the 02:59 stop is GUARD_STOPPED-7.txt)"
[ -f $OUT/DONE.txt ] && fail "DONE.txt exists"
[ -f $OUT/batch-08/BATCH_DONE ] && fail "batch-08 BATCH_DONE present"
h=$(sudo -u checker git -C $M rev-parse HEAD); [ "$h" = fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb ] || fail "clone at $h"
[ -z "$(sudo -u checker git -C $M status --porcelain)" ] || fail "clone not clean"
used=$(df -BG --output=used / | tail -1 | tr -dc 0-9); echo "WSL disk used: ${used}G"; [ "$used" -lt 75 ] || fail "disk ${used}G"
echo "MemAvailable: $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) MB"
echo "batch-08 done: $(ls $OUT/batch-08/*.done | wc -l) (expect 4); BATCH_DONE: $(ls $OUT/batch-08/BATCH_DONE 2>/dev/null || echo absent)"
echo "$(date '+%F %T') resume after the 2026-10-20 02:59 WSL disk-guard stop in batch 8 (GUARD_STOPPED-7.txt) and the 03:04 mid-batch prune; pre-flight passed (HEAD fd4aeeb, clean, disk ${used}G); starting 100_remainder_serial_v5.sh (serial, LEAN_NUM_THREADS=4, schedule 2026-10-19-corpus-remainder-schedule-split.json)" >> $OUT/run.log
setsid nohup bash /mnt/c/Users/Work/dev/siegel/wsl-comparator/100_remainder_serial_v5.sh $R/2026-10-19-corpus-remainder-schedule-split.json $OUT \
  $R/2026-10-11-corpus-headline/sample.txt >> /home/checker/corpus/remainder.out 2>&1 < /dev/null & disown
sleep 20; tail -6 $OUT/run.log; pgrep -fa 100_remainder | grep -v pgrep | cut -c1-80
