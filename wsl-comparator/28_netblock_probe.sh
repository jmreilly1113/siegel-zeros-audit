#!/usr/bin/env bash
# Step 2: show that the systemd-run wrapper with RestrictAddressFamilies blocks network for the whole process tree (seccomp), and a control without it.
UID_C=$(id -u checker)
sudo -u checker -H env XDG_RUNTIME_DIR=/run/user/$UID_C DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$UID_C/bus bash -lc '
probe="echo -n \"tcp 1.1.1.1:443: \"; (timeout 5 bash -c \"exec 3<>/dev/tcp/1.1.1.1/443\" && echo OPEN) 2>&1 | tail -1; echo -n \"curl https://github.com: \"; (timeout 10 curl -sS -o /dev/null -w %{http_code} https://github.com 2>&1; echo) | tail -1; echo -n \"python udp socket: \"; python3 -c \"import socket; socket.socket(socket.AF_INET, socket.SOCK_DGRAM); print(\\\"created\\\")\" 2>&1 | tail -1; echo -n \"unix socket: \"; python3 -c \"import socket; socket.socket(socket.AF_UNIX); print(\\\"created\\\")\" 2>&1 | tail -1"
echo "== control: README wrapper (AF_UNIX only blocked)"
systemd-run --property=RestrictAddressFamilies=~AF_UNIX --user --wait --pipe --collect -q -- bash -c "$probe"
echo "== hardened wrapper: AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET blocked"
systemd-run --property="RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET" --user --wait --pipe --collect -q -- bash -c "$probe"
echo "== hardened wrapper, child of a child (landrun as in comparator)"
systemd-run --property="RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET" --user --wait --pipe --collect -q -- landrun --best-effort --ro / --rw /dev -- bash -c "$probe"
'
