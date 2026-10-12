#!/usr/bin/env bash
# Runs inside the 73_runas_probe.sh sandbox, via `lake env`. Prints the identity and privileges of this process.
echo "inside id: $(id)"
grep -E '^(Uid|Gid|Groups|CapInh|CapPrm|CapEff|CapBnd|CapAmb|NoNewPrivs):' /proc/self/status
echo "parent: $(ps -o user=,pid=,args= -p $PPID)"
echo "cgroup: $(grep '^0::' /proc/self/cgroup)"
echo "comparator binary: $(command -v comparator) owner $(stat -c '%U:%G %a' "$(command -v comparator)")"
echo "LEAN_PATH set by lake env: ${LEAN_PATH:+yes}"
