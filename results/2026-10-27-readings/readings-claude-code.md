# Statement readings, 2026-10-27: Claude Code's reading, for Joe's review

These are Claude Code's readings, made on 2026-10-27 at Joe's request. They are **not** Joe's sign-off.
- Nothing here is copied into read_by as "J. Reilly", and no "Read by J. Reilly" line is written, until Joe gives his OK.
- Every finding is INFERRED, because it is a reading of text.
- Sources are at openai/math fd4aeeb (/home/checker/math, clean) and Mathlib d13f23b (lean/.lake/packages/mathlib, clean), unless stated otherwise.

## Readings 1-4: the four challenge statements

### 1. SiegelZeros vs the paper's Theorem 1 (refs/siegel-paper.tex:66-73)

Lean source: lean/ComparatorChallenges/SiegelZeros.lean:8-14 (exists_absolute_real_zero_gap) and 19-25 (WeightedTorusJets.dirichletRealZeroBound_proof).
- **Quantifier order:** `∃ c : ℝ, 0 < c ∧ ∀ (q : ℕ) [NeZero q], 3 ≤ q → ∀ χ ... → ∀ β ...`. The constant precedes q, χ and β, so c is absolute, as "absolute constant c > 0" requires. MATCH.
- **Hypotheses:**
  - `χ.IsPrimitive` (primitive);
  - `χ ≠ 1` (nonprincipal);
  - `∀ a : ZMod q, (χ a).im = 0` (real);
  - `3 ≤ q` (conductor ≥ 3; q is the level, and primitivity makes it the conductor);
  - `0 < β`, `β < 1`, `χ.LFunction β = 0` (a real zero in the open interval (0,1)).

  Nothing is added and nothing is missing. MATCH.
- **Conclusion:** `c ≤ (1 - β) * Real.log q`, i.e. (1 − β) log q ≥ c, non-strict as in (1.1). MATCH.
- **Mathlib meanings:**
  - IsPrimitive is `conductor χ = n` (Mathlib/NumberTheory/DirichletCharacter/Basic.lean:292). conductor is the least level through which χ factors (:246).
  - (χ a).im = 0 for all a means real-valued. The values are 0 or roots of unity, so they are 0 or ±1, which is exactly a real character.
  - `DirichletCharacter.LFunction` is `ZMod.LFunction χ` (LSeries/DirichletContinuation.lean:61), the continuation. It equals Σ χ(n) n^(−s) for Re s > 1 (:75) and is entire for χ ≠ 1 (:98). At real β in (0,1) it is the genuine L(β, χ).
  - MATCH.
- **Edge cases:**
  - q = 4 (χ₋₄, odd) and q = 8 (χ₈ even, χ₋₈ odd) are primitive, real and nonprincipal with q ≥ 3, so the statement covers them.
  - No hypothesis mentions parity, so both parities are included. lean/docs/003.md:16 also says "Both character parities are included."
  - Nothing excludes non-prime or even conductors.
  - MATCH.

**Proposed line: MATCH.**

### 2. QuasiRiemannHypothesis vs the main theorem of "The Quasi-Riemann Hypothesis" (September 30, 2026)

Paper: build/paper.tex:106-111 (thm:main): "... The same holds for every Dirichlet L-function, including ζ(s). A pole at s = 1 for a principal character is allowed."

Lean: QuasiRiemannHypothesis.lean:5-6, `{s : ℂ} (hs : (7 / 8 : ℝ) < s.re) : riemannZeta s ≠ 0`.
- **Quantifier order:** the constant 7/8 is a fixed literal, with no constant to place. MATCH.
- **Hypotheses:** only Re s > 7/8. There is no pole hypothesis; see the edge case. MATCH.
- **Conclusion:** `≠ 0` on the open half-plane Re s > 7/8 (strict). The paper says "the boundary Re s = 7/8 is not included" (l.116). MATCH.
- **Mathlib meanings:** riemannZeta is `hurwitzZetaEven 0` (LSeries/RiemannZeta.lean:121), the meromorphic continuation with a junk value at 1. MATCH.
- **Edge case s = 1:**
  - Mathlib sets riemannZeta 1 = (γ − log 4π)/2 (Harmonic/ZetaAsymp.lean:421), which is nonzero (riemannZeta_one_ne_zero).
  - So at s = 1 the Lean statement asserts a true fact about the junk value, not a claim about the pole.
  - The paper allows the pole at s = 1, so it claims no zero there.
  - The Lean statement says nothing false and leaves out nothing the paper claims. MATCH.

**Proposed line: MATCH.**

### 3. DirichletSevenEighths vs the same theorem

Lean: DirichletSevenEighths.lean:17-20, `{q : ℕ} [NeZero q] (χ : DirichletCharacter ℂ q) {s : ℂ} (hs : (7 / 8 : ℝ) < s.re) (hpole : ¬ (χ = 1 ∧ s = 1)) : LFunction χ s ≠ 0`.
- **Quantifier order:** fixed 7/8, uniform over every q ≥ 1, χ and s. MATCH.
- **Hypotheses:**
  - Any modulus q ≥ 1 and any character, including imprimitive ones and q = 1 (ζ).
  - The paper's definition is "a Dirichlet character χ modulo q, extended by zero on nonunits", with the series L(s, χ) = Σ χ(n) n^(−s) continued (l.64-70). It also includes imprimitive characters.
  - The pole allowance is `hpole : ¬ (χ = 1 ∧ s = 1)`, which excludes s = 1 only for the principal character mod q.
  - MATCH.
- **Conclusion:** `≠ 0`, strict half-plane. MATCH.
- **Mathlib meanings:**
  - LFunction is the continuation (above). For q = 1 it is riemannZeta (DirichletContinuation.lean:67, LFunction_modOne_eq).
  - For χ ≠ 1 it is entire, so its value at s = 1 is genuine and is covered.
  - MATCH.
- **Edge cases:**
  - Imprimitive nonprincipal characters have extra zeros only from Euler factors (1 − χ*(p) p^(−s)), on Re s = 0, which is outside the half-plane.
  - The principal character mod q > 1 has a pole at 1, which hpole excludes.
  - MATCH.

**Proposed line: MATCH.**

### 4. HeckeSevenEighths vs the same theorem

Paper: thm:main, first sentence (l.107-108): "Every finite-order Hecke L-function over F = Q(√−3) has no zero in Re s > 7/8". Definitions are at l.48-63.

Lean: HeckeSevenEighths.lean:217-239. The L-function is defined locally at lines 9-235 (theta construction, `LFunction χ s = continuedLattice χ s / 6`).
- **Quantifier order:** fixed 7/8; every `Character`. MATCH.
- **Hypotheses:**
  - Character = any nonzero ideal modulus 𝔪 and any MulChar on O/𝔪 trivial on units (lines 217-224). MulChar is zero on non-units (Mathlib MulChar/Basic.lean:73).
  - O = 𝓞(Q(ζ₃)) is a PID with 6 units, so these are exactly the characters of the ray class group mod 𝔪, (O/𝔪)^×/image(O^×), extended by zero to ideals not coprime to 𝔪. That is the paper's definition at l.51-53; the complex place adds nothing (l.55-56).
  - Imprimitive characters are included on both sides.
  - `period` is an auxiliary parameter; the 2026-10-20 Lean lemma HeckeHolo.period_indep shows it does not matter.
  - The pole allowance is `hpole : ¬ (χ.residue = 1 ∧ s = 1)`, the principal character only.
  - MATCH.
- **Conclusion:** `≠ 0`, strict half-plane. MATCH.
- **Definitions mean what the paper means:** this rests on the 2026-10-20 Lean lemmas (docs/statement-check-HeckeSevenEighths.md §4-5):
  - for Re s > 1, LFunction χ s = (1/6) Σ_{(x,y)≠0} χ(x + yω)/(x² − xy + y²)^s;
  - LFunction χ is holomorphic on ℂ minus {0, 1};
  - N(x + yω) = x² − xy + y² = |O/(x + yω)|.

  By the identity theorem this fixes the function in the strip 7/8 < Re s ≤ 1.
- **The identification Joe ruled on 2026-10-20 (each nonzero ideal has exactly 6 generators), re-read:**
  - O = ℤ[ω] is a PID, and its unit group {±1, ±ω, ±ω²} has 6 elements and acts freely on O minus {0}. So every nonzero ideal 𝔞 = αO has exactly 6 generators uα.
  - χ is trivial on units and multiplicative, so χ(uα) = χ(α). The norm is unit-invariant, so N(uα) = N(α).
  - The terms of Σ_{α≠0} χ(α) N(α)^(−s) are therefore constant on each set of 6 associates, and (1/6) Σ_{α≠0} = Σ_{𝔞≠0} η(𝔞) N𝔞^(−s) with η(αO) = χ(α).
  - The rearrangement is valid for Re s > 1 by absolute convergence.
  - I accept the identification.
  - The Dedekind factorization (trivial character = ζ(s)L(s, χ₋₃)) is not needed for this match. It was checked numerically only, and it remains a numerical check.
- **Edge case:** at s = 0 (outside the half-plane), the modulus-O character's value is a Γ(0) = 0 junk value. It does not affect the statement.

**Proposed line: MATCH.** This includes the identification, re-read and accepted.

## Reading 5: Lemma3.interpolation vs tex 252-267

Lean: lean-checks/comparator-copy/PaperLemma3/Lemma3.lean:817-825, with Pt at 41-43.

| check | Lean | paper | verdict |
|---|---|---|---|
| A | `(A : (Fin 4 → ℂ) →ₗ[ℂ] (Fin 3 → ℂ)) (hA : Function.Surjective A)` | "A : ℂ⁴ → ℂ³ a surjective linear map" | MATCH |
| kernel | `LinearMap.ker A = Submodule.span ℂ {c}` | ker A = ℂc | MATCH |
| ℚ-independence | `LinearIndependent ℚ c`, with c : Fin 4 → ℂ seen as a family of 4 complex numbers | "the four coordinates of c are linearly independent over ℚ" | MATCH |
| N, t | `(N : ℕ) (hN : 1 ≤ N) (t : Fin 3 → ℤ)`, `ht : ∀ j, 3 * ((N : ℤ) - 1) ≤ t j` | N ≥ 1; integers t_j ≥ 3(N − 1) | MATCH |
| budget (3.1) | `(4 * (N : ℤ) - 3) ^ 4 < ∏ j, (t j - 3 * ((N : ℤ) - 1) + 1)` | ∏ (t_j − 3(N − 1) + 1) > (4N − 3)⁴ | MATCH (exact, strict) |
| P_t | `{B | ∀ j, (B.degreeOf j : ℤ) ≤ t j}` in `MvPolynomial (Fin 3) ℂ` | deg_{z_j} B ≤ t_j (separate degrees) | MATCH |
| domain | `n : Fin 4 → Fin N` | E_N = {0,…,N−1}⁴ | MATCH |
| conclusion | `Function.Surjective (fun B : Pt t => fun n => eval (A (fun i => ((n i : ℕ) : ℂ))) B)` | B ↦ (B(An))_{n∈E_N} from P_t onto ℂ^{E_N} is surjective | MATCH |

**Proposed line: MATCH.**

## Reading 6: Lemma3.rectangle vs tex 410-420

Lean: lean-checks/comparator-copy/PaperLemma3/Bridge.lean:96-109, read from the source file.

| check | Lean | paper | verdict |
|---|---|---|---|
| hypotheses on A | the same four as Lemma 3 (hA, hker, hc) | "Let A satisfy the hypotheses of Lemma 3" | MATCH |
| H, N | `(H N : ℕ) (hH : 1 ≤ H) (hHN : H ≤ N)` | integers 1 ≤ H ≤ N | MATCH |
| bound α₀ | `(α 0 : ℝ) ≤ 32 * (H : ℝ) ^ (2 / 3 : ℝ) * (N : ℝ) ^ (4 / 3 : ℝ)` | α₁ ≤ T₁ = 32 H^{2/3} U, U = N^{4/3} | MATCH. The exponents are real (`(2 / 3 : ℝ)` is real division, not ℕ division), with real powers of positive bases. |
| bounds α₁, α₂ | `32 * (H : ℝ) ^ (-(1 / 3 : ℝ)) * (N : ℝ) ^ (4 / 3 : ℝ)` | T₂ = T₃ = 32 H^{−1/3} U | MATCH |
| α | `α : Fin 3 → ℕ`, compared as reals | α ∈ ℕ³, α_j ≤ T_j | MATCH |
| rows | `fun n => A(n) 0 ^ α 0 * A(n) 1 ^ α 1 * A(n) 2 ^ α 2` | ((An)₁^{α₁}(An)₂^{α₂}(An)₃^{α₃})_{n∈E_N} | MATCH (Lean indexes from 0, the paper from 1) |
| conclusion | `Submodule.span ℂ (rows) = ⊤` in (Fin 4 → Fin N) → ℂ | the rows span ℂ^{E_N} | MATCH |
| "the constant 32 is independent of A and H" | the literal 32 | a remark, not a hypothesis | consistent |

**Proposed line: MATCH.**

## Reading 7: Bastounis–Circelli–Hansen, arXiv:2610.08144

- **Fetch:** read-only, from arxiv.org, 2026-10-27. Abstract page and PDF v1 (PDF sha256 3282e2c4103b955d635173749e7bf887fef7af7dd39e1abdb750b951030c538b). Neither is committed.
- **Title (abstract page):** "Navier-Stokes lost in translation: Why Lean verification of AI autoformalisation does not guarantee correct natural language proofs". A. Bastounis, F. Circelli, A. C. Hansen; v1, 6 Oct 2026; math.AP.
- **What it says:**
  - Abstract: they argue that a Lean check of an AI autoformalisation "may offer no confidence in the original NL argument". They prove that resolving NL ambiguity for faithful translation has SCI = ∞, and they give "several examples of AI mistranslations".
  - The abstract ends: "we show that the formalised Lean proof does not correspond to the NL proof of blow-up of solutions to the Navier-Stokes equations".
  - §1: in the Navier-Stokes case, "the NL proof provides stronger statements than what the formal proof actually establishes". Their example 3.1 is an estimate (Lemma 8.6, (8.19)) that the paper states with C^{m+4} while the cited Lean declaration needs C^{m+5}.
  - Disclaimer (§1): "We do not make claims about the correctness of OpenAI's NL proof, we only make statements about mistranslations into Lean."
- **The proposed framing** was "they show that, for one AI-generated result, the Lean proof does not correspond to the natural-language proof". It is accurate for the Navier-Stokes example, but incomplete in two ways:
  - it is one of several examples, alongside a general impossibility result;
  - the mismatch they show is that intermediate statements in the paper are stronger than what Lean proves, not that the Lean theorem is wrong.
- **Suggested sentence:** "Bastounis, Circelli and Hansen [arXiv:2610.08144] argue that a Lean check of an AI autoformalisation need not certify the natural-language proof, and show for OpenAI's Navier–Stokes formalisation that the Lean proof does not correspond to the natural-language proof."
- **Recommendation:** cite with that sentence. Keep the one-result framing only if it names the result (Navier–Stokes blow-up).
- Their example concerns a different openai/math paper (Navier–Stokes), not family 003. Our Section 4 finding, that OAI's Corollary 4 goes through a multiplicity estimate rather than the paper's Lemma 3, is the same kind of correspondence question asked of family 003.

## Optional: the Fischler numbering

Not checked: there is no local copy of Compos. Math. 141 (2005). Use the fallback: "cited by the paper as [Fischler, Theorem 1.1 and Lemma 1.3]". Do not characterize the results.

## Paper version labels (COMPUTED; ledger v6:L143, v6:L144)

results/2026-10-27-paper-hashes/paper-hashes.txt (`python3 -I results/2026-10-27-paper-hashes/paper_hashes.py ...`, WSL, read-only `git show`):

**Siegel paper**
- Location: preprints/Uniform-exclusion-of-Landau-Siegel-zeros-October-1-2026/.
- paper.pdf sha256 fab9f6e8…214ef (404,812 bytes).
- build/paper.tex sha256 b011ba9c…8ded4.
- README.md: identical at adc7f12 and fd4aeeb.
- \title{Uniform exclusion of Landau--Siegel zeros}, \author{OpenAI}, \date{October 1, 2026} (lines 34-36). There is no version label.
- refs/siegel-paper.tex and refs/siegel-paper.pdf equal the fd4aeeb files.

**7/8 paper**
- Location: preprints/The-Quasi-Riemann-Hypothesis-September-30-2026/.
- paper.pdf sha256 8fe93046…99e7 (1,588,969 bytes).
- build/paper.tex sha256 42a5ee0f…ac6a3.
- README.md: identical at both commits.
- \title{The Quasi-Riemann Hypothesis\\ A Zero-Free Half-Plane Re s > 7/8}, \author{OpenAI}, \date{30 September 2026} (lines 29-32). There is no version label.
