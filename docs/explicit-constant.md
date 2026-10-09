# An explicit constant c, conditional on the paper

Status: **inference, not a finding.** The derivation below assumes the paper's algebraic steps (Lemma 6, Lemma 7, (5.1), first line of (5.6)) and six classical explicit inputs. It replaces every O-constant in the paper's Lemma 2 and (5.7) by an explicit number. The final inequality is certified in Arb, but the bookkeeping needs an expert check. Computation: `python src/explicit_c.py` (output reproduced in §4). Spot checks of the classical inputs: `python src/check_classical_inputs.py 10000000` → `results/2026-10-08-classical-inputs-EXPLORATORY.txt`.

Notation as in the paper: ℓ = log q, δ = (1 − β)ℓ, U = N^{4/3}, M = N⁴, and L := log U.

## 1. Classical inputs

| | Statement | Source | Spot check |
|---|---|---|---|
| I1 | For primitive χ and real s > 1: Re(−L′/L(s, χ)) = ½ log(q/π) + ½ ψ((s+ε)/2) − Σ_ρ Re 1/(s−ρ), with every term Re 1/(s−ρ) ≥ 0 | Davenport, *Multiplicative Number Theory*, ch. 12 (Re B(χ) = −Σ Re 1/ρ); the paper's (2.3) | — |
| I2 | −ζ′/ζ(s) < 1/(s−1) for real s > 1 | classical; reference to be confirmed by an expert | max over s ∈ [1.001, 2] of (s−1)(−ζ′/ζ) = 0.99942 |
| I3 | ψ(x) ≤ ψ(3/2) = 2 − γ − 2 log 2 = 0.036490 on (1/2, 3/2] | ψ increasing | ✓ |
| I4 | Σ_{p≤x} log p/p > log x + E − 1/(2 log x) for x > 1, with E = −1.3325822757 | Rosser–Schoenfeld 1962 | x ≤ 10⁷ ✓ |
| I5 | Σ_{p≤x} log p/p < log x for x > 1 | Rosser–Schoenfeld 1962 | x ≤ 10⁷ ✓ (max excess −0.347) |
| I6 | θ(x) < 1.01624 x for x > 0 | Rosser–Schoenfeld 1962, Thm 9 | x ≤ 10⁷ ✓ |

The exact equation numbers in Rosser–Schoenfeld should be confirmed by whoever checks this. The spot checks only guard against mistyped constants; the cited theorems are what cover all x.

## 2. Explicit Lemma 2

Take s = 1 + 1/log X with X ≥ e, so 1 < s ≤ 2.
- Keep only the zero β in I1 and drop the other zeros (their terms are ≥ 0).
- Add I2 and I3. This gives

  −ζ′/ζ(s) − L′/L(s, χ) ≤ 1/(s−1) − 1/(s−β) + ½ℓ − ½ log π + ½ψ(3/2).
- As in the paper, 1/(s−1) − 1/(s−β) ≤ (1−β)(log X)² = δ(log X)²/ℓ.
- The left side is at least (2/e) S₊(X), where S₊(X) = Σ_{p ≤ X, χ(p) = 1} log p/p.

Therefore

  **S₊(X) ≤ (e/4) ℓ + (e/2) δ (log X)²/ℓ − (e/2)(½ log π − ½ψ(3/2)).**

Primes dividing 2q contribute Σ_{p | 2q} log p/p ≤ (log 2)/2 + ℓ/3, because log p/p ≤ (log p)/3 for odd p. Primes p ≤ H with χ(p) = −1 contribute at most log H by I5. Combining with I4 at X = U:

  Σ_{H < p ≤ U, p ∤ 2q, χ(p) = −1} log p/p ≥ L − a ℓ − (e/2) δ L²/ℓ − b − 1/(2L),

where a = e/4 + 1/3 and b = −E + (log 2)/2 + log H − (e/2)(½ log π − ½ψ(3/2)). With H = 86,713,344 this gives b = 19.2041.

## 3. Explicit contradiction

- **Lower bound.** Lemma 7 with (5.6) line 1 and I6 gives ¼ log|N(Δ)| ≥ S₁ · [the sum above] − 1.01624 · M U.
- **Upper bound.** (5.1) gives ¼ log|N(Δ)| ≤ (M/2)(3L) + (S₁ + S₂)(¾L + ½ℓ + log 8).
- **Lemma 6** with H = 86,713,344 and N ≥ max(H, 18818) gives r = S₂/S₁ ≤ 1/12 and M/S₁ ≤ 1/(D U), where D = c₀ H^{2/3} = 5.20540.

Divide by S₁L. A contradiction follows, so no zero with this δ exists, as soon as

  F := 3/16 − A/L − 1/(2L²) − (e/2) δ L/ℓ − 1.01624/(D L) − 3/(2 D U) > 0,

with A = (a + 13/24) ℓ + b + (13/12) log 8, where a + 13/24 = 1.55457.

N is free in the construction, subject to N ≥ H. So for each q we may take N = ⌈exp(3tℓ/4)⌉ for any t > 0 with tℓ ≥ (4/3) log H. At fixed t, F increases with ℓ. A single rigorous evaluation at ℓ₀, with L ∈ [tℓ₀, tℓ₀ + 10⁻⁶] to absorb the rounding of N, therefore covers all ℓ ≥ ℓ₀.

## 4. Result (Arb, 200-bit; `python src/explicit_c.py`)

| range | best t = L/ℓ | δ certified | F lower bound | N needed |
|---|---|---|---|---|
| all q ≥ 3 (ℓ₀ = log 3) | 226.9 | 3.0379 × 10⁻⁴ | 9.48 × 10⁻⁵ | ≈ 10⁸¹ |
| q > 4·10⁵ | 34.48 | 1.99806 × 10⁻³ | 9.38 × 10⁻⁵ | ≈ 10¹⁴⁵ |
| q > 10¹⁰ | 26.60 | 2.58930 × 10⁻³ | 9.37 × 10⁻⁵ | ≈ 10²⁰⁰ |

Combined with the numerical results for small q, this gives the conditional statement:

  **(1 − β) log q ≥ 0.00258 for every real zero β of every primitive real L-function with q ≥ 3.**

The small-q inputs are:
- Platt (2016): no real zeros at all for q ≤ 4·10⁵, which also covers q = 8, i.e. d = 2, the case the paper excludes.
- Lu–Zaman–Zhao (arXiv 2602.03626, Theorem 1.1; checked against `refs/lu-zaman-zhao-2602.03626.pdf`): for q ≤ 10¹⁰ and quadratic χ mod q, L(σ, χ) ≠ 0 for σ ≥ 1 − 1/(5 log q). So δ > 1/5 there.

Without those inputs, the argument alone gives 3.0 × 10⁻⁴ for all q ≥ 3 with q ≠ 8.

## 5. Caveats

1. Everything is conditional on the paper's Lemmas 6 and 7, (5.1) and (5.6). The Lean formalization proves those (see `docs/log.md`, step 3 mapping), but only with existential constants; it does not contain these numbers.
2. I2's reference needs confirming; the numerical check covers s ∈ [1.001, 2] on a grid only.
3. The value is not optimized. H = 86,713,344 comes from the paper's crude Lemma 6. The exploratory data suggest S₂/S₁ ≈ 2/H (writeup §3.4; data in §2.6), which would allow much smaller H and a larger c. Making that rigorous would need a better proof of Lemma 6.
4. A real zero with δ ≈ 0.0026 is far outside anything ever observed. The point is that, if the paper is right, its proof yields a concrete number, which experts can sanity-check against what is known.
