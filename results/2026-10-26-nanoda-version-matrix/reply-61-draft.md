<!-- DRAFT, not posted. For nanoda_lib #61. Joe to review; replace https://github.com/jmreilly1113/siegel-zeros-audit/tree/bb6f197b69d77cf505decba848b21e7f5a12c48d/results/2026-10-26-nanoda-version-matrix with a link to results/2026-10-26-nanoda-version-matrix at a pushed commit. -->

Results from a second platform (x86_64 WSL2, Ubuntu 24.04), openai/math fd4aeeb, Lean 4.34.1, lean4export 076e8e5. Every run is `nanoda_bin config.json` directly on the export, with the config comparator writes (`num_threads` 4, `nat_extension` and `string_extension` true), a 16G memory cap and a 30 min timeout.

**1. 37cb87b + your `nanoda-let-fvar-and-succ-guard-37cb87b.patch` (sha256 edd9824f…), STACK_SIZE 64 MiB, accepts all 9 of our crash configs for which we have exports.** The six RoundTables configs among our 189 (OptimalMaxCut, UniqueGamesTheorem, VertexCover, BinPackingGap, IndependentSets, PerfectCompleteness) were not rerun here; their exports were made inside comparator and not kept.

| config | 3a24072, 16 MiB (via comparator) | 37cb87b, 16 MiB | 37cb87b + patch, 64 MiB |
|---|---|---|---|
| KaplanskyFinitelyPresented | overflow | overflow, 44 s | exit 0, 42 s, 1.3 GB |
| GroupRingDeterminant | overflow | overflow, 50 s | exit 0, 47 s, 1.3 GB |
| KaplanskyDirectFiniteness | overflow | overflow, 41 s | exit 0, 42 s, 1.3 GB |
| SquareDifference | overflow | overflow, 97 s, 3.5 GB | exit 0, 31 s, 0.66 GB |
| Laughlin | overflow | exit 0, 877 s | exit 0, 945 s, 2.1 GB |
| LaughlinPlanar | overflow | exit 0, 966 s | exit 0, 926 s, 1.9 GB |
| LaughlinFock | overflow | exit 0, 1,364 s | exit 0, 1,547 s, 8.7 GB |
| DirectedFeedback | overflow | exit 0, 48 s | exit 0, 48 s, 1.0 GB |
| MinUncut | overflow | exit 0, 54 s | exit 0, 51 s, 1.0 GB |

KaplanskyDirectFiniteness follows the same pattern as KaplanskyFinitelyPresented and GroupRingDeterminant. It overflows 3a24072 at 16 MiB and passes f67473b at 16 MiB (37 s, 1.27 GB). It overflows 37cb87b at 16 MiB.

KaplanskyDirectFiniteness isn't in #55; it appears in your stack-size results file but hasn't been reported in an issue.

SquareDifference on f67473b at 16 MiB: `thread 'thread_2' has overflowed its stack` after 98 s at 4.16 GB.

**2. Catalan and KMedianThreshold, from #55, also check on 37cb87b,** stock and patched (exports regenerated here; sha256 equal to our earlier exports):

| config | 37cb87b, 16 MiB | 37cb87b + patch, 64 MiB | 3a24072, STACK_SIZE 1 GiB |
|---|---|---|---|
| KMedianThreshold | exit 0, 25 s, 1.06 GB | exit 0, 26 s, 1.07 GB | grows to the 16G cap in 206 s |
| Catalan | exit 0, 545 s, 5.0 GB | exit 0, 551 s, 4.6 GB | grows to the 16G cap in 201 s |

We could not run ContinuumCoulombHardness: on this 20 GB machine its build was stopped by our memory guard (free memory below 1.5 GB), at 4 threads and again at 2.

**3. Our export sizes equal yours** (`results/nanoda-ab-let.jsonl`) to the byte for all of these configs, including Catalan (832,532,249) and KMedianThreshold (620,096,646), and for MatchingFPRAS (485,099,446) and ContingencyTables (492,768,597).

**4. 3a24072 with STACK_SIZE 1 GiB on the six extended configs:**
- KaplanskyDirectFiniteness passes (43 s).
- DirectedFeedback, MinUncut, LaughlinPlanar, LaughlinFock and SquareDifference each grow to the 16G cap in 106–453 s and are OOM-killed. Consistent with #55, where larger stacks didn't help. The cap bounds these runs. In #55, DirectedFeedback overflowed a 1 GiB stack at 24.6 GiB, LaughlinPlanar and LaughlinFock reached 175 and 127 GiB, and you noted that all 15 of your failures also failed at 1 GiB.

Binaries, hashes and logs: https://github.com/jmreilly1113/siegel-zeros-audit/tree/bb6f197b69d77cf505decba848b21e7f5a12c48d/results/2026-10-26-nanoda-version-matrix
