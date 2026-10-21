#!/usr/bin/env bash
# Paper prep 2 (2026-10-20): 107_run.sh with the lean dir taken from L_OVERRIDE (default /home/checker/math/lean) and the payload in 108_inner.sh (same sudo + systemd-run
# network-blocking wrapper, same timeout handling). Run as root.
# Usage: 107_run.sh <run name> <mode> <config> <timeout seconds> <log path> [<nanoda binary>]
#   mode: probe (comparator on <config>), timed (<binary> directly on nanoda <config>)
set -u
NAME=$1; MODE=$2; CFG=$3; TMO=$4; LOG=$5; BIN=${6:-}
W=/mnt/c/Users/Work/dev/siegel/wsl-comparator
L=${L_OVERRIDE:-/home/checker/math/lean}; REPO=$(dirname $L)
{
echo "== run $NAME  mode $MODE  $(date '+%F %T')"
echo "config: $CFG"; cat $CFG; echo
if [ "$MODE" != timed ]; then
  CH=$(python3 -c "import json,sys; print(json.load(open('$CFG'))['challenge_module'].split('.')[-1])")
  SHIP=$L/ComparatorChallenges/$CH.json
  if [ -f "$SHIP" ]; then echo "== diff shipped $SHIP vs this config"; diff <(python3 -m json.tool $SHIP) <(python3 -m json.tool $CFG); echo "(diff exit $?)"; fi
else
  echo "binary: $BIN sha256 $(sha256sum $BIN | cut -c1-64)"
fi
echo "== clone: HEAD $(sudo -u checker git -C $REPO rev-parse HEAD); status: $(sudo -u checker git -C $REPO status --short | tr '\n' ' ')"
echo "disk used before: $(df -BG --output=used / | tail -1 | tr -d ' ')"
UID_C=$(id -u checker)
T0=$(date +%s)
sudo -u checker -H env XDG_RUNTIME_DIR=/run/user/$UID_C DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$UID_C/bus bash -lc "
export PATH=\"\$HOME/.elan/bin:/usr/local/bin:\$PATH\"
cd $L
systemd-run --property=\"RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET\" --user --wait --pipe --collect -E PATH=\"\$PATH\" --working-directory \"\$(pwd)\" -- timeout --signal=TERM --kill-after=60 $TMO bash $W/108_inner.sh $MODE $CFG $BIN
echo \"COMPARATOR EXIT CODE: \$?\"
" 2>&1 | grep -v 'has local changes'
T1=$(date +%s)
echo "DURATION_SECONDS: $((T1-T0))"
echo "disk used after: $(df -BG --output=used / | tail -1 | tr -d ' ')"
} 2>&1 | cat > $LOG
sync
