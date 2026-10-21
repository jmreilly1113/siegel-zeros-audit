# Related work

<!-- DRAFT for reviewer-packet-v3 (2026-10-20). Merged from docs/packet-related-work-draft-v2.md; that file and v1 are kept. -->

**Read before use.** Banks was read in full (refs/banks-2610.15483.md). For Kerr and Green, only the abstract pages were read here. Every statement about the content of Kerr's and Green's papers comes from facts Joe supplied on 2026-10-20 and is marked **[CHECKED-BY-JOE, pending Joe's read]**. Green's version dates are flagged: Joe gives v2 as 2026-10-18, and the Hexagon page fetched on 2026-10-20 shows v2 dated Oct 17, 2026.

Three other accounts of the OpenAI argument (OpenAI, *Uniform exclusion of Landau–Siegel zeros*, manuscript dated October 1, 2026) have appeared.

- **Banks.** W. D. Banks, *On the OpenAI proof that Landau–Siegel zeros do not exist*, arXiv:2610.15483 (dated October 11, 2026).
  - A line-by-line exposition arranged as a direct proof with explicit constants.
  - (1 − β) log q ≥ δ₀ = 81/(5888 e^{3/2}) = 3.0696·10⁻³ for q ≥ 10¹⁰ (Theorem 1.1, Remark 7.1). With Lu–Zaman–Zhao, this holds for all q ≥ 3; he states it as 3.0·10⁻³.
  - The interpolation step is his Proposition 3.4 with hypothesis (3.1). The two convex-geometry facts it uses are written out in his Lemma 3.2 and in Step 5 of the proof of Proposition 3.4.
- **Kerr.** B. Kerr, *A simpler proof that there are no Landau–Siegel zeros*, arXiv:2610.21099 (v1 submitted 2026-10-15). **[CHECKED-BY-JOE, pending Joe's read]:**
  - same biquadratic field and points as OpenAI and Banks;
  - a pigeonhole construction (Lemmas 3–5) plus Masser's degree bound (Lemma 6), with μ ≥ 4/3 (Lemma 7), replaces the interpolation lemma and the greedy determinant;
  - constants are not made explicit.
- **Green.** B. Green, *On Landau–Siegel zeros*, Hexagon 2610.00311, v1 2026-10-17, v2 2026-10-18 [dates as supplied by Joe; the Hexagon page shows v2 dated Oct 17, 2026], CC BY 4.0. Its provenance statement attributes the mathematical arguments to ChatGPT and the text to the author. **[CHECKED-BY-JOE, pending Joe's read]:**
  - works in ℚ(√d) only, without √2;
  - a Gram-matrix determinant, whose nonsingularity is Lemma 3.1 (resultants, Schwarz–Zippel);
  - the main theorem is a prime-sum bound, (1/2 + O(1/C)) log X + O_C(1);
  - no explicit δ₀;
  - the deduction that there are no Siegel zeros is left as standard.

**How this package relates to them.**
- The explicit constant in `docs/effectivity/note-v2.md` uses the same master inequality as Banks's §7.
- `docs/effectivity/banks-comparison-v2.md` compares the two term by term:
  - each input agrees or is a different valid choice;
  - his twelve numeric claims and his δ₀ recompute in Arb;
  - our 4.467·10⁻³ (q ≥ 10¹⁰) differs from his 3.0696·10⁻³ mainly because H is left free (×1.68), and partly through five smaller choices;
  - two of his choices are sharper than ours: the primes dividing q, and the shift in σ.
- The Lean Lemma 3 is scoped in `lemma3-scope.md`.
