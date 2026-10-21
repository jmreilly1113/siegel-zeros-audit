# reviewer-packet-v3: release notes (DRAFT)

<!-- DRAFT for reviewer-packet-v3 (2026-10-20). Not published; Zenodo not contacted. -->

This draft includes `docs/v2-release-notes.md` (kept unchanged) as Part 1, and adds Part 2.

# Part 1. Corrections to the v1 methods text

Copied from `docs/v2-release-notes.md`. These correct the five mismatches in `results/2026-10-20-paper-prep/task4-manifest-vs-v1.txt`.

## (a) openai/math commit

- **v1 says:** the checks are at commit adc7f1241b42e322a6451854ab7e4b4c146bf78a (reproduce.md:7, README).
- **Correction:**
  - The v1 Siegel checks are at adc7f12.
  - The later corpus replay (Zenodo 10.5281/zenodo.23505836) is at fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb, except for the pilot (SiegelZeros, QuasiRiemannHypothesis, EditApproximation), which ran at adc7f12.
  - COMPUTED (results/2026-10-20-paper-prep-2/wsl/task3-closure-diffstat.txt and task3-diffstat-controls.txt): `git diff --stat adc7f12 fd4aeeb` over every repo file in the import closures of the four family-003 configs (DirichletSevenEighths, HeckeSevenEighths, QuasiRiemannHypothesis, SiegelZeros) and `lean/patches` is empty.
    - That is 3,239 files, all present at both commits.
    - The same command with `lean/OAI.lean` added reports that file (11 insertions), as a positive control.
  - COMPUTED (results/2026-10-20-paper-prep/task4-provenance-commands.txt): `lean-toolchain`, `lake-manifest.json` and `lakefile.lean` are byte-identical at adc7f12, fd4aeeb and main 1581d4c.
  - INFERRED: for family 003, a result at either commit is a result at the other.

## (b) landrun version

- **v1 says:** "landrun 0.1.18" (reproduce.md:43).
- **Correction:** landrun commit 811cfff51ceaf3d9843708aa6d22e9b84ccac8b4 (`git describe`: v0.1.17-4-g811cfff). The binary reports `landrun version 0.1.18`; sha256 5f6fd588dbdf5116969c3dee3fee52ba7f46aa80df2bb58277326a9186e736de.
  - INFERRED: the version string is ahead of the last tag. Cite the commit.

## (c) Lake manifest

- **v1 says:** no lake-manifest hash or package list for the WSL runs.
- **Addition:**
  - `lean/lake-manifest.json` sha256 cf6105a25d9dca2f166b241d9191bd12c7e13305890dc9c4d0952351cccc0794, 42 packages, Mathlib d13f23b723b8a846827a245b89c10fc7d3f11612.
  - Per-package revisions are in `results/2026-10-11-corpus-provenance.txt`.
  - `lake update` applies `lean/patches/*-lean4341.patch` to several packages; the counts are in the same file.

## (d) Network block

- **v1 says:** reproduce.md:45 lists `RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET` under "What we actually ran", which reads as applying to every run.
- **Correction:**
  - The first official comparator run (2026-10-08, `wsl-comparator/08_comparator.sh`, `results/2026-10-08-lean-comparator-wsl.txt`) used only `RestrictAddressFamilies=~AF_UNIX`, the comparator README's wrapper.
  - The full block applies from the nanoda run onward (2026-10-08, `29_comparator_nanoda.sh`, `results/2026-10-08-lean-comparator-nanoda-netblock.txt`).
  - The two-kernel acceptance in v1 rests on that nanoda run.
- **New run (COMPUTED, 2026-10-20, `results/2026-10-20-paper-prep-2/wsl/task3-SiegelZeros-adc7f12-shipped.log`):** the configuration of v1's first run, repeated with the full block.
  - Setup: the shipped `SiegelZeros.json` (Lean kernel only, as shipped) at adc7f12, in a separate clone, with the full block.
  - Network self-test inside the same unit: TCP to 1.1.1.1:443, an AF_INET UDP socket, an AF_INET6 socket and an AF_UNIX socket. Each fails with "Address family not supported by protocol".
  - Result: "Lean default kernel accepts the solution", "Your solution is okay!", exit 0, 750 s.
- INFERRED: v1's first-run result does not depend on network access.

## (e) Identity of the checking user

- **v1 says:** "An unprivileged user `checker`" (reproduce.md:44). No v1 run log records `id`.
- **Correction:**
  - The identity was first recorded by a separate probe with the same wrapper (2026-10-11, `results/2026-10-11-corpus-runas-2.txt`).
  - It is now recorded inside the comparator unit itself, at adc7f12, in the run of (d) (COMPUTED, same log):
    - `id`: uid=1000(checker) gid=1000(checker) groups=1000(checker);
    - Uid 1000 1000 1000 1000; CapPrm, CapEff and CapAmb all 0; NoNewPrivs 1;
    - cgroup /user.slice/user-1000.slice/user@1000.service/app.slice/run-u2.service;
    - kernel 5.15.167.4-microsoft-standard-WSL2.
  - Also recorded at fd4aeeb, POST-HOC: `results/2026-10-20-paper-prep/wsl/task4-SiegelZeros-posthoc.log` (nanoda-enabled copy, ACCEPT_BOTH, same identity).
- INFERRED: this records what the v1 runs most likely were, but it is post-hoc evidence. The v1 logs themselves still do not contain `id`.

## Superseded v2 to-do list (now done in this draft, see "New in v3")

- **Lemma 3 scope:** narrow the Lemma 3 statement in light of Banks, Proposition 3.4. Draft in `docs/packet-related-work-draft.md`.
- **Related work:** add a related-work paragraph (Banks, Kerr, Green). Same draft.
- **nanoda wording:** describe the 9 ACCEPT_LEAN_ONLY configs as "crash at nanoda 3a24072, pass at nanoda f67473b". Source: `results/2026-10-20-paper-prep-2/task2-nanoda-reclassification.txt`.

# Part 2. New in v3

- **Explicit constant, version 2:** `docs/effectivity/note-v2.md`, `note-v2.tex`, `note-v2.pdf`.
  - The same master inequality and certified values as v1 (`note.md`, kept): 4.4673780338·10⁻³ for q > 10¹⁰ with Lu–Zaman–Zhao; 3.3992904026·10⁻³ for q > 4·10⁵ with Platt; 5.0425352961·10⁻⁴ for the argument alone (q ≠ 8).
  - New: Banks's 3.0696·10⁻³ as background, and the factor attribution from Banks's value to ours (free H ×1.68, …), with its product check (`results/2026-10-20-paper-prep-3/note-v2-factor-check.txt`).
  - New: the recomputation of Banks's 12 numeric claims (`src/banks_compare.py`) and the Lemma 3 / Proposition 3.4 hypothesis match.
  - Diff summary: `results/2026-10-20-paper-prep-3/note-v2-diff-summary.txt`.
- **Comparison with Banks:** `docs/effectivity/banks-comparison-v2.md` (v1 kept). It records that our rows drop Banks's H ≤ q, and that log q > 23 serves only his absorption step (his Remark 7.2(vii)).
- **Final corpus table** (`scripts/final_table.py`; `results/2026-10-20-paper-prep-3/corpus-189.tsv`, `summary.txt`, `tables.tex`). From the raw per-config logs only, for the 189 configs referenced by `formalization.yaml` at fd4aeeb:
  - Lean kernel accepts all 189;
  - nanoda 3a24072 accepts 180 (178 at fd4aeeb, 2 at adc7f12);
  - 9 crash at nanoda 3a24072 and pass at nanoda f67473b.
  - EditApproximation (unreferenced) is reported separately.
  - Reconciliation of 178/185/187/190 is in `summary.txt`.
- **nanoda wording:** "crash at 3a24072, pass at f67473b" for the 9 configs (`results/2026-10-20-paper-prep-2/task2-nanoda-reclassification.txt`).
- **Related work and Lemma 3 scope:** `docs/packet-v3/related-work.md`, `docs/packet-v3/lemma3-scope.md`. The Kerr and Green statements are marked [CHECKED-BY-JOE, pending Joe's read].
- **README framing:** "machine-checked complement to existing human write-ups" (`docs/packet-v3/README-draft.md`).
- **Not included:** the UNREVIEWED primes-dividing-q refinement. It is in the repository but is not part of any claim in this release.
- **Files still labeled UNREVIEWED** (`git grep -l UNREVIEWED`, 2026-10-20). The device files carry the label themselves:
  - `docs/effectivity/derivation-banks-device.md`;
  - `src/effectivity_banks_device.py`, which prints the label on every result line;
  - `results/2026-10-20-effectivity-device/device-output.txt`.

  The device's tests, `tests/test_effectivity_banks_device.py`, belong to the same unreviewed work but do not carry the word.

  Files that only mention the label: `docs/log.md`, `docs/zenodo-v3-metadata.json`, `results/2026-10-20-paper-prep-3/note-v2-diff-summary.txt`, and this file.
