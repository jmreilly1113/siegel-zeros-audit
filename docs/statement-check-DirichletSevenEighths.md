# Statement check: DirichletSevenEighths (openai/math family 003)

Challenge: `lean/ComparatorChallenges/DirichletSevenEighths.lean` at openai/math fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb (sha256 8fb13ad977bca104591fcbc6ef01a58496e7385053c9b1445f95749afc0eff54). Paper: `preprints/The-Quasi-Riemann-Hypothesis-September-30-2026/build/paper.tex`, Theorem 1.1 (lines 106-111), definitions lines 65-72, Prop. `prop:hecke-dirichlet-transfer` (lines 6705-6781). Mathlib d13f23b, Lean 4.34.1.
Labels: STATED, COMPUTED, INFERRED as in the summary.

## Definition inventory (COMPUTED)

```lean
theorem LFunction_ne_zero_of_seven_eighths_lt_re
    {q : ℕ} [NeZero q] (χ : DirichletCharacter ℂ q) {s : ℂ}
    (hs : (7 / 8 : ℝ) < s.re) (hpole : ¬ (χ = 1 ∧ s = 1)) :
    _root_.DirichletCharacter.LFunction χ s ≠ 0
```

| Constant | Defined at (Mathlib d13f23b) | Kind |
|---|---|---|
| `DirichletCharacter ℂ q` | Mathlib/NumberTheory/DirichletCharacter/Basic.lean:40 (`MulChar (ZMod q) ℂ`) | Mathlib |
| `MulChar` | Mathlib/NumberTheory/MulChar/Basic.lean:72-73 (zero on non-units) | Mathlib |
| `DirichletCharacter.LFunction` | Mathlib/NumberTheory/LSeries/DirichletContinuation.lean:61 (`ZMod.LFunction χ s`) | Mathlib |
| `ZMod.LFunction` | Mathlib/NumberTheory/LSeries/ZMod.lean:85 (`N^(−s) Σ_j Φ j · hurwitzZeta (j/N) s`) | Mathlib |
| `hurwitzZeta` | Mathlib/NumberTheory/LSeries/HurwitzZeta.lean:54 | Mathlib |
| `NeZero` | Lean core Init/Data/NeZero.lean:29 | core |

No local definitions.

## Translation table

| Formal component | Paper | Verdict |
|---|---|---|
| all `q ≥ 1` (`NeZero q`), q = 1 included | every Dirichlet L-function; the character mod 1 gives ζ (l.65-72, l.109) | MATCHES |
| every `χ : DirichletCharacter ℂ q`: primitive, imprimitive, principal | "every Dirichlet L-function", χ extended by zero (l.65); imprimitive in the transfer (l.6719-6721) | MATCHES |
| `LFunction χ s` = Σ χ(n) n^(−s) for Re s > 1, continued (Mathlib `LFunction_eq_LSeries`) | L(s, χ) and its continuation (l.67-71) | MATCHES |
| `(7/8 : ℝ) < s.re` | Re s > 7/8, strict | MATCHES |
| `hpole : ¬ (χ = 1 ∧ s = 1)` | principal pole at s = 1 allowed | MATCHES. For χ ≠ 1, s = 1 is included, and Mathlib's L is entire there (`differentiable_LFunction`), so it is a genuine value. |
| `≠ 0` | "no zero" | MATCHES |

## Junk value at s = 1

- The junk value is never used: (χ = 1, s = 1) is excluded by `hpole`, as 003.md line 12 says.
- For q = 1 this exclusion is slightly more than needed, since `riemannZeta 1 ≠ 0` in Mathlib.

## Non-vacuity (COMPUTED by Lean; statement-checks/StatementChecks/Dirichlet.lean)

| Lemma | Content | `#print axioms` |
|---|---|---|
| `chi4_ne_one` | `chi4 := ZMod.χ₄` cast to ℂ is a nonprincipal character mod 4 | propext, Classical.choice, Quot.sound |
| `hyps_nonprincipal` | all hypotheses hold for `chi4`, s = 2 | same |
| `hyps_principal` | all hypotheses hold for the principal character mod 4, s = 2 | same |
| `eq_dirichlet_series` | `LFunction χ s = LSeries χ s` for `1 < re s`, every χ | same |
| `modOne_has_zero` | for q = 1, `LFunction χ (-2) = 0`: the conclusion is a real restriction | same |

Build log: results/2026-10-20-statement-checks/lean-build-final.log.

## Verdict

- COMPUTED: Mathlib definitions only. Hypotheses satisfiable for a principal and a nonprincipal character. The function is the Dirichlet series for Re s > 1 and has zeros elsewhere.
- INFERRED: the statement says exactly what Theorem 1.1 says for Dirichlet L-functions.
