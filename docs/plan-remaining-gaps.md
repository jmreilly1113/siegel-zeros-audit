# Plan: closing the gaps left after the comparator run (drafted 2026-10-08)

After the official comparator accepted the Lean proof (results/2026-10-08-lean-comparator-wsl.txt), four limits remain. This plan takes them in order of value per effort. Each step names what result would count, and in which category (computed / inferred) it belongs.

## Step 0. Prerequisite: check the hardware (Joe, ~30 min, one reboot)

The 12:05 crash was bugcheck 0x1A/0x3F, a failed check on a page read back from the pagefile. Steps 1 and 3 put similar load on the machine.
- Run Windows Memory Diagnostic (`mdsched.exe`, "Restart now"). Result appears in Event Viewer > System, source MemoryDiagnostics-Results.
- Run `chkdsk C: /scan` (online, read-only) for the disk side.
- If either reports errors, do steps 1-2 on a different machine (option 1b) and treat this machine's results as needing a rerun elsewhere. No current result depends on a single unrepeated run, except the comparator verdict itself.

## Step 1. Second, independent kernel: nanoda (gap 1). Effort: half a day, mostly machine time

Why: the comparator replayed the proof in Lean's own kernel only (`enable_nanoda: false`). nanoda is a separately written type checker (Rust). If both accept, a bug in one kernel would have to be matched by a bug in the other.

1a. In WSL (this machine):
- Install Rust (rustup, as root), clone github.com/ammkrn/nanoda_lib, pin a commit whose export format matches lean4export v4.34.0 (check its README and the comparator v4.34.0 tests), `cargo build --release`, put `nanoda_bin` on PATH.
- Write our own config `wsl-comparator/SiegelZeros-nanoda.json`, a copy of the repo's config with `enable_nanoda: true`. The repo copy stays untouched (rule 7 in spirit).
- Run the comparator exactly as in 08_comparator.sh with the new config. Watch the memory: nanoda loads the whole export (Mathlib closure). Cap with `--threads` if needed.
- Pass criterion: comparator reports both the Lean kernel and nanoda accepting, exit 0. Save as results/<date>-lean-comparator-nanoda.txt.

1b. Alternative: a fresh cloud Linux VM (needs Joe's account, about 16 GB RAM, 40 GB disk). This also covers step 2 (newer kernel) and gives independent hardware. Recommended if step 0 finds a fault.

Risk: version mismatch between nanoda and the lean4export format. If no nanoda commit reads it, record that and stop. Do not patch nanoda.

## Step 2. Full sandbox (gap 2). Effort: ~1 hour plus one comparator run (combine with step 1)

Why: on the WSL 5.15 kernel, Landlock is ABI 1. The sandbox makes the filesystem read-only but does not block network or IPC. Threat model: the build runs code from the solution, and an unconfined network could fetch or leak data. It cannot alter files outside the sandbox, so this is a hardening step, not a known hole.

- Option 2a (recommended): `wsl --update` to a WSL release with kernel 6.6 (Landlock ABI 5 or higher, which covers TCP restriction). Before any `wsl --shutdown`: `sync` and wait for writes to finish (lesson from attempt 1). Re-measure the ABI with check_landlock.sh.
- Option 2b: keep the kernel and run the comparator with networking off (`networkingMode=none` in .wslconfig, or `systemd-run -p PrivateNetwork=yes` if the user manager allows it). This needs everything already fetched, which it is after `lake update`.
- Pass criterion: same verdict, with the ABI (or network-off method) recorded in the results file. Do the nanoda run (step 1) in this same session so one run covers both gaps.

## Step 3. Lemma 3 (gap 3). The paper's own proof is not formalized

Context: the Lean proof replaces Lemma 3 with a different argument, so the machine-checked theorem does not depend on the paper's proof. This gap matters for the paper as a human proof, and for reviewers who want the short argument to be right.

3a. Written step-by-step audit (my work, ~half a day; category: inference). Expand the proof (lines 269-407 of refs/siegel-paper.tex) into numbered steps and state the fact each step uses: Carathéodory in a face of dimension at most 3, the nearest-point inequality, vertices of a face being vertices of P (so they lie in S), rational independence giving r·c ≠ 0, and the degree count for B = Q·R(z + A(m−u)). Flag anything that needs a sentence the paper omits. A quick first pass found no gap; this makes it checkable by a reader.

3b. Executable proof (my work, 1-2 days; category: computed, at small N only). Implement the proof's construction literally, with exact arithmetic over K = Q(√d, √2) as in src/. For N = 2 (and N = 3 if it is fast enough), with t_j from (3.1), take many random nonzero dual vectors v and build R, m, y, h, G, u, Q, B as in the proof. Then check exactly each intermediate claim: (3.3) on K ∩ Z^4, h ≠ 0, y/4 ∈ G, (3.5) u ∈ S ∩ G with y − u ∈ 3P, (3.7) vanishing off the face, Q's delta property, B ∈ P_t, and finally Σ v_n B(An) = v_u R(Am) ≠ 0. Include degenerate supports (S inside a line, a plane, a single point) where faces are low-dimensional. This tests the logic of the proof, not just its conclusion, which we already tested via ranks. Per rule 5, it confirms the steps at N = 2, 3 only.

3c. Formalize Lemma 3 in Lean against Mathlib (large: one to three weeks of iteration, heavy builds). Mathlib has the pieces: convex hulls, Carathéodory, exposed faces, nearest points in closed convex sets, Lagrange interpolation, and dimension counts for polynomial spaces. Value: a machine check of the paper's own argument. Recommendation: do 3a and 3b first, and decide on 3c with Joe afterwards. It does not change the status of the main theorem.

3d. Optional: comparator run on the rerouted proof (not started; needs Joe's go-ahead, since it is a Lean job). Done so far: `lean-checks/MainRerouted.lean` builds the rerouted proof with a metaprogram (`#reroute`, via `addDecl`), checked by Lean's kernel and a standalone nanoda run but not by the comparator (writeup 2.10 (c)). Plan: a solution module that imports only the OAI modules below the rerouted chain, plus the route-1 module (`exists_absolute_real_zero_gap`) unchanged, and our Lemma 3 module. It then defines the four copied theorems and `dirichletRealZeroBound_proof` as ordinary source text. Then run the official comparator with nanoda enabled.

Feasibility listing (read-only, 2026-10-09, from the `import` lines and declarations of external/openai-math/lean at adc7f12; script in the session scratchpad, not a results file):
- The rerouted chain is 4 modules, each with exactly one top-level declaration, 340 lines in total:
  - `Characters/CharacterGlobalGreedyDeterminantMasterBounds.lean`: `source_character_global_greedy_determinant_master_bounds`, the only use of Corollary 4, at line 138, as a plain term `actual_biquadratic_rectangle_span a' b' v hv σ τ`.
  - `EntireFunctions/RealZeroUniformMasterBound.lean`: `source_real_zero_uniform_master_bound`.
  - `Characters/DirichletRealZeroBound.lean`: `dirichlet_real_zero_bound`.
  - `Characters/DirichletRealZeroBoundProof.lean`: `WeightedTorusJets.dirichletRealZeroBound_proof` (the challenge theorem).
- What the chain imports from outside itself: Mathlib, `PrimeNumberTheoremAnd.SiegelZeros.HadamardSupport`, and seven OAI modules (`Characters.CharacterGlobalGreedyDeterminantFullLocalBounds`, `Determinants.NormalizedMasterBound`, `Selection.GlobalRectanglePivotBounds`, `Selection.GlobalWeightSortedJetEquiv`, `Structure.InvariantJetLinearMap`, `Structure.NotEventuallyMaster`, `Structure.QuadraticEigencharacter`). None of their import closures contains a chain module.
- Route 1, `Conclusions/Theorem.lean` (`exists_absolute_real_zero_gap`): its closure of 201 OAI modules contains no chain module.
- `Structure/InvariantJetLinearMap.lean`, which holds Corollary 4 and `source_same_witness_hyperplane` (both used by our bridge): its closure of 41 OAI modules contains no chain module.
- So importing everything the solution needs without pulling in the chain looks possible. `OAI.NumberTheory.SiegelZeros.Main` must not be imported, because it imports `DirichletRealZeroBoundProof`.
- Changes this needs on our side:
  1. Our Lemma 3 module currently imports `Main`. A comparator copy would import only `InvariantJetLinearMap` (still to confirm that every OAI name the bridge uses is defined at or below it). It would also drop the `#find_deps` command and the `#print`/`#check` lines.
  2. The simplest way to write the four theorems as source text is to copy the 340 lines verbatim with the one name changed at line 138. `#reroute`'s output (exactly these 4 theorems, no types changed) confirms that this is the whole chain.
  3. The two challenge names, plus the comparator config's solution module and permitted axioms, as in the original run (docs/reproduce.md).

## Step 4. What the check still trusts (gap 4), and expert reading

4a. Non-vacuity checks in Lean (my work, ~half a day, in WSL where Mathlib is cached; category: computed). A formal statement can be technically true but empty if its hypotheses never hold. Prove small Lean lemmas: (i) a primitive real character of conductor 3 (and of 4, 5, 8) exists and meets every hypothesis of the challenge statement; (ii) for real s > 1, `LFunction χ s` equals Σ χ(n) n^(-s); (iii) the challenge theorem, applied to the character from (i), gives the expected concrete conclusion. This guards against a mismatch in reading Mathlib's definitions, which we checked by reading (docs/log.md step 2) but not by proof.

4b. Reviewer packet (my work, ~2 hours). One folder or page with writeup.md, explicit-constant.md, lean-paper-map.md, the Lemma 3 audit from 3a, and the list of results files. Three kinds of reader cover different parts:
- an analytic number theorist: Lemma 2, the uniformity of constants in (2.1), (2.2), (5.7), and Section 6;
- someone who knows interpolation determinants and transcendence methods: Lemma 3 and Sections 3-5;
- a Lean/Mathlib user: whether the challenge statement says what Theorem 1.1 says.

4c. Choosing and contacting reviewers (Joe). I do not send anything outward.

## Suggested order

0 (Joe), then 1 + 2 together (one session), 3a, 3b, 4a, 4b, then a decision on 3c. Machine-heavy steps (1, 2, 4a, 3c) only after step 0 is clean.
