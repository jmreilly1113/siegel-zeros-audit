#!/usr/bin/env bash
cd /home/checker/math/lean/.lake/packages
for p in aesop Qq batteries mathlib plausible proofwidgets importGraph LeanSearchClient; do
  printf "%-18s " $p; if [ -d $p ]; then echo "dir: $(ls -A $p | wc -l) entries, .git: $([ -e $p/.git ] && echo yes || echo NO), files: $(find $p -type f | wc -l)"; else echo MISSING; fi
done
ls -la --time-style=+%T aesop | head -5
sudo -u checker git -C aesop status 2>&1 | head -3
