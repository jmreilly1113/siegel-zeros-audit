#!/usr/bin/env bash
# Non-official diagnostic tool: a copy of nanoda_lib (3a24072) with the checker thread stack raised from 16 MiB to
# 512 MiB (src/lib.rs STACK_SIZE). The original /root/tools/nanoda_lib and /usr/local/bin/nanoda_bin are not touched.
# Built offline with the cached crates. Output: /opt/nanoda-diag/nanoda_bin_bigstack. Run as root.
set -eu
SRC=/root/tools/nanoda_lib; DST=/root/tools/nanoda_lib-bigstack-diag
rm -rf $DST; cp -a $SRC $DST
sed -i 's/^pub(crate) const STACK_SIZE: usize = 16_777_216;/pub(crate) const STACK_SIZE: usize = 536_870_912;/' $DST/src/lib.rs
echo "== diff vs original (src only)"; diff -r $SRC/src $DST/src || true
echo "== git HEAD of the copy: $(git -C $DST rev-parse HEAD); status: $(git -C $DST status --short | tr '\n' ' ')"
cd $DST && nice -n 10 /root/.cargo/bin/cargo build --release --offline 2>&1 | tail -5
mkdir -p /opt/nanoda-diag && cp $DST/target/release/nanoda_bin /opt/nanoda-diag/nanoda_bin_bigstack && chmod 755 /opt/nanoda-diag/nanoda_bin_bigstack
echo "== built: $(ls -la /opt/nanoda-diag/nanoda_bin_bigstack); sha256 $(sha256sum /opt/nanoda-diag/nanoda_bin_bigstack | cut -c1-64)"
echo "== official: sha256 $(sha256sum /usr/local/bin/nanoda_bin | cut -c1-64) (unchanged)"
/opt/nanoda-diag/nanoda_bin_bigstack --version 2>&1 | head -2 || true
