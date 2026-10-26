<!-- DRAFT, not posted. For nanoda_lib #61. Joe to review; replace <LOGS> with a link to results/2026-10-26-nanoda-version-matrix at a pushed commit. -->

Results from a second platform (x86_64 WSL2, Ubuntu 24.04), openai/math fd4aeeb, Lean 4.34.1, lean4export 076e8e5. Every run is `nanoda_bin config.json` directly on the export, with the config comparator writes (`num_threads` 4, `nat_extension` and `string_extension` true), a 16G memory cap and a 30 min timeout.

**1. 37cb87b + your `nanoda-let-fvar-and-succ-guard-37cb87b.patch` (sha256 edd9824f…), STACK_SIZE 64 MiB, accepts all 9 of our nanoda crash configs.**

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

KaplanskyDirectFiniteness follows the same pattern as KaplanskyFinitelyPresented and GroupRingDeterminant. It overflows 3a24072 at 16 MiB and passes f67473b at 16 MiB (37 s, 1.27 GB). It overflows 37cb87b at 16 MiB, and passes 3a24072 with a 1 GiB stack (43 s).

SquareDifference on f67473b at 16 MiB: `thread 'thread_2' has overflowed its stack` after 98 s at 4.16 GB.

**2. Our export sizes equal yours** (`results/nanoda-ab-let.jsonl`) for all of these configs to the byte, and for MatchingFPRAS (485,099,446) and ContingencyTables (492,768,597).

**3. 3a24072 with STACK_SIZE 1 GiB on the six extended configs:**
- KaplanskyDirectFiniteness passes.
- DirectedFeedback, MinUncut, LaughlinPlanar, LaughlinFock and SquareDifference each grow to the 16G cap in 106–453 s and are OOM-killed. That fits "a larger stack does not help" in #55.

Binaries, hashes and logs: <LOGS>
