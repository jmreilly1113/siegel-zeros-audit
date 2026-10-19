#!/usr/bin/env bash
# UNOFFICIAL post-fix nanoda (Joe 2026-10-19, option b): a separate copy of nanoda_lib checked out at f67473b
# (master 2026-10-15, after the #49 do_nat_bin fixes; before #58, which a #57 comment says brings #55 back). Not the
# corpus-pinned version (3a24072). The original /root/tools/nanoda_lib and /usr/local/bin/nanoda_bin are not touched.
# Built with network (crates), before any comparator run. Output: /opt/nanoda-postfix/nanoda_bin. Run as root.
set -eu
export HOME=/root; . /root/.cargo/env
PIN=f67473b; SRC=/root/tools/nanoda_lib; DST=/root/tools/nanoda_lib-postfix-$PIN
OFF=$(sha256sum /usr/local/bin/nanoda_bin | cut -c1-64)
rm -rf $DST; cp -a $SRC $DST
cd $DST && git fetch -q origin && git checkout -q --detach $PIN
FULL=$(git rev-parse HEAD); case $FULL in $PIN*) ;; *) echo "checkout gave $FULL"; exit 1;; esac
echo "== nanoda postfix commit: $FULL ($(git log -1 --format='%ci %s')); Cargo version: $(grep -m1 '^version' Cargo.toml)"
echo "== STACK_SIZE: $(grep -n 'STACK_SIZE: usize' src/lib.rs)"
echo "== status: [$(git status --short | tr '\n' ' ')]"
rustc --version; cargo --version
nice -n 10 cargo build --release --locked -j 6 2>&1 | tail -3
mkdir -p /opt/nanoda-postfix && install -m 755 target/release/nanoda_bin /opt/nanoda-postfix/nanoda_bin
echo "== built: sha256 $(sha256sum /opt/nanoda-postfix/nanoda_bin | cut -c1-64)"
echo "== official /usr/local/bin/nanoda_bin: sha256 before $OFF, after $(sha256sum /usr/local/bin/nanoda_bin | cut -c1-64)"
sync
