#!/usr/bin/env bash
# One mid-batch prune after the 2026-10-20 02:59 disk-guard stop in batch 8 (no driver or build running).
# Uses results/2026-10-20-prune-only-schedule.json with <batches done>=8, so it keeps every kept config's closure plus
# PartitionPrinciple and DegreeRigidity (the 2 pending configs), and removes only what the 4 finished
# (all ACCEPT_BOTH) batch-8 configs alone needed. Usage: 102_prune_midbatch.sh [--apply]. Run as root.
R=/mnt/c/Users/Work/dev/siegel/results; OUT=$R/2026-10-12-corpus-remainder
pgrep -fa 'remainder_serial|_remainder_queue|lake build|lake env|bin/comparator|nanoda_bin' | grep -v pgrep && { echo "something is running; not pruned"; exit 1; }
echo "disk used before: $(df -BG --output=used / | tail -1 | tr -d ' ')"
python3 -I /mnt/c/Users/Work/dev/siegel/wsl-comparator/76_prune.py /home/checker/math/lean \
  /home/checker/.elan/toolchains/leanprover--lean4---v4.34.1/src/lean $R/2026-10-20-prune-only-schedule.json 8 \
  $OUT/keep-configs.txt "$@" > /tmp/prune-midbatch.log 2>&1
head -1 /tmp/prune-midbatch.log
if [ "$1" = --apply ]; then cp /tmp/prune-midbatch.log $OUT/batch-08/prune-midbatch-20261020.log
  echo "$(date '+%F %T') mid-batch prune (102_prune_midbatch.sh, prune-only schedule, after GUARD_STOPPED 02:59): $(head -1 /tmp/prune-midbatch.log); disk used $(df -BG --output=used / | tail -1 | tr -d ' ')" >> $OUT/run.log; fi
echo "disk used after: $(df -BG --output=used / | tail -1 | tr -d ' ')"; sync
