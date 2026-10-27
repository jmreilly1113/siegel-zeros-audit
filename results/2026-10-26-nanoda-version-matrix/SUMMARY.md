# nanoda version matrix, 2026-10-26 (UNOFFICIAL)

**UNOFFICIAL.** The official tables are unchanged: `results/2026-10-20-corpus-summary-final.tsv` for the 189 referenced configs, and the extended replay's nanoda 3a24072 outcomes for the 227. This folder adds unofficial runs of three more nanoda builds on retained or regenerated exports. Binaries, sources and settings are in `MANIFEST.txt`. The matrix is in `matrix.tsv`, one row per config with the source of every cell.

**Tags:**
- **COMPUTED:** our runs.
- **STATED:** quoted from nealmcb's issue text or files, cited by URL at a pinned commit, or from ammkrn's comments.
- **INFERRED:** our reading. These are flagged as such.

## Commands

All run as root in WSL Ubuntu-24.04. Each nanoda run is direct (not through comparator), as checker, network-blocked, 1800 s timeout, 16G cap on RAM plus swap, one at a time, under 69_corpus_guard.sh.

    bash wsl-comparator/141_matrix_build.sh results/2026-10-26-nanoda-version-matrix/build.log     # B2, B3
    bash wsl-comparator/142_matrix_batch.sh <dir>/plan-stage1.tsv "B1 B2 B3"                      # 6 retained exports
    bash wsl-comparator/144_matrix_chain.sh                                                       # stage 2 (Laughlin), stage 3 (KFP, GRD): 143 export + 142
    python -I scripts/nanoda_matrix.py . results/2026-10-26-nanoda-version-matrix                 # matrix.tsv
    python -I scripts/extended_final_table.py . results/2026-10-26-nanoda-version-matrix/extended-replay-227

Per-run logs are in `runs/<config>.<B>.log`, each ending in an `OUTCOME:` line. The batch log is `run.log`, and `outcomes-raw.tsv` has one line per run. Export logs are in `exports/`.

## Verification before running (COMPUTED)

- **The six retained extended-replay exports:** size and sha256 equal the values logged twice in each config's records (`-f67473b-direct.log` and `.mem.json`/`.result.json`). They were re-hashed before every run (`runs/*.log`, "export:" line).
- **Regenerated exports** (comparator d03acab's target list, lean4export 076e8e5, openai/math fd4aeeb clean):
  - KaplanskyFinitelyPresented: 657,348,158 bytes, sha256 7b923557…f398c.
  - GroupRingDeterminant: 698,227,515 bytes, sha256 bda46ad6…77e5.
  - Both are byte-identical to the 2026-10-20 exports (results/2026-10-20-nanoda-discrepancy/SUMMARY.txt).
  - Laughlin: 433,770,627 bytes, sha256 842b632a…8523. No earlier value of ours was logged.
- **Export sizes against Neal's 416-config sweep** (STATED, results/nanoda-ab-let.jsonl at 1ca7ff2):
  - Equal byte count for all 9 configs run here.
  - Also for MatchingFPRAS (485,099,446) and ContingencyTables (492,768,597), whose extended-replay exports we logged (runs/<C>.result.json).
  - His records carry no export hash. Their `sha256` field differs between the base and patched runs of the same export, so it hashes something else, probably the binary.

## The matrix (COMPUTED unless marked; every cell's source is in matrix.tsv)

| config | set | 3a24072 16 MiB (official, via comparator) | B1: 3a24072 1 GiB | f67473b 16 MiB | B2: 37cb87b 16 MiB | B3: 37cb87b + patch, 64 MiB |
|---|---|---|---|---|---|---|
| KaplanskyFinitelyPresented | 189 | overflow | pass 44 s, 1.3 GB (and 2026-10-20 R3) | pass (comparator) | overflow 44 s | pass 42 s, 1.3 GB |
| GroupRingDeterminant | 189 | overflow | pass 49 s, 1.3 GB (and R3) | pass (comparator) | overflow 50 s | pass 47 s, 1.3 GB |
| KaplanskyDirectFiniteness | 227 | overflow | pass 43 s, 1.3 GB | pass 37 s, 1.3 GB | overflow 41 s | pass 42 s, 1.3 GB |
| Laughlin | 189 | overflow | OOM at 16G, 198 s | pass (comparator) | pass 877 s, 2.1 GB | pass 945 s, 2.1 GB |
| LaughlinPlanar | 227 | overflow | OOM at 16G, 202 s | pass 941 s, 1.9 GB | pass 966 s, 1.9 GB | pass 926 s, 1.9 GB |
| LaughlinFock | 227 | overflow | OOM at 16G, 453 s | pass 1,372 s, 8.7 GB | pass 1,364 s, 8.6 GB | pass 1,547 s, 8.7 GB |
| DirectedFeedback | 227 | overflow | OOM at 16G, 138 s | pass 59 s, 1.0 GB | pass 48 s, 1.0 GB | pass 48 s, 1.0 GB |
| MinUncut | 227 | overflow | OOM at 16G, 121 s | pass 56 s, 1.0 GB | pass 54 s, 1.0 GB | pass 51 s, 1.0 GB |
| SquareDifference | 227 | overflow | OOM at 16G, 106 s | **overflow** (`thread_2`), 98 s, 4.16 GB | overflow 97 s, 3.5 GB | pass 31 s, 0.66 GB |
| OptimalMaxCut, UniqueGamesTheorem, VertexCover, BinPackingGap, IndependentSets, PerfectCompleteness | 189 | overflow | STATED: fail at 1 GiB (#55) | pass (comparator) | not run; INFERRED pass (STATED pass on 8199c74) | not run (STATED pass on 8199c74 + patch at 16 MiB) |
| ContinuumCoulombHardness | 227 | not run (deferred) | STATED: error (#55) | STATED: pass 130 s, ~24 GiB (#61) | STATED: overflow (#61) | STATED: pass 50 s, 1.8 GB |
| LogspaceEquality | 189 | ACCEPT (comparator) | | STATED: pass 19 s | STATED: overflow (three-stack-failures.md; rc 134 on 8199c74) | STATED: pass 21 s, 1.7 GB |
| RandomizedMeanPayoff | 189 | ACCEPT (comparator) | | | STATED: one of the ten master failures (#61); rc 134 on 8199c74 | STATED: pass (with patch at 16 MiB) |

**Notes on the table:**
- "overflow" in the official column is a checker-thread stack overflow, which comparator reports as "nanoda kernel rejected the solution".
  - COMPUTED: the message in each of the six extended logs (`runs/<C>-nanoda.log`) is "thread 'thread_N' has overflowed its stack".
  - For the nine 189 configs, the message is in the 2026-10-11/12 corpus logs (results/2026-10-20-paper-prep-3/corpus-189.tsv).
- "OOM at 16G" means the run reached the 16G cap (RAM plus swap) and was killed by the kernel's OOM killer (oom_kill 1 in the unit's cgroup). This is a resource outcome, not a verdict on the proof. Max RSS was 16.7 GB in each case.
- No run gave a genuine rejection (a kernel error message). No export hash failed to match. Every outcome matched the expectations in the brief.

**Neal's 416-config sweep is on 8199c74, not 37cb87b.** The "416 configurations (on 8199c74)" sweep of #61's 2026-10-25 comment is in `nanoda-ab-let.jsonl`.
- Its base is nanoda_lib master 8199c74 (2026-10-23), nine commits before 37cb87b. Its patched build is 8199c74 with the let fix and the Nat.succ guard, at 16 MiB (`tools/cloud_nanoda_let_sweep.sh` header).
- Only the ten master failures were rerun on 37cb87b (`nanoda-stack-size-2026-10-25.txt`).
- So the 37cb87b cells for the six skipped RoundTables configs are INFERRED, not STATED.
- LogspaceEquality and RandomizedMeanPayoff are among the ten master failures, so they are not "none of these".

## Three failure classes

### Class 1: recursion in 3a24072 that a bigger stack does not cure; fixed by f67473b

**Configs:** the RoundTables group (OptimalMaxCut, UniqueGamesTheorem, VertexCover, BinPackingGap, IndependentSets, PerfectCompleteness, DirectedFeedback, MinUncut) and the Laughlin group (Laughlin, LaughlinPlanar, LaughlinFock).

**Evidence:**
- **COMPUTED:**
  - All 11 overflow stock 3a24072 at 16 MiB.
  - The five we ran on B1 (DirectedFeedback, MinUncut, Laughlin, LaughlinPlanar, LaughlinFock) do not pass at 1 GiB. Each grows to the 16G cap in 2–8 min.
  - All 11 pass on f67473b at 16 MiB, through comparator for the 189 or directly for the 227.
  - All five we ran also pass on B2 and B3.
- **STATED (#55, https://github.com/ammkrn/nanoda_lib/issues/55):**
  - DirectedFeedback and UniqueGamesTheorem overflow at 1 GiB.
  - UniqueGamesTheorem with a 16 GiB stack ran 1,874 s to 285 GiB, then panicked with a 31-bit index error.
  - The Laughlin group reached 127–175 GiB.
  - A gdb backtrace of `RoundTables.sizeFactor_positive` (a DirectedFeedback declaration) shows `whnf` and `try_reduce_nat` alternating 58,000 times each.
  - nealmcb (#55, 2026-10-16): f67473b passes 14 of his 15.

**What is measured and what is inferred:**
- The recursion pattern is measured only for RoundTables (Neal's backtrace).
- INFERRED: the other RoundTables configs carry generated copies of the same code (#55), so they share it.
- INFERRED: the Laughlin group is placed here by behaviour only. No backtrace was taken (#55 says so), but it shows the same symptoms: it fails at 1 GiB with memory growth, and f67473b fixes it.
- "Does not terminate" is itself INFERRED, by Neal and by us. More stack only gives deeper recursion and more memory.

### Class 2: deep but finite Nat recursion

f67473b reduced the depth. nanoda_lib PR #58 deepened it again ("remove vestigial has_fvars check", 6239144). The stack needed grows with the size of the literal.

**Configs:** KaplanskyFinitelyPresented, GroupRingDeterminant, KaplanskyDirectFiniteness, measured here. STATED only: LogspaceEquality, MatchingFPRAS, ContingencyTables, RandomizedMeanPayoff and PeriodicGroup.

**Evidence:**
- **COMPUTED, for the three Kaplansky/GroupRing configs:**
  - They overflow 3a24072 at 16 MiB and pass it at 1 GiB, so the recursion is deep but finite.
  - They pass f67473b at 16 MiB.
  - They overflow 37cb87b at 16 MiB and pass B3 at 64 MiB.
- **COMPUTED, for MatchingFPRAS, ContingencyTables, LogspaceEquality and RandomizedMeanPayoff:** the pinned 3a24072 at 16 MiB accepts them through comparator. MatchingFPRAS and ContingencyTables come from the extended replay's result.json, the other two from the 189 table.
- **STATED:**
  - Master fails on these at 16 MiB, and a deeper stack fixes it (three-stack-failures.md and nanoda-stack-size-2026-10-25.txt at 1ca7ff2).
  - The chain is a `Nat.add`/`Nat.mul` structural-recursion unfolding on a literal, with free variables in every level. "The chain is as long as the literal": MatchingFPRAS has literal 98,008, nesting between 65,536 and 131,071.
  - LogspaceEquality overflows at 32 MiB and passes at 64 MiB with the let fix.
  - Lean Kernel Arena builds nanoda with 256 MiB (#61, 2026-10-25).

**What is measured and what is inferred:**
- The literal-size mechanism is measured by Neal for those three only.
- INFERRED: KaplanskyFinitelyPresented, GroupRingDeterminant and KaplanskyDirectFiniteness are placed here by their stack response (16 MiB fails, 64 MiB and 1 GiB pass, f67473b passes, master fails). No term was inspected.
- Not measured here: the minimum stack for any config.

**ContinuumCoulombHardness, flagged (STATED only; not run here):**
- On 3a24072 it fails with a 1 GiB stack (#55), which looks like class 1.
- On master it overflows even at 256 MiB with the let fix alone, and passes only with the Nat.succ guard (nanoda-stack-size-2026-10-25.txt).
- f67473b accepts it in 130 s at about 24 GiB (#61).
- INFERRED: it may sit in both classes: class 1 on 3a24072, and the free-variable `Nat.succ` chain on master that the guard skips.

### Class 3: the `let` bug that SquareDifference triggers

**Configs:** SquareDifference.

**Evidence:**
- **COMPUTED:**
  - It overflows 3a24072 at 16 MiB, and on B1 (1 GiB) it grows to the 16G cap in 106 s, not an overflow.
  - f67473b fails with a `thread_2` stack overflow after 98 s at 4.16 GB, the only one of the six extended crashes that f67473b does not fix.
  - 37cb87b at 16 MiB overflows after 97 s at 3.5 GB. At the default stack, on both f67473b and master, this is an overflow, not unbounded growth.
  - B3 passes in 31 s at 0.66 GB.
- **STATED:**
  - On f67473b the backtrace is `def_eq` and `lazy_delta_step` (85,249 and 12,178 frames). A 64 MiB stack overflows after 43 s, and 256 MiB and 1 GiB were killed at a 40 GiB memory limit (#55, nealmcb 2026-10-16).
  - ammkrn (#55, 2026-10-20, https://github.com/ammkrn/nanoda_lib/issues/55#issuecomment-6293428329): "I think this is due to the absence of an additional alpha equivalence check present in the C++ version and which I was hoping to omit."
  - On master 998e0a8 one declaration, `source_ordered_contraction`, still fails. The default stack overflows after 37 s at 3.1 GiB. An 8 GiB stack was still running at 34 min, 96 GB and growing (#62, https://github.com/ammkrn/nanoda_lib/issues/62, open).
  - With the let fix alone, 37cb87b at 16 MiB passes in 16.9 s at 0.65 GB. Without it, master "fails ... at any stack" (nanoda-stack-size-2026-10-25.txt).

**What is measured and what is inferred:**
- INFERRED: our B3 includes both the let fix and the Nat.succ guard, so our runs do not separate them. Attributing the pass to the let fix rests on Neal's let-only run.
- ammkrn's alpha-equivalence explanation and Neal's let explanation are not reconciled by anything run here.

## Catalan and KMedianThreshold (deferred in the extended replay for memory)

- **STATED:** #55 names both as 3a24072 failures. Catalan hit the 31-bit panic after 2,014 s at 259 GiB. KMedianThreshold "exits with an error".
- **STATED:** Neal's sweep on 8199c74 (`nanoda-ab-let.jsonl`, 8 threads, 60G cap) has both accepted by stock 8199c74.
  - Catalan: rc 0, 265 s, 7.3 GiB.
  - KMedianThreshold: rc 0, 13 s, 1.1 GiB.
- **INFERRED:** our memory stops on these two may reflect the 3a24072 bug rather than the size of the proofs. Catalan's nanoda reached 19.6 GB and was still rising; KMedianThreshold's reached 19.84 GB and was still growing.
- Their deferred status is unchanged. They have not been run here on a later nanoda.
- MUBSix, CycleCliqueRamsey and UniversalTensorSquares are different: their stops came before nanoda ran (comparator or build memory).

## Not done

- **Not run:** B2 and B3 on the six skipped RoundTables configs, LogspaceEquality and RandomizedMeanPayoff (your instruction). Their exports are not on disk.
- **Not built:** ContinuumCoulombHardness (optional step 5, pending your go-ahead).
- **Not isolated:** we did not run the let fix without the guard, or the guard without the let fix.

## Update 2026-10-26 (appended; earlier text unchanged): network block

Each nanoda run here executed directly (not through comparator) as the unprivileged user checker (setpriv, no_new_privs) in a systemd-run system unit, and each export was made in a systemd-run user unit; both used the seccomp filter (RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET) denied creating IPv4, IPv6, Unix-domain, netlink and packet sockets. A test on 2026-10-26 confirmed that TCP and UDP over IPv4 and IPv6, and DNS lookups, failed inside such a unit. AF_VSOCK sockets, which reach the Windows host, were not denied, and a test connection to the host succeeded. We did not test whether vsock offers a route to the internet. The earlier wording 'all network sockets blocked' overstated the restriction.

Test and inventory: results/2026-10-26-network-check/ (README.md, inventory.md).

## Update 2026-10-26 evening (appended): step 5, run under the full address-family deny list

**Setup.**
- From 16:52 every build, export and nanoda run used the d scripts: 146_step5_chain.sh, with 143d for exports (4 threads, into /home/checker/corpus/xr/exp-d) and 142d/140d for runs.
- Their seccomp deny list names all 45 address families of kernel 5.15.167.4 (results/2026-10-26-network-check/README.md; t25/t26 pass).
- Order: KMedianThreshold, Catalan, ContinuumCoulombHardness. Each export was checked against our logged sha256 where one exists and against nealmcb's byte count, then run on B3, B2 and B1.
- matrix-v2.tsv (`python -I scripts/nanoda_matrix.py . results/2026-10-26-nanoda-version-matrix matrix-v2.tsv`) adds these rows. matrix.tsv is unchanged.

**COMPUTED:**

| config | export (bytes, sha256) | checks | B3: 37cb87b + patch, 64 MiB | B2: 37cb87b, 16 MiB | B1: 3a24072, 1 GiB |
|---|---|---|---|---|---|
| KMedianThreshold | 620,096,646, 4bec532c… | equals the extended replay's logged sha256 (runs/KMedianThreshold-nanoda.mem.json) and nealmcb's size | pass, 26 s, 1.07 GB | pass, 25 s, 1.06 GB | OOM at the 16G cap, 206 s |
| Catalan | 832,532,249, 6cfe74f4… | equals the extended replay's logged sha256 (runs/Catalan-nanoda.mem.json) and nealmcb's size | pass, 551 s, 4.61 GB | pass, 545 s, 5.01 GB | OOM at the 16G cap, 201 s |
| ContinuumCoulombHardness | none | build stopped by the guard: "2026-10-26 19:32:36 LIMIT: disk 84G, MemAvailable 1448MB", after 3,868 s at 4 threads (exports/ContinuumCoulombHardness.export.log) | not run | not run | not run |

- **The chain stopped at the first build OOM, as instructed.** The guard's MemAvailable floor (1,500 MB) was reached during ContinuumCoulombHardness's build, with four lean processes at 3.8–7.4 GB each at 19:23. No olean for its solution module was written. The clone is clean.
- **INFERRED, now measured for these two:** both kernels-as-built that include the post-3a24072 reduction changes check KMedianThreshold and Catalan quickly and in a few GB.
  - On 3a24072 (official, 16 MiB, through comparator) the extended replay stopped them at 19.84 GB and 19.6 GB, still growing. B1 (3a24072 with a 1 GiB stack) grows to the 16G cap.
  - So their "not checked (memory)" status reflects nanoda 3a24072's class 1 behaviour (#55), not the size of the proofs.
  - They are class 1 by this behaviour; no backtrace was taken.
- **In the 227 table** (extended-replay-227/corpus-227-v2.tsv and summary-227-v2.txt, from `python -I scripts/extended_final_table.py . results/2026-10-26-nanoda-version-matrix/extended-replay-227 --unofficial=results/2026-10-26-nanoda-version-matrix --suffix=-v2`):
  - KMedianThreshold and Catalan move from "deferred (memory)" to "run here, unofficial tool set B3", with the measured peaks above.
  - Their official outcome stays NOT_CHECKED_HERE. The official tool set is nanoda 3a24072 at 16 MiB through comparator, and that run did not finish.
  - The B3 run is a different nanoda build, run directly on the export. Lean's kernel was not run on these configs here.
  - Their Lean-kernel acceptance is STATED only, by nealmcb's comparator sweep at identical pins.
  - The v1 files are unchanged.

## Update 2026-10-26 night (appended): Lean's kernel on Catalan and KMedianThreshold; ContinuumCoulombHardness retry

**Method.** wsl-comparator/147_lean_and_cch.sh ran the shipped-config comparator (enable_nanoda false), the comparator's own Lean-only check:
- It does its own build and its own export (with comparator's target list), then the Lean replay, then the statement and axiom checks.
- It ran through the new runner wsl-comparator/67d_corpus_run_capped.sh. That is 67_corpus_run.sh's command and logging, run in a system unit with the 45-family deny list and a 16G cgroup cap (RAM plus swap), dropping to checker with setpriv. It was stub-tested first: uid, the Lean toolchain, landrun, the network block, the OOM kill and the timeout.
- Timeout 7,200 s, as for the extended replay's shipped runs.
- Comparator cannot replay an outside export, so this run checks its own export, which was not hashed here. INFERRED: it is identical to ours, because lean4export output was reproducible under both properties (t26, Laughlin byte for byte) and comparator's target list is the one 143d uses.

**COMPUTED:**

| config | Lean kernel (shipped-config comparator) | wall | largest process RSS | unit cgroup peak |
|---|---|---|---|---|
| KMedianThreshold | "Lean default kernel accepts the solution", "Your solution is okay!", exit 0 (runs/KMedianThreshold.lean-shipped.log) | 369 s | 7,225,560 kB | 10.04 GB |
| Catalan | the same three lines (runs/Catalan.lean-shipped.log) | 2,234 s | 6,740,376 kB | 4.33 GB |

- For Catalan the cgroup peak is below the largest RSS. This is because mapped .olean pages already in the page cache were charged to the earlier build unit. So the 16G cap bounds what this unit was charged, not every page it touched.
- STATED, for comparison: nealmcb's Catalan comparator check took 2,246 s at 6–7 GiB on a laptop (#55).
- **Result: both kernels accepted KMedianThreshold and Catalan here.** Lean's kernel ran through comparator under the new sandbox; nanoda was B3 (and B2), run directly on our exports. Their official outcome (nanoda 3a24072 through comparator) stays NOT_CHECKED_HERE.
- **ContinuumCoulombHardness, one retry at LEAN_NUM_THREADS=2:** the guard stopped the build after 164 s ("2026-10-26 20:40:30 LIMIT: disk 84G, MemAvailable 309MB").
  - The 4-thread attempt had stopped at 19:32:36 (MemAvailable 1448MB) after 3,868 s.
  - INFERRED: a module in its closure needs more memory than this 20 GB VM leaves.
  - It is now permanently deferred here, with no further retry. Its Lean-kernel and nanoda results are STATED only, from nealmcb (#61; nanoda-stack-size-2026-10-25.txt).
- The guard was restarted after each stop. The markers are kept as /home/checker/corpus/GUARD_STOPPED-20261026-1932 and -2040.
- **New tables:** matrix-v3.tsv (adds a "status here" column) and extended-replay-227/corpus-227-v3.tsv and summary-227-v3.txt.
  - Catalan and KMedianThreshold read "both kernels accepted here; nanoda from unofficial tool set B3". ContinuumCoulombHardness reads "DEFERRED (permanent)".
  - The v2 files are unchanged. Per CLAUDE.md, results files are not overwritten, so v3 supersedes v2.
