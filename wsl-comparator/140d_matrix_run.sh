#!/usr/bin/env bash
# 140d_matrix_run.sh (2026-10-26): identical to 140_matrix_run.sh except the deny list names every address family defined by kernel 5.15.167.4 (include/linux/socket.h, AF_UNIX=1 .. AF_MCTP=45; adds AF_VSOCK, AF_ALG and the rest). Methods change: docs/log.md 2026-10-26.
# nanoda version matrix (2026-10-26, UNOFFICIAL): run ONE nanoda binary directly on ONE export, as checker, in a
# network-blocked systemd-run unit with a hard memory cap and a timeout. Run as root.
# Why not systemd-run -p MemoryMax: WSL here is cgroup hybrid (memory controller on v1); systemd 255 does not enforce
# MemoryMax there (tested 2026-10-26: a 600 MB allocation under MemoryMax=200M ran to the end, user and system units),
# and MemoryLimit= caps RAM only (the same allocation swapped past it). A system unit does get its own v1 memory cgroup
# (memory:/system.slice/run-uN.service) but cannot move to another one (EINVAL). So the unit's shell, still root, sets
# memory.limit_in_bytes = memory.memsw.limit_in_bytes = MEMMAX (RAM + swap together) on its own v1 cgroup, runs
# nanoda as a child under setpriv (uid/gid checker, no_new_privs) and /usr/bin/time -v timeout, then prints the
# cgroup's peak usage, failcnt and oom_kill count before the unit ends. Network: RestrictAddressFamilies as in
# 113_nanoda_direct.sh. Peak RSS: "Maximum resident set size" from time -v (wait4 rusage of the nanoda process);
# the cgroup max_usage also counts the page cache of the export.
# Usage: 140_matrix_run.sh <run name> <nanoda config json> <binary> <log path> [timeout s, default 1800] [memmax, default 16G]
set -u
NAME=$1; NC=$2; BIN=$3; LOG=$4; TMO=${5:-1800}; MEMMAX=${6:-16G}
UID_C=$(id -u checker); GID_C=$(id -g checker)
{
echo "== nanoda matrix run $NAME  $(date '+%F %T')  (UNOFFICIAL)"
echo "binary: $BIN sha256 $(sha256sum $BIN | cut -c1-64)"
echo "nanoda config: $NC"; cat $NC; echo
E=$(python3 -I -c "import json,sys; print(json.load(open(sys.argv[1]))['export_file_path'])" $NC)
echo "export: $E bytes $(stat -c %s $E) sha256 $(sha256sum $E | cut -c1-64)"
echo "limits: timeout ${TMO} s (TERM, KILL after 60 s); unit's v1 memory cgroup limit = memsw limit = $MEMMAX; network blocked"
T0=$(date +%s)
systemd-run --wait --pipe --collect --property="RestrictAddressFamilies=~AF_UNIX AF_INET AF_AX25 AF_IPX AF_APPLETALK AF_NETROM AF_BRIDGE AF_ATMPVC AF_X25 AF_INET6 AF_ROSE AF_DECnet AF_NETBEUI AF_SECURITY AF_KEY AF_NETLINK AF_PACKET AF_ASH AF_ECONET AF_ATMSVC AF_RDS AF_SNA AF_IRDA AF_PPPOX AF_WANPIPE AF_LLC AF_IB AF_MPLS AF_CAN AF_TIPC AF_BLUETOOTH AF_IUCV AF_RXRPC AF_ISDN AF_PHONET AF_IEEE802154 AF_CAIF AF_ALG AF_NFC AF_VSOCK AF_KCM AF_QIPCRTR AF_SMC AF_XDP AF_MCTP" \
  -E PATH=/usr/local/bin:/usr/bin:/bin --working-directory /home/checker -- /bin/bash -c "
G=/sys/fs/cgroup/memory\$(grep ':memory:' /proc/self/cgroup | cut -d: -f3)
echo $MEMMAX > \$G/memory.limit_in_bytes && echo $MEMMAX > \$G/memory.memsw.limit_in_bytes || { echo 'SETUP ERROR: memory limit'; exit 3; }
echo \"memcg \$G limit \$(cat \$G/memory.limit_in_bytes) memsw \$(cat \$G/memory.memsw.limit_in_bytes)\"
setpriv --reuid=$UID_C --regid=$GID_C --init-groups --no-new-privs env HOME=/home/checker USER=checker \
  /usr/bin/time -v timeout --signal=TERM --kill-after=60 $TMO bash -c 'echo \"INNER uid \$(id -u) ulimit -s: \$(ulimit -s); RUST_MIN_STACK=\${RUST_MIN_STACK:-unset}\"; exec $BIN $NC'
R=\$?
echo \"cgroup: max_usage_in_bytes \$(cat \$G/memory.max_usage_in_bytes) memsw.max_usage_in_bytes \$(cat \$G/memory.memsw.max_usage_in_bytes) failcnt \$(cat \$G/memory.failcnt) oom_kill \$(awk '/^oom_kill /{print \$2}' \$G/memory.oom_control)\"
exit \$R
" 2>&1
echo "SYSTEMD-RUN EXIT CODE: $?"
echo "DURATION_SECONDS: $(( $(date +%s) - T0 ))"
} 2>&1 | grep -v 'has local changes' > $LOG
# Classify from the log. Categories: pass, stack-overflow, timeout, oom (resource), other (needs a human look).
RCN=$(grep -oP '^\s*Exit status: \K[0-9]+' $LOG | tail -1)
SIG=$(grep -oP 'Command terminated by signal \K[0-9]+' $LOG | tail -1); [ -n "$SIG" ] && RCN="signal $SIG"
if grep -q '^SETUP ERROR' $LOG; then O="setup-error"
elif grep -q 'oom_kill [1-9]' $LOG; then O="oom (resource: memory cap $MEMMAX reached; not a verdict on the proof)"
elif grep -q 'has overflowed its stack' $LOG; then O="stack-overflow ($(grep -o "thread '[^']*' ([0-9]*) has overflowed\|thread '[^']*' has overflowed" $LOG | head -1))"
elif [ "${RCN:-}" = 124 ] || [ "${RCN:-}" = 137 ]; then O="timeout (${TMO} s)"
elif [ "${RCN:-}" = 0 ]; then O="pass"
else O="other (exit ${RCN:-?}): $(sed -n '/^INNER uid/,/Command being timed/p' $LOG | grep -v '^INNER uid\|Command being timed' | tail -3 | tr '\n' ' ')"
fi
MRSS=$(grep -oP 'Maximum resident set size \(kbytes\): \K[0-9]+' $LOG)
WALL=$(grep -oP '^DURATION_SECONDS: \K[0-9]+' $LOG)
echo "OUTCOME: $O; exit ${RCN:-?}; wall ${WALL:-?} s; max RSS ${MRSS:-?} kB" | tee -a $LOG
