# Paper map: what can be tested

Equation numbers refer to refs/siegel-paper.pdf. Notation: χ primitive real character of conductor q, ℓ = log q, δ = (1 − β)ℓ, K = Q(a, b) with a² = d, b² = 2, R = Z[a, b], θ_n = n1 + n2·a + n3·b + n4·ab for n in {0..N−1}^4, M = N^4, U = N^{4/3}.

## Proof structure in one paragraph

Assume a sequence of real zeros with δ → 0. Section 2 shows this forces almost all primes up to a large X to have χ(p) = −1 (eq. 2.2). Sections 4–5 build a nonzero determinant Δ in R from rows (θ_n^{α1} σ(θ_n)^{α2} στ(θ_n)^{α3}), chosen greedily by weight α1 + H(α2 + α3). For primes with χ(p) = −1, a Frobenius congruence (5.2) makes Δ divisible by p^{E_p} (Lemma 7), which gives a lower bound on log|N(Δ)| of about S1·log U (5.7). Hadamard's inequality gives an upper bound of about (S1 + S2)·(3/4)·log U (5.1). Since S2/S1 is small (Lemma 6), the two bounds contradict each other (6.2).

## Testable items

| Item | Paper location | Test | Status |
|---|---|---|---|
| Frobenius congruence | (5.2) | Random θ in R, check θ^p ≡ g_p(θ) mod pR | Done: tests/test_ring.py |
| Divisibility | Lemma 7, (5.3) | Build Δ exactly for small N, check v_p(N(Δ)) ≥ 4E_p for admissible p | Done, exact, two independent implementations: N = 2, 3 (14 fields, several H), N = 4 (14 fields, H = 2, 3, 4), N = 5 (14 fields at H = 2, 3; 8 fields at H = 4, 5); 510 admissible (run, p) pairs, no exception. Also the stated form Delta in p^E_p R. See docs/log.md 2026-10-08 and docs/writeup.md 2.3 |
| Greedy selection reaches full rank | Section 4, uses Cor. 4 | Same runs: the greedy loop must retain M rows | Holds in all runs (N <= 5) |
| Weight bound on retained rows | Section 4: weight ≤ 96 H^{2/3} U | Record max retained weight vs bound | Max weight 10-20 (N=3), 16 (N=4, H=2), 22 (N=5, H=2); bound 659-1372 and 1303 |
| Interpolation lemma | Lemma 3 / Cor. 4 | Rank of rows with α_j ≤ T_j equals M, for small N, several d, H, and also for the box with smaller t_j to see how sharp (3.1) is | Done N = 2, 3: minimal full-rank boxes have about M rows; (3.1) needs ~100x more, Corollary 4 ~30,000x. Kernel claim and 4ab minor verified. results/2026-10-08-interpolation-boxes-N*-summary.txt. Proof construction executed at N = 2, 3: src/lemma3_construct.py, results/2026-10-08-lemma3-construct-*-summary.txt. Lean formalization: lean-checks/Lemma3.lean (results/2026-10-08-lean-lemma3-full.txt) |
| S1, S2 bounds | Lemma 6, (4.4) | Tabulate S1, S2, S2/S1 vs N and H; compare with c0 = 1/(4·97²) = 1/37636, C0 = 192 | Exact N <= 5; EXPLORATORY mod-p N = 5..7: S1/(M H^2/3 U) ~ 0.43, H*S2/S1 ~ 1.6-1.8 |
| Archimedean bound | (5.1) | Compare exact log|N(Δ)| with the right side of (5.1) | Holds rigorously in all runs; LHS about 1/4 of RHS at N <= 3. src/bounds_table.py |
| Size vs divisibility ratio | (5.1) vs (5.6) | For the actual Δ, compute both sides; watch how the ratio moves with N | Done (descriptive): admissible-prime divisibility explains 5-20% of log|N(Δ)|, primes dividing 2q 50-90%. src/bounds_table.py |
| Prime-bias input | Lemma 2, (2.1)–(2.2) | Compute Σ_{p ≤ X, χ(p)=1} log p / p for real characters and fit the implied constant against ℓ; contrasts typical behavior (≈ ½ log X) with what a Siegel zero would force | Done (descriptive, exploratory float64): results/2026-10-08-prime-bias-summary.txt |
| Lean statement fidelity | refs/SiegelZeros.lean | Check hypotheses match Theorem 1 (primitive, nonprincipal, real via (χ a).im = 0, q ≥ 3, β in (0,1)) | Read once: matches. Answered 2026-10-08: the Lean proof follows this paper's route, not the 7/8 result (docs/log.md task 5). Built and accepted by the comparator with both kernels: results/2026-10-08-lean-comparator-wsl.txt, results/2026-10-08-lean-comparator-nanoda-netblock.txt; non-vacuity: lean-checks/NonVacuity.lean. |

## Observations so far

1. Lemma 7 also holds in our runs at primes with χ(p) = +1 and (2/p) = +1 (d = −3, p = 7: v_p = 40 ≥ 4E_p = 32). This is expected: for those primes θ^p ≡ θ mod pR, so the same row replacement works with g_p = identity. Primes with χ(p) = +1 and (2/p) = −1 send θ to τ(θ), which is not one of the three coordinates, and divisibility fails there (d = 13, p = 3: v_p = 4 < 12).
2. Consequence of (1), stated as an inference to be checked by a human: without a Siegel zero, three quarters of primes satisfy the divisibility, so the lower bound is about (3/4)·S1·log U, which does not beat the upper bound (3/4)·(S1 + S2)·log U. The argument needs the zero to push the admissible proportion from 3/4 toward 1. This is consistent with the paper's logic and explains why the 4/3 exponent in U is exactly what is needed. It is a useful sanity check to write up; it is not evidence that the proof is correct.

## Not testable by computation

The limiting argument in Section 6 (taking q → ∞ along a hypothetical sequence) and the existence of the absolute constants in Lemma 2 and Lemma 6. Making c explicit means tracing those constants by hand; computation can only check individual numerical inequalities along the way.
