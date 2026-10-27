# Claims ledger for the cs.LO paper (2026-10-26)

Repository HEAD at ledger time: 654b978cc114b9a82b3b6fdf9594dcad1f1fd0ba (local; origin/main bb6f197).

Built by `python -I results/2026-10-26-claims-ledger/build_ledger.py .`, which resolves every path:line by substring and fails on any mismatch. There were no new Lean runs, apart from collecting the in-progress rectangle re-check.

Rows: 90.

- By status: {'FOUND': 86, 'PENDING': 1, 'MISSING': 3}.
- By label: {'COMPUTED': 78, 'INFERRED': 7, 'STATED': 5}.
- DOC-ONLY: 0 (faithfulness findings are INFERRED, per Joe).

Files:

- ledger.tsv; gaps.md; citations-needed.md.
- challenge-copies.tsv; only-use-search.txt; patch-apply-check.txt; axioms-rectangle-2026-10-26.txt.
- statement-checks-final-v2.log: copied from WSL /lean-build-final-v2.log, sha256 2f3d3814...
- zenodo/r*.json: record JSON, fetched read-only 2026-10-26 16:02.

## By paper section

### Section 3 (15 rows; {'FOUND': 15}; {'COMPUTED': 11, 'INFERRED': 4})

Solid: the four challenge files are hashed at fd4aeeb, and the three StatementChecks copies are byte-identical to the originals (challenge-copies.tsv). All 34 Lean sub-claims of the statement checks are standard-axiom only (the v2 log, now copied into this folder). The NonVacuity lemmas have recorded axioms lines and an unchanged file hash. The audit post on #29 is pinned by API. Not solid: the faithfulness findings themselves are INFERRED readings of Lean against paper text (argument in docs/statement-check-*.md). The Hecke L-function row also rests on Joe's ruling and on one identification that is still INFERRED (6 generators per ideal).

### Section 4 (6 rows; {'FOUND': 6}; {'COMPUTED': 6})

Solid: OAI's Corollary 4 is located and hashed, identical at adc7f12 and fd4aeeb. Its single use in the SiegelZeros tree (line 138) is established two ways: a text search over all 122,458 OAI .lean files, and the before/after closure scans (116,314 -> 92,658). The CategoryTheory/AlgebraicGeometry removal is counted under both conventions (9,936 referenced; 10,107 full dump). Caveat: the text search also finds a separate copy of the code under OAI/NumberTheory/Jacobsthal/Siegel/ (theorem at :481, used at :140). "Only use" holds for the SiegelZeros chain, not for OAI as a whole.

### Section 5 (25 rows; {'FOUND': 23, 'PENDING': 1, 'MISSING': 1}; {'COMPUTED': 25})

Solid: the source of every cited declaration is pinned by path:line and LF sha256. The canonical copies are identical (Bridge.lean, PaperLemma3/Lemma3.lean and Lemma3Bridged.lean). Axioms are standard at adc7f12 (2026-10-08) and again at fd4aeeb under the 45-family deny list (2026-10-26). The standalone nanoda check (61,810 declarations) passes and both negative controls are rejected. The exact small-N execution covers 540 instances with 28 checks each, and confirms the steps at N = 2, 3 only. The two working drafts with sorry (Lemma3_Cor4.lean, Lemma3_Bridge.lean) are recorded, and the canonical Bridge.lean imports neither. Pending: axioms compiled from the comparator copy itself. Missing: a saved #check of AlgEquiv.mul_apply (only printed to the session).

### Section 6 (7 rows; {'FOUND': 6, 'MISSING': 1}; {'COMPUTED': 7})

Solid: the reroute is one file, +2/-1, and the challenge file is unchanged. The comparator run accepted it with both kernels (9,244 jobs, exit 0) at adc7f12, with nanoda 3a24072, under the 5-family filter. The rerouted scan matches only our two lemmas, and the patched PNT HadamardSupport import is recorded. The patch applies cleanly at fd4aeeb (read-only check). Not done: the reroute has never run at fd4aeeb or under the 45-family deny list (NEW RUN NEEDED).

### Section 7 (17 rows; {'FOUND': 17}; {'COMPUTED': 9, 'INFERRED': 3, 'STATED': 5})

Solid: the 189 results (187 at fd4aeeb plus 2 pilot at adc7f12; 178/9) and the f67473b 9/9 are sourced. So are the 227 results (official 205/6/1/15, kept separate from the unofficial B3 status of Catalan and KMedianThreshold) and the export-size matches (146; 11 here, 13 with two from the extended records). Neal's figures are STATED at his pinned commit 1ca7ff2 and the issue comment URLs. INFERRED: the assignment of configs to the three failure classes, an interpretation of per-config outcomes. It is measured by backtrace only for RoundTables (STATED).

### Section 8 (12 rows; {'FOUND': 11, 'MISSING': 1}; {'COMPUTED': 12})

Solid: the sandbox history is sourced at each step: the README wrapper for the first SiegelZeros run, the 5-family filter from 29_comparator_nanoda.sh (2026-10-08 14:18), the vsock/PPPOX/ALG gaps, systemd-run rejecting "none", the 45-family list, and t25 (138/138 errno 97). So are the WSL memory changes (16 -> 24 GB at 2026-10-21 13:56:21, 3 results before; 24 -> 20 GB on 10-22) and MemoryMax non-enforcement with the v1-cgroup workaround. Weak: the MemoryMax test output was printed to the session only; the record is our own script header and MANIFEST. Missing: any SiegelZeros comparator run under the 45-family list.

### Section 9 (8 rows; {'FOUND': 8}; {'COMPUTED': 8})

Solid: the five DOIs, from record JSON fetched read-only on 2026-10-26 and copied here; the GitHub tags with object ids; the toolchain and nanoda pins. Note: the corpus record archives repo commit 60552ee and openai/math fd4aeeb. The packet records archive the reviewer-packet-* tags at openai/math adc7f12.

## INFERRED rows and what each rests on

- L002 (QuasiRiemannHypothesis: the Lean challenge statement matches the paper statement (finding ...): rests on: reading of Lean statement against paper text (argument in docs/statement-check-QuasiRiemannHypothesis.md); Lean sub-claims (non-vacuity, series identities, holomorphy) are COMPUTED in statement-checks-final-v2.log
- L004 (DirichletSevenEighths: the Lean challenge statement matches the paper statement (finding o...): rests on: reading of Lean statement against paper text (argument in docs/statement-check-DirichletSevenEighths.md); Lean sub-claims (non-vacuity, series identities, holomorphy) are COMPUTED in statement-checks-final-v2.log
- L006 (HeckeSevenEighths: the Lean challenge statement matches the paper statement (finding of th...): rests on: reading of Lean statement against paper text (argument in docs/statement-check-HeckeSevenEighths.md); Lean sub-claims (non-vacuity, series identities, holomorphy) are COMPUTED in statement-checks-final-v2.log
- L008 (SiegelZeros: the challenge statement matches Theorem 1 of the paper (hypotheses primitive,...): rests on: reading of Lean statement against paper text (docs/paper-map.md); type equality challenge vs solution is COMPUTED in results/2026-10-08-lean-type-compare.txt
- L063 (nanoda failure class 1: members and evidence (matrix-v3.tsv cells, COMPUTED or STATED per ...): rests on: per-config outcomes across nanoda builds (COMPUTED or STATED cells); class membership is an interpretation of those outcomes, measured by backtrace only for RoundTables (STATED, #55)
- L064 (nanoda failure class 2: members and evidence (matrix-v3.tsv cells, COMPUTED or STATED per ...): rests on: per-config outcomes across nanoda builds (COMPUTED or STATED cells); class membership is an interpretation of those outcomes, measured by backtrace only for RoundTables (STATED, #55)
- L065 (nanoda failure class 3: members and evidence (matrix-v3.tsv cells, COMPUTED or STATED per ...): rests on: per-config outcomes across nanoda builds (COMPUTED or STATED cells); class membership is an interpretation of those outcomes, measured by backtrace only for RoundTables (STATED, #55)

## Update 2026-10-26 22:01 (appended; ledger.tsv unchanged)

- **L032 is now FOUND.** Its source is axioms-comparator-copy-2026-10-26.txt. All nine declarations of the comparator copy (Lemma3.interpolation, cor4_rpow_nat, cor4_cube, cor4_real, cor4_budget, rectangle, bridge_descent, bridge_main, actual_biquadratic_rectangle_span_via_lemma3) depend on exactly [propext, Classical.choice, Quot.sound]. Run at openai/math fd4aeeb under the 45-family deny list, from the byte-identical files installed for the accepted run.
- **Counts after this update:** FOUND 87, MISSING 3, PENDING 0, out of 90 rows.

## Update 2026-10-26 23:10 (appended): ledger-v2.tsv

**Counts:** ledger-v2.tsv has 98 rows, all FOUND (COMPUTED 86, INFERRED 7, STATED 5). gaps.md (update of the same time) maps the v1 gaps to their v2 rows.

**Section 6 now has the fd4aeeb runs.** They were made under the 45-family deny list with the official nanoda 3a24072:
- the SiegelZeros control, ACCEPT_BOTH;
- the reroute (+2/-1, comparator-copy files 1ce196f5…/af401514…), ACCEPT_BOTH;
- both dependency scans, identical to the 2026-10-09 adc7f12 blocks (116,314 and 92,658 constants).

**Section 4 now records the separate Jacobsthal/Siegel copy of OAI's Corollary 4.** It lives in namespace OAI.Erdos970 and uses its own uniform_rectangular_multiplicity. Its subtree is imported by the Jacobsthal, JacobsthalImproved and OstmannPrimes configs.

**Section 5 now records MainRerouted.lean** as a superseded metaprogram (#reroute + addDecl), not cited.
