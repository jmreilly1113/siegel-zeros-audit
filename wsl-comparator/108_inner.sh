#!/usr/bin/env bash
# Paper prep 2 (2026-10-20): runs INSIDE the corpus sandbox (systemd-run --user unit, as checker), via 108_run.sh.
# Same identity/sandbox logging as 107_inner.sh; no stack or environment changes in any mode.
# Usage: 108_inner.sh <mode> <arg> [<binary>]
#   probe <config>          : id + status + network-block self-test, then `lake env comparator <config>`
#   timed <nanoda config> <binary> : id + status, then `/usr/bin/time -v <binary> <config>` (wall time, peak RSS)
set -u
MODE=$1; ARG=$2
echo "INNER id: $(id)"
grep -E '^(Uid|Gid|Groups|CapPrm|CapEff|CapAmb|NoNewPrivs):' /proc/self/status | sed 's/^/INNER /'
echo "INNER cgroup: $(tail -1 /proc/self/cgroup)"
echo "INNER kernel: $(uname -r)"
echo "INNER cwd: $(pwd); git HEAD: $(git -C .. rev-parse HEAD 2>/dev/null)"
if [ "$MODE" = probe ]; then
  echo -n "INNER netblock tcp 1.1.1.1:443: "; (timeout 5 bash -c 'exec 3<>/dev/tcp/1.1.1.1/443' && echo OPEN) 2>&1 | tail -1
  echo -n "INNER netblock python AF_INET udp socket: "; python3 -I -c 'import socket; socket.socket(socket.AF_INET, socket.SOCK_DGRAM); print("created")' 2>&1 | tail -1
  echo -n "INNER netblock python AF_INET6 socket: "; python3 -I -c 'import socket; socket.socket(socket.AF_INET6, socket.SOCK_STREAM); print("created")' 2>&1 | tail -1
  echo -n "INNER netblock python AF_UNIX socket: "; python3 -I -c 'import socket; socket.socket(socket.AF_UNIX); print("created")' 2>&1 | tail -1
fi
echo "INNER ulimit -s: $(ulimit -s); RUST_MIN_STACK=${RUST_MIN_STACK:-unset}"
case $MODE in
  probe) exec lake env comparator "$ARG" ;;
  timed) exec /usr/bin/time -v "$3" "$ARG" ;;
esac
