# Statement check, family 003: steps 1-3 (DRAFT for Joe's review, step 4)

> Superseded for verdicts by docs/statement-check-summary.md and the three per-challenge reports (2026-10-20). The UNCLEAR rows below were resolved: `period` by the Lean lemma `period_indep`, and the LFunction row by Joe's ruling (MATCHES), after the Lean work in step 5. Kept as the step 1-3 record; it also holds the full Hecke file (Appendix).

Read-only: no builds. Sources:
- openai/math fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb (clean clone /home/checker/math): `lean/ComparatorChallenges/{QuasiRiemannHypothesis,DirichletSevenEighths,HeckeSevenEighths}.lean` and `.json`, and `lean/docs/003.md`.
- The paper: `preprints/The-Quasi-Riemann-Hypothesis-September-30-2026/build/paper.tex` (16,677 lines). Correction (Joe, 2026-10-20): `preprints/The-Quasi-Riemann-Hypothesis-October-5-2026/build/paper2.tex` is not a later version of this paper. It is the companion paper, "The Quasi-Riemann Hypothesis" (October 5, 2026, "written with human assistance"), which proves the half-plane Re s > 11/12 (paper2.tex lines 47, 74). The first draft of this file wrongly called it a later version.
- Mathlib d13f23b723b8a846827a245b89c10fc7d3f11612, read in `lean/.lake/packages/mathlib`. Lean core v4.34.1.

Labels: STATED = written in a source. COMPUTED = read off a file mechanically (grep/sed, with line numbers). INFERRED = my reasoning, not checked by machine.

All three configs (COMPUTED): `definition_names` [], permitted axioms propext, Quot.sound and Classical.choice, `enable_nanoda` false. Each challenge file has `import Mathlib` only. There are no non-Mathlib imports, so every non-Mathlib constant is defined in the challenge file itself.

---

## Step 1. Definition inventory

### 1.1 QuasiRiemannHypothesis

Statement (QuasiRiemannHypothesis.lean lines 5-7):
```lean
theorem riemannZeta_ne_zero_of_seven_eighths_lt_re
    {s : ℂ} (hs : (7 / 8 : ℝ) < s.re) : riemannZeta s ≠ 0
```

| Constant | Defined at (Mathlib d13f23b) | Kind |
|---|---|---|
| `riemannZeta` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:121, `def riemannZeta := hurwitzZetaEven 0` | Mathlib |
| `hurwitzZetaEven` (unfolding of the above) | Mathlib/NumberTheory/LSeries/HurwitzZetaEven.lean:585 | Mathlib |
| `Complex` (ℂ), `Complex.re` | Mathlib/Basic/Complex/Basic.lean:35 | Mathlib |
| `(7 / 8 : ℝ)`, `<`, `≠`, `0` | core, Mathlib real numbers | Mathlib/core |

Local definitions: none.

### 1.2 DirichletSevenEighths

Statement (DirichletSevenEighths.lean lines 8-11, inside `namespace OAI.DirichletCharacter`, with `open scoped _root_.DirichletCharacter`):
```lean
theorem LFunction_ne_zero_of_seven_eighths_lt_re
    {q : ℕ} [NeZero q] (χ : DirichletCharacter ℂ q) {s : ℂ}
    (hs : (7 / 8 : ℝ) < s.re) (hpole : ¬ (χ = 1 ∧ s = 1)) :
    _root_.DirichletCharacter.LFunction χ s ≠ 0
```

| Constant | Defined at (Mathlib d13f23b) | Kind |
|---|---|---|
| `DirichletCharacter ℂ q` | Mathlib/NumberTheory/DirichletCharacter/Basic.lean:40, `abbrev DirichletCharacter R n := MulChar (ZMod n) R` | Mathlib |
| `MulChar` | Mathlib/NumberTheory/MulChar/Basic.lean:72: a monoid hom sending non-units to 0 | Mathlib |
| `DirichletCharacter.LFunction` | Mathlib/NumberTheory/LSeries/DirichletContinuation.lean:61, `:= ZMod.LFunction χ s` | Mathlib |
| `ZMod.LFunction` | Mathlib/NumberTheory/LSeries/ZMod.lean:85, `N ^ (-s) * ∑ j : ZMod N, Φ j * hurwitzZeta (toAddCircle j) s` | Mathlib |
| `hurwitzZeta` | Mathlib/NumberTheory/LSeries/HurwitzZeta.lean:54 | Mathlib |
| `NeZero q` | Lean core Init/Data/NeZero.lean:29 | core |
| `χ = 1` (the trivial MulChar) | MulChar's `One` instance, Mathlib/NumberTheory/MulChar/Basic.lean | Mathlib |
| `Complex.re`, `s = 1`, `≠ 0` | as above | Mathlib/core |

Local definitions: none. The namespace `OAI.DirichletCharacter` only holds the theorem name; the statement uses `_root_.DirichletCharacter.LFunction`.

### 1.3 HeckeSevenEighths: every definition below is LOCAL and must be read by a human

The statement (lines 237-239):
```lean
theorem LFunction_ne_zero_of_seven_eighths_lt_re
    (χ : Character) {s : ℂ} (hs : (7 / 8 : ℝ) < s.re)
    (hpole : ¬ (χ.residue = 1 ∧ s = 1)) : LFunction χ s ≠ 0
```

Every local definition is quoted in full in the Appendix: the whole challenge file, 245 lines, copied from fd4aeeb. Its closure through the challenge file (COMPUTED by reading the file; line numbers are HeckeSevenEighths.lean):

| Local constant | Lines | Role |
|---|---|---|
| `SevenEighths.HeckeFamily.K` | 208 | `abbrev K := CyclotomicField 3 ℚ`: the field Q(ζ₃) = Q(√−3) |
| `O` | 209 | `abbrev O := NumberField.RingOfIntegers K` |
| instance `IsCyclotomicExtension {3} ℚ K` | 211 | from Mathlib `CyclotomicField.isCyclotomicExtension` |
| `omega` | 213 | `(IsCyclotomicExtension.zeta_spec 3 ℚ K).toInteger`: a primitive cube root of unity, as an element of O |
| `coordinateElement x y` | 215 | `x + y * omega` in O |
| `Character` | 217-224 | structure: `modulus : Ideal O`, `modulus ≠ ⊥`, `residue : MulChar (O ⧸ modulus) ℂ`, `unit_trivial` (residue is 1 on the image of every unit of O), `period : ℕ`, `0 < period`, `(period : O) ∈ modulus` |
| instance `NeZero χ.period` | 226 | |
| `elementCoeff χ z` | 228 | `χ.residue (Ideal.Quotient.mk χ.modulus z)` |
| `coefficients χ (a : Fin period × Fin period)` | 230-231 | `elementCoeff χ (coordinateElement a.1 a.2)` |
| `continuedLattice χ` | 233 | `HeckeTheta.latticeL (coefficients χ)` |
| `LFunction χ s` | 235 | `continuedLattice χ s / 6` |
| `HeckeTheta.latticeL w s` | 201-202 | `π ^ s * (Gamma s)⁻¹ * completed w s` |
| `HeckeTheta.completed w` | 199 | `(pair w).Λ` |
| `HeckeTheta.pair w` | 194-197 | `finitePair` over `(Fin N × Fin N) × Fin 2` of `parityPair a b N e`, weights `w (a, b)` |
| `HeckeTheta.finitePair P hk w` | 161-192 | WeakFEPair with `f = ∑ w i • (P i).f`, `g = ∑ (w i * (P i).ε) • (P i).g`, `k = 1`, `ε = 1`, `f₀ = ∑ w i * (P i).f₀`, `g₀ = ∑ w i * (P i).ε * (P i).g₀`, plus proofs |
| `HeckeTheta.locallyIntegrableOn_sum` | 155-159 | lemma used inside `finitePair` (a proof; does not affect values) |
| `EisensteinTheta.parityPair a b L hL e` | 146-148 | `rectangularPair (xShift a b L e) (yShift b L e) (L^2) (3 * L^2)` |
| `EisensteinTheta.xShift a b L e` | 143 | `(2a − b − L·e) / (2L)` |
| `EisensteinTheta.yShift b L e` | 144 | `(b + L·e) / (2L)` |
| `ThetaProduct.rectangularPair a b u v` | 128-132 | `product (scaledEvenPair a u) (scaledEvenPair b v)` |
| `ThetaProduct.rectangularPair_k` | 134-136 | lemma `k = 1`, used as the `hk` argument of `finitePair` |
| `ThetaProduct.scaledEvenPair a u` | 111-114 | `rescale (HurwitzZeta.hurwitzEvenFEPair a) … u` |
| `ThetaProduct.scaledEvenPair_f_continuous`, `_g_continuous` | 116-126 | continuity lemmas (proofs) |
| `ThetaProduct.rescale P u` | 66-89 | WeakFEPair: `f x = P.f (u x)`, `g x = P.g (u⁻¹ x)`, `k = P.k`, `ε = P.ε · u^(−P.k)`, `f₀ = P.f₀`, `g₀ = P.g₀` |
| `ThetaProduct.rapid_rescale` | 53-64 | lemma used by `rescale` (proof) |
| `ThetaProduct.product P Q` | 32-51 | WeakFEPair: `f = P.f · Q.f`, `g = P.g · Q.g`, `k = P.k + Q.k`, `ε = P.ε · Q.ε`, `f₀ = P.f₀ · Q.f₀`, `g₀ = P.g₀ · Q.g₀` |
| `ThetaProduct.rapid_product_sub` | 11-30 | lemma used by `product` (proof) |
| `ThetaProduct.shiftedPair`, `shiftedPair_k`, `shiftedPair_f`, `shiftedPair_differentiableAt` | 91-109 | in the file but NOT in the statement's closure (`pair` does not use them) |

Mathlib constants reached by the Hecke definitions (Mathlib d13f23b):

| Constant | Location | Note |
|---|---|---|
| `CyclotomicField 3 ℚ` | Mathlib/NumberTheory/Cyclotomic/Basic.lean:654, `(cyclotomic n K).SplittingField` | the field |
| `CyclotomicField.isCyclotomicExtension` | Mathlib/NumberTheory/Cyclotomic/Basic.lean:674 | instance |
| `NumberField.RingOfIntegers` (𝓞 K) | Mathlib/NumberTheory/NumberField/Basic.lean:104 | ring of integers |
| `IsCyclotomicExtension.zeta`, `zeta_spec` | Mathlib/NumberTheory/Cyclotomic/PrimitiveRoots.lean:87, :93 | a chosen primitive 3rd root of unity |
| `IsPrimitiveRoot.toInteger` | Mathlib/NumberTheory/NumberField/Cyclotomic/Basic.lean:185 | |
| `Ideal`, `Ideal.Quotient.mk` | Mathlib/RingTheory/Ideal/Defs.lean:40; Mathlib/RingTheory/Ideal/Quotient/Defs.lean:83 | |
| `MulChar` | Mathlib/NumberTheory/MulChar/Basic.lean:72-73: `structure MulChar extends MonoidHom R R'` with `map_nonunit' : ∀ a : R, ¬IsUnit a → toFun a = 0` | sends non-units to 0. The character's map is exactly this: HeckeSevenEighths.lean:220, `residue : MulChar (O ⧸ modulus) ℂ` (Joe's item 2) |
| `WeakFEPair` (structure) | Mathlib/NumberTheory/LSeries/AbstractFuncEq.lean:82 | fields f, g, k, ε, f₀, g₀ and hypotheses |
| `WeakFEPair.Λ₀`, `WeakFEPair.Λ`, `f_modif` | AbstractFuncEq.lean:378, :381, :249 | `Λ s = Λ₀ s − (1/s)•f₀ − (ε/(k−s))•g₀`; `Λ₀ = mellin f_modif` (entire, `differentiable_Λ₀`) |
| `WeakFEPair.hasMellin` | AbstractFuncEq.lean:407 | for `k < re s`, `Λ s` is the Mellin transform of `f − f₀` |
| `mellin` | Mathlib/Analysis/MellinTransform.lean:91 | |
| `HurwitzZeta.hurwitzEvenFEPair a` | Mathlib/NumberTheory/LSeries/HurwitzZetaEven.lean:256 | f = evenKernel a, g = cosKernel a, k = 1/2, ε = 1, f₀ = if a = 0 then 1 else 0, g₀ = 1 |
| `HurwitzZeta.evenKernel`, `cosKernel` | HurwitzZetaEven.lean:67, :91 | built from `jacobiTheta₂`; `hasSum_int_evenKernel` (:165) gives evenKernel a t = Σ_(n∈ℤ) exp(−π (n+a)² t) |
| `jacobiTheta₂` | Mathlib/NumberTheory/ModularForms/JacobiTheta/TwoVariable.lean:251 | |
| `UnitAddCircle` | Mathlib/Topology/Instances/AddCircle/Real.lean:48 | ℝ/ℤ; the shifts are cast into it |
| `Complex.Gamma` | Mathlib/Analysis/SpecialFunctions/Gamma/Basic.lean:287; `Gamma_zero : Gamma 0 = 0` at :340 | |
| `Real.pi` | Mathlib/Analysis/SpecialFunctions/Trigonometric/Basic.lean:128 | |
| `Complex.cpow` | Mathlib/Analysis/SpecialFunctions/Pow/Complex.lean:27 | |

**Flag: how the Hecke L-function over Q(√−3) is defined.** Each piece:
- **Field and ring of integers** (STATED by the code): K = `CyclotomicField 3 ℚ`, O = 𝓞 K. The challenge never names √−3. Q(ζ₃) = Q(√−3) is standard (INFERRED).
- **Ideals:** `Ideal O`, and the modulus must be nonzero.
- **Hecke character:** `Character` is a modulus 𝔪 ≠ 0 with a multiplicative character of the finite ring O/𝔪 (zero on non-units) that is trivial on the image of the units of O, plus an auxiliary positive integer `period` lying in 𝔪.
  - INFERRED: O is a principal ideal domain. Mathlib proves this as `three_pid`, Mathlib/NumberTheory/NumberField/Cyclotomic/PID.lean:34; the challenge does not use that lemma.
  - So the ray class group mod 𝔪 is (O/𝔪)^× / (image of O^×), and a `Character` is the same thing as a finite-order Hecke (ray class) character mod 𝔪, extended by 0 to ideals not coprime to 𝔪. This matches the paper's definition (paper.tex lines 52-56).
  - The modulus need not be the conductor, so imprimitive characters are included.
- **Conductor:** not used. No conductor or primitivity appears.
- **L-series:** no Dirichlet series is written down. `LFunction χ s = π^s Γ(s)^(−1) Λ_pair(s) / 6`, where `pair` is a finite sum, over residues (a,b) mod N = `period` and a parity bit e, of products of two rescaled even Hurwitz theta kernels with weight χ(a + bω).
- **Continuation:** comes from Mathlib's `WeakFEPair.Λ`, which is defined on all of ℂ (Λ₀ entire, minus the terms f₀/s and ε g₀/(k−s)).
- INFERRED (my hand derivation, to be tested in step 5):
  - With xShift and yShift as defined, substituting X = N(m+n) + a and y = b + N(2n+e) turns the exponent into −πt(X² − Xy + y²) = −πt·N(X + yω).
  - So `pair.f(t) = Σ_((x,y)∈ℤ²) χ(x + yω) exp(−π t N(x + yω))`.
  - By `hasMellin`, for Re s > 1: `Λ_pair(s) = π^(−s) Γ(s) Σ_(α∈O, α≠0) χ(α) N(α)^(−s)`. Hence `LFunction χ s = (1/6) Σ_(α≠0) χ(α)/N(α)^s = Σ_(𝔞≠0) χ(𝔞)/N𝔞^s`, using 6 = |O^×|, χ trivial on units, and O a PID.
  - That is the paper's L_F(s, η) (paper.tex lines 58-63).
  - This derivation is not machine-checked. It is the main thing a human (or step 5) has to confirm.

## Step 2. Translation tables

Paper statement: Theorem 1.1, `\label{thm:main}`, paper.tex lines 106-111: "Every finite-order Hecke L-function over F = Q(√−3) has no zero in Re s > 7/8. The same holds for every Dirichlet L-function, including ζ(s). A pole at s = 1 for a principal character is allowed." Definitions: lines 50-75. Reduction to primitive characters and the Dirichlet transfer: Proposition `prop:hecke-dirichlet-transfer`, lines 6705-6781. Final step: lines 16455-16463.

### 2.1 QuasiRiemannHypothesis

| Formal component | Paper (Theorem 1.1, l.106-111; l.71-72) | Verdict |
|---|---|---|
| `riemannZeta s`: Mathlib's ζ, the continuation of Σ n^(−s) (`zeta_eq_tsum_one_div_nat_cpow`, RiemannZeta.lean:207) | ζ(s), "the character modulo 1" (l.71-72) | MATCHES. The standard function. |
| `(7/8 : ℝ) < s.re` | "Re s > 7/8", strict (l.108, l.116) | MATCHES |
| `≠ 0` at every such s | "has no zero" | MATCHES away from s = 1 |
| s = 1 not excluded | "A pole at s = 1 … is allowed" (l.110): no claim at s = 1 | STRONGER, but only through a junk value. At s = 1 Lean claims ζ(1) ≠ 0 for Mathlib's assigned value (step 3), which says nothing about zeros. |

### 2.2 DirichletSevenEighths

| Formal component | Paper | Verdict |
|---|---|---|
| Moduli: every `q : ℕ` with `NeZero q`, i.e. all q ≥ 1 | "every Dirichlet L-function"; "the character modulo 1 gives ζ" (l.65-72, l.109) | MATCHES. All positive moduli, q = 1 included. |
| Characters: every `χ : DirichletCharacter ℂ q` (MulChar on ZMod q): primitive and imprimitive, principal included | "every Dirichlet L-function", "χ modulo q, extended by zero on nonunits" (l.65); imprimitive handled in Prop. prop:hecke-dirichlet-transfer (l.6719-6721) | MATCHES |
| `LFunction χ s`: Mathlib's continuation, equal to Σ χ(n) n^(−s) for Re s > 1 (`LFunction_eq_LSeries`, DirichletContinuation.lean:75) | L(s, χ) and its meromorphic continuation (l.67-71) | MATCHES |
| `(7/8 : ℝ) < s.re` | Re s > 7/8 strict | MATCHES |
| `hpole : ¬ (χ = 1 ∧ s = 1)`: only the trivial character mod q at s = 1 is excluded | "pole at s = 1 for a principal character is allowed" | MATCHES. `χ = 1` is the principal character mod q, and the paper's "principal" means the same. For χ ≠ 1, s = 1 is included; Mathlib's L is entire there (`differentiable_LFunction`, DirichletContinuation.lean:98), so this is a genuine value, not a junk one. |
| `≠ 0` | "no zero" | MATCHES |

### 2.3 HeckeSevenEighths

| Formal component | Paper | Verdict |
|---|---|---|
| Field: `CyclotomicField 3 ℚ` | F = Q(√−3) (l.50) | MATCHES. INFERRED: Q(ζ₃) = Q(√−3). |
| Ring of integers: `𝓞 K`; `omega` = ζ₃ as an integer | 𝒪 (l.50) | MATCHES. INFERRED: 𝒪 = ℤ[ζ₃], so x + yω runs over all of 𝒪 once. |
| Characters: `Character`, any modulus 𝔪 ≠ 0, any MulChar on O/𝔪 trivial on units | "finite-order Hecke character η modulo a nonzero integral ideal 𝔣 … character of the ray class group mod 𝔣, extended by zero" (l.52-54) | MATCHES (INFERRED). With class number 1 (`three_pid`), ray class characters mod 𝔪 are exactly the characters of (O/𝔪)^× trivial on the image of units. All moduli; imprimitive included; no conductor condition. |
| Order of the character | "finite-order" | MATCHES. O/𝔪 is finite, so the characters have finite order automatically. |
| `period`: positive integer in 𝔪 | not in the paper | UNCLEAR, technical. The value of LFunction should not depend on the choice of period (INFERRED from the derivation); not checked. |
| `LFunction χ s = latticeL (coefficients χ) s / 6` | L_F(s, η) = Σ_𝔞 η(𝔞) N𝔞^(−s), then its continuation (l.58-64) | UNCLEAR, pending step 5. INFERRED by hand derivation (step 1.3) to equal Σ_(𝔞≠0) η(𝔞)/N𝔞^s for Re s > 1 and its continuation elsewhere; not machine-checked. |
| `(7/8 : ℝ) < s.re` | Re s > 7/8 strict | MATCHES |
| `hpole : ¬ (χ.residue = 1 ∧ s = 1)` | pole at s = 1 for the principal character allowed | MATCHES (INFERRED). residue = 1 exactly when the character is trivial (principal). For residue ≠ 1 the pole term vanishes: g₀ of `pair` is a constant times Σ over (ℤ/N)² of χ(x+yω), which is 0 for a nontrivial character because (ℤ/N)² ≅ O/NO maps onto O/𝔪 with equal fibers. f₀ = χ(0) = 0 unless 𝔪 = O, and then residue = 1. So Λ(1) is a genuine value when residue ≠ 1. |
| `≠ 0` | "no zero" | MATCHES |

## Step 3. Junk values at s = 1

| Statement | s = 1 | Finding |
|---|---|---|
| QuasiRiemannHypothesis | NOT excluded; covered by Mathlib's assigned value | COMPUTED (Mathlib source): `riemannZeta_one : riemannZeta 1 = (γ − log (4π)) / 2`, Mathlib/NumberTheory/Harmonic/ZetaAsymp.lean:421; `riemannZeta_one_ne_zero : riemannZeta 1 ≠ 0`, ZetaAsymp.lean:444. The junk value is nonzero, so the claim at s = 1 is true by a Mathlib lemma and adds no content. (Matches davegoldblatt's note.) |
| DirichletSevenEighths | For χ = 1: excluded by `hpole`. For χ ≠ 1: included, a genuine value (L entire) | Junk value never used. Note: for q = 1, χ = 1 and s = 1 is excluded although ζ(1) ≠ 0 in Mathlib, so the exclusion is a little more than needed. |
| HeckeSevenEighths | For residue = 1: excluded by `hpole`. For residue ≠ 1: included, a genuine value (INFERRED, step 2.3) | If residue = 1, Λ(1) would use Lean's x/0 = 0 in the term ε g₀/(k − s), a junk value, but the hypothesis excludes it. |

**003.md** (lean/docs/003.md line 12): "The principal-character poles at s = 1 are excluded in the Dirichlet and Hecke statements."
- COMPUTED: true for both, via `hpole` (DirichletSevenEighths.lean:10; HeckeSevenEighths.lean:239).
- 003.md makes no such claim for ζ, and the ζ statement does not exclude s = 1. It is covered by the nonzero junk value instead.

## Open items for step 5 (subject to approval)
- Confirm the Hecke L-function by machine (5b/5c). This is the one substantive UNCLEAR row.
- Whether the value is independent of `period`: covered implicitly if 5c holds for one choice; not otherwise planned.

## Appendix: HeckeSevenEighths.lean in full (openai/math fd4aeeb)


```lean
import Mathlib

namespace OAI

noncomputable section
open Filter Asymptotics Set MeasureTheory
open scoped Topology BigOperators

namespace SevenEighths.ThetaProduct

theorem rapid_product_sub (f g : ℝ → ℂ) (a b : ℂ)
    (hf : ∀ r : ℝ, (fun x => f x - a) =O[atTop] (fun x : ℝ => x ^ r))
    (hg : ∀ r : ℝ, (fun x => g x - b) =O[atTop] (fun x : ℝ => x ^ r))
    (r : ℝ) :
    (fun x => f x * g x - a * b) =O[atTop] (fun x : ℝ => x ^ r) := by
  have hg0 : g =O[atTop] (fun _ : ℝ => (1 : ℝ)) := by
    have hc : (fun _ : ℝ => b) =O[atTop] (fun x : ℝ => x ^ (0 : ℝ)) := by
      simpa using (isBigO_const_one ℝ b (atTop : Filter ℝ))
    have h := (hg 0).add hc
    simpa using h
  have h₁ := (hf r).mul hg0
  have h₂ := (hg r).const_mul_left a
  have hid : (fun x => f x * g x - a * b) =
      fun x => (f x - a) * g x + a * (g x - b) := by
    funext x
    ring
  rw [hid]
  have h₁' : (fun x => (f x - a) * g x) =O[atTop] (fun x : ℝ => x ^ r) := by
    simpa using h₁
  exact h₁'.add h₂

def product (P Q : WeakFEPair ℂ)
    (hPf : ContinuousOn P.f (Ioi 0)) (hPg : ContinuousOn P.g (Ioi 0))
    (hQf : ContinuousOn Q.f (Ioi 0)) (hQg : ContinuousOn Q.g (Ioi 0)) :
    WeakFEPair ℂ where
  f := fun x => P.f x * Q.f x
  g := fun x => P.g x * Q.g x
  k := P.k + Q.k
  ε := P.ε * Q.ε
  f₀ := P.f₀ * Q.f₀
  g₀ := P.g₀ * Q.g₀
  hf_int := (hPf.mul hQf).locallyIntegrableOn measurableSet_Ioi
  hg_int := (hPg.mul hQg).locallyIntegrableOn measurableSet_Ioi
  hk := add_pos P.hk Q.hk
  hε := mul_ne_zero P.hε Q.hε
  h_feq x hx := by
    rw [P.h_feq x hx, Q.h_feq x hx, Real.rpow_add hx]
    simp only [smul_eq_mul, Complex.ofReal_mul]
    ring
  hf_top := rapid_product_sub P.f Q.f P.f₀ Q.f₀ P.hf_top Q.hf_top
  hg_top := rapid_product_sub P.g Q.g P.g₀ Q.g₀ P.hg_top Q.hg_top

theorem rapid_rescale (f : ℝ → ℂ) (a : ℂ)
    (hf : ∀ r : ℝ, (fun x => f x - a) =O[atTop] (fun x : ℝ => x ^ r))
    {u : ℝ} (hu : 0 < u) (r : ℝ) :
    (fun x => f (u * x) - a) =O[atTop] (fun x : ℝ => x ^ r) := by
  have ht : Tendsto (fun x : ℝ => u * x) atTop atTop :=
    (tendsto_const_mul_atTop_of_pos hu).2 tendsto_id
  have h := (hf r).comp_tendsto ht
  have heq : (fun x : ℝ => (u * x) ^ r) =ᶠ[atTop]
      (fun x : ℝ => u ^ r * x ^ r) := by
    filter_upwards [eventually_ge_atTop (0 : ℝ)] with x hx
    exact Real.mul_rpow hu.le hx
  exact h.trans (heq.isBigO.trans ((isBigO_refl (fun x : ℝ => x ^ r) atTop).const_mul_left _))

def rescale (P : WeakFEPair ℂ)
    (hPf : ContinuousOn P.f (Ioi 0)) (hPg : ContinuousOn P.g (Ioi 0))
    (u : ℝ) (hu : 0 < u) : WeakFEPair ℂ where
  f := fun x => P.f (u * x)
  g := fun x => P.g (u⁻¹ * x)
  k := P.k
  ε := P.ε * (u ^ (-P.k) : ℝ)
  f₀ := P.f₀
  g₀ := P.g₀
  hf_int := (hPf.comp (by fun_prop) (fun x hx => mul_pos hu hx)).locallyIntegrableOn
    measurableSet_Ioi
  hg_int := (hPg.comp (by fun_prop) (fun x hx => mul_pos (inv_pos.mpr hu) hx)).locallyIntegrableOn
    measurableSet_Ioi
  hk := P.hk
  hε := mul_ne_zero P.hε (Complex.ofReal_ne_zero.mpr (Real.rpow_pos_of_pos hu _).ne')
  h_feq x hx := by
    have heq : u * (1 / x) = 1 / (u⁻¹ * x) := by field_simp
    rw [heq, P.h_feq _ (mul_pos (inv_pos.mpr hu) hx),
      Real.mul_rpow (inv_pos.mpr hu).le hx.le, Real.inv_rpow hu.le,
      ← Real.rpow_neg hu.le]
    simp only [smul_eq_mul, Complex.ofReal_mul]
    ring
  hf_top := rapid_rescale P.f P.f₀ P.hf_top hu
  hg_top := rapid_rescale P.g P.g₀ P.hg_top (inv_pos.mpr hu)

def shiftedPair (a b : UnitAddCircle) : WeakFEPair ℂ :=
  product (HurwitzZeta.hurwitzEvenFEPair a) (HurwitzZeta.hurwitzEvenFEPair b)
    (Complex.continuous_ofReal.comp_continuousOn (HurwitzZeta.continuousOn_evenKernel a))
    (Complex.continuous_ofReal.comp_continuousOn (HurwitzZeta.continuousOn_cosKernel a))
    (Complex.continuous_ofReal.comp_continuousOn (HurwitzZeta.continuousOn_evenKernel b))
    (Complex.continuous_ofReal.comp_continuousOn (HurwitzZeta.continuousOn_cosKernel b))

@[simp] theorem shiftedPair_k (a b : UnitAddCircle) : (shiftedPair a b).k = 1 := by
  norm_num [shiftedPair, product, HurwitzZeta.hurwitzEvenFEPair]

@[simp] theorem shiftedPair_f (a b : UnitAddCircle) (t : ℝ) :
    (shiftedPair a b).f t =
      (HurwitzZeta.evenKernel a t : ℂ) * (HurwitzZeta.evenKernel b t : ℂ) := rfl

theorem shiftedPair_differentiableAt (a b : UnitAddCircle) {s : ℂ}
    (hs₀ : s ≠ 0) (hs₁ : s ≠ 1) :
    DifferentiableAt ℂ (shiftedPair a b).Λ s := by
  exact (shiftedPair a b).differentiableAt_Λ (Or.inl hs₀)
    (Or.inl (by simpa using hs₁))

def scaledEvenPair (a : UnitAddCircle) (u : ℝ) (hu : 0 < u) : WeakFEPair ℂ :=
  rescale (HurwitzZeta.hurwitzEvenFEPair a)
    (Complex.continuous_ofReal.comp_continuousOn (HurwitzZeta.continuousOn_evenKernel a))
    (Complex.continuous_ofReal.comp_continuousOn (HurwitzZeta.continuousOn_cosKernel a)) u hu

theorem scaledEvenPair_f_continuous (a : UnitAddCircle) (u : ℝ) (hu : 0 < u) :
    ContinuousOn (scaledEvenPair a u hu).f (Ioi 0) :=
  (Complex.continuous_ofReal.comp_continuousOn
    (HurwitzZeta.continuousOn_evenKernel a)).comp (by fun_prop)
      (fun x hx => mul_pos hu hx)

theorem scaledEvenPair_g_continuous (a : UnitAddCircle) (u : ℝ) (hu : 0 < u) :
    ContinuousOn (scaledEvenPair a u hu).g (Ioi 0) :=
  (Complex.continuous_ofReal.comp_continuousOn
    (HurwitzZeta.continuousOn_cosKernel a)).comp (by fun_prop)
      (fun x hx => mul_pos (inv_pos.mpr hu) hx)

def rectangularPair (a b : UnitAddCircle) (u v : ℝ) (hu : 0 < u) (hv : 0 < v) :
    WeakFEPair ℂ :=
  product (scaledEvenPair a u hu) (scaledEvenPair b v hv)
    (scaledEvenPair_f_continuous a u hu) (scaledEvenPair_g_continuous a u hu)
    (scaledEvenPair_f_continuous b v hv) (scaledEvenPair_g_continuous b v hv)

@[simp] theorem rectangularPair_k (a b : UnitAddCircle) (u v : ℝ)
    (hu : 0 < u) (hv : 0 < v) : (rectangularPair a b u v hu hv).k = 1 := by
  norm_num [rectangularPair, scaledEvenPair, rescale, product, HurwitzZeta.hurwitzEvenFEPair]

end SevenEighths.ThetaProduct

namespace SevenEighths.EisensteinTheta
open ThetaProduct

def xShift (a b L : ℝ) (e : Fin 2) : ℝ := (2 * a - b - L * e) / (2 * L)
def yShift (b L : ℝ) (e : Fin 2) : ℝ := (b + L * e) / (2 * L)

def parityPair (a b L : ℝ) (hL : 0 < L) (e : Fin 2) : WeakFEPair ℂ :=
  rectangularPair (xShift a b L e) (yShift b L e) (L ^ 2) (3 * L ^ 2)
    (sq_pos_of_pos hL) (mul_pos (by norm_num) (sq_pos_of_pos hL))

end SevenEighths.EisensteinTheta

namespace SevenEighths.HeckeTheta
open EisensteinTheta

theorem locallyIntegrableOn_sum {ι : Type*} (s : Finset ι)
    (f : ι → ℝ → ℂ) (hf : ∀ i ∈ s, LocallyIntegrableOn (f i) (Ioi 0)) :
    LocallyIntegrableOn (∑ i ∈ s, f i) (Ioi 0) := by
  exact Finset.sum_induction f (fun g => LocallyIntegrableOn g (Ioi 0))
    (fun _ _ => LocallyIntegrableOn.add) (locallyIntegrableOn_const 0) hf

def finitePair {ι : Type*} [Fintype ι] (P : ι → WeakFEPair ℂ)
    (hk : ∀ i, (P i).k = 1) (w : ι → ℂ) : WeakFEPair ℂ where
  f := ∑ i, w i • (P i).f
  g := ∑ i, (w i * (P i).ε) • (P i).g
  k := 1
  ε := 1
  f₀ := ∑ i, w i * (P i).f₀
  g₀ := ∑ i, w i * (P i).ε * (P i).g₀
  hf_int := locallyIntegrableOn_sum Finset.univ _
    (fun i _ => (P i).hf_int.smul (w i))
  hg_int := locallyIntegrableOn_sum Finset.univ _
    (fun i _ => (P i).hg_int.smul (w i * (P i).ε))
  hk := by norm_num
  hε := one_ne_zero
  h_feq x hx := by
    simp only [Finset.sum_apply, Pi.smul_apply, smul_eq_mul, one_mul]
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro i _
    rw [(P i).h_feq x hx, hk i]
    simp only [smul_eq_mul]
    ring
  hf_top r := by
    have h := Asymptotics.IsBigO.fun_sum (s := Finset.univ)
      (fun i _ => ((P i).hf_top r).const_mul_left (w i))
    simpa only [Finset.sum_apply, Pi.smul_apply, smul_eq_mul, ← Finset.sum_sub_distrib,
      mul_sub] using h
  hg_top r := by
    have h := Asymptotics.IsBigO.fun_sum (s := Finset.univ)
      (fun i _ => ((P i).hg_top r).const_mul_left (w i * (P i).ε))
    simpa only [Finset.sum_apply, Pi.smul_apply, smul_eq_mul, ← Finset.sum_sub_distrib,
      mul_sub] using h

def pair {N : ℕ} [NeZero N] (w : Fin N × Fin N → ℂ) : WeakFEPair ℂ :=
  finitePair (fun p : (Fin N × Fin N) × Fin 2 =>
    parityPair p.1.1 p.1.2 N (Nat.cast_pos.mpr (NeZero.pos N)) p.2)
    (fun _ => ThetaProduct.rectangularPair_k ..) (fun p => w p.1)

def completed {N : ℕ} [NeZero N] (w : Fin N × Fin N → ℂ) : ℂ → ℂ := (pair w).Λ

def latticeL {N : ℕ} [NeZero N] (w : Fin N × Fin N → ℂ) (s : ℂ) : ℂ :=
  (Real.pi : ℂ) ^ s * (Complex.Gamma s)⁻¹ * completed w s

end SevenEighths.HeckeTheta

namespace SevenEighths.HeckeFamily

abbrev K := CyclotomicField 3 ℚ
abbrev O := NumberField.RingOfIntegers K

instance : IsCyclotomicExtension {3} ℚ K := CyclotomicField.isCyclotomicExtension 3 ℚ

def omega : O := (IsCyclotomicExtension.zeta_spec 3 ℚ K).toInteger

def coordinateElement (x y : ℤ) : O := (x : O) + (y : O) * omega

structure Character where
  modulus : Ideal O
  modulus_ne_bot : modulus ≠ ⊥
  residue : MulChar (O ⧸ modulus) ℂ
  unit_trivial : ∀ u : Oˣ, residue (Ideal.Quotient.mk modulus (u : O)) = 1
  period : ℕ
  period_pos : 0 < period
  period_mem : (period : O) ∈ modulus

instance (χ : Character) : NeZero χ.period := ⟨Nat.ne_of_gt χ.period_pos⟩

def elementCoeff (χ : Character) (z : O) : ℂ := χ.residue (Ideal.Quotient.mk χ.modulus z)

def coefficients (χ : Character) (a : Fin χ.period × Fin χ.period) : ℂ :=
  elementCoeff χ (coordinateElement a.1 a.2)

def continuedLattice (χ : Character) : ℂ → ℂ := HeckeTheta.latticeL (coefficients χ)

def LFunction (χ : Character) (s : ℂ) : ℂ := continuedLattice χ s / 6

theorem LFunction_ne_zero_of_seven_eighths_lt_re
    (χ : Character) {s : ℂ} (hs : (7 / 8 : ℝ) < s.re)
    (hpole : ¬ (χ.residue = 1 ∧ s = 1)) : LFunction χ s ≠ 0 := by sorry

end SevenEighths.HeckeFamily

end

end OAI
```

sha256 of the file: cb5e404fa65a502c0a9006b9ad45c28914feb79e4b7b1ffcf05e4af82ed0cfc2
