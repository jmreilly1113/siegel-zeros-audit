# Statement check: HeckeSevenEighths (openai/math family 003)

Challenge: `lean/ComparatorChallenges/HeckeSevenEighths.lean` at openai/math fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb (sha256 cb5e404fa65a502c0a9006b9ad45c28914feb79e4b7b1ffcf05e4af82ed0cfc2; 245 lines). Paper: `preprints/The-Quasi-Riemann-Hypothesis-September-30-2026/build/paper.tex`, Theorem 1.1 (lines 106-111), definitions lines 50-64. Mathlib d13f23b, Lean 4.34.1.
Labels: STATED (in a source), COMPUTED (read off a file mechanically, or checked by Lean, or computed numerically where marked), INFERRED (my reasoning, not machine-checked).

```lean
theorem LFunction_ne_zero_of_seven_eighths_lt_re
    (χ : Character) {s : ℂ} (hs : (7 / 8 : ℝ) < s.re)
    (hpole : ¬ (χ.residue = 1 ∧ s = 1)) : LFunction χ s ≠ 0
```

## 1. Definition inventory

All of `Character`, `LFunction` and their supporting definitions are LOCAL, in the challenge file, lines 9-235. They are trusted text that a human has to read.
- The full file is quoted in docs/statement-check-003-steps1-3-DRAFT.md (Appendix).
- That draft also has the line-by-line closure table, and the Mathlib constants reached with their file:line at d13f23b.
- Not in the statement's closure: `shiftedPair` and its three lemmas (lines 91-109).

The Hecke L-function over Q(√−3) (COMPUTED from the code):
- **Field:** `K = CyclotomicField 3 ℚ`. **Ring of integers:** `O = 𝓞 K`. **ω:** `(zeta_spec 3 ℚ K).toInteger`.
- **Character:** a nonzero ideal `modulus`, and `residue : MulChar (O ⧸ modulus) ℂ` (Mathlib MulChar, zero on non-units; MulChar/Basic.lean:72-73; challenge line 220), trivial on the images of the units. Plus an auxiliary positive integer `period` in the modulus.
- **Conductor:** none is used.
- **L-function:** `LFunction χ s = π^s Γ(s)⁻¹ Λ(s) / 6`, where Λ is Mathlib's `WeakFEPair.Λ` of `pair (coefficients χ)`. That pair is a finite sum, over residues (a, b) mod `period` and a parity bit, of products of two rescaled even Hurwitz theta kernels with weight χ(a + bω).
- **Continuation:** inherited from `WeakFEPair.Λ`, which is defined on all of ℂ.

## 2. Translation table

| Formal component | Paper | Verdict |
|---|---|---|
| Field `CyclotomicField 3 ℚ` | F = Q(√−3) (l.50) | MATCHES (Q(ζ₃) = Q(√−3), INFERRED, standard) |
| Ring `𝓞 K`; every element is x + yω | 𝒪 (l.50) | MATCHES. COMPUTED by Lean: `HeckeHolo.coord_surj`. |
| `Character`: any modulus ≠ 0, any MulChar on O/𝔪 trivial on units | finite-order Hecke character mod 𝔣 = ray class character, extended by 0 (l.52-56) | MATCHES (INFERRED). O is a PID (Mathlib `three_pid`), so the ray class group mod 𝔪 is (O/𝔪)^×/image(O^×). |
| finite order | "finite-order" | MATCHES. O/𝔪 is finite (COMPUTED by Lean: the box maps onto it, `HeckeHolo.ψ_surj`). |
| imprimitive characters | included (Prop. prop:hecke-dirichlet-transfer, l.6716-6719) | MATCHES. No primitivity or conductor condition. |
| `period` (not in the paper) | not in the paper | MATCHES: settled by lemma. COMPUTED by Lean, `HeckeHolo.period_indep`: changing `period` leaves LFunction unchanged on ℂ minus {0, 1}. Also numerically: periods 7 and 14 agree (v2). |
| `LFunction χ s` | L_F(s, η) = Σ_𝔞 η(𝔞) N𝔞^(−s) for Re s > 1, and its continuation (l.58-64) | MATCHES (Joe's ruling, 2026-10-20). Rests on (a) and (b) below; see section 5. The Dedekind factorization was checked numerically for 5 characters, not proved. |
| `(7/8 : ℝ) < s.re` | Re s > 7/8, strict | MATCHES |
| `hpole : ¬ (χ.residue = 1 ∧ s = 1)` | principal pole at s = 1 allowed | MATCHES. COMPUTED by Lean: for residue ≠ 1 the pole coefficient g₀ is 0 and LFunction is holomorphic at 1 (`HeckeHolo.differentiableAt_one`). So s = 1 is a genuine value for exactly the characters the statement includes there. |
| `≠ 0` | "no zero" | MATCHES |

## 3. Junk values

- **s = 1:** excluded for residue = 1, as 003.md line 12 says. For residue ≠ 1 the value is genuine (above).
- **s = 0** (outside the half-plane): for the trivial character of modulus O, the definition gives `LFunction trivialTop 0 = 0`, because Mathlib sets Γ(0) = 0 (COMPUTED by Lean, `HeckeHolo.trivialTop_at_zero`). The Dedekind zeta function of Q(√−3) is −1/6 there (INFERRED, standard). This has no effect on the statement, which only concerns Re s > 7/8.
- For every proper modulus, f₀ = χ(0) = 0 and the function is holomorphic at 0 (`HeckeHolo.differentiableAt_zero`).

## 4. Non-vacuity and checks

### Lean (COMPUTED). Files in statement-checks/StatementChecks/

Final clean build: results/2026-10-20-statement-checks/lean-build-final-v2.log, 34 `#print axioms` outputs, all exactly [propext, Classical.choice, Quot.sound]; no lemma uses the challenge's `sorry`. Sources: lean-sources-v2.sha256. The first final build (lean-build-final.log, 32 outputs) predates HeckeNorm.lean.

| Lemma (file) | Content |
|---|---|
| `Hecke.hyps_trivialTop` | the trivial character (modulus O) meets every hypothesis at s = 2 |
| `HeckeNontrivial.chi7`, `chi7_nontrivial`, `hyps_chi7` | an explicit nontrivial character: modulus (7), χ(z) = (N z / 7) via the ring maps ω ↦ 2, 4 mod 7; trivial on the 6 units (Mathlib `Units.mem`); χ(2 + ω) = −1; meets every hypothesis for all Re s > 7/8, including s = 1 |
| `Hecke.differentiableAt_LFunction`, `differentiableOn_halfPlane` | holomorphic at every s ≠ 0, 1, for every χ |
| `HeckeHolo.sum_coefficients_eq_zero`, `g₀_eq_zero`, `differentiableAt_one`, `differentiable_of_ne_one` | for residue ≠ 1: orthogonality, g₀ = 0, entire |
| `HeckeHolo.f₀_eq_zero`, `differentiableAt_zero`, `trivialTop_at_zero` | behaviour at s = 0 (section 3) |
| `HeckeSeries.LFunction_hasSum` | for Re s > 1 and every χ: `HasSum (fun q : ℤ×ℤ => a' χ q / (x² − xy + y²)^s / 6) (LFunction χ s)`, where a' is χ(x + yω) off 0 |
| `HeckeSeries.hasSum_pair_f`, `pair_f₀` | the theta function is Σ_ℤ² χ(x + yω) e^(−πt(x² − xy + y²)), and its constant term is χ(0) |
| `HeckeHolo.period_indep` | independence of `period` |
| `HeckeNontrivial.chi7_entire`, `chi7_series` | the above, applied to the nontrivial character |
| `HeckeNorm.norm_coordinateElement`, `absNorm_span_coordinateElement` | `Algebra.norm ℤ (x + yω) = x² − xy + y²` (determinant in the basis {1, ω}), and `Ideal.absNorm (span {x + yω}) = |x² − xy + y²|`, the paper's N𝔞 = |O/𝔞| (l.51). Optional item, done 12:43-12:50 within its 1-hour box. |

### Dedekind factorization (5c)

- Not proved in Lean. That the trivial character's L-function equals ζ(s)·L(s, χ₋₃) needs the representation-number identity #{(x, y) : x² − xy + y² = n} = 6 Σ_{d|n} χ₋₃(d), i.e. how rational primes factor in ℤ[ω] according to p mod 3. I did not find it in Mathlib, and judged it days rather than hours of work.
- The time box (09:52-10:18 used) went to the lattice identity, holomorphy, period independence and the nontrivial character above.

### Numerical (COMPUTED, numerical; not proved)

- Source and output: src/hecke_numeric.py; output results/2026-10-20-statement-checks/hecke-numeric-v2.txt. v1 (hecke-numeric.txt) had a cache defect and a mislabelled exact test; see hecke-numeric-NOTE.txt.
- Python 3.14.6, python-flint 0.9.0 (Arb, 200 bits), mpmath 1.3.0 (30 digits).
- Characters: modulus O (periods 1, 2) and modulus (7) with ψⁱ∘N, i = 0, 1, 2, 3 (periods 7, 14). i = 1 has order 6, i = 2 order 3, i = 3 is quadratic and equals `chi7`.
- Structure verified by enumeration first: (O/7)^× has 36 elements, the 6 units are distinct mod 7, and each ψⁱ∘N is trivial on units, multiplicative and 7-periodic.
- **DEF:** the challenge definitions mirrored term by term: Hurwitz kernels, rescale, product, shifts, finitePair, WeakFEPair.Λ, latticeL / 6.
- **NORM:** independent: (1/6) Σ χ(x + yω)/(x² − xy + y²)^s over norms ≤ 40,000 in Arb, with a rigorous tail bound.
- **DIR:** independent: L(s, ψⁱ)·L(s, ψⁱχ₋₃) from Arb Hurwitz zeta values; for modulus O this is ζ(s)L(s, χ₋₃).
- Points: s = 2, 5/2, 3.
- Result (v2): |DEF − DIR| ≤ 1.1·10⁻¹⁶ in every case. |DEF − NORM| is within the rigorous tail bound in every case. Both periods give the same values.
- g₀ = 0 exactly for i = 1, 2, 3 (exact count of exponent classes) and ≠ 0 for the trivial characters (modulus O and ψ⁰ mod 7).
- The functional-equation spot check f(1/x) = x·g(x) at x = 3/2 agrees to ≤ 2·10⁻³⁰ for every character and period.
- v2 ran 2026-10-20 in 4,273 s. Its 30 DEF values are identical to v1's.

## 5. Verdict

**LFunction row: MATCHES (Joe's ruling, 2026-10-20).** The basis:

(a) COMPUTED by Lean:
- for Re s > 1, `LFunction χ s` equals the lattice Dirichlet series (1/6) Σ_((x,y)≠0) χ(x + yω)/(x² − xy + y²)^s (`HeckeSeries.LFunction_hasSum`);
- `LFunction χ` is holomorphic on ℂ minus {0, 1} (`Hecke.differentiableAt_LFunction`), and entire for nontrivial χ.

By the identity theorem (INFERRED; the same Mathlib theorem is used in Lean for `period_indep`), these two facts fix the function on the connected set ℂ minus {0, 1}, and so in the strip 7/8 < Re s ≤ 1 of the statement.

(b) The standard identifications that turn the lattice series into the paper's L_F(s, η) = Σ_𝔞 η(𝔞) N𝔞^(−s):
- N(x + yω) = x² − xy + y². Joe's ruling lists this as INFERRED; it is now also COMPUTED by Lean (`HeckeNorm.norm_coordinateElement`, `absNorm_span_coordinateElement`).
- Each nonzero ideal has exactly 6 generators, because O is a PID (Mathlib `three_pid`) with 6 units (Mathlib `Units.mem`), and χ is trivial on units. Hence (1/6) Σ_(α≠0) = Σ_𝔞. INFERRED; not formalized here.

Not proved: the Dedekind factorization (trivial character = ζ(s)L(s, χ₋₃)). It was checked numerically for 5 characters (section 4), not proved.

Other rows:
- All MATCHES. The `period` row is settled by `HeckeHolo.period_indep`.
- Every hypothesis is satisfiable, for a trivial and a nontrivial character (Lean).
- The only junk value found is at s = 0 for the modulus-O character, outside the half-plane.

INFERRED overall: the statement says what Theorem 1.1 says for finite-order Hecke L-functions over Q(√−3).

What remains for a human:
- read the local definitions (lines 9-235), whose behaviour the Lean lemmas now pin down;
- check identification (b2), the 6 generators, and the identification of `Character` with finite-order Hecke characters (row 3).
