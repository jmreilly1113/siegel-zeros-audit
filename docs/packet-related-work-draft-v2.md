# Draft for the packet: related work and a narrowed Lemma 3 scope note, version 2

Draft v2, 2026-10-20. `docs/packet-related-work-draft.md` (v1) is kept unchanged.

- **Change from v1:** the bracketed Kerr and Green items are filled in from facts Joe supplied on 2026-10-20 (his addendum to the paper-prep-3 brief). They are marked **CHECKED-BY-JOE (pending Joe's read)**.
- **What I read:** only the abstract pages (arxiv.org/abs/2610.21099; hexagonmath.org/2610.00311v2). I did not read either paper, and I have not verified the section, lemma or date details.
- **Green's date:** 2026-10-17 (v2), as shown on the Hexagon page and confirmed by Joe on 2026-10-20.

## Related work (paragraph for the packet)

Three other accounts of the OpenAI argument appeared after the October 1 manuscript.

- **Banks** gives a line-by-line exposition arranged as a direct proof with explicit constants. He obtains (1 − β) log q ≥ 3.0·10⁻³ for q ≥ 10¹⁰, and, with the computation of Lu, Zaman and Zhao, for all q ≥ 3 (W. D. Banks, *On the OpenAI proof that Landau–Siegel zeros do not exist*, arXiv:2610.15483).
- **Kerr** simplifies the OpenAI proof (B. Kerr, *A simpler proof that there are no Landau–Siegel zeros*, arXiv:2610.21099, v1 submitted 2026-10-15). **CHECKED-BY-JOE (pending Joe's read):**
  - He uses the same biquadratic field and the same points.
  - A pigeonhole construction (Lemmas 3–5) and Masser's degree bound (Lemma 6), with μ ≥ 4/3 (Lemma 7), replace the interpolation lemma and the greedy determinant.
  - The constants are not made explicit.
- **Green** gives a variant (B. Green, *On Landau–Siegel zeros*, Hexagon 2610.00311v2, 2026-10-17, CC BY 4.0). Its provenance statement attributes the mathematical arguments to ChatGPT and the text to the author. **CHECKED-BY-JOE (pending Joe's read):**
  - It works in ℚ(√d) only, without √2.
  - It uses a Gram-matrix determinant, whose nonsingularity is Lemma 3.1 (resultants, Schwarz–Zippel).
  - The main theorem is a prime-sum bound, (1/2 + O(1/C)) log X + O_C(1).
  - No explicit δ₀ is given, and the deduction that there are no Siegel zeros is left as standard.

Our explicit constant (docs/effectivity/note-v2.md) uses the same skeleton as Banks's §7. The term-by-term comparison is in docs/effectivity/banks-comparison-v2.md:
- every input agrees or is a different valid choice;
- his 3.0696·10⁻³ recomputes exactly in our Arb pipeline;
- our larger 4.467·10⁻³ (q ≥ 10¹⁰) comes mainly from treating H as a free parameter.

None of these works, ours included, has been refereed.

## Lemma 3: narrowed scope note

> Our Lean Lemma 3 (lean-checks/Lemma3.lean, theorem `Lemma3.interpolation`, standard axioms only) certifies a step of OpenAI's and Banks's route only.
> - Its hypotheses are identical to Banks's (3.1), and its statement is his Proposition 3.4.
> - Kerr's and Green's arguments bypass this step. Per the CHECKED-BY-JOE items above: Kerr uses a pigeonhole construction with Masser's degree bound, and Green a Gram-matrix determinant in ℚ(√d).
> - Both points were recorded in this audit (commit 447ad02, 2026-10-09). Banks writes both out (Lemma 3.2; Step 5 of the proof of Proposition 3.4).

The hypotheses comparison table is unchanged from v1 (`docs/packet-related-work-draft.md`, "Hypotheses compared").
