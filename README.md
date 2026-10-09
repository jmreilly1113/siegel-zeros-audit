# Verification package: "Uniform exclusion of Landau–Siegel zeros" (openai/math family 003)

DOI: [10.5281/zenodo.23269528](https://doi.org/10.5281/zenodo.23269528)

Cite as: Reilly, Joseph M. (2026). *Verification package for openai/math family 003, Uniform exclusion of Landau–Siegel zeros: comparator + nanoda replay, Lean formalization of the paper's Lemma 3, rerouted proof, exact small-N checks*. https://doi.org/10.5281/zenodo.23269528

This repository checks the paper and its Lean formalization at openai/math commit `adc7f12`. The pinned files are unchanged at `fd4aeeb`. We test what can be tested by exact computation and by machine-checked proof, and we record what we could not check. It is not a proof of the theorem and does not replace expert reading. Throughout, we keep apart what the paper states, what we computed (each claim cites a file in `results/`) and what we infer.

Three results that are not in openai/math itself:

1. **Second kernel.** The official Lean FRO comparator, rerun with nanoda as a second, independently written kernel and with network access blocked, accepts both challenge theorems with only the standard axioms. See `results/2026-10-08-lean-comparator-nanoda-netblock.txt`.
2. **Lemma 3.** The paper's own proof of Lemma 3, which the OAI formalization replaces with a multiplicity estimate, is formalized in Lean (`lean-checks/Lemma3.lean`). It uses only standard axioms and is accepted by nanoda.
3. **Rerouted proof.** With OAI's Corollary 4 replaced by the paper's route through Lemma 3 (one import line and one term changed), the challenge theorem `dirichletRealZeroBound_proof` is accepted by the official comparator with both kernels. See `results/2026-10-09-lean-comparator-rerouted-nanoda.txt`.

There are also exact checks at small N: 510 Lemma 7 divisibility cases, 184 Arb runs of (5.1)/(5.6), and the Lemma 3 construction executed in 540 instances. These confirm the statements at those N only.

Where to start:
- `docs/reviewer-packet.md`: what we ask of each kind of reviewer.
- `docs/writeup.md`: the full account.
- `docs/issue40-facts.md`: every key value with its source file.
- `docs/reproduce.md`: how to rerun everything, including the comparator runs.

## License

- **Code, scripts, tests and Lean files original to this project:** Apache License 2.0 (`LICENSE`). Copyright 2026 Joseph M. Reilly.
- **Prose documentation:** the `.md` files in `docs/` (including `writeup.md` and `reviewer-packet.md`) and this README are under CC BY 4.0 (`LICENSE-docs`).
- **Files copied from openai/math:** Apache-2.0 under OpenAI's copyright, unchanged. See `MODIFICATIONS.md` and `LICENSE-openai-math`.
- **Files under `lean-build/PrimeNumberTheoremAnd/`:** Apache-2.0, per their `NOTICE.md`.
- **Outputs in `results/`:** CC BY 4.0, except where they quote openai/math text.

[![DOI](https://zenodo.org/badge/1411973467.svg)](https://doi.org/10.5281/zenodo.23269527)
