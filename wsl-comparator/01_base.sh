#!/usr/bin/env bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq git curl ca-certificates build-essential golang-go zstd >/dev/null
git --version; go version; gcc --version | head -1
# elan (no default toolchain; projects pin their own)
if [ ! -x "$HOME/.elan/bin/elan" ]; then
  curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -o /tmp/elan-init.sh
  sh /tmp/elan-init.sh -y --default-toolchain none >/dev/null
fi
"$HOME/.elan/bin/elan" --version
