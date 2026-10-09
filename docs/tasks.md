# Task queue

Work top to bottom. Mark each task done with the date and the results file it produced.

## 0. Setup
- [x] (2026-10-07; setup.sh made Windows-compatible, see log) Run `scripts/setup.sh`. Confirm external/openai-math is at commit adc7f12 and contains `lean/ComparatorChallenges/SiegelZeros.lean` and `preprints/Uniform-exclusion-of-Landau-Siegel-zeros-October-1-2026/`.
- [x] (2026-10-07; no differences, see log) Diff our refs/ copies against the cloned versions. Report any difference.
- [x] (2026-10-07) Run `python -m pytest tests -q`. Record versions in docs/log.md.

## 1. Extend the Lemma 7 check (src/lemma7_check.py)
- [x] (2026-10-08) Add a `--json` output mode so results are machine-readable.
- [x] (2026-10-08; results/2026-10-07-lemma7-N3-H2346.jsonl, -summary in 2026-10-08-lemma7-N3-H2346-summary.txt) Run N = 3 for H in {2, 3, 4, 6} and at least 10 fields (both signs of d, d ≡ 1 mod 4 and not).
- [x] (2026-10-08; profile results/2026-10-08-profile-selection-N4-d-7-H2.json; port src/lemma7_flint.py; cross-check results/2026-10-08-compare-N3-fraction-vs-flint.txt) Profile N = 4 (M = 256). If too slow in pure Python, port the determinant to python-flint (`fmpz_mat` over the regular representation, or work modulo several large primes splitting completely in K and use CRT plus a Hadamard bound for the exact norm). Keep the Fraction version as the reference and cross-check on N = 2, 3.
- [x] (2026-10-08) Record for each run: retained indices, max weight, S1, S2, log|N(Δ)|, and for every prime p ≤ max α1: χ(p), (2/p), 4E_p, v_p(N(Δ)).

## 2. Interpolation lemma (Lemma 3, Corollary 4)
- [x] (2026-10-08; results/2026-10-08-interpolation-boxes-N2/N3*) For N = 2, 3, compute the rank of all rows with α_j ≤ t_j for the paper's t_j and for smaller boxes. Find the smallest boxes that still give rank M. This tests how much slack (3.1) has.
- [x] (2026-10-08; same files) Check the kernel claim after (4.1): A·(ab, b, −a, −1) = 0.

## 3. Bounds
- [x] (2026-10-08; exact N <= 5 in results/2026-10-08-bounds-*.txt, EXPLORATORY N = 5..7 in results/2026-10-08-selection-modp-N567-EXPLORATORY-summary.txt) Lemma 6: tabulate S1, S2, S2/S1 against N and H.
- [x] (2026-10-08; results/2026-10-08-bounds-N2-N4.txt, -N5.txt) (5.1): compare exact log|N(Δ)| with the Hadamard right side.
- [x] (2026-10-08; same files) (5.6)/(5.7): compute the divisibility lower bound from the actual E_p and compare with the exact log|N(Δ)|.

## 4. Prime-bias input (Lemma 2)
- [x] (2026-10-08; results/2026-10-08-prime-bias-*) With python-flint or plain sieving, compute Σ_{p ≤ X, χ(p)=1} log p / p for all fundamental discriminants |D| ≤ 10^5 and X in {10^4, 10^5, 10^6}. Plot against ℓ and log X. This is descriptive context, not a test of the lemma.

## 5. Lean
- [x] (2026-10-08; docs/log.md) Locate the proof of `exists_absolute_real_zero_gap` in external/openai-math. Determine whether it follows this paper's Sections 3–5 or goes through the 7/8 theorem. Write the answer in docs/log.md with file paths.
- [x] (2026-10-08; results/2026-10-08-lean-comparator-wsl.txt) Optional, later: rebuild with the Lean FRO comparator (see github.com/leanprover/comparator), following the approach of github.com/davegoldblatt/openai-zeta-proof-check.

## 6. Write-up
- [x] (2026-10-08; draft for Joe's review) Draft docs/writeup.md: what was checked, how, results, and the explicit list of what was not checked. Keep paper claims, computed results, and inferences in separate sections.

## 7. Next steps (added 2026-10-08)
- [x] (2026-10-08; results/2026-10-08-lean-build-summary.txt, -lean-axioms.txt, -lean-type-compare.txt; Windows leanchecker replay stopped unfinished, superseded by the comparator) Finish the Lean build (needs ~11 GB free on C:, or move lean-build/ and ~/.elan off C:). Then `lake env lean Check/SiegelCheck.lean` (statement match + #print axioms) and a leanchecker replay. See docs/reproduce.md.
- [x] (2026-10-08; results/2026-10-08-lean-comparator-wsl.txt; accepted) Run the official comparator on Linux (docs/reproduce.md, Option A).
- [x] (2026-10-08; docs/log.md step 2) Check that the Lean statement means what Theorem 1.1 says (Mathlib LFunction, IsPrimitive, real characters).
- [x] (2026-10-08; docs/lean-paper-map.md) Map Lean lemmas to paper lemmas. Finding: Lemma 3's proof is not formalized; Corollary 4 is proved by a different method.
- [x] (2026-10-08; docs/explicit-constant.md) Explicit c, conditional: 0.00258 with Platt + LZZ. Needs an expert check of the bookkeeping and the reference for -zeta'/zeta(s) < 1/(s-1).
- [x] (2026-10-08; docs/reproduce.md) Reproduction guide for an independent rerun.
- [x] (superseded by 8.4c) Send docs/writeup.md, docs/explicit-constant.md and docs/lean-paper-map.md to an analytic number theorist (Joe to choose).
- [x] (moved to section 8, step 1; done) Optional: rerun the comparator with nanoda.

## 8. Remaining gaps after the comparator (added 2026-10-08; details in docs/plan-remaining-gaps.md)
- [x] (2026-10-08; skipped by Joe: known RAM issue on this machine, unrelated to the project) 0. Hardware check.
- [x] (2026-10-08; results/2026-10-08-lean-comparator-nanoda-netblock.txt; both kernels accept; network blocked by seccomp instead of a kernel update) 1+2. Comparator rerun with nanoda as a second kernel and a full sandbox (WSL kernel 6.6 or network off).
- [x] (2026-10-08; docs/lemma3-audit.md; inference) 3a. Written step-by-step audit of the Lemma 3 proof.
- [x] (2026-10-08; results/2026-10-08-lemma3-construct-N2/N3/N2-generic4d-summary.txt; 540 instances, all 28 checks pass; N = 2, 3 only) 3b. Executable Lemma 3 proof at N = 2, 3, checking each intermediate claim exactly.
- [x] (2026-10-08; lean-checks/Lemma3.lean, results/2026-10-08-lean-lemma3-full.txt; only standard axioms) 3c. Formalize Lemma 3 in Lean (Joe: yes, in parallel pieces). Skeleton done 2026-10-08: lean-checks/Lemma3Skeleton.lean, results/2026-10-08-lean-lemma3-skeleton.txt, review docs/lemma3-lean-statement-review.md. All 12 sub-lemmas proved in five parallel pieces (results/2026-10-08-lean-lemma3-piece1..5.txt) and merged.
- [x] (2026-10-08; lean-checks/NonVacuity.lean, results/2026-10-08-lean-nonvacuity.txt) 4a. Lean non-vacuity lemmas for the challenge statement.
- [x] (2026-10-08; docs/reviewer-packet.md) 4b. Reviewer packet.
- [x] (2026-10-08; lean-checks/MainRerouted.lean, results/2026-10-08-lean-main-rerouted.txt, -main-closure-cor4-usage.txt) 3d. Rebuild the main theorem on our Lemma 3: dirichletRealZeroBound_proof rerouted (4 theorems), both kernels accept; exists_absolute_real_zero_gap never used Corollary 4.
- [x] (2026-10-09; results/2026-10-09-lean-comparator-rerouted-nanoda.txt) 3e (plan step 3d). Official comparator, both kernels, on the rerouted proof (source-level swap in a fresh clone): accepted.
- [ ] 4c. Joe chooses reviewers and sends the packet.
