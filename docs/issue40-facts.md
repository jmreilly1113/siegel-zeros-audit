# Facts sheet for a public comment on grwtsk/openai-math issue #40

Prepared 2026-10-09. Each line gives a value and the file it comes from. Paths are relative to this repository. "Computed" lines come from `results/` or `lean-checks/`. Lines marked **inference** are readings, not computations. Where a results file does not record its own command, the command is cited from `docs/log.md`.

## Versions and inputs

- Pinned commit: openai/math `adc7f1241b42e322a6451854ab7e4b4c146bf78a`. Source: `results/2026-10-08-lean-comparator-wsl.txt`, line "openai/math commit".
- Lean toolchain: `leanprover/lean4:v4.34.1` (Lean 4.34.1, commit 5045d0056413266e57c625dcd7c365b10e377c52). Source: `results/2026-10-08-lean-comparator-wsl.txt`.
- Mathlib revision: `d13f23b723b8a846827a245b89c10fc7d3f11612`. Source: `results/2026-10-08-lean-axioms.txt`, line 3.
- Comparator: tag v4.34.0 (d03acab), built with toolchain v4.34.1; binary sha256 prefix `afa65e57a1770f59`. Sources: `results/2026-10-08-lean-comparator-wsl.txt` (tag); `results/2026-10-09-lean-comparator-rerouted-nanoda.txt` (binary hash).
- lean4export: tag v4.34.0, built with v4.34.1. Source: `results/2026-10-08-lean-comparator-wsl.txt`.
- landrun: 0.1.18. Source: `results/2026-10-08-lean-comparator-wsl.txt`.
- nanoda: nanoda_lib commit 3a2407216ee84a75f9e1aead6803d0578be06ae7 (version 0.4.19), `nanoda_bin` sha256 `897971d7e99f1ac2ce3d43131d291a63858badf41cab409f70b99dbd04e0b714`. Source: `results/2026-10-08-lean-comparator-nanoda-netblock.txt`.

## Configuration and challenge file

- The only config change: `"enable_nanoda": false` became `"enable_nanoda": true` in our copy of `ComparatorChallenges/SiegelZeros.json`. The diff shows line 14 only. Sources: `results/2026-10-08-lean-comparator-nanoda-netblock.txt` (config diff); `results/2026-10-09-lean-comparator-rerouted-nanoda.txt` (same diff).
- Permitted axioms in the config: propext, Classical.choice, Quot.sound. Source: `results/2026-10-08-lean-comparator-wsl.txt` (JSON printed in full).
- The challenge file was not modified.
  - sha256 of `ComparatorChallenges/SiegelZeros.lean` is `bedaac0248a641910f79a380d9702d82c6bfbbfd3760a69d27c72c5d8fb136ce` in the original run (`results/2026-10-08-lean-comparator-wsl.txt`) and in the rerouted run (`results/2026-10-09-lean-comparator-rerouted-nanoda.txt`).
  - Its git blob at HEAD is `8bab3f83ef57af55c5826318b6c92df84117395f` (`results/2026-10-09-lean-comparator-rerouted-nanoda.txt`).
  - In the rerouted clone, `git status` lists only the edited chain file and the new `PaperLemma3/` directory (`results/2026-10-09-rerouted-comparator-diff.txt`).
- Sandbox: `systemd-run --user` with `RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET`, as user `checker`. Source: `results/2026-10-08-lean-comparator-nanoda-netblock.txt` (with the network-block probe); `results/2026-10-09-lean-comparator-rerouted-nanoda.txt`.

## Comparator: OAI's original proof, with nanoda

- Output lines: "nanoda kernel accepts the solution", "Lean default kernel accepts the solution", "Your solution is okay!", "COMPARATOR EXIT CODE: 0". Source: `results/2026-10-08-lean-comparator-nanoda-netblock.txt`, lines 43, 45, 46, 47.
- Axioms (`#print axioms`): `exists_absolute_real_zero_gap` and `dirichletRealZeroBound_proof` each depend on [propext, Classical.choice, Quot.sound]. Source: `results/2026-10-08-lean-axioms.txt`. That run used the trimmed Windows build, which has the same 309 source files, verified by git blob hash.
- Earlier run without nanoda: "Lean default kernel accepts the solution", "Your solution is okay!", exit 0. Source: `results/2026-10-08-lean-comparator-wsl.txt`, lines 44 to 46.

## Comparator: rerouted proof (our Lemma 3 in place of OAI's Corollary 4), with nanoda

- Change to the fresh clone: two new modules plus one import line and one term in `CharacterGlobalGreedyDeterminantMasterBounds.lean`. `git diff --numstat` gives `2	1	lean/OAI/NumberTheory/SiegelZeros/Characters/CharacterGlobalGreedyDeterminantMasterBounds.lean`. Source: `results/2026-10-09-rerouted-comparator-diff.txt`.
- New modules and sha256 (LF):
  - `PaperLemma3/Lemma3.lean`: `1ce196f54fa98689bbea6bd74f2abdb110f5cbcca2eecddcca9316b8af465283`
  - `PaperLemma3/Bridge.lean`: `af401514808dde5bb913ce8e87cc5280b704a234ea324897d1a1ced1f218f250`

  Source: `results/2026-10-09-rerouted-comparator-diff.txt`; the files are in `lean-checks/comparator-copy/PaperLemma3/`.
- Output lines: "Build completed successfully (9244 jobs).", "nanoda kernel accepts the solution", "Lean default kernel accepts the solution", "Your solution is okay!", "COMPARATOR EXIT CODE: 0". Source: `results/2026-10-09-lean-comparator-rerouted-nanoda.txt`, lines 50 and 53 to 60.
- Axioms in the rerouted clone: both challenge theorems depend on [propext, Classical.choice, Quot.sound]. Source: `results/2026-10-09-lean-rerouted-comparator-deps.txt`.

## Dependency scan (which proof uses OAI's Corollary 4 and its multiplicity estimate)

All results in this section come from one source, `results/2026-10-09-lean-rerouted-comparator-deps.txt` (scan file `lean-checks/ReroutedDeps.lean`). It is a transitive closure over types and values.

- **Rerouted clone:** `dirichletRealZeroBound_proof` has 92,658 constants. Its only matches are `Lemma3.actual_biquadratic_rectangle_span_via_lemma3` and `Lemma3.interpolation`, and it has no match for `actual_biquadratic_rectangle_span`, `uniform_rectangular_multiplicity` or `source_rectangle_span_of_polynomial_zero_test`.
- **Unmodified clone (the control):** `dirichletRealZeroBound_proof` has 116,314 constants and matches `actual_biquadratic_rectangle_span`, `Geometry.uniform_rectangular_multiplicity` and `Geometry.source_rectangle_span_of_polynomial_zero_test`.
- **Both clones:** `exists_absolute_real_zero_gap` has 107,760 constants and no match. It never uses OAI's Corollary 4. Also shown by a second method, lean4export closures, in `results/2026-10-08-lean-main-closure-cor4-usage.txt`.

## Lemma3.lean (the paper's Lemma 3, formalized)

- Theorem: `Lemma3.interpolation`. Source: `lean-checks/Lemma3.lean`.
- Axioms: [propext, Classical.choice, Quot.sound]. Source: `results/2026-10-08-lean-lemma3-full.txt`, line 36.
- nanoda standalone, on the closure of `Lemma3.interpolation`, `Lemma3.rectangle` and the bridge theorem:
  - "Checked 61810 declarations with no typechecker errors". The same line reports 1 pretty-printer error, "Unable to print axioms", which the results file explains is from nanoda's print_axioms option and is not a type error.
  - Control with Classical.choice not permitted: rejected.
  - Control with one proof swapped for another: rejected with `assertion failed: self.def_eq(u, v)`.

  Source: `results/2026-10-08-lean-lemma3-nanoda.txt`, lines 6, 26, 35, 46.
- sha256 of `lean-checks/Lemma3.lean`:
  - LF form, which is what a git checkout gives: `ecdbf400b24f9241cd03cf383bdcd97ed71e4812578e66d7159a846447f7b1a7`.
  - CRLF form, the one hashed on 2026-10-08: `77452a4a489981d91d6b4caa207c7c5647f39d2d8b13858ad63791e63672a128`.
  - They differ only in line endings.

  Source: `results/2026-10-09-lean-checks-line-endings.txt`.

## NonVacuity.lean

All lemmas use only [propext, Classical.choice, Quot.sound] (`results/2026-10-08-lean-nonvacuity.txt`, lean exit code 0). The statements are in `lean-checks/NonVacuity.lean`:

- `quadChar_real`: the quadratic character mod a prime p is real-valued.
- `quadChar_ne_one`: for p ≠ 2, it is not the trivial character.
- `quadChar_isPrimitive`: for p ≠ 2, it is primitive.
- `hypotheses_satisfiable`: for every odd prime p, it satisfies every hypothesis of the challenge statement on q and χ.
- `quadChar_LFunction_eq_LSeries`: for Re s > 1, Mathlib's `LFunction` of it equals the Dirichlet series Σ χ(n) n^(-s).
- `quadChar_LFunction_one_ne_zero`: for p ≠ 2, its `LFunction` does not vanish at s = 1.
- `specialization`: the solution theorem, specialized to these characters.

## Exact small-N checks (these confirm the statements at the listed N only)

- Lemma 7 divisibility, v_p(N(Δ)) ≥ 4E_p for admissible p:
  - Runs: 28 at N = 2, 70 at N = 3, 42 at N = 4 and 44 at N = 5, all with 14 fields.
  - Admissible (run, p) pairs: 15, 147, 144 and 204. That is 510 in total, and every one passes.

  Sources: `results/2026-10-08-lemma7-N2-N4-consolidated.txt`, `results/2026-10-08-lemma7-N5-consolidated.txt`. Script `src/lemma7_flint.py`, consolidated by `src/summarize_all.py` (commands in `docs/log.md`).
- Two independent implementations (Fraction reference and python-flint): N = 3, 56 runs compared, 0 disagreements; N = 4, 8 runs compared, 0 disagreements. Sources: `results/2026-10-08-compare-N3-fraction-vs-flint.txt`, `results/2026-10-08-compare-N4-fraction-vs-flint.txt`.
- (5.1) and (5.6), Arb ball arithmetic: 140 runs at N = 2 to 4 and 44 runs at N = 5. "All rigorous checks True: True" in both. Sources: `results/2026-10-08-bounds-N2-N4.txt` (line 146), `results/2026-10-08-bounds-N5.txt` (line 50). Script `src/bounds_table.py` (command in `docs/log.md`).
- Interpolation boxes and the kernel claim after (4.1): at N = 2 and at N = 3, 14 fields each, the kernel claim holds in 14 of 14 and all minimal boxes are certified in 14 of 14. Sources: `results/2026-10-08-interpolation-boxes-N2-summary.txt`, `results/2026-10-08-interpolation-boxes-N3-summary.txt`. Script `src/interpolation_boxes.py` (command in `docs/log.md`).
- The proof of Lemma 3, executed step by step with 28 exact checks per instance:
  - N = 2: 423 instances, 423 pass.
  - N = 3: 71 instances, 71 pass.
  - N = 2 with generic R in 4 dimensions: 46 instances, 46 pass.
  - In total 540 instances, with no failed check.

  Sources: `results/2026-10-08-lemma3-construct-N2-summary.txt`, `-N3-summary.txt`, `-N2-generic4d-summary.txt`. Script `src/lemma3_construct.py` (command on line 1 of `results/2026-10-08-lemma3-construct-N2.txt`).

## Task outcomes from 2026-10-09

- **Upstream drift.** Current openai/math main HEAD is `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`, two commits after `adc7f12`.
  - These paths have identical git tree and blob hashes at both commits: `lean/OAI/NumberTheory/SiegelZeros`, `ComparatorChallenges/SiegelZeros.lean`, `ComparatorChallenges/SiegelZeros.json`, `lean/docs/003.md`, the preprint folder, `lakefile.lean`, `lake-manifest.json`, `lean-toolchain` and `lean/patches`.
  - As a control, the same diff command reports 762 changed files elsewhere under `lean/`.

  Source: `results/2026-10-09-upstream-drift-adc7f12-fd4aeeb.txt`.
- **HadamardSupport.**
  - The module is created by `lean/patches/PrimeNumberTheoremAnd-lean4341.patch` and applied by the lakefile's `post_update` hook during `lake update`. It is one line, `import PrimeNumberTheoremAnd.SiegelZeros.Growth`. The patch creates 11 other `.lean` files and a NOTICE.md under `PrimeNumberTheoremAnd/SiegelZeros/`, and the module is not tracked by the PrimeNumberTheoremAnd checkout at c39a751.
  - It is in the import closures of `DirichletRealZeroBoundProof` and `CharacterGlobalGreedyDeterminantMasterBounds`, in both clones. It is absent from the closure of `Conclusions.Theorem` (`exists_absolute_real_zero_gap`), which contains no PrimeNumberTheoremAnd module.
  - Exploratory text heuristic: all 226 reconstructed public names from the patched files occur in the lean4export dumps of OAI's original analytic route and of the rerouted proof, and none occur in route 1's dump or in our Lemma 3 code's dump.

  Source: `results/2026-10-09-pnt-hadamard-dependency.txt`.

## Labeled inference in the packet (not computation)

- **inference:** the Lean challenge statement says what the paper's Theorem 1.1 says. This rests on reading Mathlib's definitions (`docs/log.md`, step 2), supported by the computed non-vacuity lemmas above.
- **inference:** the Lean statement of `Lemma3.interpolation` matches the paper's Lemma 3 clause by clause (`docs/lemma3-lean-statement-review.md`).
- **inference:** the hand audit of the proof of Lemma 3 found no gap and two routine unstated facts (`docs/lemma3-audit.md`).
- **inference:** Claude's line-by-line reading of Lemmas 2, 3, 6 and 7, Corollary 4, (5.1), (5.6) and (6.2) found no gap. It was not a human expert's reading (`docs/writeup.md` 3.3).
- **inference:** on OAI's route 1, the Bezout/multiplicity argument takes the place of Lemma 3 (`docs/writeup.md` 2.10 (c), from reading OAI's files).
- **inference:** the full challenge statement has a machine-checked proof through the paper's own proof of Lemma 3. This is drawn from the computed comparator and scan results above (`docs/writeup.md` 2.10 (c)).
- **inference:** the explicit constant c ≥ 0.00258 is conditional on the paper, and its bookkeeping needs an expert check (`docs/explicit-constant.md`, status line).
- **inference:** everything in `docs/writeup.md` section 3, "What we infer (not findings)".
- **Exploratory, not exact:** the Lemma 6 data at N = 5 to 7 (`results/2026-10-08-selection-modp-N567-EXPLORATORY-summary.txt`) and the prime-bias tables (`results/2026-10-08-prime-bias-summary.txt`), both labeled exploratory.
