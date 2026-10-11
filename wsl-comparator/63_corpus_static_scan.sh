#!/usr/bin/env bash
# Corpus checks, phase 3 (read-only, heuristic): runs 63_corpus_static_scan.py against the checker's pinned clone.
set -u
TC=/home/checker/.elan/toolchains/leanprover--lean4---v4.34.1/src/lean
echo "script sha256: $(sha256sum /mnt/c/Users/Work/dev/siegel/wsl-comparator/63_corpus_static_scan.py | cut -c1-64)"
/usr/bin/time -f "(%e s, %M KB)" python3 -I /mnt/c/Users/Work/dev/siegel/wsl-comparator/63_corpus_static_scan.py /home/checker/math/lean $TC "$1"
