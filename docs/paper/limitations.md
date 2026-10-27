# Limitations notes (paper Section 9)

## Update 2026-10-26: what a nanoda pass or failure does and does not mean

Sources:
- results/2026-10-26-nanoda-version-matrix/SUMMARY.md and matrix.tsv (UNOFFICIAL runs).
- results/2026-10-26-nanoda-version-matrix/extended-replay-227/summary-227.txt.
- nanoda_lib issues #55, #61 and #62 (read 2026-10-26).

- **A fixed stack does not guarantee acceptance of future configs (class 2).** Some configs need a deep but finite `Nat` recursion: KaplanskyFinitelyPresented, GroupRingDeterminant and KaplanskyDirectFiniteness here, and MatchingFPRAS, ContingencyTables and LogspaceEquality in nealmcb's measurements.
  - STATED (nealmcb, results/nanoda-repro/three-stack-failures.md at openai-math-lean-tooling 1ca7ff2): the recursion depth equals the size of a numeric literal in the proof ("The chain is as long as the literal"; MatchingFPRAS has literal 98,008).
  - COMPUTED here: the same three Kaplansky/GroupRing configs overflow at 16 MiB and pass at 64 MiB and at 1 GiB. The 64 MiB pass is on master 37cb87b plus the patch; the 1 GiB pass is on 3a24072.
  - So any fixed STACK_SIZE (16 MiB stock, 64 MiB in the patched build, 256 MiB in the Lean Kernel Arena build per #61) accepts these proofs only up to some literal size.
  - INFERRED: a future config with a larger literal in the same pattern could overflow any fixed stack. A nanoda stack overflow on a new config therefore says nothing about its proof.
  - The depth also depends on the nanoda version. f67473b at 16 MiB passes all of these. master after PR #58 needs more. The pinned 3a24072 passes MatchingFPRAS, ContingencyTables, LogspaceEquality and RandomizedMeanPayoff at 16 MiB (COMPUTED, our comparator runs) but not the three Kaplansky/GroupRing configs.
- **Some "not checked (memory)" configs may reflect the pinned nanoda's bug, not the proofs.**
  - STATED: nanoda_lib #55 names Catalan and KMedianThreshold among the 3a24072 failures. On 3a24072, Catalan reaches 259 GiB and then panics with a 31-bit index error; KMedianThreshold "exits with an error".
  - STATED: nealmcb's 416-config sweep on nanoda master 8199c74 has both accepted: Catalan in 265 s at 7.3 GiB, KMedianThreshold in 13 s at 1.1 GiB (results/nanoda-ab-let.jsonl).
  - INFERRED: our memory stops on these two may come from that bug. Catalan's nanoda 3a24072 run reached 19.6 GB and was still rising; KMedianThreshold's reached 19.84 GB and was still growing. That is not evidence about the size of the proofs.
  - Their deferred status is unchanged: they have not been run here on a later nanoda.
  - This does not apply to MUBSix, CycleCliqueRamsey or UniversalTensorSquares. Those stopped before nanoda ran, on comparator or build memory.
- **An OOM under the 16G cap is a resource outcome, not a failure of the proof.** In the matrix, 3a24072 with a 1 GiB stack grows to the cap on the class 1 and class 3 configs. We did not measure how far each would grow; nealmcb reports 127–285 GiB on the same group (#55).
- **The two-version picture is unofficial.** Across 3a24072, f67473b, 37cb87b and 37cb87b plus the patch, every config in the matrix has been accepted by some nanoda build. The official tables use one pinned tool set (3a24072, 16 MiB). The other builds are reported separately and labeled UNOFFICIAL.

## Update 2026-10-26 evening (appended): Catalan and KMedianThreshold measured

COMPUTED (results/2026-10-26-nanoda-version-matrix/SUMMARY.md, step 5; exports byte-identical to the extended replay's, run under the full address-family deny list):
- nanoda 37cb87b, stock and with nealmcb's patch, checks KMedianThreshold in 25–26 s at about 1.1 GB and Catalan in 545–551 s at 4.6–5.0 GB.
- 3a24072 with a 1 GiB stack grows to the 16G cap on both.
- The inference above (their memory deferrals reflect the 3a24072 bug) is now measured for nanoda. Their official outcome stays "not checked": the pinned tool set did not finish, and Lean's kernel was not run on them here.
- ContinuumCoulombHardness could not be built here: the guard stopped its build at 19:32 on 2026-10-26 when MemAvailable fell below 1,500 MB.

## Update 2026-10-26 night (appended)

- COMPUTED: Lean's kernel accepted KMedianThreshold (369 s) and Catalan (2,234 s) here, through the shipped-config comparator run under the full deny list and a 16G cap. Both kernels have now accepted these two on this platform; nanoda's run used the unofficial tool set B3. Their official outcome stays "not checked".
- COMPUTED: ContinuumCoulombHardness could not be built here. The guard stopped its build at 4 threads and again at 2 threads, at MemAvailable 1,448 MB and 309 MB. It is permanently deferred, and its results are STATED only (nealmcb).
