#!/usr/bin/env bash
# 2026-10-26 t25: socket(family, type, 0) for every family 1..AF_MAX (46, kernel 5.15.167.4 include/linux/socket.h) and
# SOCK_STREAM / SOCK_DGRAM / SOCK_RAW, inside (a) a user unit through 75d_sbx.sh, (b) a system unit with the 140d_matrix_run.sh
# property and setpriv to checker, and (c) as checker outside any unit (control). Pass: every call inside (a) and (b) fails with
# errno 97 (EAFNOSUPPORT), the error RestrictAddressFamilies' seccomp filter returns.
W=/mnt/c/Users/Work/dev/siegel/wsl-comparator; T=/tmp/t25; rm -rf $T; mkdir -p $T; chmod 777 $T
cat > $T/probe.py <<'PY'
import socket, errno, os
for fam in range(1, 47):
    row = []
    for tn, t in (("STREAM", socket.SOCK_STREAM), ("DGRAM", socket.SOCK_DGRAM), ("RAW", socket.SOCK_RAW)):
        try:
            s = socket.socket(fam, t, 0); s.close(); row.append(f"{tn}=OK")
        except OSError as e:
            row.append(f"{tn}={e.errno}({errno.errorcode.get(e.errno, '?')})")
    print("FAM", fam, " ".join(row))
PY
chmod 644 $T/probe.py
P=$(grep -o 'RestrictAddressFamilies=~[A-Za-z0-9_ ]*' $W/140d_matrix_run.sh | head -1)
echo "== kernel $(uname -r); $(systemctl --version | head -1); $(date '+%F %T')"
echo "== property: $P"
echo "== (a) user unit via 75d_sbx.sh"
bash $W/75d_sbx.sh 120 1 "grep -E \"^(Seccomp|NoNewPrivs)\" /proc/self/status; python3 -I /tmp/t25/probe.py" > $T/a.out 2>&1; cat $T/a.out
echo "== (b) system unit, same property, setpriv to checker (140d style)"
systemd-run --wait --pipe --collect --property="$P" -E PATH=/usr/local/bin:/usr/bin:/bin --working-directory /home/checker -- /bin/bash -c "setpriv --reuid=$(id -u checker) --regid=$(id -g checker) --init-groups --no-new-privs python3 -I /tmp/t25/probe.py" > $T/b.out 2>&1; cat $T/b.out
echo "== (c) control: checker outside any unit"
sudo -u checker python3 -I /tmp/t25/probe.py > $T/c.out 2>&1; cat $T/c.out
echo "== verdict"
for x in a b; do n=$(grep -c '^FAM' $T/$x.out); bad=$(grep '^FAM' $T/$x.out | grep -v -E '^FAM [0-9]+ STREAM=97\(EAFNOSUPPORT\) DGRAM=97\(EAFNOSUPPORT\) RAW=97\(EAFNOSUPPORT\)$'); echo "($x) families probed $n; not all-97: ${bad:-none}"; grep -q '=OK' $T/$x.out && echo "($x) SUCCESS FOUND: STOP"; done
echo "(c) control: families with at least one successful socket(): $(grep '^FAM' $T/c.out | grep '=OK' | awk '{print $2}' | tr '\n' ' ')"
