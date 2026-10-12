#!/usr/bin/env bash
# Which user does the comparator run as? Same sudo + systemd-run wrapper as 67_corpus_run.sh, with `set -x` so the
# systemd-run command line is printed as executed, and the comparator replaced by an identity probe (73_runas_inner.sh)
# run through `lake env` (the same launcher 67 uses for `lake env comparator`). Read-only; builds nothing.
set -u
L=/home/checker/math/lean
echo "== outside, launching shell: $(id)"
echo "== checker account: $(id checker)"
echo "== sudo rights of checker (sudo -l -U checker):"; sudo -l -U checker 2>&1
echo "== systemd processes (user, pid, args):"; ps -eo user=,pid=,args= | grep '[s]ystemd' | grep -v journald
UID_C=$(id -u checker)
sudo -u checker -H env XDG_RUNTIME_DIR=/run/user/$UID_C DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$UID_C/bus bash -lc "
export PATH=\"\$HOME/.elan/bin:/usr/local/bin:\$PATH\"
cd $L
set -x
systemd-run --property=\"RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET\" --user --wait --pipe --collect -E PATH=\"\$PATH\" --working-directory \"\$(pwd)\" -- timeout --signal=TERM --kill-after=60 600 bash -c 'lake env bash /mnt/c/Users/Work/dev/siegel/wsl-comparator/73_runas_inner.sh'
set +x
echo \"PROBE EXIT CODE: \$?\"
" 2>&1 | grep -v 'has local changes'
echo "== owners of OAI .olean files written by the pilot builds (by user:group):"
find $L/.lake/build/lib/lean -name '*.olean' -newer /home/checker/math/lean/lakefile.lean -printf '%u:%g\n' | sort | uniq -c
echo "== owners of the whole build tree:"
find $L/.lake -printf '%u:%g\n' | sort | uniq -c
