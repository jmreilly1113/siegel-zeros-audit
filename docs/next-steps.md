# Next steps after the headline batch (written 2026-10-11, before the batch finished)

This plan is conditional: which branch applies depends on `results/2026-10-11-corpus-headline/outcomes.tsv` and the four `query-*.log` files. Claude commits and pushes the headline results first in every branch. Nothing below is started without Joe's go-ahead, except recording and classifying.

## 1. Per-config outcomes

| Outcome | What it means (plainly) | Next step |
|---|---|---|
| ACCEPT_BOTH | Two independent proof checkers (Lean's own kernel and nanoda) both accept the proof of the exact statement in the challenge file. | Nothing more for that config. |
| ACCEPT_LEAN_ONLY | Lean accepts, nanoda does not. Usually a gap or bug in nanoda, not in the proof, but not assumed. | Record nanoda's message. Check whether it repeats on a config that already passed (SiegelZeros) to separate tool limits from proof issues. Report it as a tool disagreement, not as a failed proof. |
| NANODA_UNSUPPORTED | nanoda stopped on a Lean feature it does not handle. | Record the feature named. The shipped-config (Lean-only) run decides acceptance. |
| NANODA_REJECT (shipped run also fails) | Neither checker accepts. | Serious. Apply CLAUDE.md rule 6: stop, re-derive in `docs/log.md`, rerun with a second method (a Lean-level `#print axioms` and statement check in the sandbox) before calling it a finding. |
| AXIOM_VIOLATION | The proof uses an axiom outside the three permitted ones. | Serious; same rule-6 procedure. Identify the axiom with a Lean-level query (not grep). |
| BUILD_FAIL | The proof does not compile at fd4aeeb in our setup. | Record the first error. Check whether the same module also fails at adc7f12 (to separate an upstream change from our setup). No repair. |
| TIMEOUT | Did not finish within 4 h (build) or 2 h (comparator). | Record. A single rerun with a longer limit only with Joe's approval. |
| GUARD_STOPPED | Our memory/disk guard stopped the run; says nothing about the proof. | Resume from that config. This needs a small change so the driver skips configs whose logs are already complete; Joe approves the restart. |

## 2. The two Lean-level queries

- **HarmonicGrowth.** The challenge file proves its claim with `axiom mainStatement`. The comparator compares only the *statement*, and checks axioms in the *solution*.
  - Expected: the solution's `main` uses only the three standard axioms and `mainStatement` does not exist in the solution environment. Then the axiom in the challenge file is harmless, a style point to note for review.
  - If `mainStatement` (or any non-standard axiom) appears in the solution's axiom set: serious, apply rule 6.
- **NavierStokesVelocity.** The challenge has a `sorry` inside `def half`. A test run on the challenge (not yet a result) showed `half` outside the closure of the `main_result` statement.
  - If the result run confirms this on both sides: the `sorry` does not affect what is being claimed. Note it as a review pointer only.
  - If `half` is in the statement closure on either side: the stated theorem depends on a definition that contains a `sorry`, so its meaning is not fully specified. Report it as a finding (after rule 6) for human review. This config is not yaml-referenced and gets no comparator run.

## 3. The remainder (172 configs)

- **If the headline batch is clean** (all ACCEPT_BOTH or explained tool limits), proceed with the item 4 schedule (`results/2026-10-11-corpus-prune-schedule.txt`):
  - 15 batches, peak about 51 GiB on C:;
  - about 17 h of building plus 26-49 h of comparator runs (estimates);
  - same guards, with the page cache cleared every minute;
  - shipped-config runs for the 10 sampled configs (all in the remainder) and for any non-ACCEPT_BOTH.
  - Needs from Joe: approval to start; approval for pruning, which deletes build files (planned after each batch's runs and queries finish); and whether to check in after each batch or run straight through.
- **If several headline configs fail for the same tool reason** (for example the same nanoda limitation): pause before the remainder and decide whether nanoda runs are still worth the time for every config.
- **If any serious finding appears** (axiom, statement, or both checkers reject): finish rule 6 on it before starting the remainder.

## 4. Open decisions (carried over)

- Whether to include the non-referenced headline-family configs (DirectedFeedback, MinUncut, GeneralMahler, ThreeMachine, ErdosReciprocal, BarnetteHamiltonian, SquareDifference).
- When to run the WSL move to D: (deferred; plan in `docs/wsl-move-plan.md`). Not needed for the remainder on C: per item 4.
- Delete the scratchpad bundle `siegel-before-filter-repo.bundle` (contains the arXiv PDF).
- Fill the placeholders in `docs/log.md` for the issue #40 comment URL and the Zulip URL.
- Phase 6 summary (`results/<date>-corpus-summary.md`) after the remainder.
- Cleanup after the remainder (Joe, 2026-10-12): bulky logs and crash dumps go to `D:\siegel-audit-offload\` as needed; when the run is done, prune what is no longer needed (WSL build outputs, nanoda crash dumps, temp files), after checking each target and recording it in `docs/log.md`. Nothing under `results/` or `external/` is deleted.
