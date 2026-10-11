#!/usr/bin/env bash
set -u
TC=/home/checker/.elan/toolchains/leanprover--lean4---v4.34.1/src/lean
echo "script sha256: $(sha256sum /mnt/c/Users/Work/dev/siegel/wsl-comparator/65_build_estimate.py | cut -c1-64)"
/usr/bin/time -f "(%e s, %M KB)" python3 -I /mnt/c/Users/Work/dev/siegel/wsl-comparator/65_build_estimate.py /home/checker/math/lean $TC
