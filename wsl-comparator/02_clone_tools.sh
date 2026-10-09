#!/usr/bin/env bash
set -euo pipefail
mkdir -p /root/tools && cd /root/tools
for r in leanprover/comparator leanprover/lean4export Zouuup/landrun; do
  d=$(basename $r)
  [ -d $d ] || git clone -q https://github.com/$r
  echo "== $r @ $(git -C $d rev-parse HEAD) ($(git -C $d log -1 --format=%cd --date=short))"
done
echo; echo "===== comparator README ====="; cat comparator/README.md | head -120
echo; echo "===== comparator files ====="; ls comparator; cat comparator/lean-toolchain 2>/dev/null
echo; echo "===== landrun invocation in comparator ====="; grep -rn "landrun" comparator --include=*.lean | head -20
