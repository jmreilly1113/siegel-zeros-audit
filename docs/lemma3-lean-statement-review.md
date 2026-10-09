# Lemma 3 in Lean: statement review and skeleton (plan step 3c, skeleton stage, 2026-10-08)

File: `lean-checks/Lemma3Skeleton.lean`. Compile record: `results/2026-10-08-lean-lemma3-skeleton.txt` (command `wsl.exe -d Ubuntu-24.04 -u root -- bash wsl-comparator/34_lean_file.sh Lemma3Skeleton.lean`; Lean 4.34.1, Mathlib d13f23b723).

## What exists (computed)
- `Lemma3.interpolation` is the paper's Lemma 3 written in Lean. It compiles.
- Its proof is complete apart from **12 sub-lemmas**, which are stated and still marked `sorry`. Lean flags exactly those 12 declarations, and not `interpolation` itself. So the proof that turns the 12 pieces into Lemma 3 is fully machine-checked. This is the paper's argument, steps 1–16 of `docs/lemma3-audit.md`.
- Axioms: `propext, sorryAx, Classical.choice, Quot.sound`. `sorryAx` will disappear once the 12 sub-lemmas are proved.

**What this does and does not mean.** The skeleton shows that the 12 pieces are enough to give Lemma 3. It does not show that the pieces are true. Lemma 3 is formalized only when all 12 have proofs.

## Clause-by-clause comparison with the paper (inference: my reading)

Paper: `refs/siegel-paper.tex` lines 252–267. Lean as elaborated (printed by `#check`, in the result file).

| Paper | Lean | Match |
|---|---|---|
| $A:\mathbb C^4\to\mathbb C^3$ linear, surjective | `A : (Fin 4 → ℂ) →ₗ[ℂ] (Fin 3 → ℂ)`, `Function.Surjective A` | ✔ |
| $\ker A=\mathbb C c$ | `LinearMap.ker A = Submodule.span ℂ {c}` (prints as `ℂ ∙ c`) | ✔ |
| the four coordinates of $c$ are linearly independent over $\mathbb Q$ | `LinearIndependent ℚ c`, with `c : Fin 4 → ℂ` read as a family of four complex numbers, using ℂ's standard ℚ-vector-space structure | ✔ |
| $N\ge1$ | `N : ℕ`, `1 ≤ N` | ✔ |
| $t_1,t_2,t_3$ integers | `t : Fin 3 → ℤ` | ✔ |
| $t_j\ge3(N-1)$ (eq:budget) | `∀ j, 3 * ((N:ℤ) - 1) ≤ t j` | ✔ Computed in ℤ, so no truncated subtraction |
| $\prod_j(t_j-3(N-1)+1)>(4N-3)^4$ (eq:budget) | `(4 * (N:ℤ) - 3) ^ 4 < ∏ j, (t j - 3 * ((N:ℤ) - 1) + 1)` | ✔ Also in ℤ |
| $E_N=\{0,\dots,N-1\}^4$ | the type `Fin 4 → Fin N`; a point `n` becomes the vector `fun i => ((n i : ℕ) : ℂ)` in ℂ⁴ | ✔ |
| $\mathcal P_t$: $B\in\mathbb C[z_1,z_2,z_3]$ with $\deg_{z_j}B\le t_j$ | `Pt t = {B : MvPolynomial (Fin 3) ℂ \| ∀ j, degreeOf j B ≤ t j}` | ✔ Variable $z_j$ is index `j−1`. `degreeOf` is the highest power of that variable, which is the paper's $\deg_{z_j}$. The zero polynomial is in `Pt t`, as it is in the vector space $\mathcal P_t$. |
| the map $B\mapsto(B(An))_{n\in E_N}$ from $\mathcal P_t$ to $\mathbb C^{E_N}$ is surjective | `Function.Surjective (fun B : Pt t => fun n => eval (A n) B)` | ✔ The Lean map is written as a plain function on the set `Pt t` rather than as a linear map. Being onto means the same thing. |

**Conclusion (inference): the Lean statement says exactly what the paper's Lemma 3 says.** It is not weaker in any respect: no added hypotheses, no changed constants, the same conclusion. Two small notes:
- Surjectivity of A is a redundant hypothesis, in the paper and in Lean alike. A one-dimensional kernel already forces A to be onto.
- The Lean statement does not show that the hypotheses can be met. For the paper's map A from (eq:A), the hypotheses hold by `docs/lemma3-audit.md` ("Applying it with A", [K:ℚ] = 4) and our exact kernel checks. We have not proved that part in Lean.

**A reviewer should check one thing.** The paper's evaluation point is $An$ for an integer vector $n$. In Lean, that integer vector is first converted to a complex vector and A is applied to the result. That is the only possible reading.

## The 12 sub-lemmas: are they true? (inference: my reading)

A false sub-lemma would make the skeleton worthless, because Lean accepts anything built on a `sorry`. I checked each one against the audit. Step numbers are those of `docs/lemma3-audit.md`.

| Sub-lemma | Steps | Why it is true |
|---|---|---|
| `exists_annihilator` | 1 | With t ≥ 0, `Pt t` is a vector space. Its image is a subspace; a proper subspace is cut out by a nonzero linear functional Σ vₙ xₙ. **I added the hypothesis t ≥ 0 after review.** Without it, `Pt t` can be empty, and the claim fails when the index set is empty too. The main proof supplies t ≥ 0 from t_j ≥ 3(N−1) ≥ 0. |
| `four_hull_subset_cube` | 2 | The cube [0, L]⁴ is convex. Scaling it by 4 gives [0, 4L]⁴. |
| `exists_vanishing` | 3 | Fewer linear conditions than the dimension ∏(b_j + 1) leave a nonzero solution. |
| `exists_lattice_nonvanishing` | 4 | R ∘ A ≠ 0 because A is onto. A nonzero polynomial cannot vanish on all of ℤ⁴. |
| `exists_nearest` | 5 | Only finitely many lattice points lie within a given distance of a compact set, so a nearest one exists. The nearest point of a closed convex set satisfies the standard inequality. |
| `quarter_mem_face` | 6 | y/4 maximizes h· on conv S. In any convex combination giving y/4, weight can sit only on maximizing points of S. This is one of the two facts the audit found unstated in the paper; here it becomes part of the statement. |
| `exists_heavy_vertex` | 7–8 | Carathéodory, plus the fact that the points lie in a hyperplane with h ≠ 0. That gives at most 4 affinely independent points, so one weight is ≥ 1/4. |
| `closer_point` | 9–10 | y′ = y + n − u lies in 3P + P = 4P. Moving from y′ a little toward y lowers the squared distance by about 2η·h·(u − n) > 0. |
| `exists_int_hyperplane` | 12 | Suppose the differences of the integer points spanned ℚ⁴. Then they would span ℝ⁴, and h would be orthogonal to everything, so h = 0. Hence those differences lie in a proper rational subspace. Clearing denominators gives r. |
| `int_comb_ne_zero` | 12 | This is the definition of ℚ-linear independence, applied to integer coefficients. |
| `exists_lagrange` | 13–14 | r·c ≠ 0 makes A restricted to ℋ one-to-one, and A is onto, so A on ℋ is an affine bijection. Then build the paper's product of Lagrange factors. This includes the second unstated fact: two distinct points of ℋ differ in some coordinate other than i₀. |
| `exists_translate` | 15 | Substituting z ↦ z + w does not raise the degree in any variable. |

## What the skeleton changed relative to the paper's proof (inference)
- The face G is never formed as a geometric object. Wherever the proof uses G, only its points in S are needed. This is a simplification and changes nothing in the argument.
- The paper takes ℋ to contain all of G. The skeleton needs ℋ only to contain S ∩ G, which is all that Q is evaluated on.

## Next stage: DONE 2026-10-08 (see lean-checks/Lemma3.lean, results/2026-10-08-lean-lemma3-full.txt)

All 12 sub-lemmas were proved in five parallel piece files, merged with statements checked identical by script, and the merged file compiles with `Lemma3.interpolation` depending only on propext, Classical.choice, Quot.sound. Original plan:
Prove the 12 sub-lemmas, in parallel, one file per piece:
1. nearest point and face;
2. Carathéodory and the move off the face;
3. rational hyperplane;
4. Lagrange polynomial;
5. counting and degrees.

Each sub-lemma statement must be copied into its piece's file exactly as written. The finished proofs are then merged back into the skeleton, the file is recompiled, and `#print axioms Lemma3.interpolation` must show only the three standard axioms. Optional extra: derive Corollary 4 from `interpolation` and compare it with OAI's `actual_biquadratic_rectangle_span`.
