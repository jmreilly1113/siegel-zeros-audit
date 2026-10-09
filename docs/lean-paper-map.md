# Lean ↔ paper correspondence (step 3)

Source: openai/math @ adc7f12, `lean/OAI/NumberTheory/SiegelZeros/` and the 12 files that `lean/patches/PrimeNumberTheoremAnd-lean4341.patch` adds under `PrimeNumberTheoremAnd/SiegelZeros/`. Read in the byte-identical copies under `lean-build/`. Paths below are relative to `OAI/NumberTheory/SiegelZeros/` unless marked PNT/.

How this was made: a read-only sub-agent read the files. I re-read the items marked ✔ myself: the declaration exists at that line and has the quoted shape. Unmarked file:line references are the sub-agent's reading. **None of this is compiled yet** (the build is paused, see `docs/log.md`), so "formalizes" means "states and contains a proof script for", not "kernel-checked".

## Top-level structure
- The challenge contains two theorems with the same content.
  - `exists_absolute_real_zero_gap`: Conclusions/Theorem.lean:11 ✔. Route 1, via `SiegelZerosAwei.W50` and Estimates/GeometricBoundary.lean:18 ✔.
  - `dirichletRealZeroBound_proof`: Characters/DirichletRealZeroBoundProof.lean:18 ✔ → `dirichlet_real_zero_bound`, Characters/DirichletRealZeroBound.lean:14 ✔. Route 2.
- The two routes share the same architecture: determinant, greedy pivots, Frobenius, Hadamard, and a Bezout-type multiplicity estimate. They differ in which Bezout lemma they use, where the Hadamard factorization comes from (in-house in route 1, the patched PNT files in route 2), and bookkeeping. They are not independent proofs at the level of ideas. Route 2 mirrors the paper's (6.2) more literally.

## Paper item → Lean

| Paper | Lean | Match |
|---|---|---|
| Lemma 2, (2.1)–(2.2) | Structure/SumLogPrimeFactors.lean:146 `source_analytic_lemma` ✔ | Same shape. C absolute; CH chosen after H, before q, χ, β, X. |
| (2.4) log-derivative bound | Characters/RealLogDerivConductorCompletedLDivisorTsum.lean:485 | −ζ′/ζ − L′/L ≤ K log q + 1/(s−1) − 1/(s−β), 1 < s ≤ 2 |
| (2.3) Hadamard identity | same file :227; Characters/ConductorCompletedL.lean:309, :329; PNT/SiegelZeros/Growth.lean:377 (Hadamard factorization from growth, order 3/2) | Route 1 uses Structure/AffineAssembly.lean:385 instead |
| **Lemma 3 (proof)** | Not in openai/math (no convex hull, 4N−3 or 4096 appears anywhere ✔). **Formalized by us** following the paper's own proof: lean-checks/Lemma3.lean `Lemma3.interpolation`, standard axioms only (results/2026-10-08-lean-lemma3-full.txt) | Statement matches tex 252–267 clause by clause (docs/lemma3-lean-statement-review.md). Linked: lean-checks/Lemma3Bridged.lean proves OAI's `actual_biquadratic_rectangle_span` (type via `type_of%`) from it without the multiplicity estimate (dependency scan with control, results/2026-10-08-lean-lemma3-bridge.txt). nanoda accepts (results/2026-10-08-lean-lemma3-nanoda.txt). Main theorem rerouted: OAI's `dirichletRealZeroBound_proof` with Corollary 4 swapped for ours (4 theorems copied, kernel-rechecked; nanoda accepts 93,598 declarations), lean-checks/MainRerouted.lean, results/2026-10-08-lean-main-rerouted.txt. The official comparator, with both kernels, accepts the same swap made at source level in a fresh clone (one import line and one term changed, plus our two modules): results/2026-10-09-lean-comparator-rerouted-nanoda.txt, -rerouted-comparator-diff.txt, -lean-rerouted-comparator-deps.txt. Only that challenge theorem uses Corollary 4; `exists_absolute_real_zero_gap` does not (two methods, results/2026-10-08-lean-main-closure-cor4-usage.txt). The rerouted proof inherits OAI's patched PrimeNumberTheoremAnd dependency (HadamardSupport, created by lean/patches/PrimeNumberTheoremAnd-lean4341.patch), so its trust base includes that adapted source, as OAI's original analytic route does; the closure of exists_absolute_real_zero_gap contains no PrimeNumberTheoremAnd module (results/2026-10-09-pnt-hadamard-dependency.txt). |
| Corollary 4 | Structure/InvariantJetLinearMap.lean:471 `actual_biquadratic_rectangle_span` ✔ | Same T_j = 32 H^{2/3}U and 32 H^{−1/3}U, stated over K. Proved via the multiplicity estimate `uniform_rectangular_multiplicity`, Differentials/TorusQuotientDimensionPosCotangentFinrankThree.lean:205 ✔ (zero estimate on G_m⁴, projective-degree Bezout). That is the Remark's viewpoint, not the paper's proof. |
| Section 4: rows, greedy selection, weight ≤ 96 H^{2/3}U, Δ ≠ 0 | Characters/CharacterGlobalGreedyDeterminantMasterBounds.lean:19; Selection/GreedyPivotsWeightLowSpan.lean:104 | exact |
| Lemma 6 (4.4) | Selection/GreedyPivots.lean:258 `weighted_pivot_bounds` ✔ | Exact constants 1/(4·97²) and 192. Hypothesis N ≥ 18818 replaces "N large in terms of H". |
| (5.1) | Determinants/NormSqReal.lean:163 | exact, including log 8 |
| (5.2) Frobenius | Determinants/ThetaDivisibility.lean:91 | exact |
| Lemma 7 (5.3) | Characters/BiquadraticArithmeticFull.lean:233, :267; replacement expansion :196 | Same mechanism. Stated in the ring of integers rather than Z[a, b]; the conclusion has the same content. |
| (5.6), (5.7) | Determinants/NormSqReal.lean:325, :460 | Exact shape. Chebyshev constant explicit (log 4). |
| (6.1) contrary sequence, q → ∞ | Structure/SumLogPrimeFactors.lean:420, :355, :368, :323 | Uses L(1, χ) ≠ 0 (Mathlib) and continuity |
| (6.2) master inequality | Determinants/NormalizedMasterBound.lean:10 `normalized_master_bound` ✔; Structure/NotEventuallyMaster.lean:366 | exact |
| Choice of H, γ; 13/16 + 1/16 | NotEventuallyMaster.lean:164 (H ≥ 86,713,344 ⇒ S₂/S₁ ≤ 1/12), :88 (γ = 12(\|C\|+1)), :403 | exact |

## Added or changed hypotheses
- q ≠ 8: the paper's d ≠ 2, eventually true along the contrary sequence.
- N ≥ 18818.
- H fixed at 86,713,344 = 12·C₀/c₀.
- C ≥ log 4 (a normalization).

No Lean statement was found to be weaker than the paper's.

## What this means for review
- The build, axiom check and official comparator have passed, with the Lean kernel and nanoda both accepting (results/2026-10-08-lean-comparator-*.txt). OAI's formalization checks Lemma 3 only through its conclusion (Corollary 4), by a different and heavier algebraic-geometric proof. The paper's own short convex-geometry proof is formalized by us in Lean (lean-checks/Lemma3.lean, standard axioms only, nanoda accepts; results/2026-10-08-lean-lemma3-full.txt, -nanoda.txt) and bridged to OAI's Corollary 4 statement (lean-checks/Lemma3Bridged.lean, results/2026-10-08-lean-lemma3-bridge.txt). Swapped into OAI's `dirichletRealZeroBound_proof`, it gives the challenge statement through the paper's route (lean-checks/MainRerouted.lean, results/2026-10-08-lean-main-rerouted.txt; there the copies are added by a metaprogram via `addDecl`, the kind of environment manipulation the comparator guards against, so the standalone nanoda run with its two controls is the independent check). The same swap made at source level, with no metaprogram, is accepted by the official comparator with both kernels (results/2026-10-09-lean-comparator-rerouted-nanoda.txt). Additional evidence: the hand audit (`docs/lemma3-audit.md`, an inference) and the exact execution of its construction at N = 2, 3 (`src/lemma3_construct.py`, results/2026-10-08-lemma3-construct-*).
- The constants in Lean are existential. The explicit value in `docs/explicit-constant.md` is not in the formalization.
