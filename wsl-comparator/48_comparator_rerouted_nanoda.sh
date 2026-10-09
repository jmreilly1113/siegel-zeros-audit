#!/usr/bin/env bash
# Plan step 3d: official comparator on the rerouted clone (math-rerouted), with nanoda as a second kernel.
# Same as 29_comparator_nanoda.sh (our config copy: only change vs the repo's is enable_nanoda true; systemd-run
# sandbox with IP/netlink/packet sockets blocked), but in /home/checker/math-rerouted/lean. All output goes
# through one writer (cat) so the script's own lines are not overwritten in the log.
set -e
R=/home/checker/math-rerouted/lean
install -o checker -g checker -m 644 /mnt/c/Users/Work/dev/siegel/wsl-comparator/SiegelZeros-nanoda.json /home/checker/SiegelZeros-nanoda.json
{
echo "== config diff vs the clone's own ComparatorChallenges/SiegelZeros.json"
diff <(python3 -m json.tool $R/ComparatorChallenges/SiegelZeros.json) <(python3 -m json.tool /home/checker/SiegelZeros-nanoda.json) || true
echo "== clone state"; cd $R; echo "HEAD $(sudo -u checker git rev-parse HEAD)"; sudo -u checker git status --short
echo "challenge file sha256: $(sha256sum ComparatorChallenges/SiegelZeros.lean | cut -c1-64), blob at HEAD: $(sudo -u checker git rev-parse HEAD:lean/ComparatorChallenges/SiegelZeros.lean)"
sync
UID_C=$(id -u checker)
sudo -u checker -H env XDG_RUNTIME_DIR=/run/user/$UID_C DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$UID_C/bus bash -lc '
export PATH="$HOME/.elan/bin:/usr/local/bin:$PATH"
cd $HOME/math-rerouted/lean
echo "user: $(id -un)"; echo "comparator: $(which comparator) $(sha256sum $(which comparator) | cut -c1-16)"; echo "nanoda_bin: $(which nanoda_bin) $(sha256sum $(which nanoda_bin) | cut -c1-16)"; echo "lean4export: $(which lean4export)"; echo "toolchain: $(cat lean-toolchain)"; date
systemd-run --property="RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET" --user --wait --pipe --collect -E PATH="$PATH" --working-directory "$(pwd)" -- bash -c "lake env comparator /home/checker/SiegelZeros-nanoda.json"
echo "COMPARATOR EXIT CODE: $?"
date
'
} 2>&1 | cat
sync
