#!/usr/bin/env bash
# Runs one command as checker in /home/checker/math/lean inside the same network-blocking systemd-run wrapper as
# 67_corpus_run.sh, with LEAN_NUM_THREADS=<threads> and a timeout. Run as root.
# Usage: 75_sbx.sh <timeout seconds> <threads> '<command for bash -c>'
set -u
TMO=$1; THR=$2; CMD=$3
L=/home/checker/math/lean
UID_C=$(id -u checker)
sudo -u checker -H env XDG_RUNTIME_DIR=/run/user/$UID_C DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$UID_C/bus bash -lc "
export PATH=\"\$HOME/.elan/bin:/usr/local/bin:\$PATH\"; cd $L
systemd-run --property=\"RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET\" --user --wait --pipe --collect -E PATH=\"\$PATH\" -E LEAN_NUM_THREADS=$THR --working-directory \"\$(pwd)\" -- timeout --signal=TERM --kill-after=60 $TMO bash -c '$CMD'
echo \"SANDBOX EXIT CODE: \$?\"" 2>&1 | grep -v 'has local changes' | grep -v '^✔ \['
