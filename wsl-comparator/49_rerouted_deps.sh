#!/usr/bin/env bash
# Plan step 3d: dependency scan (lean-checks/ReroutedDeps.lean) in the rerouted clone after the comparator run,
# and in the unmodified clone (/home/checker/math) as the control. Both as user checker, `lake env lean`.
set -u
install -o checker -g checker -m 644 /mnt/c/Users/Work/dev/siegel/lean-checks/ReroutedDeps.lean /home/checker/ReroutedDeps.lean
sha256sum /home/checker/ReroutedDeps.lean
for C in math-rerouted math; do
  echo "== clone /home/checker/$C (HEAD $(sudo -u checker git -C /home/checker/$C rev-parse HEAD); modified tracked files: $(sudo -u checker git -C /home/checker/$C status --short --untracked-files=no | wc -l); untracked: $(sudo -u checker git -C /home/checker/$C status --short | grep -c '^??'))"
  sudo -u checker -H bash -lc "export PATH=\"\$HOME/.elan/bin:\$PATH\"; cd \$HOME/$C/lean; lake env lean /home/checker/ReroutedDeps.lean 2>&1 | grep -v 'has local changes'; echo \"LEAN EXIT CODE: \${PIPESTATUS[0]}\"" 2>&1 | cat
done
