# Verification package: "Uniform exclusion of Landau–Siegel zeros" (openai/math family 003)

DOI (all versions): [10.5281/zenodo.23269527](https://doi.org/10.5281/zenodo.23269527). Previous version (reviewer-packet-v2-preliminary): [10.5281/zenodo.23499651](https://doi.org/10.5281/zenodo.23499651). Corpus replay of openai/math: [10.5281/zenodo.23505836](https://doi.org/10.5281/zenodo.23505836).

**What this package is.** A machine-checked complement to the existing human write-ups of the OpenAI argument:
- W. D. Banks, *On the OpenAI proof that Landau–Siegel zeros do not exist*, arXiv:2610.15483, an exposition with explicit constants;
- B. Kerr, *A simpler proof that there are no Landau–Siegel zeros*, arXiv:2610.21099;
- B. Green, *On Landau–Siegel zeros*, Hexagon 2610.00311v2 (2026-10-17).

Those papers give the mathematics in human-readable form. This package records what can be checked by machine:
- kernel acceptance of the Lean formalization by two independent kernels;
- a Lean proof of the paper's Lemma 3, a step of OpenAI's and Banks's route;
- exact small-N computations;
- an Arb-certified explicit constant, compared term by term with Banks's.

It is not a proof of the theorem, and none of the works above, this one included, has been refereed. Throughout, we keep apart what the paper states, what we computed (each claim cites a file in `results/`), and what we infer.

This repository checks the paper and its Lean formalization at openai/math commit `adc7f12`. For family 003's four configs, no file in their import closures changed between `adc7f12` and `fd4aeeb` (`results/2026-10-20-paper-prep-2/wsl/task3-closure-diffstat.txt`).

Results that are not in openai/math itself:

1. **Second kernel.** The official Lean FRO comparator, rerun with nanoda as a second, independently written kernel and with network access blocked, accepts both challenge theorems with only the standard axioms (`results/2026-10-08-lean-comparator-nanoda-netblock.txt`). The shipped configuration is re-run at adc7f12 under the full network block, with the checking user's identity logged (`results/2026-10-20-paper-prep-2/wsl/task3-SiegelZeros-adc7f12-shipped.log`).
2. **Lemma 3.** The paper's Lemma 3 is formalized in Lean (`lean-checks/Lemma3.lean`), standard axioms only, and accepted by nanoda. Its hypotheses are those of Banks's Proposition 3.4, condition (3.1). It certifies a step of OpenAI's and Banks's route; Kerr's and Green's arguments bypass it (`docs/packet-v3/lemma3-scope.md`).
3. **Rerouted proof.** With OAI's Corollary 4 replaced by the paper's route through Lemma 3 (one import line and one term changed), the challenge theorem `dirichletRealZeroBound_proof` is accepted by the official comparator with both kernels (`results/2026-10-09-lean-comparator-rerouted-nanoda.txt`).
4. **Explicit constant.** Conditional on the paper's proof, (1 − β) log q > 4.467·10⁻³ with Lu–Zaman–Zhao, or > 3.399·10⁻³ with Platt only, certified in Arb. Banks gives 3.0696·10⁻³ for the same argument; the difference is mainly that H is left free (`docs/effectivity/note-v2.md`, `docs/effectivity/banks-comparison-v2.md`).

There are also exact checks at small N: 510 Lemma 7 divisibility cases, 184 Arb runs of (5.1)/(5.6), and the Lemma 3 construction executed in 540 instances. These confirm the statements at those N only.

Where to start:
- `docs/packet-v3/related-work.md`: how this package relates to Banks, Kerr and Green.
- `docs/effectivity/note-v2.md` (PDF: `note-v2.pdf`): the explicit constant.
- `docs/packet-v3/release-notes-v3.md`: what changed since v1 and v2, including the corrections to the v1 methods text.
- `docs/reviewer-packet.md`, `docs/writeup.md`, `docs/issue40-facts.md`, `docs/reproduce.md`: as in v1.

To cite: see CITATION.cff, or the concept DOI 10.5281/zenodo.23269527.

## License

- **Code, scripts, tests and Lean files original to this project:** Apache License 2.0 (`LICENSE`). Copyright 2026 Joseph M. Reilly.
- **Prose documentation:** the `.md` files in `docs/` (including `writeup.md` and `reviewer-packet.md`) and this README are under CC BY 4.0 (`LICENSE-docs`).
- **Files copied from openai/math:** Apache-2.0 under OpenAI's copyright, unchanged. See `MODIFICATIONS.md` and `LICENSE-openai-math`.
- **Files under `lean-build/PrimeNumberTheoremAnd/`:** Apache-2.0, per their `NOTICE.md`.
- **Outputs in `results/`:** CC BY 4.0, except where they quote openai/math text.

[![DOI](https://zenodo.org/badge/1411973467.svg)](https://doi.org/10.5281/zenodo.23269527)
