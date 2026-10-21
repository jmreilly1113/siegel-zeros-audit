# Draft for the packet: related work and a narrowed Lemma 3 scope note

Draft, 2026-10-20, for Joe's review. Not yet in any packet file; note.md and the reviewer packet are unchanged.

Sources:
- **Banks:** read in full (refs/banks-2610.15483.md; local PDF and TeX).
- **Kerr and Green:** only their abstract pages were read, on 2026-10-20 (arxiv.org/abs/2610.21099; hexagonmath.org/2610.00311v2). Nothing below goes beyond those pages, and the bracketed items must be checked against the papers before use.

## Related work (paragraph for the packet)

Three other accounts of the OpenAI argument appeared after the October 1 manuscript.

- **Banks** gives a line-by-line exposition arranged as a direct proof with explicit constants. He obtains (1 − β) log q ≥ 3.0·10⁻³ for q ≥ 10¹⁰, and, with the computation of Lu, Zaman and Zhao, for all q ≥ 3 (W. D. Banks, *On the OpenAI proof that Landau–Siegel zeros do not exist*, arXiv:2610.15483).
- **Kerr** presents a simplification of the OpenAI proof (B. Kerr, *A simpler proof that there are no Landau–Siegel zeros*, arXiv:2610.21099). [Describe the method only after reading the paper; the abstract says only that it simplifies the OpenAI proof.]
- **Green** gives a variant of the OpenAI proof. In its second version two parameters are decoupled to improve the constant in the main theorem. Its provenance statement attributes the mathematical arguments to ChatGPT and the text to the author (B. Green, *On Landau–Siegel zeros*, Hexagon 2610.00311 v2, 17 October 2026, CC BY 4.0). [State Green's constant only after reading the paper.]

Our explicit constant (docs/effectivity/note.md) was derived independently from the OpenAI manuscript. It uses the same skeleton as Banks's §7. A term-by-term comparison is in docs/effectivity/banks-comparison.md:
- Every input agrees or is a different valid choice.
- His 3.0696·10⁻³ recomputes exactly in our Arb pipeline.
- Our larger 4.467·10⁻³ (q ≥ 10¹⁰) comes mainly from treating H as a free parameter.
- Banks is sharper than we are on two points: the primes dividing q, and the shift in σ.

None of these works, ours included, has been refereed.

## Lemma 3: narrowed scope note

**Current packet wording (v1, reviewer-packet.md and README item 2):** "The paper's own proof of Lemma 3, which the OAI formalization replaces with a multiplicity estimate, is formalized in Lean". The hand audit "found two unstated routine facts and no gap".

**Proposed narrowed wording:**

> The paper's Lemma 3 is, statement for statement, Banks's Proposition 3.4 (arXiv:2610.15483), and Banks's proof writes out in full the convex-geometry argument the paper gives tersely. In particular, both facts our hand audit found unstated are stated and proved there:
> - the face G equals conv(S ∩ G) (his Lemma 3.2);
> - two distinct points of the hyperplane V differ in a coordinate other than j₀ (his Step 5).
>
> Our contribution on Lemma 3 is therefore narrower than "an audit": it is a machine-checked Lean proof (lean-checks/Lemma3.lean, theorem `Lemma3.interpolation`, standard axioms only) of a statement whose hypotheses are identical to Banks's (3.1). That proof was swapped into OAI's proof of `dirichletRealZeroBound_proof` and accepted by the official comparator with both kernels. Banks's Lemma 3.3 (a nonzero polynomial does not vanish on all of ℤ⁴) is left to the reader there. The form in which his Step 2 uses it (R ∘ A ≠ 0 at some lattice point, for R ≠ 0 and A surjective) is proved in our Lean file (`exists_lattice_nonvanishing`, lean-checks/Lemma3.lean:740).

**Hypotheses compared** (COMPUTED by reading: Lean statement lean-checks/Lemma3.lean:817–826; Banks (3.1) and Prop. 3.4; paper eq:budget, refs/siegel-paper.tex:252–266):

| | Lean `Lemma3.interpolation` | Banks Prop. 3.4, (3.1) | Paper Lemma 3, (3.1) |
|---|---|---|---|
| Map | `A : (Fin 4 → ℂ) →ₗ[ℂ] (Fin 3 → ℂ)`, `Function.Surjective A` | Θ : ℂ⁴ → ℂ³ surjective linear | A : ℂ⁴ → ℂ³ surjective linear |
| Kernel | `LinearMap.ker A = Submodule.span ℂ {c}` | ker Θ = ℂξ | ker A = ℂc |
| Independence | `LinearIndependent ℚ c` | the four coordinates of ξ are linearly independent over ℚ | same, for c |
| N | `1 ≤ N` | N ≥ 1 | N ≥ 1 |
| Degree floor | `3 * (N − 1) ≤ t j` for each j, t j ∈ ℤ | 𝔡_j ≥ 3(N−1), integers 𝔡_j ≥ 0 | t_j ≥ 3(N−1), integers |
| Budget | `(4N − 3)^4 < ∏ j, (t j − 3(N − 1) + 1)` | ∏(𝔡_j + 1 − 3(N−1)) > (4N−3)⁴ | ∏(t_j − 3(N−1) + 1) > (4N−3)⁴ |
| Polynomial space | `Pt t = {B | ∀ j, degreeOf j B ≤ t j}` (MvPolynomial (Fin 3) ℂ) | Poly(𝔡): deg_{z_j} ≤ 𝔡_j | 𝒫_t: deg_{z_j} B ≤ t_j |
| Conclusion | evaluation B ↦ (B(A n))_{n ∈ (Fin 4 → Fin N)} is surjective | every f on ⟦N⟧⁴ equals ℘ ∘ Θ for some ℘ ∈ Poly(𝔡) | evaluation map 𝒫_t → ℂ^{E_N} is surjective |

INFERRED: the three statements are the same.
- Lean's integer t j with 3(N−1) ≤ t j already implies t j ≥ 0, which matches Banks's 𝔡_j ≥ 0.
- `LinearIndependent ℚ c` is the Lean form of "coordinates linearly independent over ℚ". This was checked clause by clause on 2026-10-08 in docs/lemma3-lean-statement-review.md, against the paper.

Banks also proves Corollary 3.5 (a box with T₁ = 32H^{2/3}M, T₂ = T₃ = 32H^{−1/3}M) by the same route as the paper's Corollary 4. Our Lean bridge (lean-checks/Lemma3Bridged.lean) proves OAI's own Corollary 4 statement from `Lemma3.interpolation`. It does not prove Banks's Corollary 3.5 as stated.
