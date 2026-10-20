# Sources for the explicit-constant analysis (fetched and read 2026-10-20)

Each source was downloaded into its own scratch directory and its text extracted locally (pdftotext and pypdf). Quotes below are copied from that text, with the PDF's Unicode symbols kept (⩽ ⩾ σ χ). Only the statements the note relies on are quoted. All sources were eventually read in the original.

The LibKey connector, which the organization's instructions name for scholarly articles, needs a one-time authorization by Joe (`/mcp`, then "claude.ai Scholarly Full Text Article Access with LibKey"). It was not authorized during this step. The arXiv sources are open access and were fetched directly from arxiv.org. Rosser–Schoenfeld and Davenport are the sources LibKey might reach.

## S1. The paper

"Uniform exclusion of Landau–Siegel zeros", OpenAI, October 1, 2026, `refs/siegel-paper.tex`, from openai/math adc7f12; the pinned files are unchanged at fd4aeeb (README). Equations are numbered within sections, and theorems, lemmas and corollaries share one counter:

| Item | Label | Lines |
|---|---|---|
| Theorem 1 | thm:main | 66-73 |
| Lemma 2 (prime bias) | (2.1), (2.2) | 181-194 |
| (2.3) Hadamard identity, (2.4) | | 204-221 |
| Lemma 3 (interpolation) | | 252-266 |
| Corollary 4 (rectangle) | | 410-424 |
| Lemma 6 (exponents) | (4.4) | 517-550 |
| (5.1) upper bound | | 573-577 |
| Lemma 7 (divisibility) | (5.3) | 598-603 |
| (5.6) prime lower bound | | 643-649 |
| (5.7) | | 653-657 |
| (6.2) master inequality | | 680-689 |

Note on labels: the task text says "Lemma 4.1" for Lemma 6 and "(5.4)" for the lower bound. In the compiled numbering, (5.4) is the replacement identity (lines 615-619), and the lower bound is (5.6)/(5.7).

## S2. Lu, Zaman, Zhao, "Numerical Computations Concerning Landau–Siegel Zeros", arXiv:2602.03626v1 (3 Feb 2026)

PDF 616,916 bytes, sha256 77388d40267e9068… (the same file as recorded in refs/lu-zaman-zhao-2602.03626.md).

- **Theorem 1.1 (p. 1):** "If q ⩽ 10^10 and χ is a quadratic Dirichlet character modulo q, then L(σ,χ) ≠ 0 for σ ⩾ 1 − 1/(5 log q)."
  - Range: q ⩽ 10¹⁰, every quadratic character mod q, real σ.
  - Consequence used: for a primitive real χ of conductor q ⩽ 10¹⁰, every real zero has 1 − β > 1/(5 log q), i.e. δ > 1/5.
- **Their summary of Platt (2016), p. 2:** "the work of Platt [Pla16] implies that L(σ,χ) ≠ 0 for σ > 0 and q ⩽ 4×10^5."
  - Range: q ⩽ 4·10⁵, σ > 0. In context this concerns the quadratic characters of the paragraph.
  - Platt (2016) was later read in the original; see the final section.

## S3. Rosser–Schoenfeld 1962, "Approximate formulas for some functions of prime numbers", Illinois J. Math. 6, 64–94

- First reached only through S4's quotation of Theorem 6. It was later read in the original (final section).
- Their Theorem 9 is not used; S5 replaces it.

## S4. arXiv:1703.08032 (Axler), "New estimates for some functions defined over primes", §5.2 (PDF 255,613 bytes, sha256 b212b7e4fc21a2d8…)

- E = −γ − Σ_p log p/(p(p−1)) = −1.332582275733220881765828776071027748838459….
- **Rosser–Schoenfeld [31, Theorem 6], as quoted:** "log x + E − 1/(2 log x) < Σ_{p≤x} log p/p < log x + E + 1/(2 log x), where the left-hand side inequality is valid for every x > 1 and the right-hand side inequality holds for every x ≥ 319."

## S5. Platt–Trudgian, "On the first sign change of θ(x) − x", arXiv:1407.1914 (PDF 183,305 bytes, sha256 cb4ee24a1f941625…)

- **Corollary 2 (the part used):** "For x > 0, θ(x) < (1 + 7.5·10^−7)x"
- Used: C_θ = 1 + 7.5·10⁻⁷, valid for all x > 0.

## S6. arXiv:2511.13898 (Zhao), "Upper bounds on gaps between zeros of L-functions", Appendix, Lemma 12 (PDF 445,420 bytes, sha256 d67a48739a1bb906…)

- **Lemma 12, (38):** "−ζ′/ζ(σ) < 1/(σ−1), σ > 1."
- The proof reduces (38) to (40), ∫_1^∞ {u}u^{−σ−1} du < 1/(2σ−1), and then to 1/(σ−1) − (1 − 2^{−σ})/σ − 3^{1−σ}/(σ−1) < 1/(2σ−1), "which can easily be verified for all σ > 1".
- That last elementary inequality is left to the reader there. I check it in step 3 rather than rely on it.

## S7. Davenport, *Multiplicative Number Theory*, 2nd ed. (rev. Montgomery), Ch. 12

- The paper cites Davenport §§12, 14 for (2.3): for primitive χ and real s > 1,
  −L′/L(s, χ) = ½ log(q/π) + ½ Γ′/Γ((s+ε)/2) − Σ_ρ Re 1/(s−ρ), each term Re 1/(s−ρ) ≥ 0.
- At first this was taken as stated. It was later checked against Ch. 12 (17)–(18) (final section).

## S8. Elementary facts (no citation needed; checked in step 3)

- ψ = Γ′/Γ is increasing on (0, ∞); ψ(3/2) = 2 − γ − 2 log 2.
- log p/p ⩽ (log p)/2 for p ≥ 2, and ⩽ (log p)/3 for p ≥ 3.

## Lemma 12 of S6

The final elementary inequality is proved for all σ > 1 by src/effectivity.py (`lemma12_check`; output in results/2026-10-20-effectivity/effectivity-output-v2.txt).

## Originals read after the session restart (2026-10-20)

Joe retrieved the PDFs through LibKey (Northeastern) and saved them to D:\siegel-sources\. They are not redistributed. The scanned pages were read from their page images, because the OCR text garbles the formulas.

| File | sha256 |
|---|---|
| rosser-schoenfeld-1962.pdf (31 pp., scan) | 8e37b06f82e09421bceb2502578c47b61469141f0287e6acedb70e01765ab556 |
| platt-2016.pdf (Math. Comp. 85, 3009–3027) | 10e9476ecc5c5403c0b2883e49eecabfc98587f8856c4775e4babf777bbd17fa |
| 978-1-4757-5927-3.pdf (Davenport, 2nd ed., rev. Montgomery, scan) | 6ee84ae0dbd1b7c835a94ee26ac88f8e9d926c4f7f55428c93d2d331bc122658 |

- **S3, Rosser–Schoenfeld Theorem 6 (p. 70):**
  - (3.21) log x + E − 1/(2 log x) < Σ_{p≤x} (log p)/p, for 1 < x.
  - (3.22) Σ_{p≤x} (log p)/p < log x + E + 1/(2 log x), for 319 ≤ x.
  - (2.11), p. 65: E ≈ −1.33258 22757 33221.
  - The S4 quotation is exact. The code's enclosure [−1.3325822758, −1.3325822757] contains this value.
- **Platt 2016:**
  - Theorem 10.1: "GRH holds for Dirichlet L-functions of primitive characters of modulus q ≤ 400000 and to height T = max(10⁸/q, 7.5·10⁷/q + 200) for even q and to height T = max(10⁸/q, 3.75·10⁷/q + 200) for odd q."
  - Theorem 10.2: "For every Dirichlet L-function of primitive character of modulus q ≤ 2000000, we have L_χ(1/2) ≠ 0."
  - INFERENCE: a real zero has height 0 < T. By 10.1 it would lie at 1/2, and 10.2 excludes 1/2. So no primitive χ with q ≤ 4·10⁵ has a real zero in (0, 1). This matches the S2 summary.
- **S7, Davenport 2nd ed.:**
  - Ch. 12, p. 83, (17): L′/L(s,χ) = −½ log(q/π) − ½ Γ′(½s+½a)/Γ(½s+½a) + B(χ) + Σ_ρ (1/(s−ρ) + 1/ρ), for primitive χ (Ch. 12 setup).
  - (18): Re B(χ) = −Σ_ρ Re 1/ρ.
  - Ch. 9, pp. 69–70: a = 0 for χ(−1) = 1, and a = 1 for χ(−1) = −1 (the odd case uses Γ(½(s+1))). So a = ε.
  - INFERENCE (one line): take real parts of (17), substitute (18) and negate. The result is (2.3) for real s > 1. Each Re 1/(s−ρ) = (s−β)/|s−ρ|² ≥ 0.
  - Ch. 14 was not needed for (2.3).
