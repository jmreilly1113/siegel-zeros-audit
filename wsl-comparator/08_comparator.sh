#!/usr/bin/env bash
# Runs as root; the comparator itself runs as the unprivileged user 'checker' under systemd-run --user.
rm -rf /home/checker/.cache/mathlib /root/.cache/mathlib
sync
UID_C=$(id -u checker)
cd /home/checker/math/lean
sudo -u checker -H env XDG_RUNTIME_DIR=/run/user/$UID_C DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$UID_C/bus bash -lc '
export PATH="$HOME/.elan/bin:/usr/local/bin:$PATH"
cd $HOME/math/lean
echo "user: $(id -un) uid=$(id -u)"; echo "comparator: $(which comparator)"; echo "lean4export: $(which lean4export)"; echo "landrun: $(which landrun) $(landrun --version 2>&1 | head -1)"
echo "lean toolchain: $(cat lean-toolchain)"; date
systemd-run --property=RestrictAddressFamilies=~AF_UNIX --user --wait --pipe --collect -E PATH="$PATH" --working-directory "$(pwd)" -- bash -c "lake env comparator ComparatorChallenges/SiegelZeros.json"
echo "COMPARATOR EXIT CODE: $?"
date
'
