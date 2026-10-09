# Reviewer packet: independent checks of "Uniform exclusion of Landau–Siegel zeros"

Prepared 2026-10-08 for Joe to send to reviewers. Paper: openai/math, family 003, preprint dated 1 Oct 2026, commit adc7f1241b42e322a6451854ab7e4b4c146bf78a (`refs/siegel-paper.tex`, `refs/siegel-paper.pdf`).

## What this is

The paper claims an absolute c > 0 such that every real zero β ∈ (0,1) of every primitive nonprincipal real Dirichlet L-function of conductor q ≥ 3 satisfies (1 − β) log q ≥ c. We did not try to prove anything new. We tested what can be tested by exact computation, ran the official Lean checks on the accompanying formalization, and recorded what we could not check. Throughout we keep three categories apart: what the paper states, what we computed (each item cites a file in `results/` and a command), and what we infer.

## Status in one paragraph

The Lean formalization of both main-theorem statements is accepted by the official Lean FRO comparator and by a second, independently written kernel (nanoda). It uses only the three standard axioms, and the elaborated statement is identical to the challenge file. The statement's hypotheses are satisfiable: Lean proofs for all odd prime conductors. Every algebraic step we could compute held exactly at small sizes (N ≤ 5), with two independent implementations agreeing. The OAI Lean reaches Corollary 4 differently, so we formalized the paper's own proof of Lemma 3 separately in Lean (standard axioms only), after auditing it by hand and executing its construction exactly at N = 2, 3. Swapping it into OAI's proof of `dirichletRealZeroBound_proof` gives a proof of the challenge statement through the paper's Lemma 3, accepted by the official comparator with both kernels (`docs/writeup.md` 2.10 (c)). None of this replaces expert reading.

## What we ask of each kind of reviewer

**1. Analytic number theorist.** Please read the paper's Lemma 2 (prime bias), Section 6 (the limit argument) and the uniformity of the absolute constants in (2.1), (2.2) and (5.7). These are machine-checked in Lean, but nobody here has read the paper's own arguments with expert eyes. Also look at `docs/explicit-constant.md`. Assuming the paper, it derives c ≥ 0.00258 using Platt and Lu–Zaman–Zhao for small q, and it relies on an inequality −ζ′/ζ(s) < 1/(s − 1) whose reference we want confirmed.
- Start with: `docs/writeup.md` sections 1, 2.7, 2.9, 3 and 4; `docs/explicit-constant.md`.

**2. Someone who knows interpolation determinants and transcendence methods** (Laurent's interpolation determinants, multiplicity estimates; the paper cites Fischler and Laurent). Please read Lemma 3 and its proof, Corollary 4, and Sections 4–5 (the weighted row selection, Lemma 6 and Lemma 7). Is the convex-geometry proof of Lemma 3 complete? Our audit found two unstated routine facts and no gap. Do Lemma 6's constants hold uniformly in the way Section 6 needs?
- Start with: `docs/lemma3-audit.md`; `docs/writeup.md` sections 2.2–2.6 and 2.10; `docs/paper-map.md`.

**3. Lean / Mathlib user.** Please confirm that the challenge statement (`refs/SiegelZeros.lean`) says what Theorem 1.1 says: Mathlib's `DirichletCharacter.LFunction`, `IsPrimitive`, and "real" as `(χ a).im = 0`. Please also review the checking setup.
- Start with: `docs/writeup.md` section 2.8; `docs/lean-paper-map.md`; `docs/reproduce.md`; `lean-checks/NonVacuity.lean`; `results/2026-10-08-lean-*.txt`.

## Key files

| Topic | Paper statement | Our result | Evidence |
|---|---|---|---|
| Lean statement and proof | Theorem 1.1 | Accepted by Lean kernel and nanoda; standard axioms only | results/2026-10-08-lean-comparator-wsl.txt, -lean-comparator-nanoda-netblock.txt, -lean-axioms.txt, -lean-type-compare.txt |
| Non-vacuity | — | Hypotheses hold for the quadratic character mod every odd prime | results/2026-10-08-lean-nonvacuity.txt |
| Lemma 3 proof | lem:interpolation | Formalized in Lean following the paper's proof, standard axioms only, accepted by Lean's kernel and nanoda, and used to give a second proof of OAI's Corollary 4 statement and of the challenge theorem itself, by swapping Corollary 4 into OAI's `dirichletRealZeroBound_proof` (lean-checks/Lemma3.lean, Lemma3Bridged.lean, MainRerouted.lean; results/2026-10-08-lean-lemma3-full.txt, -bridge.txt, -nanoda.txt, -main-rerouted.txt, -main-closure-cor4-usage.txt; official comparator with both kernels on the source-level swap: results/2026-10-09-lean-comparator-rerouted-nanoda.txt, -rerouted-comparator-diff.txt, -lean-rerouted-comparator-deps.txt); no gap found by hand; construction executed exactly at N = 2, 3 | docs/lemma3-audit.md, results/2026-10-08-lemma3-construct-N2/N3/N2-generic4d-summary.txt (540 instances) |
| Corollary 4 | cor:rectangle | Minimal full-rank boxes far smaller than the paper's | results/2026-10-08-interpolation-boxes-N2/N3-summary.txt |
| Lemma 7 | lem:divisibility | Holds in all 510 admissible (run, p) pairs, N = 2..5 | results/2026-10-08-lemma7-*-consolidated.txt |
| (5.1), (5.6) | Section 5 | Hold in all 184 runs (Arb) | results/2026-10-08-bounds-*.txt |
| Lemma 6 | lem:exponents | Exact N ≤ 5; EXPLORATORY N ≤ 7 | results/2026-10-08-bounds-*.txt, -selection-modp-N567-EXPLORATORY-summary.txt |

## Explicitly not checked

See `docs/writeup.md` section 4. In short: Lemma 2 and the Section 6 limit by a human expert; any N large enough for the asymptotic inequalities to bite; the explicit-constant bookkeeping; the case d = 2.

## Reproducing

`docs/reproduce.md` (Python checks, Windows Lean build, the official comparator under WSL2/Linux). Every result file names the command that produced it.
