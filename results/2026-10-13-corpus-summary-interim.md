# Corpus replay: interim summary, 2026-10-13 14:27 EDT

Source table: results/2026-10-13-corpus-summary-interim.tsv
Command: `python -I wsl-comparator/87_corpus_summary.py .` (reads results files only)
The run is still going (driver 93_remainder_serial_v4.sh). This is a snapshot, not a final result.

## Outcomes so far (COMPUTED, from the tsv)

| Stage | ACCEPT_BOTH | ACCEPT_LEAN_ONLY | Pending (batch 6, running) | Not started (batch 7) | Total |
|---|---|---|---|---|---|
| Headline | 12 | 3 | 0 | 0 | 15 |
| Remainder | 149 | 4 | 7 | 12 | 172 |

- ACCEPT_BOTH: the nanoda-enabled run passed with both nanoda and Lean's own kernel accepting.
- ACCEPT_LEAN_ONLY (7 configs: OptimalMaxCut, UniqueGamesTheorem, VertexCover, KaplanskyFinitelyPresented, GroupRingDeterminant, Laughlin, BinPackingGap): the nanoda run is OTHER (nanoda stack overflow, exit 134, with Lean's kernel accepting in the same run), and the shipped-config run is ACCEPT_LEAN.
- No build failures, timeouts, illegal axioms, Lean-kernel rejections or comparator rejections in any finished config.
- Sampled configs with a shipped-config run: 9 of 10 done, all ACCEPT_LEAN. KMedianRecovery (batch 6) is left.

## Reading (INFERRED)

- The nanoda crashes are a limit of the tool (a fixed 16 MiB stack), not a verdict on the proofs: Lean's kernel accepts each of those proofs in the same run.
- These results say that the shipped Lean proofs check under the comparator for the finished configs. They do not, by themselves, check that the Lean statements match the paper; that is a separate part of the audit.

## Run notes (COMPUTED, run.log and docs/log.md)

- Batch 6 was stopped three times between 13:02 and 13:33 by the run's own guards (WSL disk limit once, Windows free-RAM floor twice). Each stopped config is rerun from the start; one done marker written for a killed run was found and set aside (MaximalSeshadriConstants, now rerun and ACCEPT_BOTH).
- Since 13:35 the run is serial (one build or check at a time, 4 threads). INFERRED finish about 20:30-21:00.
