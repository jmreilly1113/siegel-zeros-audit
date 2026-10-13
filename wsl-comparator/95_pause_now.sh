#!/usr/bin/env bash
# Pause the remainder run now (Joe 2026-10-13 ~14:35: needs the PC). Same stop as 69_corpus_guard.sh: set the stop
# marker, TERM then KILL checker's build processes, wait for the driver to exit. Resumable: unfinished configs have no
# .done (v2+ check). Run as root.
OUT=/mnt/c/Users/Work/dev/siegel/results/2026-10-12-corpus-remainder
echo "$(date '+%F %T') pause requested by Joe (needs the PC); stopping checker build processes (resumable)" >> $OUT/run.log
touch /home/checker/corpus/GUARD_STOPPED
pkill -TERM -u checker -f 'comparator|lake|lean'; sleep 20; pkill -KILL -u checker -f 'comparator|lake|lean'; sync
for i in $(seq 1 24); do pgrep -f 93_remainder_serial_v4.sh >/dev/null || break; sleep 5; done
pgrep -fa '93_remainder|69_corpus' | grep -v pgrep
pkill -f 69_corpus_guard.sh; sync
[ -f $OUT/GUARD_STOPPED.txt ] && mv $OUT/GUARD_STOPPED.txt $OUT/PAUSED-1.txt
echo "$(date '+%F %T') paused (stop file kept as PAUSED-1.txt)" >> $OUT/run.log; tail -5 $OUT/run.log; ls $OUT/batch-06/*.done | wc -l
