#!/usr/bin/env bash
# Corpus checks, phase 2 (read-only): runs 62_corpus_configs.py against the checker's pinned clone.
set -u
echo "script sha256: $(sha256sum /mnt/c/Users/Work/dev/siegel/wsl-comparator/62_corpus_configs.py | cut -c1-64)"
python3 -I /mnt/c/Users/Work/dev/siegel/wsl-comparator/62_corpus_configs.py /home/checker/math/lean "$1"
