#!/usr/bin/env bash
set -euo pipefail
export PATH="$HOME/.elan/bin:$PATH"
cd /root/tools
rm -rf comparator-v4.34 && git clone -q comparator comparator-v4.34 && cd comparator-v4.34
git checkout -q v4.34.0
echo "comparator tag v4.34.0 = $(git rev-parse HEAD); toolchain file was: $(cat lean-toolchain)"
echo "leanprover/lean4:v4.34.1" > lean-toolchain
lake build 2>&1 | tail -3
grep -A3 '"name": "lean4export"' lake-manifest.json | head -4 || true
cp .lake/build/bin/comparator /usr/local/bin/comparator
ls -l /usr/local/bin/comparator
