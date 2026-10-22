#!/usr/bin/env bash
# Extended replay, 2026-10-22 ~00:35: a stricter WSL memory guard, kept running while 119b supervises.
# Why: at ~00:20 Windows ran critically low on memory (Claude Code reaped its background shells, including the
# Windows-side monitor 78); vmmemWSL can grow toward the 24 GB cap when a large nanoda run overlaps an 8-thread build.
# This runs a second instance of the unchanged 69_corpus_guard.sh with a MemAvailable floor of 5000 MB (the instance that
# 114c starts keeps 1500 MB), so WSL's own use stays below ~19 GB and Windows keeps several GB. Its stops write the same
# guard.log LIMIT line and marker as 69 always does, so 119b treats them as WSL-guard memory stops. After it fires it
# waits until 114c's restart clears the marker, then starts again. Exits when 119b is no longer running.
# Run as root, detached. Usage: 121_strict_guard_loop.sh [floor MB]
set -u
F=${1:-5000}; W=/mnt/c/Users/Work/dev/siegel/wsl-comparator; M=/home/checker/corpus/GUARD_STOPPED
echo "$(date '+%F %T') 121: strict guard loop start (MemAvailable floor ${F}MB, disk 85G, drop_caches every 10 min)" >> /home/checker/corpus/guard.log
while pgrep -f 119b_supervise_overlap.sh >/dev/null; do
  while [ -f $M ] && pgrep -f 119b_supervise_overlap.sh >/dev/null; do sleep 15; done
  bash $W/69_corpus_guard.sh 85 $F 20
  sleep 5
done
echo "$(date '+%F %T') 121: 119b not running; strict guard loop ends" >> /home/checker/corpus/guard.log
