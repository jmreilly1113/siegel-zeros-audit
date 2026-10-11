#!/usr/bin/env bash
# Corpus checks, phase 0 (read-only): provenance of the checker's clone /home/checker/math.
set -u
R=/home/checker/math; L=$R/lean
g() { sudo -u checker git -C "$@"; }
echo "date: $(date)"
echo "== openai/math"
echo "HEAD: $(g $R rev-parse HEAD)"
echo "git status --short (tracked and untracked):"; g $R status --short | head -50; echo "(lines: $(g $R status --short | wc -l))"
echo "== toolchain"
echo "lean-toolchain: $(cat $L/lean-toolchain)"
sudo -u checker -H bash -lc 'export PATH=$HOME/.elan/bin:$PATH; cd ~/math/lean; lean --version; lake --version; elan --version'
echo "== lake-manifest.json packages (name, rev, inputRev, url)"
python3 -c "
import json; m=json.load(open('$L/lake-manifest.json'))
for p in m['packages']: print(f\"  {p['name']:<28} {p.get('rev','-'):<42} {str(p.get('inputRev','-')):<24} {p.get('url', p.get('dir','-'))}\")
print('  packages:', len(m['packages']))"
echo "== checked-out package HEADs and local changes (lake update applies lean/patches/*.patch)"
for d in $L/.lake/packages/*/; do n=$(basename $d); h=$(g $d rev-parse HEAD 2>/dev/null); c=$(g $d status --short 2>/dev/null | wc -l); echo "  $n $h changed-or-untracked: $c"; done
echo "== tools"
echo "comparator: $(sha256sum /usr/local/bin/comparator | cut -c1-64) (tag v4.34.0 d03acab per results/2026-10-08-lean-comparator-wsl.txt)"
echo "lean4export: $(sha256sum /usr/local/bin/lean4export | cut -c1-64) (tag v4.34.0)"
echo "nanoda_bin: $(sha256sum /usr/local/bin/nanoda_bin | cut -c1-64) (nanoda_lib 3a24072, 0.4.19)"
echo "landrun: $(landrun --version 2>&1 | head -1)"
echo "kernel: $(uname -r)"
echo "== sha256 of formalization.yaml and ComparatorChallenges/*.json"
cd $L; sha256sum formalization.yaml; ls ComparatorChallenges/*.json | wc -l; sha256sum ComparatorChallenges/*.json
