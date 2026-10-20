# Explicit-constant derivation for "Uniform exclusion of Landau–Siegel zeros" (step 1, for approval)

Status: a line-by-line reconstruction of the paper's §2, §5 and §6 with every implicit constant named. Everything is INFERRED (my reasoning) unless marked STATED (quoted from a source in docs/effectivity/sources.md, labels S1–S8) or COMPUTED (none yet; step 3). No code has been run except one EXPLORATORY float check, marked as such.

Notation (paper): χ primitive, nonprincipal, real, conductor q ≥ 3; β ∈ (0,1) a real zero; ℓ = log q; δ = (1−β)ℓ. N ≥ 1 integer, U = N^{4/3}, M = N⁴ = U³, L = log U, λ = L/ℓ. S₁, S₂ and r = S₂/S₁ as in (4.3).

The proof is assumed correct throughout (see §6). The output is an explicit inequality for which, if it fails, no real zero with that δ exists.

---

## 1. Lemma 2 made explicit: (2.1) and (2.2) (paper lines 181–244)

### 1.1 Inputs

- **(I1) Hadamard identity**, STATED by the paper ((2.3), lines 204–210; checked against S7 (Davenport Ch. 12 (17)–(18)) after step 4). For real s > 1:
  −L′/L(s,χ) = ½ log(q/π) + ½ ψ((s+ε)/2) − Σ_ρ Re 1/(s−ρ), where ε = (1−χ(−1))/2 ∈ {0,1}, ψ = Γ′/Γ, and every Re 1/(s−ρ) ≥ 0.
  - Each term is nonnegative because Re ρ ≤ 1 < s, so Re(s−ρ) > 0.
- **(I2)** −ζ′/ζ(σ) < 1/(σ−1) for σ > 1. STATED, S6, Lemma 12 (the last elementary step is left to the reader there; step 3 checks it).
- **(I3)** For 1 < s ≤ 2, (s+ε)/2 ∈ (½, 3/2], and ψ is increasing, so ψ((s+ε)/2) ≤ ψ(3/2) = 2 − γ − 2 log 2 (S8).

Take X ≥ 3 and s = 1 + 1/log X, so 1 < s < 2 (paper line 223; X > e suffices).

### 1.2 Upper bound

By (I1), dropping every zero except β (each dropped term is ≥ 0; this includes the zero 1−β of a real χ), then adding (I2) and (I3):

  −ζ′/ζ(s) − L′/L(s,χ) < 1/(s−1) − 1/(s−β) + ℓ/2 + κ,  with κ := ½ ψ(3/2) − ½ log π = 1 − γ/2 − log 2 − ½ log π.

EXPLORATORY: κ ≈ −0.5538 < 0.

Also 1/(s−1) − 1/(s−β) = (1−β)/((s−1)(s−β)) ≤ (1−β)/(s−1)² = (1−β)(log X)² = δ(log X)²/ℓ, using s − β ≥ s − 1 > 0 (paper lines 232–236).

### 1.3 Lower bound

Paper lines 224–230:

  −ζ′/ζ(s) − L′/L(s,χ) = Σ_n Λ(n)(1+χ(n))/n^s ≥ Σ_{p≤X, χ(p)=1} 2 log p · p^{−s} ≥ (2/e) S₊(X),

where S₊(X) := Σ_{p≤X, χ(p)=1} log p/p. This uses 1+χ(n) ≥ 0 and, for p ≤ X, p^{−s} = p^{−1}·p^{−1/log X} ≥ p^{−1}e^{−1}.

### 1.4 Explicit (2.1)

  **S₊(X) ≤ (e/2)·(ℓ/2 + κ + δ(log X)²/ℓ)**  (X ≥ 3).

Check of your derivation:
- Your formula S₊ ≤ (e/2)(ℓ/2 + (1−β)(log X)²) is TRUE, since κ < 0.
- The stated justification is incomplete. Bounding ½ log(q/π) ≤ ℓ/2 alone discards −½ log π but leaves +½ψ(3/2) ≈ +0.0182, which your formula omits.
- The two constants must be combined into κ < 0. Keeping κ improves C_H by (e/2)|κ| ≈ 0.753 (EXPLORATORY value).

### 1.5 Explicit (2.2)

Let A(X) := Σ_{H<p≤X, p∤2q, χ(p)=−1} log p/p, the admissible primes up to X. Every prime p ≤ X has χ(p) ∈ {1, 0, −1}, and χ(p) = 0 exactly when p | q. A prime with χ(p) = −1 and p > H is automatically odd (H ≥ 2) and prime to q. Hence, exactly:

  Σ_{p≤X} log p/p = S₊(X) + Σ_{p≤X, p|q} log p/p + Σ_{p≤min(H,X), χ(p)=−1} log p/p + A(X).

Bound the pieces:
- **(I4)** Σ_{p≤X} log p/p > log X + E − 1/(2 log X) for X > 1. STATED, S4 quoting Rosser–Schoenfeld Thm 6, left inequality.
- **(I5)** Σ_{p≤min(H,X), χ(p)=−1} log p/p ≤ Σ_{p≤H} log p/p < log H + E + 1/(2 log H) for H ≥ 319. STATED, S4, right inequality.
- **(I6)** Σ_{p|q} log p/p ≤ c_q ℓ, with three valid choices:
  - the paper's c_q = 1, which is the 1 in your C_ℓ;
  - c_q = ½, since log p/p ≤ (log p)/2 and Σ_{p|q} log p = log(rad q) ≤ ℓ;
  - (log 2)/(2ℓ) + 1/3, since log p/p ≤ (log p)/3 for odd p (S8).

E cancels between (I4) and (I5), as you say. Then:

  **A(X) > log X − C_ℓ ℓ − C_δ δ(log X)²/ℓ − C_H(X)**,  for X ≥ 3 and H ≥ 319,

  C_ℓ = e/4 + c_q,  C_δ = e/2,  C_H(X) = log H + 1/(2 log H) + 1/(2 log X) + (e/2)κ.

Check of your constants:
- **C_ℓ = 1 + e/4:** valid (c_q = 1), but not the best available. c_q = ½ gives C_ℓ = ½ + e/4.
- **C_δ = e/2:** correct.
- **C_H = log H + 1/(2 log H) + 1/(2 log X):** valid. It is the version without the (e/2)κ term, which is negative.
- **"Needs H ≥ 319":** correct, from the range of (I5).

## 2. The Archimedean bound (5.1) (paper lines 562–577)

STATED by the paper; the steps check out:
- Every embedding ν and n ∈ E_N give |ν(θ_n)| ≤ (N−1)(1+√|d|)(1+√2) ≤ 8N√q, using |d| ≤ q (line 454).
  - The second step uses (1+√q)(1+√2) ≤ 2√q·2.415 < 8√q for q ≥ 1.
  - It could be sharpened (for q ≥ 3, (1+1/√3)(1+√2) < 3.82), but the paper's 8 is kept.
- Each row's Euclidean norm is ≤ √M·(8N√q)^{α₁+α₂+α₃}. Hadamard's inequality at each of the four embeddings gives

  **¼ log|Nm(Δ)| ≤ (M/2) log M + (S₁+S₂)(log N + ℓ/2 + log 8).**  No implicit constant.

## 3. The divisibility lower bound: (5.6) and (5.7) (paper lines 640–657)

(The task called this "(5.4)". In the paper (5.4) is the replacement identity, line 615; the lower bound is (5.6)/(5.7).)

- Lemma 7 (STATED): p^{E_p} | Δ for admissible p, so p^{4E_p} | Nm(Δ) ≠ 0.
- E_p = Σ_{α∈𝒫} ⌊α₁/p⌋ ≥ S₁/p − M, because ⌊x⌋ ≥ x − 1 and there are M rows.
- Summing over admissible p ≤ U:

  ¼ log|Nm(Δ)| ≥ Σ_{adm p≤U} E_p log p ≥ S₁ A(U) − M θ(U).

- **(I7)** θ(U) < C_θ U with C_θ = 1 + 7.5·10⁻⁷, for all U > 0. STATED, S5, Platt–Trudgian Cor. 2. This replaces the paper's "Chebyshev ≪ U" and Rosser–Schoenfeld Thm 9.
- With §1.5 at X = U (needs U ≥ 3):

  **¼ log|Nm(Δ)| ≥ S₁(L − C_ℓ ℓ − C_δ δ L²/ℓ − C_H(U)) − C_θ M U.**

## 4. Lemma 6 made explicit (paper lines 517–550)

STATED by the paper, with c₀ = (4·97²)⁻¹ and C₀ = 192. The proof needs exactly:
- (a) N ≥ H, used for Q₀ ≤ 97²H^{−2/3}U² and in Corollary 4 (whose proof needs 1 ≤ H ≤ N; lines 410–424);
- (b) M ≥ 2Q₀, which holds when H^{2/3}N^{4/3} ≥ 2·97² (lines 543–544).

Under (a) and (b):
- S₂ ≤ 192 M H^{−1/3} U and S₁ ≥ M H^{2/3} U/(4·97²);
- so **r ≤ ρ_H := C₀/(c₀H) = 768·97²/H = 7,226,112/H**, and **M/S₁ ≤ 4·97²/(H^{2/3}U)**.
- The paper's "sufficiently large N in terms of H" is exactly (a) and (b).

Your values:
- H = ⌈12·7,226,112⌉ = 86,713,344 is the arithmetic for r ≤ 1/12, correct; it is also the H in the Lean formalization.
- **Correction:** H is a free parameter, not fixed by the proof. Any integer H ≥ 319 works with r ≤ 7,226,112/H. A larger H lowers r and the fifth term but raises C_H by log H, so step 3 optimizes over H too. 86,713,344 is the paper's choice for r ≤ 1/12.

## 5. The master inequality (6.2), explicit (paper lines 678–689)

Combine §2 and §3, divide by S₁L > 0, use log N = ¾L and log M = 3L, and bound r ≤ ρ_H (the right side is increasing in r):

  1 ≤ ¾(1+ρ_H) + (C_ℓ + ½(1+ρ_H))/λ + C_δ δ λ + (C_H(U) + (1+ρ_H) log 8)/L + C_θ·4·97²/(H^{2/3}L) + 6·97²/(H^{2/3}U).

The last term is (3/2)·M/S₁, from (M/2) log M/(S₁L) = (3/2)M/S₁.

**Use (contrapositive):** fix q (q ≠ 8) and admissible N and H. If the right side is < 1 for a given δ, no real zero with that δ exists. The right side increases in δ, so this gives δ > δ₀(q, N, H) for every real zero.

Check of your (6.2):
- It matches term by term, with r in place of ρ_H.
- Your bound for the fifth term is right.
- The "negligible" term is exactly 6·97²/(H^{2/3}U); it is kept in the computation.

**EXPLORATORY float check of your figure:** λ = 35.5, q = 1.2·10⁴, ρ_H = 1/12, your constants.
- The terms other than δ sum to 0.1249 out of the margin 3/16.
- The remainder 0.0626 = (e/2)·35.5·δ gives δ ≈ 1.30·10⁻³.

This agrees with your 1.29·10⁻³; the rigorous values come in step 3.

## 6. Choice of N, uniformity in q, and small q

- **N = ⌈q^γ⌉.** Then λ = (4/3) log N/ℓ ∈ [4γ/3, 4γ/3 + (4/3) log(1+q^{−γ})/ℓ]. Step 3 bounds the right side of (6.2) over this whole interval and over all q ≥ q₀:
  - the terms 1/λ, 1/L and 1/U decrease in q (for fixed γ, L ≥ (4/3)γℓ);
  - the δλ term needs the upper end of λ.
- **Small conductors** (STATED, S2; Platt 2016 Thms 10.1–10.2 read after step 4):
  - q ≤ 4·10⁵: no real zero with σ > 0 (Platt, via S2). This covers q = 8, the excluded d = 2.
  - q ≤ 10¹⁰: δ > 1/5 (S2, Theorem 1.1).
- **Final constant:** c = min(δ₀(q₀), small-q constant), with:
  - q₀ ≤ 4·10⁵ (Platt regime): c = δ₀(q₀);
  - q₀ ≤ 10¹⁰ (LZZ regime): c = min(δ₀(q₀), 1/5).

## 7. Side conditions (every one; step 3 verifies each at q₀ and shows it persists for q ≥ q₀)

| # | Condition | Where needed |
|---|---|---|
| SC1 | χ primitive, nonprincipal, real, q ≥ 3; q ≠ 8 (d ≠ 2) for the field K | §4 of paper (lines 451–461) |
| SC2 | H integer ≥ 319 (Mertens upper bound at H); H ≥ 2 (admissible primes are odd) | (I5); line 652 |
| SC3 | N integer, N ≥ H | Corollary 4; Lemma 6 (Q₀ bound) |
| SC4 | H^{2/3}N^{4/3} ≥ 2·97² (M ≥ 2Q₀) | Lemma 6 |
| SC5 | U = N^{4/3} ≥ 3, so X = U ≥ 3 and s = 1 + 1/L ∈ (1,2) | Lemma 2 |
| SC6 | Mertens lower bound for X > 1; upper for H ≥ 319 | (I4), (I5) |
| SC7 | θ bound for U > 0 | (I7) |
| SC8 | −ζ′/ζ bound at σ = s > 1 | (I2) |
| SC9 | (s+ε)/2 ∈ (½, 3/2], i.e. s ≤ 2 | (I3) |
| SC10 | S₁ > 0 and L > 0 (division) | follows from SC3–SC5 |
| SC11 | admissible primes p > H, p ∤ 2q, χ(p) = −1 (Lemma 7's weight drop needs p > H) | paper lines 580–622 |
| SC12 | χ(p) = (d/p) for odd p ∤ q; \|d\| ≤ q | STATED, paper line 454, citing Davenport |
| SC13 | N = ⌈q^γ⌉ ⇒ λ range above | §6 |
| SC14 | Small-q ranges: q ≤ 4·10⁵ (Platt via S2), q ≤ 10¹⁰ (S2 Thm 1.1) | §6 |

## 8. Summary of corrections to your derivation

1. **(2.1) constant:** your formula is true, but the step "½ψ(3/2) term, then ½ log(q/π) ≤ ℓ/2" drops +½ψ(3/2). The two must be combined as κ = ½ψ(3/2) − ½ log π < 0. Keeping κ lowers C_H by about 0.75.
2. **C_ℓ = 1 + e/4:** valid but loose; ½ + e/4 is also valid (Σ_{p|q} log p/p ≤ ℓ/2).
3. **H:** 86,713,344 is the paper's choice for r ≤ 1/12, not forced. H is a free integer ≥ 319, with r ≤ 7,226,112/H.
4. **Labels:** "Lemma 4.1" is Lemma 6, and "(5.4)" should be (5.6)/(5.7).
5. **Fifth term:** the "negligible" piece is exactly 6·97²/(H^{2/3}U) and is kept.
6. **Sources:**
   - θ bound: Platt–Trudgian Cor. 2 (C_θ = 1 + 7.5·10⁻⁷, all x > 0) replaces Rosser–Schoenfeld Thm 9.
   - Rosser–Schoenfeld, Platt (2016) and Davenport were read in the original after step 4 (sources.md, final section). All three agree with the quotations used here.
7. **No sign or direction errors found** in your master inequality or in the λ/δ dependence.

## 9. Relation to docs/explicit-constant.md (2026-10-08)

That earlier note follows the same route and reports 3.0·10⁻⁴ (all q ≥ 3, q ≠ 8), 2.0·10⁻³ (q > 4·10⁵) and 2.6·10⁻³ (q > 10¹⁰). Where it differs from this derivation:
- it used c_q via (log 2)/(2ℓ) + 1/3;
- it used an unsourced "Σ_{p≤x} log p/p < log x" for primes ≤ H, where this uses (I5), the upper Mertens bound from S4;
- it used Rosser–Schoenfeld Thm 9 for θ;
- it fixed H = 86,713,344.

Step 3 recomputes from this derivation, does not reuse that code, and will say whether the numbers agree.
