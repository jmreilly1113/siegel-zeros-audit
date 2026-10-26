#!/usr/bin/env bash
# 75d_sbx.sh (2026-10-26): identical to 75_sbx.sh except the deny list names every address family defined by kernel 5.15.167.4 (include/linux/socket.h, AF_UNIX=1 .. AF_MCTP=45; adds AF_VSOCK, AF_ALG and the rest). Methods change: docs/log.md 2026-10-26.
# Runs one command as checker in /home/checker/math/lean inside the same network-blocking systemd-run wrapper as
# 67_corpus_run.sh, with LEAN_NUM_THREADS=<threads> and a timeout. Run as root.
# Usage: 75_sbx.sh <timeout seconds> <threads> '<command for bash -c>'
set -u
TMO=$1; THR=$2; CMD=$3
L=/home/checker/math/lean
UID_C=$(id -u checker)
sudo -u checker -H env XDG_RUNTIME_DIR=/run/user/$UID_C DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$UID_C/bus bash -lc "
export PATH=\"\$HOME/.elan/bin:/usr/local/bin:\$PATH\"; cd $L
systemd-run --property=\"RestrictAddressFamilies=~AF_UNIX AF_INET AF_AX25 AF_IPX AF_APPLETALK AF_NETROM AF_BRIDGE AF_ATMPVC AF_X25 AF_INET6 AF_ROSE AF_DECnet AF_NETBEUI AF_SECURITY AF_KEY AF_NETLINK AF_PACKET AF_ASH AF_ECONET AF_ATMSVC AF_RDS AF_SNA AF_IRDA AF_PPPOX AF_WANPIPE AF_LLC AF_IB AF_MPLS AF_CAN AF_TIPC AF_BLUETOOTH AF_IUCV AF_RXRPC AF_ISDN AF_PHONET AF_IEEE802154 AF_CAIF AF_ALG AF_NFC AF_VSOCK AF_KCM AF_QIPCRTR AF_SMC AF_XDP AF_MCTP\" --user --wait --pipe --collect -E PATH=\"\$PATH\" -E LEAN_NUM_THREADS=$THR --working-directory \"\$(pwd)\" -- timeout --signal=TERM --kill-after=60 $TMO bash -c '$CMD'
echo \"SANDBOX EXIT CODE: \$?\"" 2>&1 | grep -v 'has local changes' | grep -v '^✔ \['
