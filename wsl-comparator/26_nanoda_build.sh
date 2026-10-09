#!/usr/bin/env bash
# Step 1: build nanoda_bin (pinned commit) with a current stable Rust, install to /usr/local/bin.
set -e
export HOME=/root
if [ ! -x /root/.cargo/bin/cargo ]; then curl -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal >/dev/null 2>&1; fi
. /root/.cargo/env
rustc --version; cargo --version
cd /root/tools/nanoda_lib
git checkout -q 3a2407216ee84a75f9e1aead6803d0578be06ae7
echo "nanoda commit: $(git rev-parse HEAD), Cargo version: $(grep -m1 '^version' Cargo.toml)"
cargo build --release --locked -j 6 2>&1 | tail -3
install -m 755 target/release/nanoda_bin /usr/local/bin/nanoda_bin
ls -la /usr/local/bin/nanoda_bin; sha256sum /usr/local/bin/nanoda_bin
sync
