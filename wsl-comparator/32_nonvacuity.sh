#!/usr/bin/env bash
# Step 4a: compile lean-checks/NonVacuity.lean against the comparator-checked build (as 'checker', outside the clone).
install -d -o checker -g checker /home/checker/nonvacuity
install -o checker -g checker -m 644 /mnt/c/Users/Work/dev/siegel/lean-checks/NonVacuity.lean /home/checker/nonvacuity/NonVacuity.lean
sha256sum /home/checker/nonvacuity/NonVacuity.lean
cd /home/checker/math/lean
sudo -u checker -H bash -lc 'export PATH="$HOME/.elan/bin:$PATH"; cd $HOME/math/lean; date; time lake env lean /home/checker/nonvacuity/NonVacuity.lean; echo "LEAN EXIT CODE: $?"'
