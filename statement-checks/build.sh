#!/usr/bin/env bash
# Build the statement-checks project as checker, with the corpus WSL guard (85G disk, 1.5 GB MemAvailable).
# Usage (root): build.sh <log file> [lake args...]   Default target: StatementChecks.
LOG=$1; shift; DST=/home/checker/statement-checks; W=/mnt/c/Users/Work/dev/siegel/wsl-comparator
rm -f /home/checker/corpus/GUARD_STOPPED
nohup bash $W/69_corpus_guard.sh 85 1500 2 >/dev/null 2>&1 & GD=$!
{ echo "== build $(date '+%F %T') lake build $*"; t0=$(date +%s)
  sudo -u checker -H bash -lc "export PATH=\$HOME/.elan/bin:\$PATH LEAN_NUM_THREADS=4; cd $DST && lake build $* 2>&1; echo \"LAKE EXIT CODE: \$?\""
  echo "SECONDS: $(( $(date +%s) - t0 )); disk $(df -BG --output=used / | tail -1 | tr -d ' ')"
  [ -f /home/checker/corpus/GUARD_STOPPED ] && echo "GUARD STOPPED"; } > $LOG 2>&1
kill $GD 2>/dev/null; sync
