# lean-checks/: what each Lean file is (DRAFT, 2026-10-26)

**Roles:**
- **canonical:** the file to cite for that declaration.
- **comparator copy:** the module form installed for the accepted rerouted comparator run (2026-10-09). The paper cites these.
- **working draft:** an intermediate piece kept for the record. Not to be cited. Some are proved with `sorry`.
- **superseded approach:** an earlier method kept for the record, not cited. MainRerouted.lean's `#reroute` metaprogram adds declarations with `addDecl` outside comparator; the comparator route replaced it.
- **query:** asks Lean about other declarations (`#print axioms`, dependency scans). It proves nothing.

**Hashes:** sha256 of the LF file, as checked out. Three files were CRLF when their hashes were first recorded; results/2026-10-09-lean-checks-line-endings.txt maps both forms.

**Two working drafts define a `Lemma3.rectangle` that is not proved.** Lemma3_Cor4.lean proves `interpolation` by `sorry`, so its `rectangle` depends on `sorryAx`. Lemma3_Bridge.lean proves `rectangle` itself by `sorry`. The canonical declarations are in Lemma3Bridged.lean and comparator-copy/PaperLemma3/. Neither canonical file imports a draft, and their texts are identical (results/2026-10-26-claims-ledger/ledger-v2.tsv, Section 5).

| file | role | `sorry` | what it is | covering results file(s) |
|---|---|---|---|---|
| comparator-copy/PaperLemma3/Lemma3.lean | comparator copy (cited) | no | `Lemma3.interpolation` (the paper's Lemma 3) as module `OAI.NumberTheory.SiegelZeros.PaperLemma3.Lemma3`. Identical to Lemma3.lean through `end Lemma3`. Imports Mathlib only. | results/2026-10-09-rerouted-comparator-diff.txt (installed copy, sha256 1ce196f5…); results/2026-10-09-lean-comparator-rerouted-nanoda.txt; results/2026-10-26-claims-ledger/axioms-comparator-copy-2026-10-26.txt |
| comparator-copy/PaperLemma3/Bridge.lean | comparator copy (cited) | no | Corollary 4 (`Lemma3.rectangle`), `bridge_descent`, `bridge_main`, and `actual_biquadratic_rectangle_span_via_lemma3` (OAI's Corollary 4 via `type_of%`). Imports Mathlib, PaperLemma3.Lemma3 and OAI's InvariantJetLinearMap. | the same three files (installed copy, sha256 af401514…) |
| Lemma3.lean | canonical (Lemma 3) | no | the proof of Lemma 3, Mathlib only; ends with `#print axioms Lemma3.interpolation` | results/2026-10-08-lean-lemma3-full.txt |
| Lemma3Bridged.lean | canonical (Lemma 3 + Corollary 4 + bridge, one file) | no | Lemma3.lean + the Corollary 4 and bridge parts, merged by script. Imports OAI.NumberTheory.SiegelZeros.Main. | results/2026-10-08-lean-lemma3-bridge.txt; results/2026-10-08-lean-lemma3-nanoda.txt; results/2026-10-26-claims-ledger/axioms-rectangle-2026-10-26.txt |
| MainRerouted.lean | superseded approach (metaprogram; not cited) | no (no `sorry` in the file) | A metaprogram. It defines `elab "#reroute"` (line 24), which copies every constant in the closure of the roots and sends each copy to the kernel with `addDecl` (line 90). It is invoked at line 101. Replaced by the comparator route: the +2/−1 patch plus comparator-copy/PaperLemma3/. | results/2026-10-08-lean-main-rerouted.txt |
| NonVacuity.lean | canonical (non-vacuity) | no | the challenge hypotheses are satisfiable (quadratic characters); specialisation | results/2026-10-08-lean-nonvacuity.txt |
| Lemma3Skeleton.lean | working draft | **yes** (the 12 sub-lemmas are stubbed) | skeleton of Lemma 3: the main theorem proved from 12 sub-lemmas left as `sorry` | results/2026-10-08-lean-lemma3-skeleton.txt |
| Lemma3_P1.lean … Lemma3_P5.lean | working draft (proved pieces) | no | the five sub-lemma groups, proved separately and then merged into Lemma3.lean | results/2026-10-08-lean-lemma3-piece1.txt … piece5.txt |
| Lemma3_Cor4.lean | working draft | **yes**: `interpolation` by `sorry` (line 31) | Corollary 4 against a stubbed Lemma 3. Its `rectangle` text equals the canonical one but depends on `sorryAx`. | results/2026-10-08-lean-lemma3-cor4-piece.txt |
| Lemma3_Bridge.lean | working draft | **yes**: `rectangle` by `sorry` (line 20) | the bridge against a stubbed Corollary 4; `bridge_main` and `bridge_descent` equal the canonical ones | results/2026-10-08-lean-lemma3-bridge-piece.txt |
| MainDeps.lean | query | no | which constants OAI's main theorems depend on (Corollary 4 usage). It covers the SiegelZeros chain only: OAI also has a separate copy of the same code under OAI/NumberTheory/Jacobsthal/Siegel/, in namespace OAI.Erdos970, with its own `actual_biquadratic_rectangle_span` and `uniform_rectangular_multiplicity`. That copy is imported by the Jacobsthal, JacobsthalImproved and OstmannPrimes configs (results/2026-10-26-claims-ledger/jacobsthal-import-scan.txt). | results/2026-10-08-lean-main-closure-cor4-usage.txt |
| ReroutedDeps.lean | query | no | dependency scan after the rerouted comparator run, with the unmodified clone as control (SiegelZeros chain only, as above) | results/2026-10-09-lean-rerouted-comparator-deps.txt (adc7f12); results/2026-10-27-reroute-fd4aeeb/control-deps.log and reroute-deps.log (fd4aeeb) |
| corpus-queries/*.lean (6 files: HarmonicGrowth, NavierStokes; Challenge/Solution) | query | no | audit queries on two corpus configs | results/2026-10-11-corpus-headline/query-*.log |
| paper-prep/*.lean (4 files: HG/NS Challenge/Solution PrintAxioms) | query | no | `#print axioms` for the same two configs | results/2026-10-20-paper-prep/wsl/task2-query-*.log |
| extended-replay/*.lean (233 files: 227 `<Config>-axioms.lean`, 3 `-audit-challenge.lean`, 3 `-audit-solution.lean`) | query (generated by scripts/extended_plan.py) | no | `#print axioms` per config, and placeholder audits | results/2026-10-21-extended-replay/runs/<Config>-axioms.log and -audit-*.log |

The generated query folders are one row each, not one row per file. Their per-file results follow the naming pattern shown.
