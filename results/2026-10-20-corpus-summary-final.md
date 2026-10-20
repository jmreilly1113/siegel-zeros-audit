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
- **Nothing else went wrong in any config:** no build failures, timeouts or illegal axioms, no rejections by Lean's kernel, and no statement mismatches.
- **Shipped-config runs:** 17 in all (10 sampled, 9 Lean-only, with 2 in both groups), all ACCEPT_LEAN.

## Reading (INFERRED)

- **The 9 nanoda aborts are a limit of the tool, not a verdict on the proofs.**
  - Lean's kernel accepts each of these proofs in the same run.
  - nanoda's checker threads have a fixed 16 MiB stack (src/lib.rs STACK_SIZE), and ulimit -s does not change it.
  - nanoda issue #55 reports the same failure on 7 of the 9 configs, at this corpus commit with the same tool commits. It found that 1 GiB and 16 GiB stacks did not help: the backtraces show a recursion that does not progress.
  - Our own 512 MiB-stack copy also overflowed on OptimalMaxCut (results/2026-10-12-nanoda-bigstack-diag/findings.txt).
  - A post-fix nanoda (f67473b) was tried on these 9 as a separate, unofficial batch; see below.
- **What two kernels agreeing does and does not mean.** Agreement between two independent kernels lowers the risk that a kernel bug lets a false proof through, but it does not remove that risk.
  - The Lean v4.33.1 release notes (#14807) describe an `is_prop` soundness bug that gave a proof of False. They say the bogus proof "was also accepted by nanoda, an independent implementation of the Lean kernel."
  - Our toolchain (4.34.1) comes after that fix, but the episode shows that two kernels can share a bug.
- **A possible further check:** lean-inductive-models (github.com/nomeata/lean-inductive-models) validates inductive declarations from a lean4export export. It is a partial third check, for inductive types only, not a third full kernel. Not run.
- **What these results say:** the shipped Lean proofs pass the comparator for all 187 configs at fd4aeeb, and both kernels accept 178 of them.
- **What they do not say:** whether each Lean statement means what its paper claims. We checked that only for SiegelZeros (docs/log.md 2026-10-08, step 2).

## Outside checks (STATED by the sources; details in results/2026-10-19-external-checks-comparison.txt)

- **nealmcb/openai-math-lean-tooling:**
  - Ran comparator, as shipped (nanoda off in 414 of 416 configs), on all 416 configs at fd4aeeb, and all were accepted.
  - COMPUTED: that covers all 190 of our configs, so it is an independent Lean-kernel replay of our scope.
  - Its nanoda runs were on exported proof files, not through comparator.
  - OPEN: there, nanoda 3a24072 accepted KaplanskyFinitelyPresented and GroupRingDeterminant; through comparator here, it overflowed on both. Not investigated.
- **davegoldblatt/openai-zeta-proof-check:** QuasiRiemannHypothesis only, at adc7f12, with the Lean kernel and nanoda. Both accepted, the same result as our pilot.

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
  - The 9 official nanoda failures were bugs in nanoda 3a24072, fixed upstream by f67473b. They were not a need for a larger stack, since f67473b passes with the same 16 MiB.
  - Across the two nanoda versions, all 187 configs have now been accepted by both nanoda and Lean's kernel. The official table above, which uses one pinned tool set, stays 178 + 9.
