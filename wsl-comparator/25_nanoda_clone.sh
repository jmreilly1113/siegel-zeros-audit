#!/usr/bin/env bash
# Step 1: second kernel. Clone nanoda_lib and inspect which export format / Lean versions it supports.
set -e
cd /root/tools
[ -d nanoda_lib ] || git clone -q https://github.com/ammkrn/nanoda_lib
cd nanoda_lib
echo "HEAD: $(git log -1 --format='%H %cd %s' --date=short)"
git log --format='%h %cd %s' --date=short | head -25
ls
grep -n -i 'version\|format\|ndjson\|lean4export\|config' README.md | head -40
