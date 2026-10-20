<!-- DRAFT, not posted. Target: grwtsk/openai-math#29 ([AUDIT.26] bind paper statements to exact Lean declarations;
     its example is the September 30 quasi-Riemann manuscript). Related open issue: #10 (hostile statement and vacuity
     review). Approval needed before posting (Joe, 2026-10-20). -->

Statement check for the three other family-003 challenges, against Theorem 1.1 of The-Quasi-Riemann-Hypothesis-September-30-2026 (paper.tex l.106-111), at openai/math fd4aeeb, Mathlib d13f23b, Lean 4.34.1.

This covers the statement-binding part of this issue, not the PDF reproduction.

- **QuasiRiemannHypothesis:** matches Theorem 1.1 for ζ, with one point to note: the statement does not exclude s = 1. There it is covered by Mathlib's assigned value riemannZeta 1 = (γ − log 4π)/2, which is nonzero (riemannZeta_one_ne_zero). So the Lean statement is formally stronger only at s = 1, and only through that convention. Mathlib definitions only.
- **DirichletSevenEighths:** matches. All q ≥ 1, all characters (principal and imprimitive included), with exactly the principal pole at s = 1 excluded, as 003.md says. Mathlib definitions only.
- **HeckeSevenEighths:** matches. Character and LFunction are local definitions (challenge lines 9-235): a theta-function Mellin construction. The L-function identification rests on:
  - (a) Lean, in a separate project importing only the challenge file:
    - for Re s > 1, LFunction χ s = (1/6) Σ_((x,y)≠0) χ(x + yω)/(x² − xy + y²)^s, for every Character;
    - LFunction is holomorphic on ℂ minus {0, 1}, and entire for nontrivial characters.
    By the identity theorem these fix the function in the strip.
  - (b) Two standard identifications:
    - N(x + yω) = x² − xy + y², also proved in Lean (Algebra.norm, and Ideal.absNorm of the principal ideal);
    - each nonzero ideal has exactly 6 generators (O a PID, 6 units, χ trivial on units). This one is not formalized.

  Also proved in Lean: the value does not depend on the auxiliary period field, and an explicit nontrivial character mod (7) meets every hypothesis. The Dedekind factorization (trivial character = ζ(s)L(s, χ₋₃)) and its analogues for characters mod 7 were checked numerically, at s = 2, 5/2 and 3 for 5 characters, not proved. One junk value turned up: at s = 0, for the modulus-O character, the definition gives 0 (Mathlib Γ(0) = 0), outside the stated half-plane.

All Lean lemmas: 34 #print axioms outputs, each exactly [propext, Classical.choice, Quot.sound]; none uses the challenges' sorry.

The non-vacuity lemmas (satisfiable hypotheses, an explicit nontrivial Hecke character mod (7), ζ(−2) = 0, Dirichlet series agreement for Re s > 1) are also relevant to #10.

Scope: this checks that each Lean statement says what Theorem 1.1 says. It is not a review of the proofs (replayed separately, see #40) or of the paper's mathematics.

- Summary: https://github.com/jmreilly1113/siegel-zeros-audit/blob/1a11952e126ef4ec60af022de4fd056971332202/docs/statement-check-summary.md
- Reports: https://github.com/jmreilly1113/siegel-zeros-audit/blob/1a11952e126ef4ec60af022de4fd056971332202/docs/statement-check-QuasiRiemannHypothesis.md, https://github.com/jmreilly1113/siegel-zeros-audit/blob/1a11952e126ef4ec60af022de4fd056971332202/docs/statement-check-DirichletSevenEighths.md, https://github.com/jmreilly1113/siegel-zeros-audit/blob/1a11952e126ef4ec60af022de4fd056971332202/docs/statement-check-HeckeSevenEighths.md
- Lean project: https://github.com/jmreilly1113/siegel-zeros-audit/tree/1a11952e126ef4ec60af022de4fd056971332202/statement-checks
- Build log and numerical check: https://github.com/jmreilly1113/siegel-zeros-audit/tree/1a11952e126ef4ec60af022de4fd056971332202/results/2026-10-20-statement-checks
