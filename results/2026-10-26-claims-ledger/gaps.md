# Gaps in the claims ledger (2026-10-26). None are closed here.

| id | claim | status | cheapest way to close |
|---|---|---|---|
| L032 | Axioms of interpolation, rectangle and via_lemma3 compiled from the comparator copy (PaperLemma3/Bridge.lean itself), fd4aeeb, deny list. | PENDING | Run the prepared q77 driver (compile PaperLemma3/Lemma3 to an olean under /tmp, feed Bridge.lean plus #print axioms on stdin; no build). Scheduled as the separate step after the ledger. |
| L041 | (sigma * tau) x = sigma (tau x) in Mathlib d13f23b (AlgEquiv.mul_apply), so the third row of A is phi(sigma(tau(1, a, b, ab))). | MISSING | Re-run `printf "import Mathlib\n#check @AlgEquiv.mul_apply\n" | lake env lean --stdin` under 75d (about 10 s), saving the output here. Or cite the Mathlib source line of AlgEquiv.mul_apply at d13f23b (read-only). |
| L050 | The reroute has not been run at openai/math fd4aeeb or under the 45-family deny list. | MISSING | NEW RUN NEEDED: the reroute at fd4aeeb under the 45-family deny list, with a 67d-style comparator run on a scratch copy of the clone plus the PaperLemma3 modules and the +2/-1 patch. The patch applies cleanly (patch-apply-check.txt). About 25 min plus the SiegelZeros build. Not run. |
| L079 | No SiegelZeros comparator run exists under the 45-family deny list (only the rectangle/interpolation axioms re-check). | MISSING | Closed by the same NEW RUN as the reroute item. Alternatively, run the unmodified SiegelZeros comparator under 67d at fd4aeeb (about 15 min). |

## Weak or qualified rows (status FOUND, but worth knowing)

- **MemoryMax not enforced:** the 600 MB-under-200M test output was printed to the session only. The ledger row rests on our own script header (140_matrix_run.sh) and MANIFEST.txt. Cheapest fix: re-run the 2-unit test (seconds) and save the output.
- **Statement-check axioms:** the docs (docs/statement-check-summary.md:41, docs/statement-check-HeckeSevenEighths.md:51, docs/log.md:664) cite results/2026-10-20-statement-checks/lean-build-final-v2.log, which never existed. The file was written to WSL `/`. It is now copied here; the docs path is still wrong. Cheapest fix: an appended dated note in those docs pointing here.
- **Only use:** holds within the SiegelZeros tree. OAI also contains a separate copy under OAI/NumberTheory/Jacobsthal/Siegel/ with its own use at :140, so the paper should say "in the SiegelZeros chain".
- **Faithfulness findings (4 rows) and failure classes (3 rows):** INFERRED by design (reading and interpretation); see LEDGER.md.
- **Fresh rectangle re-check:** this used Lemma3Bridged.lean (canonical, identical text), not the comparator-copy files the paper cites. The PENDING row closes that.

## Update 2026-10-26 22:01 (appended)

- **L032 (PENDING) is closed** by axioms-comparator-copy-2026-10-26.txt: all nine declarations depend only on the standard axioms. The remaining gaps are L041, L050 and L079 (MISSING).

## Update 2026-10-26 23:10 (appended): ledger-v2.tsv

**ledger-v2.tsv** (`python -I results/2026-10-26-claims-ledger/build_ledger.py . ledger-v2.tsv`) has 98 rows: FOUND 98, MISSING 0, PENDING 0, DOC-ONLY 0, CONFLICT 0. By label: COMPUTED 86, INFERRED 7, STATED 5. ledger.tsv (v1, 90 rows) is unchanged. The ids are renumbered in v2.

| v1 gap | how it was closed | v2 rows |
|---|---|---|
| L032 (PENDING) | axioms-comparator-copy-2026-10-26.txt | the same claim, FOUND |
| L041 (MISSING) | mathlib-algequiv-mul_apply.txt: Mathlib d13f23b, Mathlib/Algebra/Algebra/Equiv.lean:663, plus the saved #check | the same claim, FOUND |
| L050 (MISSING: reroute at fd4aeeb under the deny list) | results/2026-10-27-reroute-fd4aeeb/: comparator ACCEPT_BOTH, exit 0; scan identical to 10-09 | L095, L096, L097 |
| L079 (MISSING: no SiegelZeros comparator run under the deny list) | the same folder: control comparator ACCEPT_BOTH, exit 0; scan identical | L093, L094 |

**New rows from the step-1 read-only checks:**
- L089: the Jacobsthal copy depends on its own Erdos970 lemmas.
- L090: three configs import the Jacobsthal subtree.
- L091: MainRerouted.lean is a metaprogram.
- L092: full Comparator and lean4export commits.
- L098: the MemoryMax test, rerun.

**Still open (weak or qualified, not gaps):**
- The statement-check docs still cite a v2 log path in results/2026-10-20-statement-checks/ that never existed. The log is now in this folder.
- "Only use" holds for the SiegelZeros chain. L089 and L090 record the separate Jacobsthal copy, which is imported by three configs (an import closure, not a declaration closure; no declaration scan was run).
- The 7 INFERRED rows are inferred by design.
- ContinuumCoulombHardness is permanently deferred (results/2026-10-27-reroute-fd4aeeb/optional/README.md).
