# The constant in [OpenAI, Uniform exclusion of Landau–Siegel zeros] is effective: c ≥ 3.39 × 10⁻³

Joseph M. Reilly. Draft of 2026-10-20, not reviewed by a specialist. Computation: `src/effectivity.py`; output: `results/2026-10-20-effectivity/effectivity-output-v2.txt`. Derivation: `docs/effectivity/derivation.md`. Sources and quotations: `docs/effectivity/sources.md` (S1–S8).

## 1. Statement

**Assuming the proof in [S1] is correct** (see §7), every real zero β ∈ (0,1) of every primitive nonprincipal real Dirichlet L-function of conductor q ≥ 3 satisfies

  **(1 − β) log q > 3.399 × 10⁻³**, using Platt's computation for q ≤ 4·10⁵, and

  **(1 − β) log q > 4.467 × 10⁻³**, using Lu–Zaman–Zhao's computation for q ≤ 10¹⁰ instead.

The argument of [S1] alone, without any computation for small q, gives (1 − β) log q > 5.04 × 10⁻⁴ for every q ≥ 3 except q = 8.

These bounds are certified in Arb ball arithmetic from exact rational parameters.

## 2. What the paper proves and what is added here

- **The paper (Theorem 1):** some absolute c > 0 exists. Its proof argues by contradiction along a sequence with q → ∞ and δ := (1 − β) log q → 0, and it leaves every analytic constant implicit (≪, C, C_H).
- **Added here:**
  - every implicit constant replaced by an explicit one, with a cited source and its range of validity;
  - the limiting argument replaced by a direct inequality valid for each q ≥ q₀;
  - the parameters (γ, H) chosen to maximize the resulting bound;
  - a verification of every side condition on which the paper's lemmas depend.

  No step of the paper's algebra (Lemmas 3, 6 and 7, Corollary 4) is changed.

## 3. Explicit inputs

| Input | Statement used | Source and range |
|---|---|---|
| Hadamard identity (2.3) | Re(−L′/L)(s,χ) = ½ log(q/π) + ½ψ((s+ε)/2) − Σ_ρ Re 1/(s−ρ), terms ≥ 0, real s > 1 | as stated in [S1] §2, checked against Davenport, 2nd ed., Ch. 12 (17)–(18), p. 83 |
| ζ log-derivative | −ζ′/ζ(σ) < 1/(σ−1), σ > 1 | [S6] Lemma 12; its final elementary inequality proved here for all σ > 1 (§4) |
| Digamma | ψ((s+ε)/2) ≤ ψ(3/2) = 2 − γ − 2 log 2 for 1 < s ≤ 2 | ψ increasing |
| Mertens | log x + E − 1/(2 log x) < Σ_{p≤x} log p/p (x > 1); Σ_{p≤x} log p/p < log x + E + 1/(2 log x) (x ≥ 319) | Rosser–Schoenfeld Thm 6, (3.21)–(3.22), p. 70, read in the original |
| Chebyshev | θ(x) < (1 + 7.5·10⁻⁷)x, x > 0 | [S5] Platt–Trudgian Cor. 2 |
| Primes dividing q | Σ_{p\|q} log p/p ≤ min(½, (log 2)/(2 log q) + ⅓)·log q | elementary |
| Lemma 6 | S₂ ≤ 192 M H^(−1/3) U, S₁ ≥ M H^(2/3) U/(4·97²), given N ≥ H and H^(2/3)N^(4/3) ≥ 2·97² | [S1] lines 517–550 |
| Small q | no real zero with σ > 0 for q ≤ 4·10⁵ (Platt 2016); δ > 1/5 for q ≤ 10¹⁰ | Platt 2016 Thms 10.1–10.2, read in the original; [S2] Theorem 1.1 |

## 4. The direct inequality and the parameter choice

Combining the explicit Lemma 2, (5.1), (5.6) with the θ bound, and Lemma 6 (derivation.md §§1–5): if a real zero with δ = (1−β) log q exists and N ≥ H, then

  1 ≤ ¾(1 + ρ_H) + (C_ℓ + ½(1+ρ_H))/λ + (e/2) δ λ + (C_H + (1+ρ_H) log 8)/L + (1 + 7.5·10⁻⁷)·4·97²/(H^(2/3) L) + 6·97²/(H^(2/3) U),

where:
- ρ_H = 7,226,112/H, C_ℓ = e/4 + c_q, C_H = log H + 1/(2 log H) + 1/(2L) + (e/2)κ;
- κ = ½ψ(3/2) − ½ log π = −0.55412… < 0;
- L = log U = (4/3) log N and λ = L/log q.

Take N = ⌈q^γ⌉. For all q ≥ q₀:
- λ lies in [4γ/3, 4γ/3 + (4/3) log(1 + q₀^(−γ))/log q₀];
- every term except the δ term is largest at q = q₀;
- so every real zero with q ≥ q₀ has δ > δ₀(q₀, γ, H), with δ₀ given in closed form (src/effectivity.py, `delta0`).

The paper's split of the margin (13/16 + 1/16) is not needed: for fixed (γ, H), δ₀ is determined exactly.

The parameters were found by a floating-point search and then certified in Arb at the exact values below (`effectivity-output-v2.txt`; every printed bound is the Arb lower endpoint rounded down):

| Regime | q₀ | γ | H | c_q | certified δ₀ > |
|---|---|---|---|---|---|
| Platt | 400,001 | 201/10 | 1,995,262,314 | (log 2)/(2ℓ) + ⅓ | **3.3992904026 × 10⁻³** |
| Lu–Zaman–Zhao | 10¹⁰ + 1 | 153/10 | 2,818,382,931 | (log 2)/(2ℓ) + ⅓ | **4.4673780338 × 10⁻³** |
| argument alone | 3 | 671/5 | 1,122,018,454 | ½ | **5.0425352961 × 10⁻⁴** |

At the paper's own H = 86,713,344, the same three regimes give 2.064, 2.652 and 0.3245 (×10⁻³). Optimizing over H is worth a factor of about 1.6.

**Side conditions** (derivation.md §7), certified at q₀ and implied for all q ≥ q₀:
- H ≥ 319;
- N ≥ H (γ log q₀ > log H);
- H^(2/3)N^(4/3) ≥ 2·97² (from N ≥ H ≥ 319);
- U ≥ 3, and s = 1 + 1/L ∈ (1, 2];
- κ < 0.

**Lemma 12's last step:** φ(σ) = 1/(2σ−1) − [1/(σ−1) − (1−2^(−σ))/σ − 3^(1−σ)/(σ−1)] > 0 for all σ > 1. Proved in three pieces:
- on (1, 1.01], by the exact chain (1 − 3^(−t))/t ≤ log 3 and (1 − 2^(−σ))/σ ≥ 1/(2σ), which reduces it to log 3 − 1/2.02 < 1/1.02;
- on [1.01, 5], by Arb on 4,000 intervals (minimum certified lower bound of φ: 0.03878);
- for σ ≥ 5, by φ > 0 ⇐ σ² − 5σ + 2 > 0.

## 5. Small conductors

- **Platt regime:**
  - for q ≤ 4·10⁵ there is no real zero with σ > 0 at all, so the bound holds vacuously;
  - this range includes q = 8, the conductor the paper's field construction excludes (d = 2);
  - q > 4·10⁵ is covered by the first row.
- **Lu–Zaman–Zhao regime:**
  - for q ≤ 10¹⁰, δ > 1/5, which also covers q = 8;
  - q > 10¹⁰ is covered by the second row;
  - so c = min(4.467·10⁻³, 1/5) = 4.467·10⁻³.
- **Argument alone:** covers q ≥ 3 with q ≠ 8 by taking γ large (λ ≈ 179), i.e. N ≈ q^134. q = 8 needs a separate input.

## 6. The final constant

  **c = 3.399 × 10⁻³** (with Platt), or **c = 4.467 × 10⁻³** (with Lu–Zaman–Zhao), both rounded down from the certified values.

**Context:**
- The companion paper on the zero-free half-plane Re s > 7/8 would, if correct, give 1 − β ≥ 1/8 for every such β, a far stronger statement.
- The point here is narrower: the nine-page Landau–Siegel argument, on its own, yields an explicit constant.
- A real zero with δ ≈ 0.003 is far outside anything ever observed. These numbers are for checking the argument, not a claim about zeros.

**Comparison with an earlier version** (docs/explicit-constant.md, 2026-10-08), whose figures were 3.0379·10⁻⁴, 1.99806·10⁻³ and 2.58930·10⁻³:
- **Same inputs reproduce it.** With its inputs switched back on, this code gives slightly larger maxima (3.040·10⁻⁴, 2.0000·10⁻³, 2.5918·10⁻³, rounded down). The earlier note reported a δ with a positive safety margin (F ≈ 9.4·10⁻⁵) rather than the maximum.
- **Its "all q ≥ 3" figure** covered small q the same way as row 3 here: by taking λ large, not by any computation (q = 8 again excepted).
- **It used three inputs replaced here:**
  - an unsourced "Σ_{p≤x} log p/p < log x" for the primes up to H, which costs |E| = 1.33 in C_H against the sourced Rosser–Schoenfeld upper bound;
  - Rosser–Schoenfeld Thm 9 for θ;
  - a fixed H.
- **The gain comes mainly from freeing H** (×1.6). Of the other changes, c_q = ½ is worse than its c_q at large q but better at q = 3, and the sourced Mertens bound and the θ bound are improvements.

## 7. Assumptions (everything the constant depends on)

1. **The paper's proof is correct:** in particular Lemma 3, Corollary 4, Lemma 6, Lemma 7 and the bounds (5.1) and (5.6).
   - This note does not re-verify them mathematically.
   - Independent evidence: the Lean formalization of Theorem 1 is accepted by the official comparator with two kernels (Lean and nanoda), including a version rerouted through the paper's own Lemma 3. See the replay packet (DOI 10.5281/zenodo.23269527) and the statement audit on grwtsk/openai-math #40.
   - The Lean proof has existential constants only and does not contain these numbers.
2. **The Hadamard identity (2.3).** Checked against Davenport, *Multiplicative Number Theory*, 2nd ed., Ch. 12, (17) and (18) on p. 83, with a = ε (p. 70). Taking real parts of (17) and using (18), Re B(χ) = −Σ Re 1/ρ, gives (2.3).
3. **Rosser–Schoenfeld Theorem 6,** read in the original: (3.21) for 1 < x and (3.22) for 319 ≤ x, p. 70. E ≈ −1.33258 22757 33221, (2.11). This agrees with the quotation in arXiv:1703.08032 and with the enclosure in src/effectivity.py.
4. **Platt (2016),** read in the original. Theorem 10.1 states GRH for primitive characters of modulus q ≤ 400 000, up to a positive height. Theorem 10.2 states L(1/2, χ) ≠ 0 for q ≤ 2 000 000. Together (our inference) they rule out a real zero in (0, 1) for q ≤ 4·10⁵, matching the Lu–Zaman–Zhao summary. Needed only for the 3.399·10⁻³ statement.
5. **Lu–Zaman–Zhao Theorem 1.1** (arXiv:2602.03626v1, a preprint), read in the original. Needed only for the 4.467·10⁻³ statement.
6. **Platt–Trudgian Corollary 2,** read in the original.
7. **Lemma 12 of arXiv:2511.13898** (a preprint), read in the original. Its reduction steps are taken from that proof; its final inequality is proved here.
8. **χ(p) = (d/p) for odd p ∤ q, and |d| ≤ q,** as stated in the paper.

Not used: any unproved hypothesis (GRH or similar), or any floating-point value in a claimed inequality.
