#!/usr/bin/env bash
# Plan step 3d, check 1 (read-only): import closure of our bridge code, against the checker's pinned clone.
set -u
TC=/home/checker/.elan/toolchains/leanprover--lean4---$(sudo -u checker cat /home/checker/math/lean/lean-toolchain | sed 's#.*:##')/src/lean
echo "clone HEAD: $(sudo -u checker git -C /home/checker/math rev-parse HEAD); dirty files: $(sudo -u checker git -C /home/checker/math status --short | wc -l); toolchain: $(cat /home/checker/math/lean/lean-toolchain); toolchain src: $TC"
echo "Lemma3Bridged.lean sha256: $(sha256sum /mnt/c/Users/Work/dev/siegel/lean-checks/Lemma3Bridged.lean | cut -c1-64)"
echo "script sha256: $(sha256sum /mnt/c/Users/Work/dev/siegel/wsl-comparator/43_bridge_import_closure.py | cut -c1-64)"
python3 -I /mnt/c/Users/Work/dev/siegel/wsl-comparator/43_bridge_import_closure.py /home/checker/math/lean /mnt/c/Users/Work/dev/siegel/lean-checks/Lemma3Bridged.lean "$TC"
