#!/usr/bin/env bash
# UNOFFICIAL post-fix run: same as 67_corpus_run.sh / 79_corpus_run_bigstack.sh, but the comparator uses the post-fix
# nanoda (COMPARATOR_NANODA=/opt/nanoda-postfix/nanoda_bin, nanoda_lib f67473b, built by 97). Config, sandbox, timeout
# and clone are as in the corpus runs. Usage: 98_postfix_run.sh <run name> <config json> <timeout seconds> <log path>
set -u
NAME=$1; CFG=$2; TMO=$3; LOG=$4
L=/home/checker/math/lean; NB=/opt/nanoda-postfix/nanoda_bin
{
echo "== UNOFFICIAL post-fix run $NAME (nanoda_lib f67473b, not the corpus-pinned 3a24072)  $(date '+%F %T')"
echo "nanoda_bin: $NB sha256 $(sha256sum $NB | cut -c1-64)"
echo "config: $CFG"; cat $CFG
CH=$(python3 -c "import json,sys; print(json.load(open('$CFG'))['challenge_module'].split('.')[-1])")
SHIP=$L/ComparatorChallenges/$CH.json
if [ -f "$SHIP" ]; then echo "== diff shipped $SHIP vs this config"; diff <(python3 -m json.tool $SHIP) <(python3 -m json.tool $CFG); echo "(diff exit $?)"; fi
echo "== clone: HEAD $(sudo -u checker git -C /home/checker/math rev-parse HEAD); status: $(sudo -u checker git -C /home/checker/math status --short | tr '\n' ' ')"
UID_C=$(id -u checker)
T0=$(date +%s)
sudo -u checker -H env XDG_RUNTIME_DIR=/run/user/$UID_C DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$UID_C/bus bash -lc "
export PATH=\"\$HOME/.elan/bin:/usr/local/bin:\$PATH\"
cd $L
systemd-run --property=\"RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET\" --user --wait --pipe --collect -E PATH=\"\$PATH\" -E COMPARATOR_NANODA=$NB --working-directory \"\$(pwd)\" -- timeout --signal=TERM --kill-after=60 $TMO bash -c 'lake env comparator $CFG'
echo \"COMPARATOR EXIT CODE: \$?\"
" 2>&1 | grep -v 'has local changes'
echo "DURATION_SECONDS: $(( $(date +%s) - T0 ))"
} 2>&1 | cat > $LOG
sync
