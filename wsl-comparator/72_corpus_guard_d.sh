#!/usr/bin/env bash
# PREPARED, NOT YET IN USE (apply after the WSL move to D:; see docs/wsl-move-plan.md).
# Replacement for 69_corpus_guard.sh once the WSL disk image lives on D:. The old guard capped WSL disk use at 42 GB
# because the image on C: could not grow (C: had ~2 GB free). On D: the image can grow into D:'s free space,
# so this guard watches D: directly (via /mnt/d) and keeps the same memory floor and page-cache dropping.
# Stops checker's lake/lean/comparator processes (resumable) if D: free < DFREE_GB (default 25) or
# MemAvailable < MEM_MB (default 1500).
DFREE=${1:-25}; MEM=${2:-1500}; LOG=/home/checker/corpus/guard.log; n=0
echo "$(date '+%F %T') guard(D:) start: D: free floor ${DFREE}G, MemAvailable floor ${MEM}MB" >> $LOG
while true; do
  f=$(df -BG --output=avail /mnt/d | tail -1 | tr -dc 0-9); a=$(awk '/MemAvailable/ {print int($2/1024)}' /proc/meminfo)
  if [ -z "$f" ] || [ "$f" -lt "$DFREE" ] || [ "$a" -lt "$MEM" ]; then
    echo "$(date '+%F %T') LIMIT: D: free ${f:-unreadable}G, MemAvailable ${a}MB; stopping checker build processes" >> $LOG
    pkill -TERM -u checker -f 'comparator|lake|lean'; sleep 20; pkill -KILL -u checker -f 'comparator|lake|lean'; sync
    echo "$(date '+%F %T') stopped" >> $LOG; touch /home/checker/corpus/GUARD_STOPPED; exit 1
  fi
  n=$((n+1)); if [ $((n % 20)) -eq 0 ]; then sync; echo 1 > /proc/sys/vm/drop_caches; echo "$(date '+%F %T') drop_caches; D: free ${f}G MemAvailable ${a}MB" >> $LOG; fi
  sleep 30
done
