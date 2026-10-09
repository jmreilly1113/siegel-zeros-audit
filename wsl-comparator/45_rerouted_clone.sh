#!/usr/bin/env bash
# Plan step 3d: fresh clone of openai/math at adc7f12 for the rerouted comparator run, as user 'checker'.
# Same steps as 06_user_clone.sh (clone + checkout) and 07_lake_update.sh (lake update, which applies
# lean/patches/*.patch, and the Mathlib cache), into a separate directory so the original clone is untouched.
set -u
sudo -u checker -H bash -lc '
set -u
export PATH="$HOME/.elan/bin:$PATH"
cd $HOME
if [ -d math-rerouted ]; then echo "math-rerouted already exists; stopping"; exit 1; fi
date; git clone -q https://github.com/openai/math math-rerouted
cd math-rerouted && git checkout -q adc7f1241b42e322a6451854ab7e4b4c146bf78a
echo "openai/math HEAD: $(git rev-parse HEAD); autocrlf=$(git config core.autocrlf || echo unset); dirty files: $(git status --short | wc -l)"
echo "challenge blob: $(git rev-parse HEAD:lean/ComparatorChallenges/SiegelZeros.lean) json: $(cat lean/ComparatorChallenges/SiegelZeros.json | tr -d " \n")"
cd lean
date; echo "== lake update"
lake update 2>&1 | grep -v "^\s*$" | grep -v "has local changes" | tail -40
echo "lake update exit: ${PIPESTATUS[0]}"
echo "== lake exe cache get"
lake exe cache get 2>&1 | tr "\r" "\n" | grep -v "^Downloaded:" | tail -8
echo "cache exit: ${PIPESTATUS[0]}"
du -sh .lake/packages; ls .lake/packages | wc -l
echo "dirty files after update: $(git -C $HOME/math-rerouted status --short | wc -l)"; git -C $HOME/math-rerouted status --short | head
date
'
sync
