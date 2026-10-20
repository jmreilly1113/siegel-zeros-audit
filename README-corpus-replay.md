# Corpus replay of openai/math, and family-003 statement checks

This record is an independent replay of the Lean proofs in [openai/math](https://github.com/openai/math) through the Lean FRO comparator, with a second kernel (nanoda), plus a check that the four family-003 Lean statements say what their paper says. It is a replay and statement check, not a mathematical review, and it has not been reviewed by a specialist.

In this archive this file is `README.md`. In the repository it is `README-corpus-replay.md`, and the repository's own README (about the Siegel-zero packet) is included here as `README-siegel-packet.md`. The archive was built from [jmreilly1113/siegel-zeros-audit](https://github.com/jmreilly1113/siegel-zeros-audit) at the commit named in the Zenodo record's notes.

## Scope

- **Configurations:** the 189 Comparator configurations referenced by `formalization.yaml`.
  - 187 were replayed at openai/math `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`.
  - SiegelZeros and QuasiRiemannHypothesis ran at `adc7f1241b42e322a6451854ab7e4b4c146bf78a`, where nothing their proofs import differs from fd4aeeb.
- **Toolchain:** Lean 4.34.1, Mathlib `d13f23b`, comparator `d03acab`, lean4export `076e8e5`, landrun `811cfff`, nanoda_lib `3a24072`.
- **Platform:** x86_64 WSL2, with each run in a network-blocked systemd-run sandbox as an unprivileged user.
- **Kernels:** each configuration was run through comparator with `enable_nanoda: true`, so nanoda and Lean's kernel both check the proof in the run that checks the statement and axioms.

## Results

- **178 configurations:** accepted by both kernels.
- **9 configurations:** accepted by Lean's kernel, while nanoda 3a24072 aborted with a stack overflow. No other failures.
- **The 9, with nanoda f67473b:** a separate, unofficial batch with the same 16 MiB stack accepted all 9.
  - A diagnostic showed that two of them (KaplanskyFinitelyPresented, GroupRingDeterminant) need more than 16 MiB but at most 1 GiB of stack with stock 3a24072.
  - The other 7 match nanoda_lib issue #55.
- **Statement checks, family 003:** all four statements match Theorem 1.1 of the September 30, 2026 quasi-Riemann manuscript.
  - SiegelZeros was checked earlier, in the Siegel packet.
  - QuasiRiemannHypothesis, DirichletSevenEighths and HeckeSevenEighths are checked here, with Lean lemmas (34 `#print axioms` outputs, all standard) and a numerical check.
  - The zeta statement also covers s = 1, through Mathlib's nonzero assigned value `riemannZeta 1`.
  - The Dedekind factorization for the Hecke L-function was checked numerically, not proved.

Not checked:
- whether the statements of the other configurations match their papers;
- the papers' mathematics.

Agreement of two kernels reduces but does not remove kernel-bug risk: the Lean v4.33.1 release notes (#14807) describe a proof of False that nanoda also accepted.

## Where things are

| What | Path |
|---|---|
| Final corpus summary (table and write-up) | `results/2026-10-20-corpus-summary-final.md`, `.tsv` |
| Comparison with other replays | `results/2026-10-19-external-checks-comparison.txt` |
| Stack-size diagnostic | `results/2026-10-20-nanoda-discrepancy/SUMMARY.txt` |
| Post-fix nanoda batch | `results/2026-10-20-nanoda-postfix-f67473b/SUMMARY.txt` |
| Per-config logs | `results/2026-10-11-corpus-headline/`, `results/2026-10-12-corpus-remainder/` |
| Statement checks | `docs/statement-check-summary.md` and the three `docs/statement-check-*.md` reports |
| Statement-check Lean project (sources) | `statement-checks/` |
| Statement-check build log and numerical check | `results/2026-10-20-statement-checks/` |
| Replay scripts | `wsl-comparator/60_*` to `105_*` |
| Running log | `docs/log.md` |

## Related work

- **Siegel-zero packet:** this record supplements the Siegel-zero verification packet, concept DOI [10.5281/zenodo.23269527](https://doi.org/10.5281/zenodo.23269527).
- **nealmcb/openai-math-lean-tooling:** ran comparator, as shipped, on all 416 configurations at fd4aeeb and accepted all of them. That includes every configuration here, so the Lean-kernel half of this replay replicates his. His nanoda runs were on exports with a 1 GiB checker stack, as he clarified on nanoda_lib #55.
- **davegoldblatt/openai-zeta-proof-check:** replayed QuasiRiemannHypothesis at adc7f12 with both kernels, with the same result.
- **What is new here:** nanoda run through comparator for the whole scope on a second platform, the stack-size diagnosis, and the statement checks.

## License

- Code, scripts and Lean files original to the project: Apache License 2.0 (`LICENSE`).
- Prose documentation and outputs in `results/`: CC BY 4.0 (`LICENSE-docs`).
- The Zenodo record is licensed CC BY 4.0.
