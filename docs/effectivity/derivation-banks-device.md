# UNREVIEWED: derivation.md with Banks's primes-dividing-q device

**UNREVIEWED.** Nobody but its author has checked this. It is not part of `note.md` or `note-v2`. Draft, 2026-10-20.

- Computation: `src/effectivity_banks_device.py`. Output: `results/2026-10-20-effectivity-device/device-output.txt`. Command: `.venv/Scripts/python -I src/effectivity_banks_device.py`. Tests: `tests/test_effectivity_banks_device.py`.
- Source of the device: W. D. Banks, arXiv:2610.15483v1, Lemma 2.1 and its proof, eqs. (2.3)–(2.8) (refs/banks-2610.15483.md).

Everything in `derivation.md` stays as it is except §1.2–§1.5, which change in exactly two places, (D1) and (D2) below. §§2–7 are unchanged: the Archimedean bound, the divisibility bound, Lemma 6, the master inequality, the choice of N and the side conditions SC1–SC14. The master inequality keeps its form, with three constants replaced.

## (D2) The shift: σ = 1 + s/log X, with 0 < s ≤ 2

- **derivation.md §1.2–1.3:** s = 1, that is σ = 1 + 1/log X.
- **Change (Banks Lemma 2.1, (2.5)–(2.6)):** for p ≤ X, p^{−σ} ≥ e^{−s}/p. Bounding 1/(σ−1) − 1/(σ−β) ≤ δ(log X)²/(s²ℓ) gives
  - C_δ = e^s/(2s²) (Banks's C₁, (2.3));
  - the ℓ/2 term becomes (e^s/4)ℓ (Banks's C₂, (2.3));
  - κ enters as (e^s/2)κ, still with κ < 0.
- **Conditions:** σ ≤ 2, i.e. L ≥ s, so (σ+ε)/2 ≤ 3/2 and (I3) applies; and X = U ≥ 8, Banks's hypothesis. Both are checked for every q ≥ q₀ (`side_conditions`, "D2" rows).
  - INFERRED: for σ ∈ (1, 2], (I2) is the same Lemma 12 bound, already proved for all σ > 1 (`lemma12_check`, reused).
- With s = 1 these are derivation.md's constants; the test `test_shift_one_with_c_q_half_reproduces_effectivity` checks this.

## (D1) Primes dividing q

- **derivation.md §1.5, (I6):** Σ_{p|q} log p/p ≤ c_q ℓ, with c_q ∈ {1, ½, ln2/(2ℓ) + ⅓}. This enters C_ℓ = e/4 + c_q.
- **Change (Banks (2.5), (2.6), (2.8) and the bound after (2.8)):**
  - A prime p | q has 1 + χ(p) = 1, so it stays in Σ Λ(n)(1+χ(n))/n^σ with weight 1. The lower bound of §1.3 becomes e^{−s}(2S₊ + S₀), where S₀ = Σ_{p≤X, p|q} log p/p. So **S₊ + ½S₀ ≤ (e^s/2)(ℓ/2 + κ + δ(log X)²/(s²ℓ))** (Banks (2.6), in our sign convention for κ).
  - In the split of Σ_{p≤X} log p/p, the primes p | q with p ≤ H already sit inside the Σ_{p≤H} term bounded by (I5). Only p ∈ (H, X] with p | q must be removed, and Σ_{H<p≤X, p|q} log p/p ≤ ½S₀ + ½Σ_{p>H, p|q} log p/p (Banks (2.8)).
  - If k primes p > H divide q, then H^k < q, so k < ℓ/log H. Since (log t)/t decreases for t ≥ e, **½Σ_{p>H, p|q} log p/p ≤ ℓ/(2H)**.
- **Result:** in §1.5, C_ℓ = e/4 + c_q is replaced by **C_ℓ = e^s/4 + 1/(2H)**. C_δ is as in (D2). C_H = log H + 1/(2 log H) + 1/(2 log X) + (e^s/2)κ, the same form with e/2 replaced by e^s/2. The (log 2)/2 term of the c_q = ln2/(2ℓ) + ⅓ option disappears.
- **No condition H ≤ q is needed.** If H ≥ q, no prime p > H divides q, so the sum is 0 ≤ ℓ/(2H). Banks's §7 assumes 319 ≤ H ≤ q ≤ N, but he uses H ≤ q only to get N ≥ H (Corollary 3.5, Lemma 4.2). Here N ≥ H comes from γ log q₀ > log H (SC3), checked for every q ≥ q₀.

## Master inequality (derivation.md §5) with (D1) and (D2)

  1 ≤ ¾(1+ρ_H) + (e^s/4 + 1/(2H) + ½(1+ρ_H))/λ + (e^s/(2s²)) δ λ + (C_H(U) + (1+ρ_H) log 8)/L + C_θ·4·97²/(H^{2/3}L) + 6·97²/(H^{2/3}U),

with C_H(U) = log H + 1/(2 log H) + 1/(2L) + (e^s/2)κ. Uniformity in q ≥ q₀ is as in derivation.md §6: every term except the δ term decreases in L and λ, and the δ term uses the upper end of λ.

## Result (COMPUTED, UNREVIEWED)

| Regime | q₀ | s | γ | H | certified δ₀ > | note.md value | ratio |
|---|---|---|---|---|---|---|---|
| Platt | 400,001 | 31/20 | 103/5 | 1,995,262,314 | 4.5799298821·10⁻³ | 3.3992904026·10⁻³ | 1.3473 |
| LZZ | 10¹⁰ + 1 | 29/20 | 77/5 | 2,660,725,059 | 5.9439667682·10⁻³ | 4.4673780338·10⁻³ | 1.3305 |

- With (D1) alone (s = 1, note.md's γ and H), the values are 3.7682773365·10⁻³ and 5.0833123747·10⁻³.
- Every side condition holds at q₀ and for every q ≥ q₀ (output, "side conditions"). The parameters came from a floating-point search, and the values are certified in Arb at those exact rationals.
- Before any use, this needs a second reader to check (D1) against Banks (2.6)–(2.8). In particular, the claim that p | q with p ≤ H need no separate bound, because (I5) bounds all p ≤ H regardless of χ(p).
