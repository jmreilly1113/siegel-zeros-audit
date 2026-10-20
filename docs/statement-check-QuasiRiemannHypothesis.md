# Statement check: QuasiRiemannHypothesis (openai/math family 003)

Challenge: `lean/ComparatorChallenges/QuasiRiemannHypothesis.lean` at openai/math fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb (sha256 065f8c9a01d28db78c8b1bfc5083b535082a2d2aac2230d563f98b8caa812cc5). Paper: `preprints/The-Quasi-Riemann-Hypothesis-September-30-2026/build/paper.tex`, Theorem 1.1 (`thm:main`, lines 106-111). Mathlib d13f23b, Lean 4.34.1.
Labels: STATED (in a source), COMPUTED (read off a file mechanically, or checked by Lean), INFERRED (my reasoning, not machine-checked).

## Definition inventory (COMPUTED)

```lean
theorem riemannZeta_ne_zero_of_seven_eighths_lt_re
    {s : ℂ} (hs : (7 / 8 : ℝ) < s.re) : riemannZeta s ≠ 0
```

| Constant | Defined at (Mathlib d13f23b) | Kind |
|---|---|---|
| `riemannZeta` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:121 (`hurwitzZetaEven 0`) | Mathlib |
| `hurwitzZetaEven` | Mathlib/NumberTheory/LSeries/HurwitzZetaEven.lean:585 | Mathlib |
| `Complex`, `Complex.re` | Mathlib/Basic/Complex/Basic.lean:35 | Mathlib |

No local definitions: the file imports only Mathlib.

## Translation table

| Formal component | Paper (Theorem 1.1, l.106-111; l.71-72) | Verdict |
|---|---|---|
| `riemannZeta s`, the continuation of Σ n^(−s) (Mathlib `zeta_eq_tsum_one_div_nat_cpow`) | ζ(s) | MATCHES |
| `(7/8 : ℝ) < s.re` | Re s > 7/8, strict (l.108, l.116) | MATCHES |
| `≠ 0` | "has no zero" | MATCHES |
| s = 1 not excluded | the pole is "allowed" (l.110): no claim at s = 1 | STRONGER, only through a junk value (see below) |

## Junk value at s = 1 (COMPUTED)

- The statement covers s = 1. There Mathlib assigns `riemannZeta 1 = (γ − log (4π)) / 2` (`riemannZeta_one`, Mathlib/NumberTheory/Harmonic/ZetaAsymp.lean:421), which is nonzero (`riemannZeta_one_ne_zero`, :444).
- So the claim at s = 1 is true by a Mathlib lemma and says nothing about zeros.
- Re-proved here as `StatementChecks.QRH.junk_at_one` and `junk_at_one_ne_zero`.
- This should be stated in any report of the result: the Lean theorem is formally stronger than the paper only at that one point, and only through Mathlib's convention.

## Non-vacuity (COMPUTED by Lean; statement-checks/StatementChecks/QRH.lean)

| Lemma | Content | `#print axioms` |
|---|---|---|
| `hyp_satisfiable` | `(7/8 : ℝ) < (2 : ℂ).re` | propext, Classical.choice, Quot.sound |
| `has_trivial_zero` | `riemannZeta (-2) = 0`: the conclusion is a real restriction | same |
| `eq_dirichlet_series` | `riemannZeta s = ∑' n, 1/n^s` for `1 < re s` | same |
| `junk_at_one`, `junk_at_one_ne_zero` | the value at s = 1 and its nonvanishing | same |

- Build: results/2026-10-20-statement-checks/lean-build-final.log.
- Sources and their sha256: results/2026-10-20-statement-checks/lean-sources.sha256.
- Only the challenge's own theorem uses `sorry`, and no lemma here depends on it (their axiom lists contain no `sorryAx`).

## Verdict

- COMPUTED: the statement uses only Mathlib definitions. Its hypothesis is satisfiable, and its function has zeros elsewhere and is the usual Dirichlet series for Re s > 1.
- INFERRED: the statement says what Theorem 1.1 says for ζ, plus the junk-value point s = 1, which is true by Mathlib and adds no content.
