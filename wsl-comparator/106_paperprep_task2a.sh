#!/bin/bash
# Paper prep Task 2a (read-only): challenge file, solution main theorem, config JSON for two flagged configs.
# Run as checker: wsl -d Ubuntu-24.04 -u checker -e bash 106_paperprep_task2a.sh > results/2026-10-20-paper-prep/task2a-files.txt
cd /home/checker/math || exit 1
echo "openai/math commit: $(git rev-parse HEAD)  (git status --short lines: $(git status --short | wc -l))"
for c in HarmonicGrowth:OAI/Geometry/HarmonicGrowth/Main.lean:main NavierStokesVelocity:OAI/MathematicalPhysics/NavierStokes/VelocityDetection/Main.lean:main_result; do
  n=${c%%:*}; rest=${c#*:}; sol=${rest%%:*}; thm=${rest#*:}
  echo; echo "################ $n"
  echo "=== lean/ComparatorChallenges/$n.json  sha256 $(sha256sum lean/ComparatorChallenges/$n.json | cut -c1-64)"
  cat lean/ComparatorChallenges/$n.json; echo
  echo "=== lean/ComparatorChallenges/$n.lean  sha256 $(sha256sum lean/ComparatorChallenges/$n.lean | cut -c1-64)  lines $(wc -l < lean/ComparatorChallenges/$n.lean)"
  cat -n lean/ComparatorChallenges/$n.lean
  echo "=== solution lean/$sol  sha256 $(sha256sum lean/$sol | cut -c1-64): declaration of $thm (grep -rn in the solution module directory, 12 lines after)"
  grep -rn -A12 -E "^(theorem|lemma) $thm\b" "lean/$(dirname "$sol")"
done
