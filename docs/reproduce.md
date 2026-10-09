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

## 2. Lean (done here on 2026-10-08: accepted by the Lean kernel and nanoda)

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
