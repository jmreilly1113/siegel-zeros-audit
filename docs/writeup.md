# Computational checks of "Uniform exclusion of Landau–Siegel zeros"

DRAFT, 2026-10-08 (all runs complete). Paper: openai/math, family 003, preprint dated 1 Oct 2026, commit adc7f1241b42e322a6451854ab7e4b4c146bf78a (`refs/siegel-paper.tex`, byte-identical to the repo copy). Equation numbers below are the paper's: (2.1)–(2.2) Lemma 2, (3.1) the box condition of Lemma 3, (4.1) the map A, (4.4) Lemma 6, (5.1) the Archimedean bound, (5.2) the Frobenius relation, (5.3) Lemma 7, (5.6)–(5.7) the divisibility lower bound, (6.2) the master inequality.

This note keeps three things apart: **what the paper states**, **what we computed** (each item points to a file in `results/` and the command that made it), and **what we infer** from that. A computation at small N confirms the stated lemma at that N and for those fields only. Nothing here verifies the theorem.

## 1. What the paper claims, in brief

**Theorem.** There is an absolute c > 0 such that every real zero β in (0, 1) of every primitive nonprincipal real Dirichlet L-function of conductor q ≥ 3 satisfies (1 − β) log q ≥ c.

**Proof outline** (paper's own route; not via the 7/8 half-plane paper):

1. *Prime bias* (Lemma 2, Section 2). Suppose there is a real zero with δ = (1 − β) log q small. Then χ(p) = −1 for almost all primes up to large X, measured by Σ log p / p. The argument is classical.
2. *Interpolation* (Lemma 3, Corollary 4, Section 3). Let A : C⁴ → C³ be linear with a rationally independent kernel. Then monomials in the three coordinates of An, of bounded separate degrees, span all functions on the box {0..N−1}⁴.
3. *Determinant* (Section 4). Work in K = Q(√d, √2) and let θ_n = n₁ + n₂√d + n₃√2 + n₄√(2d). Rows are (θ_n^α₁ σ(θ_n)^α₂ στ(θ_n)^α₃), taken greedily in order of weight α₁ + H(α₂ + α₃) until there are M = N⁴ independent rows. Their determinant Δ is a nonzero element of Z[√d, √2]. Lemma 6 says most of the total exponent sits in α₁: S₂/S₁ ≤ (C₀/c₀)/H.
4. *Two bounds* (Section 5).
   - Upper bound (5.1): Hadamard's inequality gives |N(Δ)| ≲ N^{4(S₁+S₂)} roughly.
   - Lower bound (5.6): if χ(p) = −1 and p > H, then Frobenius at p maps θ to σθ or στθ, and Δ is divisible by p^{E_p} with E_p ≈ S₁/p (Lemma 7). Summing over primes up to U = N^{4/3} gives log|N(Δ)| ≳ 4 S₁ log U.
5. *Contradiction* (Section 6). With N = q^γ, log U = (4/3) log N. A Siegel zero makes nearly all primes up to U qualify. The lower bound S₁ log U then beats the upper bound (S₁ + S₂)(3/4) log U once H is large: 1 ≤ 13/16 + 1/16.

## 2. What we computed

All exact unless marked EXPLORATORY. Environment: Windows 11, Python 3.14.6, python-flint 0.9.0 (details in `docs/log.md`).

### 2.1 Integrity of sources
- `refs/` copies of the paper (PDF and .tex), the Lean comparator statement and the Lean scope page are byte-identical to the repo at the pinned commit. The family-003 catalogue excerpt occurs verbatim in CONTENTS.md. (docs/log.md, 2026-10-07 entry; method: git blob hashes.)

### 2.2 Frobenius relation (5.2)
- θ^p ≡ g_p(θ) mod pR for random θ, primes p ≤ 31, six fields. When χ(p) = +1 the identity also holds with g_p = id if (2/p) = +1, and with g_p = τ if (2/p) = −1. (`tests/test_ring.py`; `python -m pytest tests -q`.)

### 2.3 Lemma 7 (divisibility of Δ) at small N
Δ and N(Δ) were computed exactly for every case below. Lemma 7 states Δ ∈ p^{E_p} Z[√d, √2] for admissible p (p > H, p ∤ 2q, χ(p) = −1). We check that statement directly (all four coordinates of Δ divisible by p^{E_p}), and also the consequence used in the paper, v_p(N(Δ)) ≥ 4E_p.

| N | M | fields | H | runs | admissible (run, p) pairs | Lemma 7 holds | file |
|---|---|---|---|---|---|---|---|
| 2 | 16 | 14 | 1, 2 | 28 | 15 | all 15 | results/2026-10-08-lemma7-N2-H12-flint.jsonl |
| 3 | 81 | 14 | 1, 2, 3, 4*, 6* | 70 | 147 | all 147 | results/2026-10-08-lemma7-N3-H1-flint.jsonl, results/2026-10-08-lemma7-N3-H2346-flint.jsonl |
| 4 | 256 | 14 | 2, 3, 4 | 42 | 144 | all 144 | results/2026-10-08-lemma7-N4-H234-flint.jsonl |
| 5 | 625 | 14 | 2, 3 (14 fields); 4, 5 (8 fields) | 44 | 204 | all 204 | results/2026-10-08-lemma7-N5-H2345-flint.jsonl, results/2026-10-08-lemma7-N5-H23-more-flint.jsonl |

\* H > N is outside the paper's range (it assumes H ≤ N). The proof of Lemma 7 uses only p > H, so these runs still test Lemma 7.

Counts are in `results/2026-10-08-lemma7-N2-N4-consolidated.txt` and `results/2026-10-08-lemma7-N5-consolidated.txt` (command: `python src/summarize_all.py <the jsonl files>`). In total, 184 distinct runs (N = 2 to 5) and 510 admissible (run, p) pairs, with no exception. Fields: d ∈ {5, 13, 17, −3, −7, −11} (d ≡ 1 mod 4), {3, 7, −1, −5} (d ≡ 3 mod 4), {6, 10, −2, −6} (d ≡ 2 mod 4).

- Equality v_p(N(Δ)) = 4E_p occurs often, so at these sizes the lemma's exponent is attained, not just bounded.
- Primes outside the admissible class behave as the proof predicts (N = 3 / 4 / 5):
  - χ(p) = +1, (2/p) = +1: divisibility holds in 18/18, 21/21 and 40/40 cases.
  - χ(p) = +1, (2/p) = −1: it holds in only 11/86, 6/72 and 6/104.
  - χ(p) = −1 but p ≤ H, where the proof does not apply: it holds in 4/19, 8/8 and 14/15.
- **Two independent methods.** The original Fraction implementation (`src/lemma7_check.py`) and the flint implementation (`src/lemma7_flint.py`, a different algorithm) agree on the retained rows, Δ, N(Δ) and every valuation in all 56 N = 3 runs and all 8 N = 4 runs that both computed. A third computation of N(Δ), as the determinant of the 4M × 4M integer regular-representation matrix, agrees in all 140 runs with N ≤ 4. Every row the flint version rejected modulo a prime was certified dependent by an exact solve over K (1,004 rejections at N ≤ 4, 333 at N = 5). At N = 5 there is no second method for N(Δ). The CRT computation there is self-checking: a rigorous Hadamard bound plus 3 extra primes that leave the result unchanged. (`results/2026-10-08-compare-N3-fraction-vs-flint.txt`, `results/2026-10-08-compare-N4-fraction-vs-flint.txt`.)

### 2.4 Greedy selection and the weight bound (Section 4)
- The greedy loop always reached M independent rows.
- Maximum retained weight was 10/14/16/20 at N = 3, H = 2/3/4/6; 16/22/25 at N = 4, H = 2/3/4; and 22/30/35/41 at N = 5, H = 2/3/4/5. The paper's bound 96 H^{2/3} N^{4/3} is 659/864/1047/1372, 965/1265/1532 and 1303/1707/2068/2400. (Same files.)

### 2.5 Interpolation lemma (Lemma 3, Corollary 4) and the claims after (4.1)
- A·(ab, b, −a, −1) = 0 and the minor in the first three columns equals 4ab, exactly, in all 14 fields.
- Minimal full-rank boxes (certified exactly in both directions):

  | N | M | minimal full-rank box | smallest box allowed by (3.1) | Corollary 4 box |
  |---|---|---|---|---|
  | 2 | 16 | 16–20 rows (24 for d = −1) | 1,560 rows | ≈ 530,000 rows |
  | 3 | 81 | 81–100 rows | 15,288 rows | ≈ 2.7 million rows |

  Sources: `results/2026-10-08-interpolation-boxes-N2-summary.txt`, `-N3-summary.txt`; command `python src/interpolation_boxes.py N d-list tmax`.

### 2.6 Bounds (5.1), (5.6) and Lemma 6
- Checked rigorously (Arb) in all 184 runs with N ≤ 5: (5.1) holds, the divisibility bound Σ_{adm} E_p log p ≤ ¼ log|N(Δ)| holds, and the second line of (5.6) is ≤ its first line. (`results/2026-10-08-bounds-N2-N4.txt`, `results/2026-10-08-bounds-N5.txt`; command `python src/bounds_table.py <jsonl files>`.)
- The actual ¼ log|N(Δ)| is 18–30% (N = 2), 23–36% (N = 3), 27–39% (N = 4) and 30–41% (N = 5) of the right side of (5.1).
- Primes dividing 2q (2 and the ramified prime) account for 34–100% of log|N(Δ)|, and admissible primes for 0–29%. The paper's argument does not use the primes dividing 2q.
- Suppose every prime p > H with p ∤ 2q were admissible. The divisibility bound would then give at most 19% (N = 2), 32% (N = 3), 37% (N = 4) and 41% (N = 5) of ¼ log|N(Δ)|. For the paper's contradiction to appear at finite N, this would have to exceed 100%. It rises with N, but small N is far from the asymptotic regime.
- EXPLORATORY, Lemma 6 at larger N. The selection was run modulo two primes; rejections are not certified. (`results/2026-10-08-selection-modp-N567-EXPLORATORY.jsonl`.)
  - N = 5, 6, 7 (72 runs; the two primes agree in all of them). Summary: `results/2026-10-08-selection-modp-N567-EXPLORATORY-summary.txt`.
  - S₁/(M H^{2/3} U) = 0.43–0.455. The paper proves at least c₀ = 1/37636 ≈ 2.7×10⁻⁵.
  - H·S₂/S₁ = 1.58–1.89, rising slowly with N. The paper proves at most C₀/c₀ ≈ 7.2×10⁶.

### 2.7 Prime-bias context (Section 2; descriptive only)
- S₊(D, X) = Σ_{p ≤ X, χ_D(p) = +1} log p / p, for all 60,786 fundamental discriminants |D| ≤ 10⁵ and X = 10⁴, 10⁵, 10⁶. EXPLORATORY float64; the 20 smallest values were rechecked in Arb.
- S₊ − ½ log X has mean −0.86 and sd 0.39.
- The minimum is at D = 6888 = 2³·3·7·41 (S₊ = 4.63 at X = 10⁶). D = −163 ranks 113th.
- Nothing here is near the regime a Siegel zero would force, which is consistent with the known numerical results (Platt; Lu–Zaman–Zhao). (`results/2026-10-08-prime-bias-summary.txt`.)

### 2.8 Lean formalization (accepted by the official comparator and a second kernel; details in `docs/lean-paper-map.md` and `docs/log.md`, step 1)
- **Statement.** The challenge statements match the paper's Theorem 1.1. Mathlib's `LFunction` is the genuine meromorphic continuation (equal to Σ χ(n)n⁻ˢ for Re s > 1). `IsPrimitive` means conductor = q. `(χ a).im = 0` picks out the real characters.
- **What the proof needs.** The import closure is 307 OAI modules (≈ 70,000 lines) plus 12 files that the repo's patch adds to PrimeNumberTheoremAnd. Beyond those it uses only Lean core and Mathlib. It does not use the 7/8 result.
- **Source scan.** No `sorry`, `axiom`, `native_decide`, `unsafe`, `implemented_by`, kernel-skip options, custom syntax or environment manipulation in any of the 318 solution files.
- **Constants.** H = 86,713,344 = 12·C₀/c₀ and N ≥ 18,818 = 2·97², matching the paper.
- **Build and checks: done.** (1) Windows build: all 306 Siegel modules and 12 PNT files compiled, 0 errors, 0 warnings (`results/2026-10-08-lean-build-summary.txt`). (2) `#print axioms`: both challenge theorems depend only on `propext`, `Classical.choice`, `Quot.sound`, the standard axioms (`results/2026-10-08-lean-axioms.txt`). (3) The elaborated challenge and solution types are identical (`results/2026-10-08-lean-type-compare.txt`). (4) **Official Lean FRO comparator** (Linux sandbox in WSL2, unprivileged user, fresh clone): "Lean default kernel accepts the solution / Your solution is okay!", exit 0 (`results/2026-10-08-lean-comparator-wsl.txt`, command `wsl-comparator/08_comparator.sh`). The comparator rebuilt the challenge file from scratch, exported both theorems with their full dependency closure, checked that the statements match, checked the axioms against the permitted list, and replayed every proof in Lean's kernel. (5) **Second, independent kernel.** Rerun with nanoda (a separately written type checker, v0.4.19) added. Our config copy differs from the repo's only in `enable_nanoda: true`. Both "nanoda kernel accepts the solution" and "Lean default kernel accepts the solution", exit 0. The sandbox also blocked all network sockets (IPv4/IPv6/netlink/packet, via seccomp; the block was shown to work beforehand) (`results/2026-10-08-lean-comparator-nanoda-netblock.txt`). (6) **Non-vacuity.** In Lean, for every odd prime p the quadratic character mod p satisfies every hypothesis of the challenge statement (primitive, nontrivial, real, q ≥ 3). For these characters Mathlib's `LFunction` equals Σ χ(n)n⁻ˢ for Re s > 1 and is nonzero at s = 1, and the solution theorem specializes to them. Only the standard axioms are used (`lean-checks/NonVacuity.lean`, `results/2026-10-08-lean-nonvacuity.txt`). So the statement is not true merely because its hypotheses can never hold. It is still a statement about real zeros, none of which is known to exist. Remaining caveats: both kernels read the same lean4export output, so they share that tool; Landlock IPC scoping is unavailable on this WSL kernel (AF_UNIX sockets are blocked, signals are not).
- **Coverage.** Every paper step from Corollary 4 onward has a direct Lean counterpart with the same constants. **The OAI formalization does not contain the paper's own proof of Lemma 3 (convex geometry); we formalized it separately (2.10).** The OAI Lean proves Corollary 4's conclusion by a different algebraic-geometric multiplicity estimate. The two challenge theorems are two largely parallel proofs, not independent ones.

### 2.9 Explicit constant (conditional; `docs/explicit-constant.md`)
- Assume the paper's Lemmas 6 and 7, (5.1) and (5.6), plus six classical explicit inputs (Davenport ch. 12; −ζ′/ζ(s) < 1/(s−1); Rosser–Schoenfeld). Then replacing every O-constant by a number and optimizing N for each q gives a contradiction whenever δ < 3.04 × 10⁻⁴ (all q ≥ 3, q ≠ 8), δ < 2.00 × 10⁻³ (q > 4·10⁵), or δ < 2.59 × 10⁻³ (q > 10¹⁰). Each case is certified in Arb.
- Together with Platt and Lu–Zaman–Zhao for small q, this gives **(1 − β) log q ≥ 0.00258 for all q ≥ 3, conditional on the paper.** The Lean formalization contains only existential constants, not this value.

### 2.10 Lemma 3 proof executed exactly at N = 2, 3 (`src/lemma3_construct.py`; audit in `docs/lemma3-audit.md`)
- **Why.** The Lean proves Corollary 4 by a different route, so the paper's own proof of Lemma 3 (tex lines 252–407) was the one step with no machine check in the OAI formalization. We wrote that proof as a program. Given a support S, a target vector v and a polynomial R that vanishes on the lattice points of K, the program follows the proof's construction step by step: the nearest point m, the face G, the Carathéodory vertices, the vertex u, the Lagrange polynomial Q and B = Q·R(z + A(m − u)). It checks every intermediate claim exactly in `Fraction`s, 28 checks per instance, keyed by the proof's step numbers 2–16. The nearest-point step uses Wolfe's algorithm, and its answer is certified by the nearest-point inequality, so the program does not rely on Wolfe being correct.
- **Two kinds of R.** "Product": R is a product of linear forms vanishing on K. "Generic": R is a random element of the null space of the vanishing conditions. Generic R can also vanish at lattice points outside K, which product R cannot. That is the case where the proof's choice of m matters.
- **Results (computed).**

  | Run | Instances | Passed all 28 checks | dim P reached | File |
  |---|---|---|---|---|
  | N = 2, d ∈ {−7, −3, −1, 3, 5, 13}, both kinds | 423 | 423 | 0–4 | `results/2026-10-08-lemma3-construct-N2-summary.txt` |
  | N = 3, d ∈ {−7, 5}, both kinds; up to \|S\| = 81, 6,561 lattice points in K | 71 | 71 | 0–4 | `results/2026-10-08-lemma3-construct-N3-summary.txt` |
  | N = 2, d ∈ {−7, 5}, generic R on supports up to dimension 4 | 46 | 46 | 0–4 (9 instances at 4) | `results/2026-10-08-lemma3-construct-N2-generic4d-summary.txt` |

  Commands: `python src/lemma3_construct.py --N 2 --d -7 -3 -1 3 5 13 --count 40 --seed 20261008 --json …`; `--N 3 --d -7 5 --count 15 --seed 20261009`; `--N 2 --d -7 5 --count 25 --seed 20261010 --modes generic --max-lattice-generic 160`. Each `.txt` file holds the exact command line. In 18 generic instances R vanished at lattice points outside K that lie closer than m, so that case was exercised. Tests (`tests/test_lemma3.py`) confirm that the checks catch planted errors: a wrong vertex u is caught, and so is a non-minimal m (53 of 80 cases, by checks 11 and 16).
- **Now also machine-checked (2026-10-08).** The paper's proof is formalized in Lean, following the paper's own steps: `lean-checks/Lemma3.lean`, theorem `Lemma3.interpolation`. It compiles with only the three standard axioms (`results/2026-10-08-lean-lemma3-full.txt`; command `wsl-comparator/34_lean_file.sh Lemma3.lean`). The statement was compared with tex lines 252–267 clause by clause (`docs/lemma3-lean-statement-review.md`). **Extras, done the same day.** (a) *Linked to the OAI formalization.* Corollary 4 is derived from this Lemma 3 in Lean, and from it a proof of OAI's own `actual_biquadratic_rectangle_span` (the Corollary 4 statement used by the challenge theorem `dirichletRealZeroBound_proof`; its type is taken literally from OAI's with `type_of%`). A dependency scan shows this proof never touches OAI's multiplicity estimate, while the same scan on OAI's own proof finds it (`lean-checks/Lemma3Bridged.lean`, `results/2026-10-08-lean-lemma3-bridge.txt`). So OAI's Corollary 4 now has two proofs: its own, and the paper's. (b) *Second kernel.* nanoda checked the full dependency closure of the three theorems (61,810 declarations) with no errors. As controls, it rejected the same export when `Classical.choice` was not permitted, and it rejected a copy in which one proof had been swapped for another (`results/2026-10-08-lean-lemma3-nanoda.txt`, command `wsl-comparator/36_nanoda_lemma3.sh`). (c) *Main theorem rebuilt on the paper's route.*
  - *Which challenge theorem uses Corollary 4 (computed, two methods).* The comparator challenge has two theorems, and OAI proves them along two parallel routes. Two independent methods agree on which uses Corollary 4: a Lean dependency scan (`lean-checks/MainDeps.lean`) and lean4export's own dump of each theorem's dependency closure (`wsl-comparator/41_main_closure_export.sh`). Only `dirichletRealZeroBound_proof` uses OAI's Corollary 4 and its multiplicity estimate. `exists_absolute_real_zero_gap`, across 105,474 exported declarations, uses neither (`results/2026-10-08-lean-main-closure-cor4-usage.txt`). The `#reroute` command in `lean-checks/MainRerouted.lean` walks the same closure the same way as the `#find_deps` scan used for `Lemma3Bridged`, and it reports that `exists_absolute_real_zero_gap` does not depend on OAI's Corollary 4 (`results/2026-10-08-lean-main-rerouted.txt`, line 25). So it is not rerouted. Its own top-level step is OAI's `SiegelZerosAwei.W50.uniform_exclusion_of_local_isolated_bezout` (external/openai-math/lean/OAI/NumberTheory/SiegelZeros/Conclusions/Theorem.lean:18), and its closure contains OAI multiplicity lemmas such as `W22.component_multiplicity_sum_bound` (same usage file). That this Bezout/multiplicity argument is what takes the place of Lemma 3 on that route is an inference from reading OAI's files (`docs/lean-paper-map.md`), not a computed fact. Our earlier wording, "the Corollary 4 statement the main theorem uses", was too broad, and is corrected here.
  - *Rerouting (computed).* `lean-checks/MainRerouted.lean` leaves OAI's sources untouched. It takes OAI's compiled proofs, finds every theorem between Corollary 4 and `dirichletRealZeroBound_proof` (4 theorems), and copies each with OAI's Corollary 4 replaced by ours. Lean's kernel rechecks every copy. Nothing else changes: these are OAI's proofs, term for term, with one lemma swapped. The copies are produced by a metaprogram in `MainRerouted.lean` (`#reroute`) that adds declarations with `addDecl`, which is environment manipulation of the kind the comparator guards against; each added declaration is still kernel-checked, `#print axioms` is standard, and the standalone nanoda run on the exported closure, with its two controls, is the independent check against that risk.
  - *How the statement is tied to the challenge (computed).* Both checks below are made by Lean when `MainRerouted.lean` compiles (exit 0 in `results/2026-10-08-lean-main-rerouted.txt`, which records the source sha256).
    - **Primary tie.** `dirichletRealZeroBound_via_lemma3` is declared with type `type_of% @OAI...dirichletRealZeroBound_proof`, so its type is OAI's own statement. The comparator matched that statement to the challenge (2.8, `results/2026-10-08-lean-comparator-wsl.txt`).
    - **Secondary check.** `challenge_dirichletRealZeroBound_proof` restates the challenge text verbatim from `refs/SiegelZeros.lean`, and Lean accepts the rerouted proof for it. `challenge_exists_absolute_real_zero_gap`, the curried form, is derived from it in two lines.
    - **Closed 2026-10-09.** The official comparator has since accepted a source-level version of the same swap (next bullet), which checks the statement against the challenge file directly.
  - *Kernels and axioms (computed).* Lean's kernel checked each of the 4 copied theorems when `addDecl` added it, and checked the final theorems as the file compiled. nanoda checked the export of both challenge-named theorems (93,598 declarations, no errors), run standalone by `wsl-comparator/39_main_rerouted.sh` with the comparator's nanoda settings, not through the comparator. Controls: rejected with Classical.choice not permitted, and rejected with two proofs swapped. `#print axioms` for both theorems gives exactly propext, Classical.choice, Quot.sound. A dependency scan of the rerouted proof finds no use of OAI's Corollary 4 or its multiplicity lemmas; the control scan on OAI's original finds all three. Results: `results/2026-10-08-lean-main-rerouted.txt`.
  - *Inference.* The full challenge statement now has a machine-checked proof that uses the paper's own Lemma 3 proof and not OAI's substitute.
  - *Official comparator on the rerouted proof (computed, 2026-10-09; plan step 3d).* The comparator needs the solution under OAI's theorem names, so the swap was redone at source level in a fresh clone of openai/math at adc7f12 (`wsl-comparator/45_rerouted_clone.sh`, same steps as the original setup).
    - **What changed in the clone.** Two new modules: our Lemma 3 and the bridge, under `OAI/NumberTheory/SiegelZeros/PaperLemma3/`, generated by `wsl-comparator/46_make_comparator_copy.py` with proofs only. In `CharacterGlobalGreedyDeterminantMasterBounds.lean`, one import line was added and the single reference to OAI's Corollary 4 (line 138) was replaced by `Lemma3.actual_biquadratic_rectangle_span_via_lemma3`. No other file changed; `git diff` shows 1 file, 2 lines added, 1 removed (`results/2026-10-09-rerouted-comparator-diff.txt`).
    - **No metaprogram.** This version uses no `#reroute` and no `addDecl`. It is ordinary source compiled by Lake inside the comparator's sandbox.
    - **Import check.** A read-only check beforehand showed that the bridge's import closure (Mathlib plus `InvariantJetLinearMap`, 10,702 modules, 41 of them OAI) contains none of the four chain modules and not `Main` (`results/2026-10-09-rerouted-comparator-feasibility.txt`).
    - **Result.** With the unmodified challenge file, our config copy (only `enable_nanoda: true` changed) and the same sandbox and network block as 2.8, the comparator rebuilt everything (9,244 jobs), and reported "nanoda kernel accepts the solution", "Lean default kernel accepts the solution" and "Your solution is okay!", exit 0 (`results/2026-10-09-lean-comparator-rerouted-nanoda.txt`, command `wsl-comparator/48_comparator_rerouted_nanoda.sh`).
    - **Dependency scan afterwards** (`results/2026-10-09-lean-rerouted-comparator-deps.txt`, command `wsl-comparator/49_rerouted_deps.sh`). In the rerouted clone, the challenge-named `dirichletRealZeroBound_proof` reaches `Lemma3.actual_biquadratic_rectangle_span_via_lemma3` and `Lemma3.interpolation`, and none of OAI's `actual_biquadratic_rectangle_span`, `uniform_rectangular_multiplicity` or `source_rectangle_span_of_polynomial_zero_test`. In the unmodified clone (the control), it reaches all three OAI names. `exists_absolute_real_zero_gap` is the same in both (107,760 constants, no match). All four theorems use exactly propext, Classical.choice, Quot.sound.
    - **Inherited dependency (computed, 2026-10-09).** The rerouted proof inherits OAI's patched PrimeNumberTheoremAnd dependency (HadamardSupport, created by lean/patches/PrimeNumberTheoremAnd-lean4341.patch), so its trust base includes that adapted source, as OAI's original analytic route does; the closure of exists_absolute_real_zero_gap contains no PrimeNumberTheoremAnd module (results/2026-10-09-pnt-hadamard-dependency.txt).
- **What the Python run shows.** The construction works as the proof says, at N = 2 and 3 only, for these fields and these supports. It does not prove Lemma 3 for general N. The hand audit (`docs/lemma3-audit.md`, an inference) found no gap and two routine unstated facts: the vertices of G lie in S, and distinct points of ℋ differ in some coordinate other than i₀.

## 3. What we infer (not findings)

1. **The computable algebra is right at small N.** Every algebraic statement we could compute held exactly in every case: (5.2), Lemma 7 in the stated form, the kernel claim, Corollary 4's conclusion, (5.1) and (5.6). The two independent implementations agree.
2. **Why the argument needs the zero.** Consider each coordinate choice:
   - With all four conjugates as coordinates, every prime satisfies a Frobenius relation, but the image of the box is 4-dimensional. Interpolation then needs degree about N, and the size and divisibility bounds balance with ratio log N / log N = 1.
   - With three of the four coordinates, as in the paper, the degree is about N^{4/3} = U. The gain becomes log U / log N = 4/3. But only primes with Frobenius in {id, σ, στ} qualify, about ¾ of them unconditionally, and ¾ · 4/3 = 1 gives no contradiction.
   - A Siegel zero pushes the qualifying fraction toward 1, and that produces the contradiction.

   Our data matches the "¾ of primes" part: divisibility holds for the χ(p) = +1, (2/p) = +1 class and fails for the χ(p) = +1, (2/p) = −1 class. This explains why the construction is not obviously self-contradictory. It is not evidence that the proof is correct.
3. **Where a reader should look.** Every step we could test numerically held. Claude's line-by-line reading (not a human expert's) of Lemma 2, Lemma 3, Corollary 4, Lemma 6, Lemma 7, (5.1), (5.6) and (6.2) found no gap (an inference, not a verification). So the parts that deserve expert scrutiny are the ones computation cannot reach:
   - the uniformity of the constants C in Lemma 2 and (5.7);
   - the limit argument of Section 6;
   - whether anything in the chain silently depends on q or d beyond what is stated.

   The Lean build, axiom check and official comparator have now passed (2.8), so Lemma 2 and the limit argument move from "unchecked" to "machine-checked" (`docs/lean-paper-map.md`). The paper's own proof of Lemma 3 is now audited by hand, executed exactly at N = 2, 3, and formalized in Lean (2.10). What remains for human readers is expert reading of the analytic parts above and of whether the Lean statement says what the paper says (we found that it does).

   A result of this strength (no Siegel zeros) would be a major advance. Independent expert reading is essential whatever the computations show.
4. **The constants have very large slack at the sizes we can reach** (Sections 2.5 and 2.6 above).
   - A simple model fits the Lemma 6 data. If the greedy selection meets no dependencies before weight W, the retained indices fill the simplex α₁ + H(α₂ + α₃) ≤ W. That predicts S₂/S₁ → 2/H and S₁/(M H^{2/3} U) → 6^{1/3}/4 ≈ 0.454. The data at N ≤ 7 match the second and approach the first.
   - If that holds asymptotically, H > 6 would already make the first term of (6.2) less than 1. The paper takes H ≈ 8.7×10⁷.
   - This does not affect correctness. It does suggest an explicit c could be far better than the proof's constants give.

## 4. What was not checked

- Lemma 2 and the absolute constants in (2.1), (2.2), (5.7). Analytic; not computable here. (Their Lean counterparts are machine-checked, see 2.8 and `docs/lean-paper-map.md`; no human has checked the paper's own proofs of them here.)
- The limiting argument in Section 6 (by hand; its Lean counterpart is machine-checked, 2.8).
- Any N large enough for the asymptotic inequalities to bite. The contradiction needs log U ≫ log q and H ≈ 10⁸; we reach N ≤ 5.
- Lemma 6 at large N, except the exploratory mod-p data in Section 2.6.
- The Lean proof is machine-checked by two independent kernels (2.8). This rests on trusting at least one of the two kernels, lean4export (shared by both), Mathlib's definitions and the standard axioms. The OAI Lean proves Corollary 4 a different way; we formalized the paper's own proof of Lemma 3 separately (2.10). It is checked by both kernels, and it yields a second proof of OAI's Corollary 4 statement. We also rebuilt the challenge theorem `dirichletRealZeroBound_proof` on top of ours, by swapping that one lemma in OAI's proof (2.10 (c)). Both kernels accept it, and so does the official comparator, run on a source-level version of the swap with nanoda enabled (2.10 (c), `results/2026-10-09-lean-comparator-rerouted-nanoda.txt`). OAI's other proof, `exists_absolute_real_zero_gap`, never used Corollary 4, so there was nothing to swap there.
- The explicit constant in 2.9: the bookkeeping and the reference for −ζ′/ζ(s) < 1/(s−1) need an expert check.
- Fields with d = 2 (excluded by the paper; handled there separately).

## 5. Reproduction
`bash scripts/setup.sh`, then the commands listed with each item above (all also in `docs/log.md`). Tests: `python -m pytest tests -q`.
