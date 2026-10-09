#!/usr/bin/env bash
# Run from the project root: bash scripts/setup.sh
set -euo pipefail

COMMIT=adc7f1241b42e322a6451854ab7e4b4c146bf78a
mkdir -p external

if [ ! -d external/openai-math ]; then
  git clone https://github.com/openai/math external/openai-math
fi
git -C external/openai-math fetch --all --quiet || true
git -C external/openai-math checkout --quiet "$COMMIT" || {
  echo "Could not check out $COMMIT. The repo may have been rewritten; record the current HEAD in docs/log.md."
}
echo "openai/math at: $(git -C external/openai-math rev-parse HEAD)"

if [ ! -d external/lzz-tester ]; then
  git clone https://github.com/asif-z/landau-siegel-zero-tester external/lzz-tester
fi

# Python environment
# python3 on Windows is often the Microsoft Store stub; fall back to python.
PY=python3
"$PY" -c 'import sys' 2>/dev/null || PY=python
"$PY" -m venv .venv
if [ -f .venv/bin/activate ]; then . .venv/bin/activate; else . .venv/Scripts/activate; fi
python -m pip install --upgrade pip
python -m pip install python-flint mpmath sympy numpy matplotlib pytest

python -c "import flint, mpmath, sympy; print('python-flint', flint.__version__, '| mpmath', mpmath.__version__, '| sympy', sympy.__version__)"

# Quick integrity checks
PRE=external/openai-math/preprints/Uniform-exclusion-of-Landau-Siegel-zeros-October-1-2026
ls "$PRE" || echo "Siegel preprint folder not found at expected path"
ls external/openai-math/lean/ComparatorChallenges/SiegelZeros.lean || echo "SiegelZeros.lean not found"
cmp -s "$PRE/paper.pdf" refs/siegel-paper.pdf && echo "refs/siegel-paper.pdf matches repo" || echo "refs/siegel-paper.pdf DIFFERS from repo copy"

python -m pytest tests -q

# Optional: Lean toolchain for task 5. Uncomment when ready.
# curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh -s -- -y
