#!/usr/bin/env bash
# Compile one file from lean-checks/ against the comparator-checked build, as user 'checker'.
# Usage: bash wsl-comparator/34_lean_file.sh <FileName.lean>
f="$1"
install -d -o checker -g checker /home/checker/leanchecks
install -o checker -g checker -m 644 "/mnt/c/Users/Work/dev/siegel/lean-checks/$f" "/home/checker/leanchecks/$f"
sha256sum "/home/checker/leanchecks/$f"
sudo -u checker -H bash -lc "export PATH=\"\$HOME/.elan/bin:\$PATH\"; cd \$HOME/math/lean; time lake env lean /home/checker/leanchecks/$f 2>&1 | grep -v 'has local changes'; echo \"LEAN EXIT CODE: \${PIPESTATUS[0]}\""
