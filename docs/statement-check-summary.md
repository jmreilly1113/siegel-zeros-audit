# Statement checks, family 003: summary (2026-10-20)

Per-challenge reports: docs/statement-check-QuasiRiemannHypothesis.md, docs/statement-check-DirichletSevenEighths.md and docs/statement-check-HeckeSevenEighths.md. Steps 1-3 draft, with the full Hecke file: docs/statement-check-003-steps1-3-DRAFT.md. Results: results/2026-10-20-statement-checks/. Lean project: statement-checks/. openai/math fd4aeeb, Mathlib d13f23b, Lean 4.34.1, paper The-Quasi-Riemann-Hypothesis-September-30-2026 (Theorem 1.1, paper.tex l.106-111).

## One line per challenge

- **QuasiRiemannHypothesis:** MATCHES Theorem 1.1 for ζ, except that s = 1 is covered by Mathlib's junk value ζ(1) = (γ − log 4π)/2 ≠ 0 (formally stronger only there, and with no content). Mathlib definitions only. Non-vacuity proved in Lean.
- **DirichletSevenEighths:** MATCHES. All q ≥ 1 and all characters, with exactly the principal pole excluded. Mathlib definitions only. Non-vacuity proved in Lean for a principal and a nonprincipal character.
- **HeckeSevenEighths:** MATCHES (L-function row by Joe's ruling, 2026-10-20). Local definitions throughout. The L-function row rests on:
  - (a) the Lean lattice identity for Re s > 1 plus Lean holomorphy on ℂ minus {0, 1} (entire for nontrivial characters), which by the identity theorem fixes the function in the strip;
  - (b) two standard identifications: N(x + yω) = x² − xy + y², which is now also proved in Lean (`HeckeNorm.norm_coordinateElement`); and each nonzero ideal has exactly 6 generators (PID, 6 units, χ trivial on units), which remains INFERRED.

  Also proved in Lean: independence of `period`, and an explicit nontrivial character that meets every hypothesis. The Dedekind factorization was checked numerically for 5 characters, not proved. Junk value at s = 0 for modulus O, outside the half-plane.

## Every UNCLEAR row

None. The Hecke `LFunction` row was ruled MATCHES by Joe (2026-10-20), on the basis above. The `period` row is settled by `HeckeHolo.period_indep`.

## Every local definition a human still needs to read

All are in lean/ComparatorChallenges/HeckeSevenEighths.lean at fd4aeeb, quoted in full in the steps 1-3 draft. QRH and Dirichlet have none.

| Lines | Definitions |
|---|---|
| 11-30, 32-51 | `ThetaProduct.rapid_product_sub`, `product` |
| 53-64, 66-89 | `ThetaProduct.rapid_rescale`, `rescale` |
| 111-114, 116-126 | `scaledEvenPair`, `scaledEvenPair_f_continuous`, `scaledEvenPair_g_continuous` |
| 128-136 | `rectangularPair`, `rectangularPair_k` |
| 143-148 | `EisensteinTheta.xShift`, `yShift`, `parityPair` |
| 155-159, 161-192 | `HeckeTheta.locallyIntegrableOn_sum`, `finitePair` |
| 194-202 | `HeckeTheta.pair`, `completed`, `latticeL` |
| 208-215 | `HeckeFamily.K`, `O`, the cyclotomic instance, `omega`, `coordinateElement` |
| 217-226 | `Character` and its `NeZero` instance |
| 228-235 | `elementCoeff`, `coefficients`, `continuedLattice`, `LFunction` |
| 91-109 | in the file but not in the statement's closure: `shiftedPair` and its lemmas |

The Lean lemmas reduce what this reading must establish: the definitions are proved to yield a holomorphic function that equals the lattice Dirichlet series and does not depend on `period`. What reading still has to confirm is identification (b2), the 6 generators, and that `Character` matches the finite-order Hecke characters.

## Category check

- COMPUTED (Lean): 34 `#print axioms` outputs, all exactly [propext, Classical.choice, Quot.sound]. Log: results/2026-10-20-statement-checks/lean-build-final-v2.log; sources: lean-sources-v2.sha256.
- COMPUTED (numerical, not proved): results/2026-10-20-statement-checks/hecke-numeric-v2.txt. v1 is superseded; see hecke-numeric-NOTE.txt.
- STATED: the paper, 003.md and the Mathlib sources, cited by line in each report.
- INFERRED: marked in each report. The main ones: Q(ζ₃) = Q(√−3); `Character` = finite-order Hecke characters; the lattice sum = the ideal sum (6 generators per ideal); the identity theorem giving the continuation.
