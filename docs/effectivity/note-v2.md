# An explicit constant for [OpenAI, Uniform exclusion of Landau–Siegel zeros] with H free: c ≥ 4.467 × 10⁻³ (with Lu–Zaman–Zhao)

Joseph M. Reilly. Draft v2 of 2026-10-20, not reviewed by a specialist. Version 1 (`note.md`, `note.tex`, `note.pdf`) is kept unchanged.

- Computation: `src/effectivity.py`; output: `results/2026-10-20-effectivity/effectivity-output-v2.txt`.
- Comparison with Banks: `src/banks_compare.py`; output: `results/2026-10-20-paper-prep-2/banks-compare-output.txt`; term-by-term table: `docs/effectivity/banks-comparison-v2.md`.
- Derivation: `docs/effectivity/derivation.md`. Sources: [S1]–[S10], listed at the end; [S1]–[S8] are as in `docs/effectivity/sources.md`, where the quotations are; [S10] is described in `refs/banks-2610.15483.md`.

**Author's note.** The derivation and the Arb code were produced with Claude (Anthropic) via Claude Code. [JOE: what you checked and how]

## 1. Background: Banks's explicit constant

[S1] proves that some absolute c > 0 exists. Its proof argues by contradiction along a sequence with q → ∞ and δ := (1 − β) log q → 0, and it leaves every analytic constant implicit.

W. D. Banks [S10] (arXiv:2610.15483, dated October 11, 2026) rearranges the argument as a direct proof with explicit constants:
- δ₀ = 81/(5888 e^{3/2}) = 3.0696·10⁻³ for q ≥ 10¹⁰ (his Theorem 1.1 and Remark 7.1);
- with Lu–Zaman–Zhao's computation, (1 − β) log q ≥ 3.0696·10⁻³ for every q ≥ 3. He states this rounded, as 3.0·10⁻³.

Kerr (arXiv:2610.21099) and Green (hexagon:2610.00311v2, 2026-10-17) give no explicit constant.

This note uses the same master inequality as Banks's §7, with H left free and a few other changes (§4).

## 2. Statement

**Assuming the proof in [S1] is correct** (see §8), every real zero β ∈ (0,1) of every primitive nonprincipal real Dirichlet L-function of conductor q ≥ 3 satisfies

  **(1 − β) log q > 4.467 × 10⁻³**, using Lu–Zaman–Zhao's computation for q ≤ 10¹⁰ (the LZZ range), and

  **(1 − β) log q > 3.399 × 10⁻³**, using only Platt's computation for q ≤ 4·10⁵ (the Platt range).

The argument of [S1] alone, without any computation for small q, gives (1 − β) log q > 5.04 × 10⁻⁴ for every q ≥ 3 except q = 8.

These bounds are certified in Arb ball arithmetic from exact rational parameters.

## 3. Explicit inputs

**Definitions.** Here M = N⁴ and U = N^(4/3), with L = log U. Banks writes N⁴ for our M and uses M for our U = N^(4/3). The real variable of the L-function is σ throughout. derivation.md writes s for it; s is kept for the shift in docs/effectivity/derivation-banks-device.md.

| Input | Statement used | Source and range |
|---|---|---|
| Hadamard identity (2.3) | Re(−L′/L)(σ,χ) = ½ log(q/π) + ½ψ((σ+ε)/2) − Σ_ρ Re 1/(σ−ρ), terms ≥ 0, real σ > 1 | as stated in [S1] §2, checked against Davenport, 2nd ed., Ch. 12 (17)–(18), p. 83 |
| ζ log-derivative | −ζ′/ζ(σ) < 1/(σ−1), σ > 1 | [S6] Lemma 12; its final elementary inequality proved here for all σ > 1 (§5) |
| Digamma | ψ((σ+ε)/2) ≤ ψ(3/2) = 2 − γ − 2 log 2 for 1 < σ ≤ 2 | ψ increasing |
| Mertens | log x + E − 1/(2 log x) < Σ_{p≤x} log p/p (x > 1); Σ_{p≤x} log p/p < log x + E + 1/(2 log x) (x ≥ 319) | Rosser–Schoenfeld Thm 6, (3.21)–(3.22), p. 70, read in the original |
| Chebyshev | θ(x) < (1 + 7.5·10⁻⁷)x, x > 0 | [S5] Platt–Trudgian Cor. 2 |
| Primes dividing q | Σ_{p\|q} log p/p ≤ min(½, (log 2)/(2 log q) + ⅓)·log q | elementary |
| Lemma 6 | S₂ ≤ 192 M H^(−1/3) U, S₁ ≥ M H^(2/3) U/(4·97²), given N ≥ H and H^(2/3)N^(4/3) ≥ 2·97² | [S1] lines 517–550 (= Banks Lemma 4.2) |
| Small q | no real zero with σ > 0 for q ≤ 4·10⁵ ([S9]); δ > 1/5 for q ≤ 10¹⁰ | [S9] Thms 10.1–10.2, read in the original; [S2] Theorem 1.1 |

## 4. The master inequality, the parameters, and the comparison with Banks

Combining the explicit Lemma 2, (5.1), (5.6) with the θ bound, and Lemma 6 (derivation.md §§1–5): if a real zero with δ = (1−β) log q exists and N ≥ H, then

  1 ≤ ¾(1 + ρ_H) + (C_ℓ + ½(1+ρ_H))/λ + (e/2) δ λ + (C_H + (1+ρ_H) log 8)/L + (1 + 7.5·10⁻⁷)·4·97²/(H^(2/3) L) + 6·97²/(H^(2/3) U),

where:
- ρ_H = 7,226,112/H, C_ℓ = e/4 + c_q, and C_H = log H + 1/(2 log H) + 1/(2L) + (e/2)κ;
- κ = ½ψ(3/2) − ½ log π = −0.55412… < 0;
- L = log U = (4/3) log N and λ = L/log q.

This is Banks's Step 3 inequality (§7), term for term, in a different accounting (`docs/effectivity/banks-comparison-v2.md`, rows 1–21).

Take N = ⌈q^γ⌉. For all q ≥ q₀:
- λ lies in [4γ/3, 4γ/3 + (4/3) log(1 + q₀^(−γ))/log q₀];
- every term except the δ term is largest at q = q₀;
- so every real zero with q ≥ q₀ has δ > δ₀(q₀, γ, H), with δ₀ given in closed form (src/effectivity.py, `delta0`).

For fixed (γ, H), δ₀ is determined exactly; no fixed split of the margin is used. The parameters were found by a floating-point search and then certified in Arb at the exact values below. Every printed bound is the Arb lower endpoint rounded down.

| Range | q₀ | γ | H | c_q | certified δ₀ > |
|---|---|---|---|---|---|
| Platt | 400,001 | 201/10 | 1,995,262,314 | (log 2)/(2ℓ) + ⅓ | **3.3992904026 × 10⁻³** |
| Lu–Zaman–Zhao | 10¹⁰ + 1 | 153/10 | 2,818,382,931 | (log 2)/(2ℓ) + ⅓ | **4.4673780338 × 10⁻³** |
| argument alone | 3 | 671/5 | 1,122,018,454 | ½ | **5.0425352961 × 10⁻⁴** |

Unlike Banks's §7, our rows do not need H ≤ q: the Platt row has H > q₀. Banks uses H ≤ q only to get N ≥ H, and here γ secures that (side condition N ≥ H below; banks-comparison-v2.md, row 21).

**From Banks's 3.0696·10⁻³ to 4.467·10⁻³** (COMPUTED; banks-comparison-v2.md (c); `results/2026-10-20-paper-prep-2/banks-compare-output.txt`). The waterfall below starts from Banks's published value at q₀ = 10¹⁰ and switches his choices to ours one at a time. γ is re-optimized at each step; H is the paper's until the last step. The factors depend on the order.

| Change from Banks's choice to ours | Factor |
|---|---|
| exact solve instead of the 3/32 split and the log q > 23 absorption | ×1.024 |
| tight upper end of λ (N ≤ q^γ + 1, not q^{ω+1}) | ×1.046 |
| our S₁, S₂ bounds (S₁ ≥ N⁴H^{2/3}U/(4·97²), not N⁴U) | ×1.044 |
| Platt–Trudgian θ bound instead of θ(M) ≤ 2M | ×1.003 |
| κ < 0 kept (with the Mertens terms) | ×1.02 |
| shift 1 in σ = 1 + s/log X, instead of Banks's 3/2 (a cost) | ×0.88 |
| our primes-dividing-q bound, instead of Banks's ½S₀ device (a cost) | ×0.86 |
| H free (γ = 153/10, H = 2,818,382,931), instead of H = 86,713,344 | ×1.68 |

Check (COMPUTED, `results/2026-10-20-paper-prep-3/note-v2-factor-check.txt`):
- The exact factors multiply to the ratio 4.4673780338/3.0695555319 = 1.45538.
- The seven rounded factors other than θ multiply to 1.45018 (−0.36%). With θ they multiply to 1.45453 (−0.06%).
- Both products lie within the rounding of the stated factors.

At the paper's own H = 86,713,344, the same three ranges give 2.064, 2.652 and 0.3245 (×10⁻³).

A further refinement of the accounting is under review and is not used here.

**Side conditions** (derivation.md §7), certified at q₀ and implied for all q ≥ q₀:
- H ≥ 319;
- N ≥ H (γ log q₀ > log H);
- H^(2/3)N^(4/3) ≥ 2·97² (from N ≥ H ≥ 319);
- U ≥ 3, and σ = 1 + 1/L ∈ (1, 2];
- κ < 0.

**Lemma 12's last step:** φ(σ) = 1/(2σ−1) − [1/(σ−1) − (1−2^(−σ))/σ − 3^(1−σ)/(σ−1)] > 0 for all σ > 1. Proved in three pieces:
- on (1, 1.01], by the exact chain (1 − 3^(−t))/t ≤ log 3 and (1 − 2^(−σ))/σ ≥ 1/(2σ), which reduces it to log 3 − 1/2.02 < 1/1.02;
- on [1.01, 5], by Arb on 4,000 intervals (minimum certified lower bound of φ: 0.03878);
- for σ ≥ 5, by φ > 0 ⇐ σ² − 5σ + 2 > 0.

## 5. Remarks

- **Banks's numbers recomputed.** Each of the 12 numeric claims in Banks's Lemma 2.1 and §7 was recomputed independently in Arb, and all 12 hold. His δ₀ = 81/(5888 e^{3/2}) recomputes as [0.00306955553193322 ± 2.9·10⁻¹⁸] (`src/banks_compare.py`, Part A; output as above).
- **Lemma 3.** Our Lean proof of [S1]'s Lemma 3 (lean-checks/Lemma3.lean, theorem `Lemma3.interpolation`) has hypotheses identical to Banks's condition (3.1), the hypothesis of his Proposition 3.4. The clause-by-clause comparison is in docs/packet-related-work-draft-v2.md, which points to the table in docs/packet-related-work-draft.md.

## 6. Small conductors

- **Platt range:**
  - for q ≤ 4·10⁵ there is no real zero with σ > 0 at all, so the bound holds vacuously;
  - this range includes q = 8, the conductor the paper's field construction excludes (d = 2);
  - q > 4·10⁵ is covered by the first row.
- **Lu–Zaman–Zhao range:**
  - for q ≤ 10¹⁰, δ > 1/5, which also covers q = 8;
  - q > 10¹⁰ is covered by the second row;
  - so c = min(4.467·10⁻³, 1/5) = 4.467·10⁻³.
- **Argument alone:** covers q ≥ 3 with q ≠ 8 by taking γ large (λ ≈ 179), i.e. N ≈ q^134. q = 8 needs a separate input.

## 7. The final constant

  **c = 4.467 × 10⁻³** (with Lu–Zaman–Zhao), or **c = 3.399 × 10⁻³** (with Platt only), both rounded down from the certified values.

**Context:**
- The companion paper on the zero-free half-plane Re s > 7/8 would, if correct, give 1 − β ≥ 1/8 for every such β, a far stronger statement.
- A real zero with δ ≈ 0.003 is far outside anything ever observed. These numbers are for checking the argument, not a claim about zeros.

**Comparison with an earlier version** (docs/explicit-constant.md, written 2026-10-08, public in reviewer packet v1 on 2026-10-09: tag reviewer-packet-v1, commit 3a36016, Zenodo 10.5281/zenodo.23269528). Its figures were 3.0379·10⁻⁴ (row "all q ≥ 3"), 1.99806·10⁻³ (q > 4·10⁵) and 2.58930·10⁻³ (q > 10¹⁰):
- **Same inputs reproduce it.** With its inputs switched back on, this code gives slightly larger maxima (3.040·10⁻⁴, 2.0000·10⁻³, 2.5918·10⁻³, rounded down). The earlier note reported a δ with a positive safety margin (F ≈ 9.4·10⁻⁵) rather than the maximum.
- **"All q ≥ 3" is used there twice:**
  - its table row "all q ≥ 3" (3.0379·10⁻⁴) covers small q the same way as row 3 here: by taking λ large, not by any computation (q = 8 again excepted);
  - its bold conditional statement "(1 − β) log q ≥ 0.00258 … with q ≥ 3" combines the q > 10¹⁰ row with the small-q computations of Lu–Zaman–Zhao (and Platt).

  Source: results/2026-10-20-paper-prep-4/task2-earlier-constant.txt.
- **It used three inputs replaced here:**
  - an unsourced "Σ_{p≤x} log p/p < log x" for the primes up to H, which costs |E| = 1.33 in C_H against the sourced Rosser–Schoenfeld upper bound;
  - Rosser–Schoenfeld Thm 9 for θ;
  - a fixed H.
- **The gain comes mainly from freeing H** (×1.6). Of the other changes, c_q = ½ is worse than its c_q at large q but better at q = 3, and the sourced Mertens bound and the θ bound are improvements.

## 8. Assumptions (everything the constant depends on)

1. **The paper's proof is correct:** in particular Lemma 3, Corollary 4, Lemma 6, Lemma 7 and the bounds (5.1) and (5.6).
   - This note does not re-verify them mathematically.
   - Independent evidence: the Lean formalization of Theorem 1 is accepted by the official comparator with two kernels (Lean and nanoda), including a version rerouted through the paper's own Lemma 3. See the replay packet (DOI 10.5281/zenodo.23269527) and the statement audit on grwtsk/openai-math #40.
   - The Lean proof has existential constants only and does not contain these numbers.
2. **The Hadamard identity (2.3).** Checked against Davenport, *Multiplicative Number Theory*, 2nd ed., Ch. 12, (17) and (18) on p. 83, with a = ε (p. 70). Taking real parts of (17) and using (18), Re B(χ) = −Σ Re 1/ρ, gives (2.3).
3. **Rosser–Schoenfeld Theorem 6,** read in the original: (3.21) for 1 < x and (3.22) for 319 ≤ x, p. 70. E ≈ −1.33258 22757 33221, (2.11). This agrees with the quotation in arXiv:1703.08032 and with the enclosure in src/effectivity.py.
4. **Platt (2016) [S9],** read in the original. Theorem 10.1 states GRH for primitive characters of modulus q ≤ 400 000, up to a positive height. Theorem 10.2 states L(1/2, χ) ≠ 0 for q ≤ 2 000 000. Together (our inference) they rule out a real zero in (0, 1) for q ≤ 4·10⁵, matching the Lu–Zaman–Zhao summary. Needed only for the 3.399·10⁻³ statement.
5. **Lu–Zaman–Zhao Theorem 1.1** (arXiv:2602.03626v1, a preprint), read in the original. Needed only for the 4.467·10⁻³ statement.
6. **Platt–Trudgian Corollary 2,** read in the original.
7. **Lemma 12 of arXiv:2511.13898** (a preprint), read in the original. Its reduction steps are taken from that proof; its final inequality is proved here.
8. **χ(p) = (d/p) for odd p ∤ q, and |d| ≤ q,** as stated in the paper.

Not used: any unproved hypothesis (GRH or similar), or any floating-point value in a claimed inequality.

## References

- [S1] OpenAI, *Uniform exclusion of Landau–Siegel zeros*, October 1, 2026, github.com/openai/math, commit adc7f12, family 003.
- [S2] R. F. Lu, A. Zaman, H. Zhao, *Numerical computations concerning Landau–Siegel zeros*, arXiv:2602.03626v1 (2026).
- [S3] J. B. Rosser, L. Schoenfeld, *Approximate formulas for some functions of prime numbers*, Illinois J. Math. 6 (1962), 64–94, doi:10.1215/ijm/1255631807.
- [S4] C. Axler, *New estimates for some functions defined over primes*, arXiv:1703.08032.
- [S5] Platt, Trudgian, *On the first sign change of θ(x) − x*, arXiv:1407.1914.
- [S6] T. Zhao, *Upper bounds on gaps between zeros of L-functions*, arXiv:2511.13898, Appendix, Lemma 12.
- [S7] H. Davenport, *Multiplicative Number Theory*, 2nd ed., rev. H. L. Montgomery, Springer GTM 74.
- [S8] Elementary facts (no citation): ψ increasing on (0, ∞), ψ(3/2) = 2 − γ − 2 log 2, and log p/p ≤ (log p)/2 for p ≥ 2 (docs/effectivity/sources.md §S8).
- [S9] D. J. Platt, *Numerical computations concerning the GRH*, Math. Comp. 85 (2016), 3009–3027, doi:10.1090/mcom/3077.
- [S10] W. D. Banks, *On the OpenAI proof that Landau–Siegel zeros do not exist*, arXiv:2610.15483v1 (2026).
