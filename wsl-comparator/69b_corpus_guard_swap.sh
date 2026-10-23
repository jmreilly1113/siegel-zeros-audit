#!/usr/bin/env bash
# Corpus guard 69b (2026-10-23): 69_corpus_guard.sh with the memory test counting free swap. Stops checker's
# lake/lean/comparator processes if disk use > DISK_GB or MemAvailable + SwapFree < MEM_MB. With WSL's 5 GB swap and
# MEM_MB 2000 this lets a short build spike use up to ~3 GB of swap instead of stopping at MemAvailable < 1500 MB as 69 does
# (PlanarPacking 14:20:28 at 1473 MB, NuclearUltrapower 13:41:51 at 1397 MB, both 8-thread builds running alone).
# Same log lines as 69 ("guard start", "LIMIT: disk <u>G, MemAvailable <a>MB ...", "stopped"), so 114c and 119c read it
# unchanged. Usage: 69b_corpus_guard_swap.sh DISK_GB MEM_MB DROP_EVERY
# Test hooks (defaults are the live paths): GUARD_LOG, GUARD_MARK, GUARD_MEMINFO; GUARD_DRYRUN=1 kills nothing, drops no cache.
DISK=${1:-85}; MEM=${2:-2000}; DROP=${3:-2}; n=0
LOG=${GUARD_LOG:-/home/checker/corpus/guard.log}; MARK=${GUARD_MARK:-/home/checker/corpus/GUARD_STOPPED}
MI=${GUARD_MEMINFO:-/proc/meminfo}; DRY=${GUARD_DRYRUN:-0}
echo "$(date '+%F %T') guard start: disk limit ${DISK}G, MemAvailable+SwapFree floor ${MEM}MB (69b), drop_caches every $((DROP*30)) s" >> $LOG
while true; do
  u=$(df -BG --output=used / | tail -1 | tr -dc 0-9)
  a=$(awk '/^MemAvailable:/ {print int($2/1024)}' $MI); s=$(awk '/^SwapFree:/ {print int($2/1024)}' $MI)
  if [ "$u" -gt "$DISK" ] || [ $((a + s)) -lt "$MEM" ]; then
    echo "$(date '+%F %T') LIMIT: disk ${u}G, MemAvailable ${a}MB, SwapFree ${s}MB; stopping checker build processes" >> $LOG
    if [ "$DRY" = 1 ]; then echo "$(date '+%F %T') (dry run: nothing killed)" >> $LOG
    else pkill -TERM -u checker -f 'comparator|lake|lean'; sleep 20; pkill -KILL -u checker -f 'comparator|lake|lean'; sync; fi
    echo "$(date '+%F %T') stopped" >> $LOG; touch $MARK; exit 1
  fi
  n=$((n+1)); if [ $((n % DROP)) -eq 0 ]; then
    [ "$DRY" = 1 ] || { sync; echo 1 > /proc/sys/vm/drop_caches; }
    echo "$(date '+%F %T') drop_caches; disk ${u}G MemAvailable ${a}MB SwapFree ${s}MB" >> $LOG; fi
  sleep ${GUARD_POLL:-30}
done
