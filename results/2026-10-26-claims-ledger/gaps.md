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
