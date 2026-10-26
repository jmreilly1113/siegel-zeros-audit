#!/usr/bin/env bash
# Network-block test (2026-10-26): same unit properties as 67_corpus_run.sh / 75_sbx.sh, as checker; plus a control outside the unit.
UID_C=$(id -u checker)
cat > /tmp/t22_probe.py <<'PY'
import socket, errno
def t(name, f):
    try: r = f(); print(f"PROBE {name}: ALLOWED {r}")
    except Exception as e: print(f"PROBE {name}: blocked/failed {type(e).__name__}: {e}")
def tcp():
    s = socket.create_connection(("1.1.1.1", 443), timeout=5); s.close(); return "connected 1.1.1.1:443"
def tcp6():
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM); s.settimeout(5); s.connect(("2606:4700:4700::1111", 443)); s.close(); return "connected"
t("tcp connect 1.1.1.1:443", tcp)
t("tcp6 connect", tcp6)
t("dns getaddrinfo github.com", lambda: socket.getaddrinfo("github.com", 443)[0][4])
t("udp socket", lambda: socket.socket(socket.AF_INET, socket.SOCK_DGRAM) and "created")
t("unix socket", lambda: socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) and "created")
t("netlink socket", lambda: socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, 0) and "created")
t("packet socket", lambda: socket.socket(socket.AF_PACKET, socket.SOCK_RAW) and "created")
VS = getattr(socket, "AF_VSOCK", 40)
t("vsock socket create", lambda: socket.socket(VS, socket.SOCK_STREAM) and "created")
def vsock_host():
    s = socket.socket(VS, socket.SOCK_STREAM); s.settimeout(3); s.connect((2, 50000)); return "connected to host CID 2 port 50000"
t("vsock connect host CID 2", vsock_host)
for fam, name in ((31, "AF_BLUETOOTH"), (38, "AF_ALG"), (30, "AF_TIPC"), (21, "AF_RDS"), (29, "AF_CAN"), (44, "AF_XDP")):
    t(f"{name} socket create", lambda fam=fam: socket.socket(fam, socket.SOCK_SEQPACKET if fam == 30 else socket.SOCK_RAW if fam in (29, 44) else socket.SOCK_STREAM if fam in (31,) else socket.SOCK_SEQPACKET) and "created")
PY
chmod 644 /tmp/t22_probe.py
echo "== kernel $(uname -r); systemd $(systemctl --version | head -1)"
echo "== (A) inside the unit, as checker: exact property string from 67_corpus_run.sh line 23"
sudo -u checker -H env XDG_RUNTIME_DIR=/run/user/$UID_C DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$UID_C/bus bash -lc '
systemd-run --property="RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET" --user --wait --pipe --collect -- bash -c "id -u; grep -E \"^(Seccomp|NoNewPrivs)\" /proc/self/status; python3 -I /tmp/t22_probe.py; timeout 10 curl -sS -m 8 -o /dev/null -w \"curl https://github.com http %{http_code}\n\" https://github.com 2>&1 | head -2; getent hosts github.com || echo \"getent hosts github.com: no result (exit \$?)\"; (exec 3<>/dev/tcp/1.1.1.1/443) 2>&1 | head -1"
'
echo "== (B) control: same checks as checker, outside any unit"
sudo -u checker -H bash -c 'python3 -I /tmp/t22_probe.py 2>&1 | grep -E "tcp connect|dns|vsock"; timeout 10 curl -sS -m 8 -o /dev/null -w "curl https://github.com http %{http_code}\n" https://github.com 2>&1 | head -1'
rm -f /tmp/t22_probe.py
