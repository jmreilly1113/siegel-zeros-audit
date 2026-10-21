#!/usr/bin/env bash
# Paper prep (2026-10-20): runs INSIDE the corpus sandbox (systemd-run --user unit, as checker), via 107_run.sh.
# Logs the identity and sandbox state of the unit, then execs the payload.
# Usage: 107_inner.sh <mode> <arg>
#   probe  <config>  : id + /proc/self/status + network-block self-test, then `lake env comparator <config>`
#   plain  <config>  : id + status, then `lake env comparator <config>`
#   bigenv <config>  : ulimit -s unlimited and RUST_MIN_STACK=1073741824, then `lake env comparator <config>`
#   nanoda <nanoda config> <binary> : ulimit -s unlimited and RUST_MIN_STACK=1073741824, then exec <binary> <config>
set -u
MODE=$1; ARG=$2
echo "INNER id: $(id)"
grep -E '^(Uid|Gid|Groups|CapPrm|CapEff|CapAmb|NoNewPrivs):' /proc/self/status | sed 's/^/INNER /'
echo "INNER cgroup: $(tail -1 /proc/self/cgroup)"
echo "INNER kernel: $(uname -r)"
if [ "$MODE" = probe ]; then
  echo -n "INNER netblock tcp 1.1.1.1:443: "; (timeout 5 bash -c 'exec 3<>/dev/tcp/1.1.1.1/443' && echo OPEN) 2>&1 | tail -1
  echo -n "INNER netblock python AF_INET udp socket: "; python3 -I -c 'import socket; socket.socket(socket.AF_INET, socket.SOCK_DGRAM); print("created")' 2>&1 | tail -1
  echo -n "INNER netblock python AF_INET6 socket: "; python3 -I -c 'import socket; socket.socket(socket.AF_INET6, socket.SOCK_STREAM); print("created")' 2>&1 | tail -1
  echo -n "INNER netblock python AF_UNIX socket: "; python3 -I -c 'import socket; socket.socket(socket.AF_UNIX); print("created")' 2>&1 | tail -1
fi
if [ "$MODE" = bigenv ] || [ "$MODE" = nanoda ]; then
  ulimit -s unlimited
  export RUST_MIN_STACK=1073741824
fi
echo "INNER ulimit -s: $(ulimit -s); ulimit -Hs: $(ulimit -Hs); RUST_MIN_STACK=${RUST_MIN_STACK:-unset}"
case $MODE in
  probe|plain|bigenv) exec lake env comparator "$ARG" ;;
  nanoda) exec "$3" "$ARG" ;;
esac
