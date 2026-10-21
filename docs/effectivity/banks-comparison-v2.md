# Our explicit constant compared with Banks (arXiv:2610.15483v1), version 2

Draft v2, 2026-10-20. It supersedes `banks-comparison.md` (v1, kept unchanged) on three points:
- row 21 (Banks's H ≤ q);
- section (a) (Remark 7.2(vii));
- the label of the 3.998·10⁻³ result.

The Platt row's side conditions, rechecked with H > q noted, are in `results/2026-10-20-paper-prep-3/banks-v2-platt-side-conditions.txt`.

Sources: `docs/effectivity/note.md` (ours, unchanged), `refs/banks-2610.15483.md` (Banks; PDF and TeX kept locally, sha256 there). Computation: `src/banks_compare.py`. Output: `results/2026-10-20-paper-prep-2/banks-compare-output.txt`. Command: `.venv/Scripts/python -I src/banks_compare.py`. Environment: Python 3.14.6, python-flint 0.9.0, Arb at 256 bits.

Labels:
- **COMPUTED:** an Arb ball, from that output file.
- **STATED:** quoted from Banks or from our note.
- **INFERRED:** reasoning, not computed.

Section and equation numbers for Banks are from his PDF.

**Notation clash.**
- Banks's λ is the shift in σ = 1 + λ/log X; ours is 1.
- Banks's ω is our γ, the exponent in N = ⌈q^γ⌉.
- Our λ is L/log q = (4/3) log N/log q, which is about (4/3)γ.
- Banks's M = N^{4/3} is our U; our M = N⁴ is his N⁴.

## Result of the check

- **No inequality of ours fails under Banks's accounting.**
  - His argument has the same structure as our master inequality (derivation.md §5), term for term.
  - With every switch at his setting, `delta0(BANKS, …)` is exactly his Step 3 inequality (§7) solved for δ.
  - With every switch at ours, it reproduces our certified values, ball for ball. COMPUTED: 3.39929040265590e-3 and 4.46737803384182e-3; both balls overlap `src/effectivity.delta0`.
- **Banks's 3.0696·10⁻³ recomputed, COMPUTED:**
  - δ₀ = 9/(128(ω+1)C₁) = 81/(5888 e^{3/2}) = [0.00306955553193322 ± 2.9e-18], certified > 3.0695555319·10⁻³.
  - All twelve numeric claims in his §7 and Lemma 2.1 hold in Arb (Part A of the output).
- **Neither account is uniformly sharper.**
  - Banks is sharper on two choices: primes dividing q, and the shift.
  - We are sharper on five: free H, the tight upper end of λ, the S₁ bounds, κ with the Mertens terms, and the θ bound.

## Row by row

| # | Inequality or constant (ours, note.md / derivation.md) | Ours | Banks (section / eq.) | Banks's value | Agree? |
|---|---|---|---|---|---|
| 1 | Hadamard identity (2.3) of the paper | −L′/L(σ) = ½log(q/π) + ½ψ((σ+ε)/2) − Σ Re 1/(σ−ρ), σ > 1; checked against Davenport Ch. 12 (17)–(18) | §2, (2.1), from Davenport (17)–(18) | same formula | **Agree** (same source, same identity) |
| 2 | Keep only ρ = β | each Re 1/(σ−ρ) ≥ 0 | (2.2) | same | **Agree** |
| 3 | −ζ′/ζ(σ) < 1/(σ−1) | for all σ > 1, Zhao Lemma 12; last step proved here in Arb (min of φ > 3.878·10⁻²) | before (2.5): "−ζ′/ζ(σ) ≤ 1/(σ−1) for σ ∈ (1,2]", no citation | same bound | **Agree** in value; Banks gives no source |
| 4 | κ | κ = ½ψ(3/2) − ½log π = −0.5541199559…, kept in C_H as (e/2)κ | Lemma 2.1 proof: κ_B = ½log π − ½ψ(3/2) = 0.5541… = −κ | COMPUTED: κ_B + κ = 0 within 10⁻⁶⁰ | **Agree** in value. Banks keeps it in (2.6) but discards it in (2.4) together with −1/log H |
| 5 | Shift in σ | σ = 1 + 1/L (shift 1) | Lemma 2.1, σ = 1 + λ/log X with λ ∈ (0,2]; §7 uses λ = 3/2 | λ = 3/2 | **Differ** (choice; both valid) |
| 6 | Coefficient of δ(log X)²/ℓ | C_δ = e/2 = 1.35914 | C₁ ≥ e^λ/(2λ²), Lemma 2.1 | λ = 1: e/2 (same); λ = 3/2: 2e^{3/2}/9 = 0.9959309045 | **Agree** at λ = 1 |
| 7 | Coefficient of ℓ in (2.2) | C_ℓ = e/4 + c_q; LZZ row c_q = ln2/(2ℓ) + 1/3, i.e. 1.0129 plus ln2/2 in C_H | (2.4): C₂ + 1/(2H), C₂ ≥ e^λ/4 | λ = 1: 0.6796; λ = 3/2: 1.1204222 + 1/(2H) | **Differ.** At equal shift, ours is larger by c_q − 1/(2H) |
| 8 | Primes dividing q | Σ_{p\|q} log p/p ≤ c_q ℓ (three valid choices) | (2.3), (2.6), (2.8): p \| q enter the Λ(n)(1+χ(n)) sum with weight 1, so ½S₀ is bounded together with S₊; only p > H, p \| q cost ℓ/(2H) | 1/(2H) | **Differ.** Banks's bound is sharper. INFERRED: valid; checked line by line against (2.6)–(2.8) |
| 9 | Mertens (Rosser–Schoenfeld Thm 6) | lower bound for x > 1, upper for x ≥ 319; E cancels; keeps 1/(2 log H) + 1/(2L) | (2.7), same theorem and ranges | bounds the two terms by 1/log H, then discards that with κ: e^{3/2}κ_B/2 > 0.277 > 0.174 > 1/log 319 | **Agree** (same source). COMPUTED: his inequality holds (1.2417 > 0.277; 1/log 319 < 0.174) |
| 10 | θ(x) bound | θ(x) < (1 + 7.5·10⁻⁷)x, Platt–Trudgian Cor. 2 | Cor. 6.3: Σ_{p≤M} log p ≤ 2M, "Chebyshev's bound", no citation | 2 | **Differ** (both valid; ours sharper; effect ×1.0003) |
| 11 | Archimedean bound (5.1) | ¼log\|NΔ\| ≤ (N⁴/2) log N⁴ + (S₁+S₂)(log N + ℓ/2 + log 8) | Lemma 5.1, (5.1): 2N⁴ log N + (S₁+S₂₃)(log N + ℓ/2 + log 8) | same, since (N⁴/2)·4 log N = 2N⁴ log N | **Agree** exactly |
| 12 | p-adic lower bound (5.6)/(5.7) | ¼log\|NΔ\| ≥ S₁A(U) − N⁴θ(U), with E_p ≥ S₁/p − N⁴ | Lemma 6.2, Cor. 6.3 | same form, θ ≤ 2M | **Agree** |
| 13 | Lemma 6 (paper) | S₂ ≤ 192N⁴H^{−1/3}U, S₁ ≥ N⁴H^{2/3}U/(4·97²), given N ≥ H, H^{2/3}N^{4/3} ≥ 2·97² | Lemma 4.2 | same constants, same hypotheses | **Agree** |
| 14 | ρ_H = S₂/S₁ bound | 768·97²/H = 7,226,112/H | §7 Step 2: S₂₃ ≤ (768·97²/H)S₁ = S₁/12 | COMPUTED: 768·97²/86,713,344 = 1/12 exactly | **Agree** |
| 15 | N⁴/S₁ | ≤ 4·97²/(H^{2/3}U) | §7 Step 2: S₁ ≥ N⁴M (needs H^{2/3} ≥ 4·97², i.e. H ≥ 8·97³ = 7,301,384) | weaker by the factor H^{2/3}/(4·97²) = 5.21 at his H | **Differ** (ours sharper; effect ×1.034) |
| 16 | Term from 2N⁴ log N | 6·97²/(H^{2/3}U), kept exactly | §7: (3/2)N⁴ log M ≤ S₁, giving 1/L after division | — | **Differ** (ours sharper; negligible) |
| 17 | Bounded terms (log H, log 8, constants) | divided by L directly; no condition on q | §7 Step 3: log H + 3 + (13/12) log 8 < 24 < (24/23)ℓ, needs ℓ > 23 | COMPUTED: 23.5308 < 24; log 10¹⁰ = 23.0259 > 23 | **Differ** (presentation; see (a)) |
| 18 | N and the upper end of λ | N = ⌈q^γ⌉, γ rational and optimized; λ ≤ 4γ/3 + (4/3)log(1+q₀^{−γ})/log q₀ | (7.1): N = ⌈q^ω⌉, ω = 22 integer; log M ≤ (4/3)(ω+1)ℓ | λ ∈ [29.33, 30.67] | **Differ** (choice) |
| 19 | H | free; optimized (LZZ row 2,818,382,931; Platt row 1,995,262,314) | §7: H = 9216·97² = 86,713,344 (the paper's) | 86,713,344 | **Differ** (choice; the largest single effect, see (c)) |
| 20 | Margin | exact solve: δ₀ = (1 − T)/(C_δ λ_hi) | §7 Step 4: 3/16 = 1 − 13/16; ℓ-terms forced ≤ 3/32 by ω = ⌈8(C₂ + 8/5)⌉; remaining 3/32 for δ | COMPUTED: ω_real = 21.7634, so ω = 22; 3(C₂+8/5)/(4·22) = 0.092742 ≤ 3/32 | **Differ** (presentation; ×1.024) |
| 21 | Side conditions | H ≥ 319; N ≥ H; H^{2/3}N^{4/3} ≥ 2·97²; U ≥ 3; σ ≤ 2; κ < 0; q ≠ 8. **No condition H ≤ q.** Platt row: H = 1,995,262,314 > q₀ = 4·10⁵ + 1 | Lemma 2.1: X ≥ 8, λ ≤ 2, H ≥ 319; Lemma 4.2: 1 ≤ H ≤ N and H^{2/3}N^{4/3} ≥ 2·97²; §7 Step 1: **319 ≤ H ≤ q ≤ N**; q ≥ q₀ ≥ H ≥ 9, so d ≠ 2; M ≥ 8 | — | **Agree, except that our rows drop Banks's H ≤ q.** INFERRED: Banks uses H ≤ q only to get N ≥ H, which Corollary 3.5 and Lemma 4.2 need. Our γ secures N ≥ H directly (SC3: γ log q₀ > log H; COMPUTED for the Platt row: 259.27 > 21.41). H ≤ q is not needed anywhere else. In our accounting, the primes dividing q are bounded by c_q ℓ with no reference to H. In Banks's device, the primes p > H dividing q contribute 0 when H > q. X ≥ 8 versus U ≥ 3 is immaterial, since U ≥ q₀^{4γ/3}. The Platt row's side conditions, rechecked with this noted, are all OK (results/2026-10-20-paper-prep-3/banks-v2-platt-side-conditions.txt) |
| 22 | Small q | Platt 2016 (no real zero, q ≤ 4·10⁵) or LZZ Thm 1.1 (δ > 1/5, q ≤ 10¹⁰) | Thm 1.1 proof: LZZ Thm 1.1; Remark "Effectivity": a computation "that we have not verified" | — | **Agree** (LZZ). Platt not used by Banks |
| 23 | Result, q ≥ 10¹⁰ | δ₀ > 4.4673780338·10⁻³ (γ = 153/10, H = 2,818,382,931) | Thm 1.1, Remark "Effectivity": δ₀ = 81/(5888e^{3/2}) | COMPUTED: 3.0695555319·10⁻³ | **Differ** (both valid; explained in (c)) |
| 24 | Result, q > 4·10⁵ | δ₀ > 3.3992904026·10⁻³ | not given (his §7 needs ℓ > 23 and H ≤ q) | COMPUTED: Banks's inequalities with H ≤ q and integer ω relaxed, solved exactly: 3.9979·10⁻³ | see (a) |
| 25 | Lemma 3 (interpolation) | Lean `Lemma3.interpolation`, hypotheses = paper (3.1) | Prop. 3.4 with (3.1) | identical hypotheses and conclusion | **Agree** (docs/packet-related-work-draft.md) |

## (a) The Platt case: q₀ = 4·10⁵ + 1, where log q₀ = 12.899 < 23

COMPUTED (output, "Platt case"):
- In our row, L ≥ (4/3)γ log q₀ = 345.70 (γ = 201/10).
- The bounded terms sit in t₃ = (C_H + (1+ρ_H) log 8)/L = 0.0669. Here C_H contains log H = 21.414, 1/(2 log H) + 1/(2L), (e/2)κ = −0.753 and ln2/2.
- The other terms: t₁ = 0.7527, t₂ = 0.0565, t₄ = 6.9·10⁻⁵, total T = 0.87618, giving δ₀ > 3.3992904026·10⁻³.

INFERRED: why the q > 23 condition doesn't bind us.
- We divide the bounded terms by L, which is large because N = ⌈q^γ⌉, whatever the size of log q.
- Banks instead turns them into a multiple of ℓ, (24/23)ℓ, so that one integer ω makes every ℓ-sized term at most (3/32) log M. That conversion is the only place log q > 23 is used.
- STATED (Banks, Remark 7.2(vii)): the condition q ≥ q₀ has three uses:
  1. absorbing the bounded terms log H + 3 + (13/12) log 8 into a multiple of ℓ;
  2. q ≥ 9, hence d ≠ 2;
  3. N ≥ H.

  INFERRED: log q > 23 serves only the first. The second is q ≠ 8, which we handle separately (Platt or LZZ cover q = 8). The third our γ secures.
- Our only condition linking q₀ and H is N ≥ H, i.e. γ log q₀ > log H: 259.3 > 21.41.

COMPUTED: Banks's inequalities with H ≤ q and integer ω relaxed.
- Banks's inequalities (shift 3/2, his primes-dividing-q bound, his S₁, θ and λ_hi bounds), with his conditions H ≤ q and integer ω relaxed and the result solved exactly at q₀ = 4·10⁵ + 1 with γ and H free, gives δ₀ = 3.99789·10⁻³ (γ = 114/5, H = 2,238,721,138), with H ≥ 8·97³ enforced.
- That run has H = 2,238,721,138 > q₀ and a non-integer γ, so it is not "his accounting" as published.
- INFERRED: what it shows is that, once H ≤ q and integer ω are relaxed, log q > 23 is a feature of his presentation, not a requirement of the inequalities themselves.

## (b) Parameters

| | Banks (§7) | Ours, LZZ row (note.md) | Ours, Platt row |
|---|---|---|---|
| Shift in σ | λ = 3/2 | 1 | 1 |
| Exponent of N | ω = 22 (integer, ⌈8(C₂+8/5)⌉) | γ = 153/10 | γ = 201/10 |
| Our λ = L/log q | [29.33, 30.67] (his (7.1)) | [20.4, 20.4 + η], η < 10⁻¹⁵⁴ | [26.8, 26.8 + η], η < 10⁻¹¹³ |
| H | 86,713,344 | 2,818,382,931 | 1,995,262,314 |
| ρ_H | 1/12 | 0.002564 | 0.003622 |
| Split of the margin | 13/16 main, 3/32 to ℓ-terms, 3/32 to δ | none: T = 0.87614, the rest 0.12386 to δ | T = 0.87618 |
| q₀ | 10¹⁰ | 10¹⁰ + 1 | 4·10⁵ + 1 |
| δ₀ | 3.0696·10⁻³ | 4.4674·10⁻³ | 3.3993·10⁻³ |

(ρ_H values: 7,226,112/H. T values: COMPUTED, output rows B8 and "Platt case".)

## (c) What accounts for 4.467·10⁻³ against 3.0696·10⁻³

COMPUTED, waterfall at q₀ = 10¹⁰. Each step keeps the previous switches, γ is re-optimized at each step, and H is the paper's until the last step (output, "Part C").

| Step | Change | δ₀ | Factor |
|---|---|---|---|
| B0 | Banks as published (3/32 split, ℓ > 23 absorption) | 3.0696·10⁻³ | — |
| B1 | his Step 3 inequality solved exactly | 3.1432·10⁻³ | ×1.024 |
| B2 | tight upper end of λ (N ≤ q^γ + 1, not q^{ω+1}) | 3.2880·10⁻³ | ×1.046 |
| B3 | our S₁, S₂ bounds (row 15–16) | 3.4333·10⁻³ | ×1.044 |
| B4 | Platt–Trudgian θ (row 10) | 3.4445·10⁻³ | ×1.003 |
| B5 | κ and the Mertens terms kept (rows 4, 9) | 3.5168·10⁻³ | ×1.021 |
| B6 | shift 1 (ours) instead of 3/2 (row 5) | 3.0945·10⁻³ | ×0.880 |
| B7 | our primes-dividing-q bound (rows 7–8) | 2.6523·10⁻³ | ×0.857 |
| B8 | H free (row 19): γ = 153/10, H = 2,818,382,931 | 4.4674·10⁻³ | ×1.684 |

B7 equals our own value at the paper's H (note.md §4: 2.652·10⁻³), and B8 is our LZZ row. Both are cross-checks on the switch implementation.

One switch at a time, from our LZZ row back to Banks's choice, with γ and H re-optimized (COMPUTED):

| Reverted to Banks | δ₀ | Ratio to ours |
|---|---|---|
| H fixed at 86,713,344 | 2.6523·10⁻³ | 0.594 |
| upper end of λ from ω + 1 | 4.1976·10⁻³ | 0.940 |
| S₁ ≥ N⁴M and 1/L for the last term | 4.3207·10⁻³ | 0.967 |
| κ and Mertens terms dropped | 4.4123·10⁻³ | 0.988 |
| θ constant 2 | 4.4660·10⁻³ | 0.9997 |
| shift 3/2 | 5.2308·10⁻³ | 1.171 |
| primes dividing q as Banks | 5.1812·10⁻³ | 1.160 |

Answer to (c):
- **Free H is the main reason**, worth a factor of about 1.68 (0.594 one at a time).
- Next come the tight upper end of λ (about 1.05), our S₁ bounds (about 1.04), the exact solve instead of his 3/32 split (1.024), and κ (about 1.02, together with the Mertens terms kept).
- **C_ℓ = ½ + e/4 plays no part.** Our best rows use c_q = ln2/(2ℓ) + 1/3, not ½. In both forms our primes-dividing-q bound is weaker than Banks's ½S₀ device and costs us about 14%.
- **Our shift 1 also costs us**, about 12% against his 3/2.

## Not in note.md (COMPUTED; not reviewed; note.md is unchanged)

Our accounting with Banks's primes-dividing-q device and the shift optimized (step 1/20, λ ≤ 2) gives:
- **Platt row, q₀ = 4·10⁵ + 1:** δ₀ > 4.5799298821·10⁻³ (shift 31/20, γ = 103/5, H = 1,995,262,314);
- **LZZ row, q₀ = 10¹⁰ + 1:** δ₀ > 5.9439667682·10⁻³ (shift 29/20, γ = 77/5, H = 2,660,725,059).

These rest on Banks's (2.6)–(2.8) for the primes dividing q, which I checked by reading, not by computation. I'd want a second reader before they replace anything in note.md.
