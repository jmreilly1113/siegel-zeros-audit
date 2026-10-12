#!/usr/bin/env bash
# Item 4 (read-only): batch-and-prune schedule for the remainder configs. Run as root in WSL.
python3 -I /mnt/c/Users/Work/dev/siegel/wsl-comparator/74_prune_schedule.py /home/checker/math/lean \
  /home/checker/.elan/toolchains/leanprover--lean4---v4.34.1/src/lean
