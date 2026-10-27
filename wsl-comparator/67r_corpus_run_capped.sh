#!/usr/bin/env bash
# 67r_corpus_run_capped.sh (2026-10-26): identical to 67d_corpus_run_capped.sh except the clone directory comes from XR_L (default /home/checker/math/lean), for the fd4aeeb reroute clone.
# 67d (2026-10-26): one official comparator run, as 67_corpus_run.sh (same command `lake env comparator <config>`, same log
# lines: config, diff against the shipped config, clone state, verdict lines, exit code, duration), with two changes:
#  - the seccomp deny list names every address family of kernel 5.15.167.4 (as 75d/140d; results/2026-10-26-network-check/);
#  - a hard memory cap (RAM + swap; default 16G): a system unit that sets its own v1 memory cgroup limit (as 140d) and drops to
#    checker with setpriv (no_new_privs); HOME=/home/checker, PATH with checker's elan, working directory /home/checker/math/lean.
#    Peak memory: /usr/bin/time -v (largest single process) and the cgroup's max_usage_in_bytes (whole tree, incl. page cache).
# Usage: 67d_corpus_run_capped.sh <run name> <config json> <timeout s> <log path> [memmax, default 16G]
# XR_CMD (test hook only): replaces 'lake env comparator <config>'.
set -u
NAME=$1; CFG=$2; TMO=$3; LOG=$4; MEMMAX=${5:-16G}
L=${XR_L:-/home/checker/math/lean}; UID_C=$(id -u checker); GID_C=$(id -g checker)
CMD=${XR_CMD:-lake env comparator $CFG}
{
echo "== run $NAME  $(date '+%F %T')  (67d: full deny list, $MEMMAX cap)"
echo "config: $CFG"; cat $CFG
CH=$(python3 -c "import json,sys; print(json.load(open('$CFG'))['challenge_module'].split('.')[-1])")
SHIP=$L/ComparatorChallenges/$CH.json
if [ -f "$SHIP" ]; then echo "== diff shipped $SHIP vs this config"; diff <(python3 -m json.tool $SHIP) <(python3 -m json.tool $CFG); echo "(diff exit $?)"; else echo "== no shipped config named $CH.json (copied challenge)"; fi
echo "== clone: HEAD $(sudo -u checker git -C $L/.. rev-parse HEAD); status: $(sudo -u checker git -C $L/.. status --short | tr '\n' ' ')"
echo "disk used before: $(df -BG --output=used / | tail -1 | tr -d ' ')"
T0=$(date +%s)
systemd-run --wait --pipe --collect --property="RestrictAddressFamilies=~AF_UNIX AF_INET AF_AX25 AF_IPX AF_APPLETALK AF_NETROM AF_BRIDGE AF_ATMPVC AF_X25 AF_INET6 AF_ROSE AF_DECnet AF_NETBEUI AF_SECURITY AF_KEY AF_NETLINK AF_PACKET AF_ASH AF_ECONET AF_ATMSVC AF_RDS AF_SNA AF_IRDA AF_PPPOX AF_WANPIPE AF_LLC AF_IB AF_MPLS AF_CAN AF_TIPC AF_BLUETOOTH AF_IUCV AF_RXRPC AF_ISDN AF_PHONET AF_IEEE802154 AF_CAIF AF_ALG AF_NFC AF_VSOCK AF_KCM AF_QIPCRTR AF_SMC AF_XDP AF_MCTP" \
  -E PATH=/home/checker/.elan/bin:/usr/local/bin:/usr/bin:/bin --working-directory $L -- /bin/bash -c "
G=/sys/fs/cgroup/memory\$(grep ':memory:' /proc/self/cgroup | cut -d: -f3)
echo $MEMMAX > \$G/memory.limit_in_bytes && echo $MEMMAX > \$G/memory.memsw.limit_in_bytes || { echo 'SETUP ERROR: memory limit'; exit 3; }
echo \"memcg \$G limit \$(cat \$G/memory.limit_in_bytes) memsw \$(cat \$G/memory.memsw.limit_in_bytes)\"
setpriv --reuid=$UID_C --regid=$GID_C --init-groups --no-new-privs env HOME=/home/checker USER=checker LOGNAME=checker \
  /usr/bin/time -v timeout --signal=TERM --kill-after=60 $TMO bash -c 'echo \"INNER uid \$(id -u)\"; $CMD'
R=\$?
echo \"cgroup: max_usage_in_bytes \$(cat \$G/memory.max_usage_in_bytes) memsw.max_usage_in_bytes \$(cat \$G/memory.memsw.max_usage_in_bytes) failcnt \$(cat \$G/memory.failcnt) oom_kill \$(awk '/^oom_kill /{print \$2}' \$G/memory.oom_control)\"
echo \"COMPARATOR EXIT CODE: \$R\"
exit \$R
" 2>&1 | grep -v 'has local changes'
T1=$(date +%s)
echo "DURATION_SECONDS: $((T1-T0))"
echo "disk used after: $(df -BG --output=used / | tail -1 | tr -d ' ')"
} 2>&1 | cat > $LOG
sync
