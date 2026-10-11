#!/usr/bin/env bash
set -u
echo "script sha256: $(sha256sum /mnt/c/Users/Work/dev/siegel/wsl-comparator/64_challenge_pattern_scan.py | cut -c1-64)"
python3 -I /mnt/c/Users/Work/dev/siegel/wsl-comparator/64_challenge_pattern_scan.py /home/checker/math/lean
