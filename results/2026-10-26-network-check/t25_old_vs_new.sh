# t25 probe under the OLD property (75_sbx.sh) for comparison, plus SOCK_SEQPACKET for AF_ALG under old and new
W=/mnt/c/Users/Work/dev/siegel/wsl-comparator
cat > /tmp/t25/seq.py <<'PY'
import socket, errno
for fam in (38, 40, 24):
    try: socket.socket(fam, socket.SOCK_SEQPACKET, 0).close(); print("SEQPACKET", fam, "OK")
    except OSError as e: print("SEQPACKET", fam, e.errno, errno.errorcode.get(e.errno))
PY
chmod 644 /tmp/t25/seq.py
echo "== old property (75_sbx.sh), families with any successful socket():"
bash $W/75_sbx.sh 120 1 "python3 -I /tmp/t25/probe.py; python3 -I /tmp/t25/seq.py" > /tmp/t25/old.out 2>&1
grep '^FAM' /tmp/t25/old.out | grep '=OK'; grep '^SEQPACKET' /tmp/t25/old.out
echo "== new property (75d_sbx.sh), SEQPACKET:"; bash $W/75d_sbx.sh 120 1 "python3 -I /tmp/t25/seq.py" 2>&1 | grep '^SEQPACKET'
echo "== control SEQPACKET:"; sudo -u checker python3 -I /tmp/t25/seq.py
