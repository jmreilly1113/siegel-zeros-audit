# Reproducing these checks

Written for an independent reviewer. All commands run from the project root. Expected outputs are in `results/`, and every claim in `docs/writeup.md` names the file it comes from.

## 0. Environment
- Python 3.10 or later; tested on 3.14.6.
- `bash scripts/setup.sh` creates `.venv`, clones openai/math at commit adc7f1241b42e322a6451854ab7e4b4c146bf78a into `external/openai-math`, and runs the tests. It works on Linux and on Windows under Git Bash.
- On Windows, git may convert line endings in the clone. Extract anything you want to hash with `git -c core.autocrlf=false archive`.
- `python -m pytest tests -q` should report 8 passed.

## 1. Computations (Python, exact or Arb)

| What | Command | Time (12-core laptop) | Expected output |
|---|---|---|---|
| Lemma 7, N = 3 (Fraction reference) | `python src/batch_lemma7.py OUT.jsonl 3 2,3,4,6 5,13,17,-3,-7,-11,3,7,-1,-5,6,10,-2,-6 --procs 11` | ~6 min | results/2026-10-07-lemma7-N3-H2346.jsonl |
| Lemma 7, N = 2–5 (flint) | `python src/batch_lemma7.py OUT.jsonl N H-list d-list --procs K --flint [--regdet]` | N = 4: ~4 min/run; N = 5: ~20 min/run | results/2026-10-08-lemma7-N*-flint.jsonl |
| Cross-check two methods | `python src/compare_runs.py REF.jsonl OTHER.jsonl` | seconds | results/2026-10-08-compare-N3/N4-*.txt |
| Consolidated counts | `python src/summarize_all.py FILES...` | seconds | results/2026-10-08-lemma7-N2-N4-consolidated.txt, -N5-consolidated.txt |
| Bounds (5.1), (5.6), Lemma 6 | `python src/bounds_table.py FILES...` | seconds | results/2026-10-08-bounds-N2-N4.txt, -N5.txt |
| Interpolation boxes | `python src/interpolation_boxes.py 3 d-list 12` then `python src/summarize_boxes.py` | ~5 min | results/2026-10-08-interpolation-boxes-N*-summary.txt |
| Lemma 6 at N = 5–7 (EXPLORATORY) | `python src/selection_modp.py N 1,...,N d-list` | ~30 min | results/2026-10-08-selection-modp-N567-EXPLORATORY*.{jsonl,txt} |
| Prime-bias sums (EXPLORATORY) | `python src/prime_bias.py --dmax 100000 --procs 3 --date YYYY-MM-DD` | ~12 min | results/2026-10-08-prime-bias-* |
| Explicit c (conditional) | `python src/explicit_c.py` | < 1 s | docs/explicit-constant.md §4 |
| Classical-input spot checks | `python src/check_classical_inputs.py 10000000` | ~1 min | results/2026-10-08-classical-inputs-EXPLORATORY.txt |

Output files are opened in exclusive mode and never overwritten. Choose a new name for every rerun.

## 2. Lean (done here on 2026-10-08: accepted by the Lean kernel and nanoda; rerouted proof accepted 2026-10-09, Option A2)

### Option A: the official comparator (Linux only; recommended)
From `external/openai-math/lean/` on a Linux machine with about 30 GB free:
1. Install `comparator`, `landrun` and `lean4export` (see github.com/leanprover/comparator) and put them on PATH.
2. Run:
   ```
   lake update            # clones 43 packages and applies lean/patches/*.patch
   lake exe cache get
   lake env comparator ComparatorChallenges/SiegelZeros.json
   ```
3. Expect both theorems in `SiegelZeros.json` to be accepted, using only the axioms propext, Classical.choice and Quot.sound.
4. The README warns that a full build may need a larger `vm.max_map_count`.

What we actually ran (WSL2 Ubuntu-24.04 on Windows; scripts in `wsl-comparator/`, numbered in run order):
- Tools: landrun 0.1.18; lean4export tag v4.34.0 and comparator tag v4.34.0 (d03acab), both built with toolchain v4.34.1. The comparator links lean4export and reads .olean files, so it must match the project's Lean; comparator `main` (v4.35.0-rc4) does not work. Script `05_build_tools.sh`.
- An unprivileged user `checker` with lingering enabled, and a fresh clone (`06_user_clone.sh`, `07_lake_update.sh`).
- Run under `systemd-run --user --wait --pipe --collect`, with `--property="RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET"`. This extends the README's AF_UNIX block to all network sockets. It matters on kernels below 6.7, where Landlock cannot restrict network access; WSL's 5.15 kernel has Landlock ABI 1. `28_netblock_probe.sh` shows that the block works.
- Second kernel: nanoda_lib at 3a24072 (v0.4.19), `cargo build --release --locked`, `nanoda_bin` on PATH. Then use a copy of `SiegelZeros.json` with `"enable_nanoda": true` (`26_nanoda_build.sh`, `29_comparator_nanoda.sh`).
- Expected output ends with "nanoda kernel accepts the solution", "Lean default kernel accepts the solution", "Your solution is okay!". Our times: about 26 min for the first run, including the solution build; 14 min for the rerun with nanoda.

Lessons from this machine (docs/log.md, 2026-10-08):
- Do not enable sparse VHD (`wsl --manage --set-sparse`) on WSL 2.4.x, and do not run `fstrim` on it. It corrupted ext4.
- Do not `wsl --shutdown` right after large writes. Run `sync` and wait first.
- After any crash, scan for zero-filled .olean files (`18_olean_scan.sh`) and delete the build outputs the interrupted run wrote (`19_crash_dirty.sh`, `20_clean_crash_debris.sh`) before rerunning.
- Do not redirect the outer script's output and the systemd service's output into the same file on /mnt/c. The two writers overwrite each other's lines. Record versions in a separate step.

### Option A2: the rerouted proof under the official comparator (done here on 2026-10-09: accepted)
This reruns the check that the challenge theorem `dirichletRealZeroBound_proof` passes the comparator when OAI's Corollary 4 is replaced by our proof of the paper's Lemma 3 (`docs/writeup.md` 2.10 (c)). It needs the same tools as Option A, including `nanoda_bin`. Results: `results/2026-10-09-lean-comparator-rerouted-nanoda.txt`, `-rerouted-comparator-diff.txt`, `-rerouted-comparator-feasibility.txt`, `-lean-rerouted-comparator-deps.txt`.

1. **Fresh clone.** Same steps as Option A, in a separate directory so that an existing clone stays untouched. Our script is `wsl-comparator/45_rerouted_clone.sh`; it runs as `checker` and writes `/home/checker/math-rerouted`.
   ```
   git clone https://github.com/openai/math math-rerouted
   cd math-rerouted && git checkout adc7f1241b42e322a6451854ab7e4b4c146bf78a
   cd lean
   lake update            # applies lean/patches/*.patch
   lake exe cache get
   git -C .. status --short   # expect no output
   ```
   On our run: 42 packages, Mathlib cache 8908 files, no modified files after the update.

2. **The two added files.** Generate them from this project with `python -I wsl-comparator/46_make_comparator_copy.py <project root>`. That writes `lean-checks/comparator-copy/PaperLemma3/`:
   - `Lemma3.lean`: `lean-checks/Lemma3.lean` through `end Lemma3`, without the trailing `#print`/`#check` lines. Imports only Mathlib. Sha256 `1ce196f54fa98689bbea6bd74f2abdb110f5cbcca2eecddcca9316b8af465283`.
   - `Bridge.lean`: lines 989-1265 of `lean-checks/Lemma3Bridged.lean` (Corollary 4 from Lemma 3, and the bridge), under a new header. Imports Mathlib, `OAI.NumberTheory.SiegelZeros.PaperLemma3.Lemma3` and `OAI.NumberTheory.SiegelZeros.Structure.InvariantJetLinearMap`. No `#find_deps`, `#print`, `#check` or `#reroute`. Sha256 `af401514808dde5bb913ce8e87cc5280b704a234ea324897d1a1ced1f218f250`.

   The hashes are of the files with LF line endings, which is what the script writes. The repository's `.gitattributes` (`*.lean text eol=lf`, `*.sh text eol=lf`) makes every checkout give LF, whatever the local `core.autocrlf` setting, so a fresh clone of this project reproduces these hashes. Three older files, `lean-checks/Lemma3.lean`, `Lemma3Bridged.lean` and `Lemma3Skeleton.lean`, were CRLF on this machine when their hashes were recorded in the 2026-10-08 results. A checkout gives their LF form, which has a different hash. `results/2026-10-09-lean-checks-line-endings.txt` lists both hashes for each, and shows that the files differ only in line endings.

   Copy both into the clone as `lean/OAI/NumberTheory/SiegelZeros/PaperLemma3/Lemma3.lean` and `.../Bridge.lean`. The lakefile's `OAI.NumberTheory.+` glob picks them up; no lakefile change is needed.

   Optional read-only check first: `wsl-comparator/44_feasibility.sh` (runs `43_bridge_import_closure.py`). It confirms that the import closure of these files (10,702 modules, 41 of them OAI) contains none of the four modules of the rerouted chain and not `OAI.NumberTheory.SiegelZeros.Main`. Expected last line: `CHECK PASSED`.

3. **The one-term diff.** Edit `lean/OAI/NumberTheory/SiegelZeros/Characters/CharacterGlobalGreedyDeterminantMasterBounds.lean`, the only file in the chain that uses Corollary 4. Change nothing else. `wsl-comparator/47_rerouted_install.sh` does steps 2 and 3, and checks both lines before editing. Expected `git diff`:
   ```
   @@ -4,6 +4,7 @@ import OAI.NumberTheory.SiegelZeros.Characters.CharacterGlobalGreedyDeterminantF
    import OAI.NumberTheory.SiegelZeros.Determinants.NormalizedMasterBound
    import OAI.NumberTheory.SiegelZeros.Selection.GlobalRectanglePivotBounds
    import OAI.NumberTheory.SiegelZeros.Structure.InvariantJetLinearMap
   +import OAI.NumberTheory.SiegelZeros.PaperLemma3.Bridge

    namespace OAI

   @@ -135,7 +136,7 @@ theorem source_character_global_greedy_determinant_master_bounds :
        apply n.injective
        funext i
        exact Fin.ext (congrFun h i)
   -  have hspan := actual_biquadratic_rectangle_span a' b' v hv σ τ
   +  have hspan := Lemma3.actual_biquadratic_rectangle_span_via_lemma3 a' b' v hv σ τ
        hσa hσb hτa hτb H N hH hHN (fun j i => (n j i : ℕ)) hninj
        (fun j i => (n j i).isLt)
   ```
   This printed diff is for reading only. It is indented, and the blank context lines have lost their leading space, so `git apply` rejects a copy of it as a corrupt patch. The authoritative patch is in `results/2026-10-09-rerouted-comparator-diff.txt`, from the `diff --git` line up to, not including, the `== check` line. Extract it with `sed -n '/^diff --git/,/^== check/p' results/2026-10-09-rerouted-comparator-diff.txt | sed '$d' > rerouted.patch`. From the clone's root, `git apply rerouted.patch` then makes this exact change; we checked it with `git apply --check` against the file at adc7f12. Script 47 makes the same change without a patch file.

   `git diff --numstat` must show exactly one file with 2 added lines and 1 removed. `git status --short` shows that file as modified and `lean/OAI/NumberTheory/SiegelZeros/PaperLemma3/` as untracked, nothing else. The challenge file `ComparatorChallenges/SiegelZeros.lean` is not touched.

4. **Run the comparator** with `wsl-comparator/48_comparator_rerouted_nanoda.sh`. It is `29_comparator_nanoda.sh` pointed at the new clone:
   - the same sandbox (`systemd-run --user`, all network sockets blocked);
   - the same config copy `wsl-comparator/SiegelZeros-nanoda.json`, which differs from the repo's `SiegelZeros.json` only in `"enable_nanoda": true`;
   - the same solution module, `OAI.NumberTheory.SiegelZeros.Main`.

   By hand, from the clone's `lean/` directory: `lake env comparator <path to SiegelZeros-nanoda.json>`. Expected output:
   - `Build completed successfully (9244 jobs).` The job list includes `OAI.NumberTheory.SiegelZeros.PaperLemma3.Lemma3`, `...PaperLemma3.Bridge` and `...Characters.CharacterGlobalGreedyDeterminantMasterBounds`. Lemma3 shows only linter warnings: unused simp arguments, and one deprecated `if_neg`.
   - Then `nanoda kernel accepts the solution`, `Lean default kernel accepts the solution` and `Your solution is okay!`, with exit code 0.
   - The only `sorry` warnings are the two in `ComparatorChallenges/SiegelZeros.lean` itself (lines 8 and 19), the challenge stubs.
   - Our time: 24 min for the full build and both kernels.

5. **Optional dependency scan:** `wsl-comparator/49_rerouted_deps.sh` (`lean-checks/ReroutedDeps.lean`, run with `lake env lean` in the rerouted clone and in an unmodified clone). Expected:
   - **Rerouted clone:** `dirichletRealZeroBound_proof` matches only `Lemma3.actual_biquadratic_rectangle_span_via_lemma3` and `Lemma3.interpolation`.
   - **Unmodified clone:** it matches OAI's `actual_biquadratic_rectangle_span`, `uniform_rectangular_multiplicity` and `source_rectangle_span_of_polynomial_zero_test`.
   - **Both clones:** `exists_absolute_real_zero_gap` has no match. All theorems use only propext, Classical.choice and Quot.sound.

Our scripts hard-code `/home/checker/...` and `/mnt/c/Users/Work/dev/siegel/...`. Adjust the paths on another machine. The Option A lessons apply here too, in particular `sync` before any `wsl --shutdown`.

### Option B: trimmed build (what we used; works on Windows)
`lean-build/` holds byte-identical copies of the 306 files of `OAI/NumberTheory/SiegelZeros/`, the challenge file, and the 12 files the PNT patch creates. Its lakefile requires only Mathlib at d13f23b. Rebuild it from scratch as described in `docs/log.md` (2026-10-08, step 1 setup), then:
```
cd lean-build
export PATH="$HOME/.elan/bin:$PATH"
lake update                                   # Mathlib + cache, ~7.5 GB
LEAN_NUM_THREADS=1 bash build_with_watchdog.sh  # each Lean process transiently costs ~0.9 GB of disk on Windows
lake env lean Check/SiegelCheck.lean          # verbatim challenge statements + #print axioms
lake env leanchecker OAI.NumberTheory.SiegelZeros.Main   # independent kernel replay (syntax unconfirmed; see `leanchecker --help`)
```
Expected: every `#print axioms` lists only `propext`, `Classical.choice` and `Quot.sound`, and `leanchecker` reports no errors.

Option B differs from the comparator in two ways:
- It does not sandbox the build.
- It does not compare the challenge and solution environments through `lean4export`. Instead, `Check/SiegelCheck.lean` re-elaborates the challenge statements against the solution.
