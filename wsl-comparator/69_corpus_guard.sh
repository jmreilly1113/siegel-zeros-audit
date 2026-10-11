#!/usr/bin/env bash
# Corpus pilot guard (inside WSL, as root): every 30 s check disk and memory; every 10 min drop the page cache so
# WSL returns cached memory to Windows. Stops checker's lake/lean/comparator processes (resumable) if
# disk use > DISK_GB (default 42) or MemAvailable < MEM_MB (default 1500).
DISK=${1:-42}; MEM=${2:-1500}; LOG=/home/checker/corpus/guard.log; n=0
echo "$(date '+%F %T') guard start: disk limit ${DISK}G, MemAvailable floor ${MEM}MB" >> $LOG
while true; do
  u=$(df -BG --output=used / | tail -1 | tr -dc 0-9); a=$(awk '/MemAvailable/ {print int($2/1024)}' /proc/meminfo)
  if [ "$u" -gt "$DISK" ] || [ "$a" -lt "$MEM" ]; then
    echo "$(date '+%F %T') LIMIT: disk ${u}G, MemAvailable ${a}MB; stopping checker build processes" >> $LOG
    pkill -TERM -u checker -f 'comparator|lake|lean'; sleep 20; pkill -KILL -u checker -f 'comparator|lake|lean'; sync
    echo "$(date '+%F %T') stopped" >> $LOG; touch /home/checker/corpus/GUARD_STOPPED; exit 1
  fi
  n=$((n+1)); if [ $((n % 20)) -eq 0 ]; then sync; echo 1 > /proc/sys/vm/drop_caches; echo "$(date '+%F %T') drop_caches; disk ${u}G MemAvailable ${a}MB" >> $LOG; fi
  sleep 30
done
