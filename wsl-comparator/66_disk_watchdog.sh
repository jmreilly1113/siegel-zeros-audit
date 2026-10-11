#!/usr/bin/env bash
# Corpus pilot: stop checker's lake/lean/comparator processes if WSL disk use exceeds LIMIT_GB (default 42).
# The WSL virtual disk is already >= 43 GB (high-water mark 2026-10-11), so staying below that reuses freed space
# without growing the image on Windows C:, which has ~3 GB free.
LIMIT=${1:-42}; LOG=/home/checker/corpus/watchdog.log
mkdir -p /home/checker/corpus
echo "$(date '+%F %T') watchdog start, limit ${LIMIT}G, used $(df -BG --output=used / | tail -1)" >> $LOG
while true; do
  u=$(df -BG --output=used / | tail -1 | tr -dc 0-9)
  if [ "$u" -gt "$LIMIT" ]; then
    echo "$(date '+%F %T') LIMIT EXCEEDED: used ${u}G > ${LIMIT}G; stopping checker build processes" >> $LOG
    pkill -TERM -u checker -f 'comparator|lake|lean' ; sleep 20; pkill -KILL -u checker -f 'comparator|lake|lean'
    sync; echo "$(date '+%F %T') stopped" >> $LOG; exit 1
  fi
  sleep 30
done
