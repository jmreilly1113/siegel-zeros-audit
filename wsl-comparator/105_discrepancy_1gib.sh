#!/usr/bin/env bash
# DIAGNOSTIC R3 (2026-10-20, step 2c, within the 2 h box). R1 used the official nanoda 3a24072 with comparator's config,
# which equals nealmcb's stated config except his checker stack: his kernel_pair_sweep.py ran nanoda_bin.timing with
# NANODA_STACK_MB=1024 (1 GiB), from 3a24072 with STACK_SIZE changed (tools/build_nanoda_big_stack.sh,
# tools/patches/nanoda-stack-and-decl-times.patch). R3 changes ONLY that: a copy of nanoda_lib 3a24072 with
# STACK_SIZE = 1_073_741_824, built offline; same exports, same R1 config (num_threads 4). The official binary is untouched.
# Run as root, detached. Usage: 105_discrepancy_1gib.sh <out dir>
set -u
OUT=$1; W=/mnt/c/Users/Work/dev/siegel/wsl-comparator; D=/home/checker/corpus/disc; L=/home/checker/math/lean
SRC=/root/tools/nanoda_lib; DST=/root/tools/nanoda_lib-1gib-diag; NB=/opt/nanoda-1gib-diag/nanoda_bin
log() { echo "$(date '+%F %T') $*" >> $OUT/run.log; }
stopped() { [ -f /home/checker/corpus/GUARD_STOPPED ]; }
export HOME=/root; . /root/.cargo/env
{ echo "== build $(date '+%F %T')"; rm -rf $DST; cp -a $SRC $DST
  sed -i 's/^pub(crate) const STACK_SIZE: usize = 16_777_216;/pub(crate) const STACK_SIZE: usize = 1_073_741_824;/' $DST/src/lib.rs
  echo "git HEAD of copy: $(git -C $DST rev-parse HEAD)"; echo "diff vs original src:"; diff -r $SRC/src $DST/src
  (cd $DST && cargo build --release --offline 2>&1 | tail -3)
  mkdir -p /opt/nanoda-1gib-diag && install -m 755 $DST/target/release/nanoda_bin $NB
  echo "built $NB sha256 $(sha256sum $NB | cut -c1-64)"; echo "official /usr/local/bin/nanoda_bin sha256 $(sha256sum /usr/local/bin/nanoda_bin | cut -c1-64)"
} > $OUT/R3-build.log 2>&1
[ -x $NB ] || { log "R3: build failed (R3-build.log)"; exit 1; }
log "R3 build: $(grep '^built' $OUT/R3-build.log)"
rm -f /home/checker/corpus/GUARD_STOPPED
nohup bash $W/69_corpus_guard.sh 85 1500 2 >/dev/null 2>&1 &
GD=$!
UID_C=$(id -u checker)
for N in KaplanskyFinitelyPresented GroupRingDeterminant; do
  stopped && break
  E=$D/$N.export; CF=$D/$N.R1.json
  { echo "== R3 $N: nanoda 3a24072 with STACK_SIZE 1 GiB (DIAGNOSTIC), num_threads 4, R1 config  $(date '+%F %T')"
    echo "export sha256 $(sha256sum $E | cut -c1-64)"; echo "binary: $NB sha256 $(sha256sum $NB | cut -c1-64)"
    echo "config: $(cat $CF)"; echo "command: $NB $CF"; t0=$(date +%s)
    sudo -u checker -H env XDG_RUNTIME_DIR=/run/user/$UID_C DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$UID_C/bus bash -lc "
cd $L
systemd-run --property=\"RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET\" --user --wait --pipe --collect --working-directory \"\$(pwd)\" -- timeout --signal=TERM --kill-after=60 3600 bash -c '$NB $CF'
echo \"EXIT CODE: \$?\""
    echo "WALL_SECONDS: $(( $(date +%s) - t0 ))"; } > $OUT/$N.R3.log 2>&1
  log "$N R3 (1 GiB stack, threads 4): $(grep -h -E 'EXIT CODE|overflowed|Checked|panicked' $OUT/$N.R3.log | tr '\n' ';' | cut -c1-200) $(grep WALL $OUT/$N.R3.log)"
done
kill $GD 2>/dev/null
if stopped; then echo "GUARD STOPPED $(date '+%F %T')" > $OUT/GUARD_STOPPED-R3.txt; log "R3 guard stopped"; else echo "R3 DONE $(date '+%F %T')" > $OUT/DONE-R3.txt; log "R3 end"; fi
sync
