#!/usr/bin/env bash
# Corpus checks, phase 1 (read-only): runs 61_corpus_catalog.py against the checker's pinned clone.
set -u
echo "script sha256: $(sha256sum /mnt/c/Users/Work/dev/siegel/wsl-comparator/61_corpus_catalog.py | cut -c1-64); PyYAML $(python3 -c 'import yaml; print(yaml.__version__)')"
python3 -I /mnt/c/Users/Work/dev/siegel/wsl-comparator/61_corpus_catalog.py /home/checker/math/lean "$1"
