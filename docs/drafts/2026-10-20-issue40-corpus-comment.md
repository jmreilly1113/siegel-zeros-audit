<!-- DRAFT, not posted. Target: grwtsk/openai-math#40. Approval needed before posting (Joe, 2026-10-20).
     Base: Joe's draft of 2026-10-20. Changes from it: the commit URLs were filled in; "Cause not yet known." was
     replaced with Joe's sentence; and the two edits listed at the end of this comment were made (Joe to accept or revert). -->

Corpus replay at openai/math fd4aeeb, following the SiegelZeros packet above.

Scope: the 189 Comparator configs referenced in formalization.yaml. 187 replayed at
fd4aeeb; SiegelZeros and QuasiRiemannHypothesis ran at adc7f12 (import closures
unchanged). Toolchain: Lean 4.34.1, Mathlib d13f23b, comparator d03acab,
lean4export 076e8e5, landrun 811cfff, nanoda_lib 3a24072. x86_64 WSL2.

Each config was run through comparator with enable_nanoda: true, so both kernels
check the proof in the same run that checks the statement and axioms.
Results: 178 ACCEPT_BOTH; 9 Lean kernel accepts, nanoda crashes (stack overflow).
No other failures. With nanoda f67473b (separate, unofficial batch, same 16 MiB
stack) all 9 pass.

Relation to other work: nealmcb/openai-math-lean-tooling ran comparator on all
416 configs (Lean kernel) and nanoda directly on exports. Our Lean-kernel results
replicate his for this scope. Seven of our nine nanoda crashes match nanoda_lib #55.
Two do not: KaplanskyFinitelyPresented and GroupRingDeterminant crash stock nanoda
3a24072 here but pass in his runs. Cause identified: his nanoda accepts for
these two used a 3a24072 build patched to a 1 GiB checker stack. Stock 3a24072
(16 MiB) overflows on both; the same source with only the stack set to 1 GiB accepts
both. Our exports match his byte counts.

Scope limits: this checks that each solution proves its challenge statement within
the permitted axioms, not that the statements match the papers. Two-kernel
agreement reduces but does not remove kernel-bug risk (Lean v4.33.1 #14807).

Results:
- Summary: https://github.com/jmreilly1113/siegel-zeros-audit/blob/814bf7453b2086b6fccf2acd737b00a9abd68bf3/results/2026-10-20-corpus-summary-final.md
- Per-config table: https://github.com/jmreilly1113/siegel-zeros-audit/blob/814bf7453b2086b6fccf2acd737b00a9abd68bf3/results/2026-10-20-corpus-summary-final.tsv
- Post-fix nanoda batch: https://github.com/jmreilly1113/siegel-zeros-audit/blob/814bf7453b2086b6fccf2acd737b00a9abd68bf3/results/2026-10-20-nanoda-postfix-f67473b/SUMMARY.txt
- Comparison with other replays: https://github.com/jmreilly1113/siegel-zeros-audit/blob/814bf7453b2086b6fccf2acd737b00a9abd68bf3/results/2026-10-19-external-checks-comparison.txt
- Stack-size test: https://github.com/jmreilly1113/siegel-zeros-audit/blob/814bf7453b2086b6fccf2acd737b00a9abd68bf3/results/2026-10-20-nanoda-discrepancy/SUMMARY.txt

On grwtsk/math#80: the packet makes no Riemann Hypothesis claim, and GRWTSK
applications are not part of this work.

<!-- Number check against the files (all match):
  189 referenced / 187 at fd4aeeb / 2 at adc7f12: corpus-mainplan.txt; summary .md "What was run".
  Tool commits: corpus-provenance.txt, docs/log.md 2026-10-08; nanoda 3a24072: lean-comparator-nanoda-netblock.txt.
  178 + 9, no other failures: corpus-summary-final.tsv. f67473b 9/9 at 16 MiB: postfix SUMMARY.txt and build.log.
  416 configs: nealmcb results/cmp-all/STATUS.md. 7 of 9 in #55: issue body (5 named + IndependentSets, PerfectCompleteness
  in the RoundTables group). Byte counts 657,348,158 / 698,227,515: discrepancy SUMMARY.txt vs his kernel-pair-sweep.jsonl.
  #14807: Lean v4.33.1 release notes.
  Edits beyond Joe's two changes, for Joe to accept or revert:
  (1) "crash nanoda 3a24072 through comparator here but pass in his direct runs" -> "crash stock nanoda 3a24072 here
      but pass in his runs". The cause was the stack, not comparator vs direct (Joe's step-3 edit 2).
  (2) "Results: [link after push]" -> five links.
  Not changed, but worth knowing: his comparator run was "as shipped", which had nanoda on in 2 of the 416 configs; "(Lean kernel)" is true for our scope. -->
