<!-- DRAFT, not posted. Target: ammkrn/nanoda_lib#55. Approval needed before posting (Joe, 2026-10-20). Facts and commands only. -->

Two results and a question from a comparator replay of openai/math at fd4aeeb (Lean 4.34.1, comparator d03acab, lean4export 076e8e5, x86_64 WSL2).

**1. f67473b passes all 9 of our crash configs through comparator at the default 16 MiB stack.**
With nanoda_lib 3a24072, through comparator (`enable_nanoda: true`, default config: `num_threads` 4, `nat_extension` and `string_extension` true), these 9 configs aborted with "has overflowed its stack" while Lean's kernel accepted: OptimalMaxCut, UniqueGamesTheorem, VertexCover, KaplanskyFinitelyPresented, GroupRingDeterminant, Laughlin, BinPackingGap, IndependentSets, PerfectCompleteness. With f67473b, unmodified (STACK_SIZE 16 MiB), through comparator via `COMPARATOR_NANODA`, all 9 print "nanoda kernel accepts the solution" and exit 0 (243-527 s; Laughlin 4,737 s).
Logs: https://github.com/jmreilly1113/siegel-zeros-audit/blob/814bf7453b2086b6fccf2acd737b00a9abd68bf3/results/2026-10-20-nanoda-postfix-f67473b/SUMMARY.txt

**2. KaplanskyFinitelyPresented and GroupRingDeterminant overflow 3a24072 at 16 MiB and pass at 1 GiB, unlike the configs reported above as failing at 1 GiB and 16 GiB.**
Exports made with comparator's command (`lake env lean4export <solution_module> -- Quot Quot.mk Quot.lift Quot.ind <theorem> propext Quot.sound Classical.choice <26 primitives>`; `definition_names` is empty in both configs):
- KaplanskyFinitelyPresented: 657,348,158 bytes, sha256 7b9235575213e672a217d9cfdf783ac7590d6f346002309e0b0c276b707f398c
- GroupRingDeterminant: 698,227,515 bytes, sha256 bda46ad6b35cc220ba4fbb8c7c93329d920682e3040257134f923bd0a53877e5

`nanoda_bin config.json` directly on each export, with comparator's config:

| nanoda | num_threads | KaplanskyFinitelyPresented | GroupRingDeterminant |
|---|---|---|---|
| 3a24072, STACK_SIZE 16 MiB | 4 | stack overflow (thread_1), 40 s | stack overflow (thread_2), 48 s |
| 3a24072, STACK_SIZE 16 MiB | 1 | stack overflow ('main'), 93 s | stack overflow ('main'), 118 s |
| 3a24072, STACK_SIZE 1 GiB (only change: src/lib.rs:23) | 4 | exit 0, 38 s | exit 0, 46 s |

Logs and configs: https://github.com/jmreilly1113/siegel-zeros-audit/blob/814bf7453b2086b6fccf2acd737b00a9abd68bf3/results/2026-10-20-nanoda-discrepancy/SUMMARY.txt

**3. Question for @nealmcb.**
`tools/kernel_pair_sweep.py` runs `ext/bin/nanoda_bin.timing` with `NANODA_STACK_MB=1024` (`tools/patches/nanoda-stack-and-decl-times.patch`). The records for KaplanskyFinitelyPresented and GroupRingDeterminant in `results/kernel-pair-sweep.jsonl` (`nanoda_rc` 0) come from that script. The issue body says the exports were "checked with nanoda_lib 3a24072 (v0.4.19)" and reports "416 solution configurations (each the export of one theorem and everything it depends on, 18 MB to 3.9 GB): nanoda accepts 401." Does that count include runs on the 1 GiB build?
