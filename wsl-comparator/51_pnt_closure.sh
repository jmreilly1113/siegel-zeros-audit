#!/usr/bin/env bash
# Task 2 (read-only): is PrimeNumberTheoremAnd.SiegelZeros.HadamardSupport in the import closures of the two
# challenge routes? Unmodified clone (/home/checker/math) and rerouted clone (/home/checker/math-rerouted).
set -u
TC=/home/checker/.elan/toolchains/leanprover--lean4---v4.34.1/src/lean
echo "script sha256: $(sha256sum /mnt/c/Users/Work/dev/siegel/wsl-comparator/50_module_closure.py | cut -c1-64)"
P=OAI.NumberTheory.SiegelZeros
for C in math math-rerouted; do
  echo; echo "######## clone /home/checker/$C: HEAD $(sudo -u checker git -C /home/checker/$C rev-parse HEAD), status: $(sudo -u checker git -C /home/checker/$C status --short | tr '\n' ' ')"
  echo "PNT package HEAD: $(sudo -u checker git -C /home/checker/$C/lean/.lake/packages/PrimeNumberTheoremAnd rev-parse HEAD); HadamardSupport.lean tracked by PNT git: $(sudo -u checker git -C /home/checker/$C/lean/.lake/packages/PrimeNumberTheoremAnd ls-files --error-unmatch PrimeNumberTheoremAnd/SiegelZeros/HadamardSupport.lean >/dev/null 2>&1 && echo yes || echo no)"
  python3 -I /mnt/c/Users/Work/dev/siegel/wsl-comparator/50_module_closure.py /home/checker/$C/lean $TC \
    $P.Characters.DirichletRealZeroBoundProof $P.Conclusions.Theorem $P.Characters.CharacterGlobalGreedyDeterminantMasterBounds $P.PaperLemma3.Bridge
done
