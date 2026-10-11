#!/usr/bin/env bash
# Corpus checks: one official comparator run, as checker, in /home/checker/math/lean, inside the same systemd-run
# sandbox as 29_comparator_nanoda.sh (all network sockets blocked), with a timeout.
# Usage: 67_corpus_run.sh <run name> <config json (absolute path, readable by checker)> <timeout seconds> <log path>
# Prints: config, its diff against the shipped config of the same challenge, clone state, verdict lines,
# exit code, duration and the last 50 lines. One writer (cat) per log.
set -u
NAME=$1; CFG=$2; TMO=$3; LOG=$4
L=/home/checker/math/lean
{
echo "== run $NAME  $(date '+%F %T')"
echo "config: $CFG"; cat $CFG
CH=$(python3 -c "import json,sys; print(json.load(open('$CFG'))['challenge_module'].split('.')[-1])")
SHIP=$L/ComparatorChallenges/$CH.json
if [ -f "$SHIP" ]; then echo "== diff shipped $SHIP vs this config"; diff <(python3 -m json.tool $SHIP) <(python3 -m json.tool $CFG); echo "(diff exit $?)"; else echo "== no shipped config named $CH.json (copied challenge)"; fi
echo "== clone: HEAD $(sudo -u checker git -C /home/checker/math rev-parse HEAD); status: $(sudo -u checker git -C /home/checker/math status --short | tr '\n' ' ')"
echo "disk used before: $(df -BG --output=used / | tail -1 | tr -d ' ')"
UID_C=$(id -u checker)
T0=$(date +%s)
sudo -u checker -H env XDG_RUNTIME_DIR=/run/user/$UID_C DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$UID_C/bus bash -lc "
export PATH=\"\$HOME/.elan/bin:/usr/local/bin:\$PATH\"
cd $L
systemd-run --property=\"RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET\" --user --wait --pipe --collect -E PATH=\"\$PATH\" --working-directory \"\$(pwd)\" -- timeout --signal=TERM --kill-after=60 $TMO bash -c 'lake env comparator $CFG'
echo \"COMPARATOR EXIT CODE: \$?\"
" 2>&1 | grep -v 'has local changes'
T1=$(date +%s)
echo "DURATION_SECONDS: $((T1-T0))"
echo "disk used after: $(df -BG --output=used / | tail -1 | tr -d ' ')"
} 2>&1 | cat > $LOG
sync
