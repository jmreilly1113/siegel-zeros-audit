# Lemma 3 (lem:interpolation): step-by-step audit (task 8.3a, 2026-10-08)

Category: **inference** (a careful human-style reading by Claude, not a machine check). Source: refs/siegel-paper.tex lines 252–407 (Lemma 3 and its proof), 410–432 (Corollary 4), 470–495 (the map A in (4.1)). Equation labels below are the .tex labels.

Why this matters: the Lean formalization does not contain this proof. It proves Corollary 4's conclusion by a different multiplicity argument (docs/lean-paper-map.md). So the main theorem's machine check does not depend on this proof, but the paper as a human-readable argument does.

Plain-language summary: the lemma says that polynomials of bounded degree in each of three variables can take any prescribed values at the N⁴ points An. The proof argues by contradiction. If they could not, some nonzero weighting v of the points would annihilate every such polynomial. The proof then builds one specific polynomial B that the weighting does not annihilate. B is a product of two pieces. The first, R, vanishes on a lot of lattice points and is used, through a nearest-point argument, to kill every point not on one face of the support. The second, Q, is a Lagrange polynomial that kills every point on that face except one.

## Setting
A : ℂ⁴ → ℂ³ surjective, ker A = ℂc, the coordinates of c linearly independent over ℚ. E_N = {0,…,N−1}⁴. 𝒫_t = polynomials in z₁,z₂,z₃ with deg_{z_j} ≤ t_j. Hypothesis (eq:budget): t_j ≥ 3(N−1) and ∏(t_j − 3(N−1) + 1) > (4N−3)⁴.

## Steps and the fact each uses

| # | Paper's step | Justification | Status |
|---|---|---|---|
| 1 | Non-surjective ⇒ nonzero v with Σ v_n B(An) = 0 for all B ∈ 𝒫_t (eq:moments) | A proper subspace of ℂ^{E_N} is annihilated by a nonzero linear functional. | ✔ |
| 2 | S = supp v ≠ ∅, P = conv S, 𝒦 = 4P ⊂ [0, 4(N−1)]⁴, #(𝒦 ∩ ℤ⁴) ≤ (4N−3)⁴ | S ⊂ E_N ⊂ [0,N−1]⁴. The cube [0,4(N−1)]⁴ contains (4N−3)⁴ lattice points. | ✔ |
| 3 | A nonzero R with deg_{z_j} R ≤ b_j := t_j − 3(N−1) and R(Am) = 0 on 𝒦 ∩ ℤ⁴ (eq:zeros) | b_j ≥ 0 by the first half of (eq:budget). The space has dimension ∏(b_j+1) > (4N−3)⁴, which is at least the number of linear conditions. | ✔ |
| 4 | R∘A ≢ 0, hence some m ∈ ℤ⁴ has R(Am) ≠ 0 | If R∘A = 0 then R vanishes on A(ℂ⁴) = ℂ³, so R = 0. A nonzero polynomial cannot vanish on all of ℤ⁴ (one-variable root bound, coordinate by coordinate). | ✔ |
| 5 | Choose such m with dist(m, 𝒦) minimal; y = nearest point of 𝒦; h = m − y ≠ 0 | Only finitely many lattice points lie within any bounded distance of the compact 𝒦, so the minimum is attained. 𝒦 is nonempty, compact and convex, so the nearest point y is unique. m ∉ 𝒦 by step 3, so h ≠ 0. Also dist(m,𝒦) = ‖h‖. | ✔ |
| 6 | y/4 ∈ G := {v ∈ P : h·v = max_P h·v} | Nearest-point inequality h·(x − y) ≤ 0 on 𝒦: y maximizes h· on 𝒦 = 4P, so y/4 maximizes h· on P. | ✔ |
| 7 | dim G ≤ 3 | If dim P = 4, G lies in the hyperplane h·v = max with h ≠ 0. Otherwise dim G ≤ dim P ≤ 3. | ✔ |
| 8 | y/4 is a convex combination of ≤ 4 vertices of G, one with coefficient ≥ 1/4; call it u. Then u ∈ S ∩ G and y − u ∈ 3P (eq:vertex) | Carathéodory in affine dimension ≤ 3. Unstated but standard: G is an exposed face of the polytope conv S, so G = conv(S ∩ G), and its vertices lie in S. The bound "≥ 1/4" holds because at most four nonnegative coefficients sum to 1. y − u = (4λ_u − 1)u + Σ_{i≠u} 4λ_i w_i has nonnegative coefficients summing to 3, so it lies in 3P by convexity. | ✔ (one standard fact unstated) |
| 9 | For n ∈ S ∖ G: y' = y + n − u ∈ 4P and m' = m + n − u = y' + h | y' = (y − u) + n ∈ 3P + P = 4P (P convex). m' ∈ ℤ⁴. | ✔ |
| 10 | h·(u − n) > 0, and ‖m' − z_η‖² = ‖h − η(u−n)‖² < ‖h‖² for small η > 0, where z_η = y' + η(y − y') ∈ 𝒦 (eq:distance) | u maximizes h· on P, n ∈ P ∖ G does not. y − y' = u − n. The square expands to ‖h‖² − 2η h·(u−n) + η²‖u−n‖². z_η ∈ 𝒦 for all η ∈ [0,1] by convexity (the paper says "sufficiently small", which is also true). | ✔ |
| 11 | R(A(m + n − u)) = 0 for n ∈ S ∖ G (eq:offface) | dist(m', 𝒦) < ‖h‖ = dist(m, 𝒦), so by the minimality in step 5, R(Am') = 0. | ✔ |
| 12 | A rational hyperplane ℋ = {r·v = k}, 0 ≠ r ∈ ℤ⁴, contains G, and r·c ≠ 0 | G's affine hull is spanned by integer points (S ∩ G), so it is a rational affine subspace of dimension ≤ 3. Any such subspace lies in a rational hyperplane; clear denominators. r·c = 0 would be a nontrivial ℚ-relation among c's coordinates. | ✔ |
| 13 | A restricted to ℋ is an affine bijection onto ℂ³ | The linear part {r·v = 0} meets ker A = ℂc only in 0 because r·c ≠ 0. Injective between 3-dimensional spaces, hence bijective. | ✔ |
| 14 | Coordinates λ_i (i ≠ i₀) with λ_i(An) = n_i for n ∈ ℋ; Q = ∏_{i≠i₀} ∏_{a≠u_i} (λ_i − a)/(u_i − a) has total degree ≤ 3(N−1); Q(Au) = 1 and Q(An) = 0 for n ∈ (S ∩ G) ∖ {u} | r_{i₀} ≠ 0, so a point of ℋ is determined by its other three coordinates, and λ_i is affine. Unstated but immediate: if n ≠ u are both in ℋ, they differ in some coordinate i ≠ i₀ (equal other coordinates plus r·n = r·u = k forces n_{i₀} = u_{i₀}), and n_i ∈ {0,…,N−1}, so a Lagrange factor vanishes. | ✔ (one immediate step unstated) |
| 15 | B(z) = Q(z) R(z + A(m − u)) ∈ 𝒫_t | Translation keeps each separate degree of R ≤ b_j. deg_{z_j} Q ≤ total degree ≤ 3(N−1). The sum is ≤ t_j. | ✔ |
| 16 | Σ_n v_n B(An) = v_u R(Am) ≠ 0, contradicting (eq:moments) | Terms with n ∈ S ∖ G vanish by step 11 (R(A(n + m − u)) = R(Am')). Terms with n ∈ (S ∩ G) ∖ {u} vanish by step 14. At n = u: Q(Au) = 1 and R(A(u + m − u)) = R(Am) ≠ 0, and v_u ≠ 0 because u ∈ S. | ✔ |

## Corollary 4 (cor:rectangle)
- T_j ≥ 32N: T₁ = 32H^{2/3}N^{4/3} ≥ 32N always. T₂ = T₃ = 32H^{-1/3}N^{4/3} ≥ 32N exactly when H ≤ N. ✔
- t_j ≥ 3(N−1) follows. ∏(t_j − 3(N−1) + 1) > ∏(T_j − 3(N−1)), since t_j + 1 > T_j. Each factor is ≥ T_j/2 because T_j ≥ 6(N−1). So the product is ≥ T₁T₂T₃/8 = 32³N⁴/8 = 4096N⁴ > (4N−3)⁴. ✔
- The basis of 𝒫_t is the monomials z^α with α_j ≤ t_j, which gives the stated rows. ✔

## Applying it with A from (eq:A)
- d squarefree, d ≠ 1, d ≠ 2. Then d, 2 and 2d are all non-squares (2d square with d squarefree forces d = 2), so [K:ℚ] = 4 and 1, a, b, ab is a ℚ-basis. So c = (ab, b, −a, −1) has ℚ-independent coordinates. ✔
- The kernel and rank-3 claim were checked exactly (docs/tasks.md section 2, results/2026-10-08-interpolation-boxes-N2/N3*). ✔ computed.
- The paper's box is much larger than needed at small N: the minimal boxes in results/2026-10-08-interpolation-boxes-N*-summary.txt are far below the t_j of (eq:budget). This is consistent with a lemma that holds with room to spare.

## Findings of this audit (inference)
1. No gap found. Every step follows from standard facts.
2. Two facts are used without being stated: (step 8) the vertices of the face G lie in S, because G = conv(S ∩ G); and (step 14) two distinct points of ℋ differ in some coordinate other than i₀. Both are routine, and a referee would likely accept them as written.
3. The proof does not need the points An to be distinct, but distinctness follows from the conclusion (and directly from the ℚ-independence of c).
4. Nothing in the proof depends on q, d, H or any arithmetic, which matches the paper's claim (line 250).

Executable check of these steps: src/lemma3_construct.py, 540 instances at N = 2, 3, all 28 checks pass (results/2026-10-08-lemma3-construct-N2-summary.txt, -N3-summary.txt, -N2-generic4d-summary.txt). Lean formalization of the proof: lean-checks/Lemma3.lean.
