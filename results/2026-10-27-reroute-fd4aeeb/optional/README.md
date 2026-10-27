# Optional overnight items A and B (Joe, 2026-10-26 ~22:25)

Both items had already been run and saved earlier on 2026-10-26, under the 45-family deny list, the guard and the 16G cap. Nothing was rerun. This file records the check, points to the existing logs, and gives their exit codes.

## A. Lean's kernel on the Catalan and KMedianThreshold exports: ALREADY RUN

**Method.** The comparator's Lean-only check: the shipped config, with `enable_nanoda` false. Comparator does its own build and export, replays in Lean's kernel, and runs its statement and axiom checks.
- **Runner:** wsl-comparator/67d_corpus_run_capped.sh, a system unit with the 45-family deny list, a 16G v1 cgroup cap, and setpriv to checker. Timeout 7,200 s.
- **Driver:** wsl-comparator/147_lean_and_cch.sh.
- **Source:** openai/math fd4aeeb (/home/checker/math, clean).

| config | log (sha256 prefix) | outcome lines | exit | wall | largest process RSS | unit cgroup peak | oom_kill |
|---|---|---|---|---|---|---|---|
| KMedianThreshold | results/2026-10-26-nanoda-version-matrix/runs/KMedianThreshold.lean-shipped.log (cad60883…) | "Lean default kernel accepts the solution", "Your solution is okay!" | COMPARATOR EXIT CODE: 0 | 369 s | 7,225,560 kB | 10,044,485,632 B | 0 |
| Catalan | results/2026-10-26-nanoda-version-matrix/runs/Catalan.lean-shipped.log (6ba78950…) | the same two lines | COMPARATOR EXIT CODE: 0 | 2,234 s | 6,740,376 kB | 4,331,089,920 B | 0 |

- **Run log:** results/2026-10-26-nanoda-version-matrix/run.log, at 2026-10-26 20:00:28 for KMedianThreshold and 20:37:44 for Catalan.
- **Summary:** results/2026-10-26-nanoda-version-matrix/SUMMARY.md ("Update 2026-10-26 night").
- **Caveat:** comparator checks its own export, which was not hashed here. INFERRED: it is identical to ours, as SUMMARY.md explains.

## B. ContinuumCoulombHardness retry at LEAN_NUM_THREADS=2: ALREADY RUN; PERMANENTLY DEFERRED

**Run.** 147_lean_and_cch.sh started the retry at 2026-10-26 20:37:44 (results/2026-10-26-nanoda-version-matrix/run.log:104). It used 143d, 2 threads, with the guard floor unchanged (69_corpus_guard.sh 95 1500 20).

**Outcome:** the build was stopped by the guard. The guard logged "2026-10-26 20:40:30 LIMIT: disk 84G, MemAvailable 309MB; stopping checker build processes" (run.log:105). Details:
- build log: exports/ContinuumCoulombHardness.export.log;
- BUILD_SECONDS 164;
- the 143d export step exited 1 ("build failed or stopped").

**Earlier 4-thread attempt:** stopped at 2026-10-26 19:32:36 (MemAvailable 1448MB) after 3,868 s; its log is exports/ContinuumCoulombHardness.export.stopped-20261026-1932.log.

**Status:** permanently deferred here, per Joe's rule. No export was made, and no nanoda or Lean run was done. The 227 table (corpus-227-v3.tsv) and matrix-v3.tsv already read "DEFERRED (permanent)".

**STATED (nealmcb):**
- f67473b accepts it, at 130 s and about 24 GiB (https://github.com/ammkrn/nanoda_lib/issues/61).
- 37cb87b with the let fix and Nat.succ guard at 64 MiB passes, at 50.0 s and 1.8 GB (https://github.com/nealmcb/openai-math-lean-tooling/blob/1ca7ff2a0280760783ee2b198c0d6f2a1cfeaba4/results/nanoda-stack-size-2026-10-25.txt).
- His comparator run accepts it (results/cmp-all/STATUS.md at the same commit).

**Not retried.** Nothing runs after B.
