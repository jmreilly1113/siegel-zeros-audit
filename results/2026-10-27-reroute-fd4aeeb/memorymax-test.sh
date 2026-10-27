#!/usr/bin/env bash
# MemoryMax non-enforcement test (2026-10-26/27 rerun of the 2026-10-26 test): does MemoryMax=200M stop a 600 MB allocation? (a) user unit as checker, (b) system unit User=checker; then (c) the v1-cgroup cap that 140/140d/67d use instead.
UID_C=$(id -u checker); P='import time; b=bytearray(600*1024*1024); b[::4096]=b"x"*len(b[::4096]); time.sleep(2); print("ALLOCATED 600MB, not killed")'
echo "systemd $(systemctl --version | head -1)"; stat -fc %T /sys/fs/cgroup; ls /sys/fs/cgroup
echo "== (a) user unit"
sudo -u checker -H env XDG_RUNTIME_DIR=/run/user/$UID_C DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$UID_C/bus systemd-run --user --wait --pipe --collect -p MemoryMax=200M -p MemorySwapMax=0 -- python3 -I -c "$P"; echo "exit $?"
echo "== (b) system unit"
systemd-run --wait --pipe --collect -p User=checker -p MemoryMax=200M -p MemorySwapMax=0 -p "RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET" -- python3 -I -c "$P"; echo "exit $?"
echo "== (b2) system unit network check"
systemd-run --wait --pipe --collect -p User=checker -p "RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET" -- python3 -I -c 'import socket
try: socket.socket(); print("SOCKET OPENED")
except Exception as e: print("blocked:", e)'
echo "== (c) the workaround: system unit sets its own v1 memory cgroup limit = memsw = 200M, then the allocation as checker"
systemd-run --wait --pipe --collect -- /bin/bash -c "G=/sys/fs/cgroup/memory\$(grep ':memory:' /proc/self/cgroup | cut -d: -f3); echo 200M > \$G/memory.limit_in_bytes && echo 200M > \$G/memory.memsw.limit_in_bytes && echo limit \$(cat \$G/memory.limit_in_bytes); setpriv --reuid=$(id -u checker) --regid=$(id -g checker) --init-groups --no-new-privs python3 -I -c '$P'; echo inner exit \$?"; echo "exit $?"
