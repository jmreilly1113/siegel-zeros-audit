#!/usr/bin/env bash
# Extended replay: run a nanoda binary DIRECTLY on a retained export, at nanoda's default stack (no ulimit change, no
# RUST_MIN_STACK), as checker inside the same network-blocking systemd-run wrapper as 67_corpus_run.sh. The nanoda
# config is the one Comparator wrote for the crashed run (captured by 111_memsample.py), with export_file_path pointed
# at the retained copy; nothing else changed. Comparator runs nanoda under landrun; this direct run does not (as in
# 107_run.sh nanoda mode). nanoda is not modified. Run as root.
# Usage: 113_nanoda_direct.sh <run name> <nanoda config json> <binary> <timeout seconds> <log path>
set -u
NAME=$1; NC=$2; BIN=$3; TMO=$4; LOG=$5
L=/home/checker/math/lean
{
echo "== nanoda direct run $NAME  $(date '+%F %T')"
echo "binary: $BIN sha256 $(sha256sum $BIN | cut -c1-64)"
echo "nanoda config: $NC"; cat $NC; echo
E=$(python3 -I -c "import json,sys; print(json.load(open(sys.argv[1]))['export_file_path'])" $NC)
echo "export: $E bytes $(stat -c %s $E) sha256 $(sha256sum $E | cut -c1-64)"
echo "== clone: HEAD $(sudo -u checker git -C /home/checker/math rev-parse HEAD); status: $(sudo -u checker git -C /home/checker/math status --short | tr '\n' ' ')"
UID_C=$(id -u checker)
T0=$(date +%s)
sudo -u checker -H env XDG_RUNTIME_DIR=/run/user/$UID_C DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$UID_C/bus bash -lc "
export PATH=\"\$HOME/.elan/bin:/usr/local/bin:\$PATH\"
cd $L
systemd-run --property=\"RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET\" --user --wait --pipe --collect -E PATH=\"\$PATH\" --working-directory \"\$(pwd)\" -- timeout --signal=TERM --kill-after=60 $TMO bash -c 'echo \"INNER ulimit -s: \$(ulimit -s); RUST_MIN_STACK=\${RUST_MIN_STACK:-unset}\"; exec $BIN $NC'
echo \"NANODA EXIT CODE: \$?\"
" 2>&1 | grep -v 'has local changes'
echo "DURATION_SECONDS: $(( $(date +%s) - T0 ))"
} 2>&1 | cat > $LOG
sync
