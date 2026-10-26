# Corpus replay: final summary, 2026-10-20

Source table: `results/2026-10-20-corpus-summary-final.tsv` (187 rows, one per config)
Command: `python -I wsl-comparator/87_corpus_summary.py . > results/2026-10-20-corpus-summary-final.tsv` (Python 3.14.6; reads results files only)
Replaces the interim snapshot `results/2026-10-13-corpus-summary-interim.md`; that file is kept.

## What was run

- **Scope:** the 189 comparator configs that openai/math's `formalization.yaml` references at fd4aeeb (results/2026-10-11-corpus-mainplan.txt).
  - 187 were replayed at fd4aeeb: a headline batch of 15 and a remainder of 172.
  - The other 2, SiegelZeros and QuasiRiemannHypothesis, ran in the pilot at adc7f12. The pilot also ran EditApproximation, which is not in the 187.
  - The pilot configs were not rerun at fd4aeeb, because none of the modules their proofs import changed between the two commits (mainplan lines 49-51).
- **openai/math commits:**
  - fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb for all 187 configs in the table.
  - adc7f1241b42e322a6451854ab7e4b4c146bf78a for the pilot (SiegelZeros, QuasiRiemannHypothesis, EditApproximation).
- **Tools:**
  - Lean 4.34.1 (5045d005) and Mathlib d13f23b.
  - comparator d03acab and lean4export 076e8e5 (both v4.34.0, built with 4.34.1).
  - landrun 811cfff and nanoda_lib 3a24072 (v0.4.19), the corpus-pinned version.
- **Platform:** WSL2 Ubuntu 24.04 on Windows 11. Each comparator run ran as the unprivileged user `checker` inside a systemd-run unit with all network sockets blocked.
- **Per config:**
  - One comparator run of a copy of the shipped config with `enable_nanoda: true`, so nanoda and Lean's kernel both check the proof.
  - A second run of the shipped config itself, as OpenAI ships it, when the first run was not accepted by both kernels, or when the config was in a seeded random sample of 10 (`results/2026-10-11-corpus-headline/sample.txt`).

## Outcomes (COMPUTED, from the tsv)

| Stage | ACCEPT_BOTH | ACCEPT_LEAN_ONLY | Total |
|---|---|---|---|
| Headline (fd4aeeb) | 12 | 3 | 15 |
| Remainder (fd4aeeb) | 166 | 6 | 172 |
| **All, fd4aeeb** | **178** | **9** | **187** |
| Pilot (adc7f12, results/2026-10-11-corpus-pilot-summary.txt) | 3 | 0 | 3 |

- **ACCEPT_BOTH:** in the nanoda-enabled run, nanoda accepted, Lean's kernel accepted, comparator printed "Your solution is okay!" and exited 0.
- **ACCEPT_LEAN_ONLY (9):** OptimalMaxCut, UniqueGamesTheorem, VertexCover, KaplanskyFinitelyPresented, GroupRingDeterminant, Laughlin, BinPackingGap, IndependentSets, PerfectCompleteness.
  - In each, nanoda aborted with a stack overflow (exit 134), and Lean's kernel accepted the proof in the same run. comparator reports such an abort as "nanoda kernel rejected the solution".
  - The run of the shipped config was ACCEPT_LEAN for all 9.
  - In the tsv, these runs have nanoda_run = NANODA_CRASH. That label was added 2026-10-20; the earlier version said OTHER. config_outcome is unchanged.
- **Nothing else went wrong in any config:** no build failures, timeouts or illegal axioms, no rejections by Lean's kernel, and no statement mismatches.
- **Shipped-config runs:** 17 in all (10 sampled, 9 Lean-only, with 2 in both groups), all ACCEPT_LEAN.

## Reading (INFERRED)

- **The 9 nanoda aborts are a limit of the tool, not a verdict on the proofs.**
  - Lean's kernel accepts each of these proofs in the same run.
  - nanoda's checker threads have a fixed 16 MiB stack (src/lib.rs STACK_SIZE), and ulimit -s does not change it.
  - nanoda issue #55 reports the same failure on 7 of the 9 configs, at this corpus commit with the same tool commits. It found that 1 GiB and 16 GiB stacks did not help: the backtraces show a recursion that does not progress.
  - Our own 512 MiB-stack copy also overflowed on OptimalMaxCut (results/2026-10-12-nanoda-bigstack-diag/findings.txt).
  - The other 2 of the 9, KaplanskyFinitelyPresented and GroupRingDeterminant, are not in #55. For them a larger stack does help: 3a24072 with a 1 GiB stack accepts both (see "Discrepancy test").
  - A post-fix nanoda (f67473b) was tried on these 9 as a separate, unofficial batch; see below.
- **What two kernels agreeing does and does not mean.** Agreement between two independent kernels lowers the risk that a kernel bug lets a false proof through, but it does not remove that risk.
  - The Lean v4.33.1 release notes (#14807) describe an `is_prop` soundness bug that gave a proof of False. They say the bogus proof "was also accepted by nanoda, an independent implementation of the Lean kernel."
  - Our toolchain (4.34.1) comes after that fix, but the episode shows that two kernels can share a bug.
- **A possible further check:** lean-inductive-models (github.com/nomeata/lean-inductive-models) validates inductive declarations from a lean4export export. It is a partial third check, for inductive types only, not a third full kernel. Not run.
- **What these results say:** the shipped Lean proofs pass the comparator for all 187 configs at fd4aeeb, and both kernels accept 178 of them.
- **What they do not say:** whether each Lean statement means what its paper claims. We checked that only for SiegelZeros (docs/log.md 2026-10-08, step 2).

## Outside checks (STATED by the sources; details in results/2026-10-19-external-checks-comparison.txt)

- **nealmcb/openai-math-lean-tooling already replicates our Lean-kernel results for all 190 of our configs.**
  - STATED: he ran comparator, as shipped (nanoda off in 414 of 416), on all 416 configs at fd4aeeb, and all were accepted.
  - COMPUTED: his 416 include all 190 of ours, and every one of them is accepted there. For our 3 pilot configs, his run is at fd4aeeb and ours at adc7f12.
  - So the Lean-kernel half of our replay is not new.
- **Our distinct contribution:**
  - nanoda run through comparator, for the whole scope, on a second platform (x86_64 WSL2 on Windows 11, systemd-run sandbox). His nanoda runs were on exported proof files, not through comparator.
  - Two apparent differences from his nanoda results, both resolved: KaplanskyFinitelyPresented and GroupRingDeterminant. Stock 3a24072 (16 MiB stack) overflowed on both here; his accepts came from a 3a24072 build patched to a 1 GiB stack. Export, nanoda config and thread count matched. Calling nanoda through comparator or directly on exports made no difference. See "Discrepancy test" below.
- **davegoldblatt/openai-zeta-proof-check:** QuasiRiemannHypothesis only, at adc7f12, with the Lean kernel and nanoda. Both accepted, the same result as our pilot.
- **Update 2026-10-20 (appended), resolved:** nealmcb confirmed on nanoda_lib #55 (https://github.com/ammkrn/nanoda_lib/issues/55#issuecomment-6293743601) that his 401/416 nanoda count used 3a24072 with a 1 GiB checker stack, not stock 3a24072. His 15 failures also failed at 1 GiB, and he states our 16 MiB and f67473b results are consistent with his master retest. His READMEs now say this.

## Discrepancy test, resolved (DIAGNOSTIC; does not change the table; results/2026-10-20-nanoda-discrepancy/SUMMARY.txt)

- **STATED:** his accepts for these two came from tools/kernel_pair_sweep.py, using a nanoda 3a24072 build patched to a 1 GiB checker stack (NANODA_STACK_MB=1024). Its export command and nanoda config match comparator's.
- **COMPUTED:**
  - Our exports, made with comparator's command, have exactly his byte counts: 657,348,158 and 698,227,515. He published no hashes, so the contents can't be compared further.
  - Official nanoda 3a24072 (16 MiB stack) on these exports: stack overflow on both, with 4 threads and with 1 thread.
  - The same source with only STACK_SIZE set to 1 GiB: exit 0 on both, in 38 s and 46 s.
- **INFERRED:** the cause is the stack size. These two proofs need a deep but finite recursion: more than 16 MiB, at most 1 GiB. That is unlike the RoundTables configs in #55, which fail even at 16 GiB. f67473b lowers the depth enough to pass at 16 MiB.
- **Update 2026-10-20 (appended):** RESOLVED. nealmcb's reply (https://github.com/ammkrn/nanoda_lib/issues/55#issuecomment-6293743601) STATES that the accepts for these two came from the 1 GiB build, that his 15 failures failed at 1 GiB too, and that our results are consistent with his.

## Run notes (COMPUTED, run.log and docs/log.md)

- **Guard stops:** the run's guards stopped it 7 times, 2 of them in this final session (WSL disk over 85G at 2026-10-19 19:25 and 2026-10-20 02:59). Every stopped config was rerun from the start.
- **Two driver errors, both Claude's, both found and corrected before any result depended on them:**
  - 2026-10-13: a done marker was written for a run the guard had killed.
  - 2026-10-19: batch 6 was classified and marked done before the guard's marker appeared, and YauCounterexample was labeled BUILD_FAIL for what was a guard kill.
  - The wrong files were set aside, not deleted: `.invalid-*` in batch-06, plus `MaximalSeshadriConstants.done.invalid-killed-by-guard`. The affected configs were rerun, and both are ACCEPT_BOTH.
- **Schedule changes:** the last batch was split in two, and one mid-batch prune was done (results/2026-10-20-prune-only-schedule.json, batch-08/prune-midbatch-20261020.log). Only built files of configs that had already passed both kernels were removed.

## Post-fix nanoda (UNOFFICIAL; not part of the table above)

Details: `results/2026-10-20-nanoda-postfix-f67473b/SUMMARY.txt`.

- **Tool:** nanoda_lib f67473b (2026-10-15; Cargo version 0.4.24), built as a separate binary.
  - Stack unchanged: 16 MiB per checker thread, with no ulimit change.
  - The official 3a24072 binary was not touched.
- **Same setup as the corpus runs:** same comparator, sandbox and clone (fd4aeeb), and the same nanoda-enabled configs, which differ from the shipped ones only in `enable_nanoda`.
- **COMPUTED:** all 9 ACCEPT_LEAN_ONLY configs got "nanoda kernel accepts", "Lean default kernel accepts", "Your solution is okay!" and exit 0. Runs took 243-527 s each, except Laughlin at 4,737 s. There were no guard stops.
- **INFERRED:**
  - For the 7 configs in #55 (OptimalMaxCut, UniqueGamesTheorem, VertexCover, Laughlin, BinPackingGap, IndependentSets, PerfectCompleteness), the failures are a nanoda 3a24072 bug that f67473b fixes. A larger stack does not help.
  - For KaplanskyFinitelyPresented and GroupRingDeterminant, stock 3a24072 needs more than 16 MiB of stack. Either a 1 GiB stack or f67473b is enough.
  - Across the two nanoda versions, all 187 configs have now been accepted by both nanoda and Lean's kernel. The official table above, which uses one pinned tool set, stays 178 + 9.

## Update 2026-10-26 (appended; earlier text unchanged)

- **Correction to "The other 2 of the 9, KaplanskyFinitelyPresented and GroupRingDeterminant, are not in #55"** (Reading, fifth bullet).
  - That is true of the issue as filed. nealmcb's issue body is dated 2026-10-15 and was never edited (GitHub `lastEditedAt` null, read 2026-10-26).
  - STATED: both configs were added to #55 by our own comment of 2026-10-20 12:50:34 UTC (https://github.com/ammkrn/nanoda_lib/issues/55#issuecomment-6291244827, account jmreilly1113). That comment reported their 16 MiB overflow and 1 GiB pass on 3a24072.
  - STATED: nealmcb's #61 (2026-10-23) lists both among three configs that need a deeper stack on master: "The last two are the ones @jmreilly1113 reported in #55."
  - Corrected reading: "not in #55's original report; added to #55 by us on 2026-10-20."
- COMPUTED (UNOFFICIAL; results/2026-10-26-nanoda-version-matrix/SUMMARY.md):
  - Both exports regenerated on 2026-10-26 are byte-identical to the 2026-10-20 ones (sha256 7b923557… and bda46ad6…).
  - On them: 3a24072 with a 1 GiB stack passes, as on 2026-10-20. nanoda master 37cb87b (16 MiB) overflows. 37cb87b with nealmcb's let fix and Nat.succ guard at 64 MiB passes.
  - Laughlin on 3a24072 with a 1 GiB stack grows to the 16G memory cap; f67473b, 37cb87b and the patched build pass it. This fits the "A larger stack does not help" reading above for the #55 configs.
  - The official table is unchanged.

## Update 2026-10-26 (appended; earlier text unchanged): network block

Each comparator run executed as the unprivileged user checker in a systemd-run unit whose seccomp filter (RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET) denied creating IPv4, IPv6, Unix-domain, netlink and packet sockets. A test on 2026-10-26 confirmed that TCP and UDP over IPv4 and IPv6, and DNS lookups, failed inside such a unit. AF_VSOCK sockets, which reach the Windows host, were not denied, and a test connection to the host succeeded. We did not test whether vsock offers a route to the internet. The earlier wording 'all network sockets blocked' overstated the restriction.

Test and inventory: results/2026-10-26-network-check/ (README.md, inventory.md).
