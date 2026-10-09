#!/usr/bin/env bash
# Steps 1+2: comparator with nanoda as a second kernel (our config copy; only change vs the repo's: enable_nanoda true),
# under the README's systemd-run wrapper hardened to also block IP/netlink/packet sockets (see 28_netblock_probe.log).
set -e
install -o checker -g checker -m 644 /mnt/c/Users/Work/dev/siegel/wsl-comparator/SiegelZeros-nanoda.json /home/checker/SiegelZeros-nanoda.json
diff <(python3 -m json.tool /home/checker/math/lean/ComparatorChallenges/SiegelZeros.json) <(python3 -m json.tool /home/checker/SiegelZeros-nanoda.json) || true
sync
UID_C=$(id -u checker)
cd /home/checker/math/lean
sudo -u checker -H env XDG_RUNTIME_DIR=/run/user/$UID_C DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$UID_C/bus bash -lc '
export PATH="$HOME/.elan/bin:/usr/local/bin:$PATH"
cd $HOME/math/lean
echo "user: $(id -un)"; echo "nanoda_bin: $(which nanoda_bin) $(sha256sum $(which nanoda_bin) | cut -c1-16)"; date
systemd-run --property="RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET" --user --wait --pipe --collect -E PATH="$PATH" --working-directory "$(pwd)" -- bash -c "lake env comparator /home/checker/SiegelZeros-nanoda.json"
echo "COMPARATOR EXIT CODE: $?"
date
'
