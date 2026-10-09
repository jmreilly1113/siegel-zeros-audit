#!/usr/bin/env bash
set -euo pipefail
export PATH="$HOME/.elan/bin:$PATH"
cd /root/tools
echo "== landrun (main) go.mod go version: $(grep -m1 '^go ' landrun/go.mod)"
(cd landrun && go build -o /usr/local/bin/landrun ./cmd/landrun 2>&1 || go build -o /usr/local/bin/landrun . 2>&1) | tail -5
landrun --version 2>&1 | head -2 || true
echo "== lean4export @ v4.34.0 with toolchain v4.34.1"
cd lean4export && git checkout -q v4.34.0 && cat lean-toolchain && echo "leanprover/lean4:v4.34.1" > lean-toolchain && lake build 2>&1 | tail -3 && cd ..
ls lean4export/.lake/build/bin/
echo "== comparator @ tag v4.34.0 with toolchain v4.34.1 (it links lean4export and reads .olean files, so it must match the project's Lean)"
cd comparator && git checkout -q v4.34.0 && echo "comparator commit $(git rev-parse HEAD), toolchain file was: $(cat lean-toolchain)" && echo "leanprover/lean4:v4.34.1" > lean-toolchain && lake build 2>&1 | tail -3 && cd ..
ls comparator/.lake/build/bin/
sync
