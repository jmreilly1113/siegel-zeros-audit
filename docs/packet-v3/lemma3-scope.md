# Lemma 3: narrowed scope note

<!-- DRAFT for reviewer-packet-v3 (2026-10-20). -->

Our Lean Lemma 3 (`lean-checks/Lemma3.lean`, theorem `Lemma3.interpolation`; standard axioms only; accepted by nanoda) certifies **one step of OpenAI's and Banks's route**:
- Its hypotheses are identical to Banks's condition (3.1), the hypothesis of his Proposition 3.4: a surjective linear map ℂ⁴ → ℂ³ whose kernel is spanned by a vector with ℚ-independent coordinates; N ≥ 1; each degree ≥ 3(N−1); and ∏(t_j − 3(N−1) + 1) > (4N−3)⁴.
- Its conclusion is his: the evaluation map is surjective.
- The clause-by-clause comparison is in `docs/packet-related-work-draft.md`, "Hypotheses compared".
- Swapped into OAI's proof of `dirichletRealZeroBound_proof`, it gives a proof of the challenge statement accepted by the official comparator with both kernels (`results/2026-10-09-lean-comparator-rerouted-nanoda.txt`).

What it does **not** cover:
- **Kerr and Green.** Kerr's and Green's arguments bypass this step. Per the [CHECKED-BY-JOE, pending Joe's read] items in `related-work.md`: Kerr uses a pigeonhole construction with Masser's degree bound, and Green a Gram-matrix determinant in ℚ(√d).
- **Banks's Corollary 3.5.** Our Lean bridge (`lean-checks/Lemma3Bridged.lean`) proves OAI's own Corollary 4 statement from `Lemma3.interpolation`. It does not prove Banks's Corollary 3.5 (box T₁ = 32H^{2/3}M, T₂ = T₃ = 32H^{−1/3}M) as stated.
- **The rest of the argument.** The Lean Lemma 3 says nothing about the analytic input, the determinant, or the explicit constant.

Banks's proof of Proposition 3.4 writes out the two facts our hand audit (`docs/lemma3-audit.md`) recorded as unstated in the OpenAI manuscript: his Lemma 3.2, and Step 5 of the proof. Banks leaves his Lemma 3.3 to the reader. The form his Step 2 uses is proved in our Lean file (`exists_lattice_nonvanishing`, lean-checks/Lemma3.lean:740).
