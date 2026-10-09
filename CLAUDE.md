# Siegel-zero paper verification

## Goal

Independently check the paper "Uniform exclusion of Landau–Siegel zeros" (OpenAI, Oct 1 2026, family 003 of github.com/openai/math, commit adc7f1241b42e322a6451854ab7e4b4c146bf78a). The paper claims an absolute c > 0 such that every real zero β in (0,1) of every primitive nonprincipal real Dirichlet L-function of conductor q ≥ 3 satisfies (1 − β) log q ≥ c.

We are not trying to prove anything new. We test every step of the paper that can be tested by exact or rigorous computation, record what holds and what fails, and write it up for human number theorists. The owner (Joe) is a data scientist and education researcher, not a number theorist. Explain mathematical reasoning in plain terms when reporting results.

## Context that changes how to read the paper

- If the 7/8 zero-free half-plane (the Sept 30 paper in the same family) is correct, the Siegel statement follows trivially with c = (log 3)/8. The standalone paper matters as an independent proof, so we check it on its own terms.
- No real zero in (0,1) of a primitive real L-function has ever been found. Platt (2016) rules them out for q ≤ 4×10^5; Lu–Zaman–Zhao (refs/) rule out zeros in [1 − 1/(5 log q), 1) for q ≤ 10^10. Do not plan computations that need an actual Siegel zero.
- The analytic input (Section 2) is the classical prime-bias argument. The new content is algebraic (Sections 3–5): an interpolation determinant Δ over K = Q(√d, √2) whose norm is divisible by large prime powers. Sections 3–5 do not depend on any zero existing, so they can be tested exactly for any d.

## Layout

- `refs/` source documents: the paper (PDF and .tex), Lean comparator statement, Lean scope page, the family-003 catalogue entry, and the Lu–Zaman–Zhao citation (refs/lu-zaman-zhao-2602.03626.md; the PDF is not redistributed).
- `external/` cloned repos (created by `scripts/setup.sh`): openai/math pinned to the commit above, and asif-z/landau-siegel-zero-tester.
- `src/` our code. `src/lemma7_check.py` is a working exact prototype for Sections 4–5.
- `tests/` unit tests. Run `python -m pytest tests -q` before and after any change to `src/`.
- `results/` dated plain-text outputs of every run used in a claim. Never overwrite; add a new dated file.
- `docs/paper-map.md` which equations are testable and how. `docs/tasks.md` the work queue.
- `docs/log.md` running log: date, what was run, what it showed, open questions.

## Rules

1. Exact arithmetic only for anything we will cite: Python `Fraction`/integers, or Arb ball arithmetic via python-flint. Floating point is allowed for exploration only, and results from it must be labeled exploratory in `docs/log.md`.
2. Every claim in a write-up must point to a file in `results/` and the command that produced it.
3. Keep three categories separate in all notes: what the paper states, what we computed, and what we infer. Do not upgrade an inference to a finding.
4. Quote equation numbers from `refs/siegel-paper.tex` when referring to the paper.
5. A small-N check confirms a lemma at that N only. Never describe it as verifying the theorem.
6. If a computation contradicts the paper, stop, re-derive by hand in `docs/log.md`, rerun with a second independent method, and only then report it.
7. Do not modify anything under `external/`. Copy files out if needed.
8. Pin and record versions (Python, python-flint, Lean toolchain) in `docs/log.md` when results are produced.
