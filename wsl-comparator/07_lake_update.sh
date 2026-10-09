#!/usr/bin/env bash
# Runs as root; does the work as the unprivileged user 'checker'.
sudo -u checker -H bash -lc '
export PATH="$HOME/.elan/bin:$PATH"
cd $HOME/math/lean
date; echo "== lake update"
lake update 2>&1 | grep -v "^\s*$" | tail -40
echo "lake update exit: ${PIPESTATUS[0]}"
echo "== lake exe cache get"
lake exe cache get 2>&1 | tr "\r" "\n" | grep -v "^Downloaded:" | tail -8
echo "cache exit: ${PIPESTATUS[0]}"
du -sh .lake/packages; ls .lake/packages | wc -l
git -C $HOME/math status --short | head
date
'
sync
