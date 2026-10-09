#!/usr/bin/env bash
# After the 12:05 bugcheck: look for zero-filled or truncated build files (.olean must start with "olean").
for root in /home/checker/math/lean/.lake /home/checker/.elan/toolchains; do
  total=0; bad=0; empty=0
  while IFS= read -r -d '' f; do
    total=$((total+1))
    if [ ! -s "$f" ]; then empty=$((empty+1)); echo "EMPTY $f"; continue; fi
    [ "$(head -c 5 "$f")" = "olean" ] || { bad=$((bad+1)); echo "BADHDR $f $(stat -c '%y' "$f")"; }
  done < <(find "$root" -name '*.olean' -print0)
  echo "== $root: $total .olean files, $bad bad header, $empty empty"
done
echo "== solution build dir (math/lean/.lake/build), newest files:"
find /home/checker/math/lean/.lake/build -type f -newermt '2026-10-08 11:58' 2>/dev/null | wc -l
ls -la --time-style=full-iso /home/checker/math/lean/.lake/build/lib/lean/OAI/NumberTheory/SiegelZeros 2>/dev/null | tail -3
