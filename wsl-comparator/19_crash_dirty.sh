#!/usr/bin/env bash
# Which build directories received writes from the comparator run that was interrupted by the 12:05 bugcheck (run started ~11:57)?
cd /home/checker/math/lean/.lake
for d in build packages/*/.lake/build; do
  n=$(find "$d" -type f -newermt "2026-10-08 11:57" 2>/dev/null | wc -l)
  [ "$n" -gt 0 ] && echo "$d: $n of $(find "$d" -type f | wc -l) files written during the interrupted run"
done
echo "other package files written after 11:57:"; find packages -path '*/.lake' -prune -o -type f -newermt "2026-10-08 11:57" -print
