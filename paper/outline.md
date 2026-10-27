# Paper outline (LIPIcs, about 15 pages): from the claims ledger, v4 (2026-10-27)

Source of claims: results/2026-10-26-claims-ledger/ledger-v7.tsv (146 rows: v6 added v6:L143-L144; v7 adds v7:L145-L146, which supersede v4:L100-L101, and fills read_by for the four challenge readings).
- Other inputs: citations-needed.md, gaps.md, LEDGER.md and id-stability.md (same folder); results/2026-10-27-reroute-fd4aeeb/SUMMARY.md; lean-checks/README.md (commit 758b44f).
- The row-by-row mapping is in paper/claim-map.tsv.
- Ids are append-only (id-stability.md). Every id here carries its version. v2:, v3:, v4: and v5: ids agree wherever the id exists; only v1:L050-L090 differ (erratum-ids.md). Rows added in v5 are cited as v5:, all others as v4:.

Conventions:
- Every claim cites its ledger id. The value after "=" is copied from the ledger's value column. The exception is v4:L057, which is rendered as counts at Joe's request.
- [INFERRED Lxxx] and [STATED Lxxx] stay visible in the prose. Rows without a tag are COMPUTED.
- No claim is BLOCKED any more. All six statement-match rows (v7:L002, v7:L004, v7:L006, v7:L008, v7:L145, v7:L146) have read_by "Read by J. Reilly, 2026-10-27: MATCH" (docs/log.md:1802-1807). The earlier rule was that a claim resting on a statement-match row whose read_by did not include Joe was not written as prose until Joe's reading is recorded.
- A "Missing claims" item has no ledger row. It gets no value.
- Vocabulary:
  - "accepted by Comparator with both kernels" (never "verified");
  - "replay" (never "verification");
  - "the paper's Theorem 1" (the source numbers it Theorem 1, v4:L106);
  - "matches" for comparisons done by reading;
  - "proved" for Lean proofs only.
  - Lean statements are quoted from source files.
- Numbering: amsart with one shared counter (v4:L106-L111 note). The results are Theorem 1, Lemma 2, Lemma 3, Corollary 4, Remark 5, Lemma 6, Lemma 7.

## 0. Title and abstract (0.5 page)

Purpose: state the four results in the abstract, each backed by ledger rows.

Abstract claims (revised 2026-10-27; abstract text is Joe's):
1. The SiegelZeros challenge has two checked theorems with equivalent statements, proved by two OAI routes, neither through the paper's proof of Lemma 3.
   - Two checked theorems (v11:L147). The statements are not the same Lean proposition (v11:L198), but they are proved equivalent in Lean (v11:L251 = [propext, Classical.choice, Quot.sound]).
   - OAI's formalization.yaml names exists_absolute_real_zero_gap as the main result [STATED v11:L202].
   - The main route gets its spanning hypothesis from a local Bezout argument (v11:L201, v11:L252, v11:L255) and does not use actual_biquadratic_rectangle_span (v11:L200).
     - Wording check: on the way it proves RectangularAssertion, a zero test with Corollary 4's exact bounds, 32 H^(2/3) N^(4/3) and 32 H^(-1/3) N^(4/3) (v11:L253).
     - So "without Corollary 4" is true of OAI's Corollary 4 theorem, not of a Corollary-4-shaped statement. The abstract should say "without OAI's Corollary 4 theorem" or name the zero test.
   - The second route proves Corollary 4 by a multiplicity estimate: the control scan (v11:L019 = 116314 constants in closure) and the two invocation lines (v11:L099).
2. The paper's Lemma 3 and Corollary 4 are proved in Lean, and the Lean statements match the paper's.
   - Lemma3.interpolation (v4:L022, v4:L024) and Lemma3.rectangle (v4:L025).
   - Axioms of all nine comparator-copy declarations (v4:L032) = [propext, Classical.choice, Quot.sound].
   - The statement match: [INFERRED v7:L145] = MATCH and [INFERRED v7:L146] = MATCH, both Read by J. Reilly, 2026-10-27: MATCH.
3. The +2/-1 substitution is in dirichletRealZeroBound_proof. The result is accepted by Comparator with both kernels at fd4aeeb under the 45-family deny list, and that theorem's closure no longer contains the three named OAI lemmas.
   - Diff (v11:L097) = 1 file, +2/-1.
   - Verdict (v11:L095) = ACCEPT_BOTH; exit 0.
   - Scan (v11:L096) = 92658 constants in closure; matches only via_lemma3 and interpolation (v11:L051).
   - exists_absolute_real_zero_gap is untouched: 107760 constants in both clones, with none of the three lemmas (v11:L148, v11:L149).
   - Deny list (v11:L076) = 45 families.
4. Every config with a verdict on both sides agrees with an independent replay on a second platform: 402 of 402.
   - Outcomes (v11:L141): 416 compared; 402 agree; 0 disagree; 14 no verdict here; 0 no verdict there. His side is STATED (cmp-all/all.jsonl at 1ca7ff2).
   - Export sizes equal for v11:L060 = 146 and v11:L061 = 11 (13 incl. 2 from extended records).

Missing claims: none.

Citations: the paper (by title, date October 1, 2026, author OpenAI, openai/math path and sha256; v6:L143); openai/math at both commits; Comparator; nanoda_lib; nealmcb/openai-math-lean-tooling at 1ca7ff2.

## 1. Introduction (1.5 pages)

Purpose: give the four results and the boundary of what is claimed.

Claims:
- The four abstract claims, with the same ids as Section 0. Each is restated in one sentence with a forward pointer.

Not claimed (scope statements, no values):
- Nothing about the paper's analytic sections (Lemma 2, v4:L107).
- No specialist review of the mathematics.
- Statement faithfulness is checked by reading [INFERRED v7:L002, v7:L004, v7:L006, v7:L008; Read by J. Reilly, 2026-10-27: MATCH].
- The reroute concerns the SiegelZeros chain only. Three further configurations load modules from a separate copy of this code (namespace OAI.Erdos970), with its own multiplicity estimate (v4:L089 = Erdos970 copies; v4:L090 = 3 of 416).
- Nothing about the explicit constant beyond a pointer to arXiv:2610.15483.

Missing claims: none.

Citations: the paper; arXiv:2610.15483 (the explicit-constant pointer only).

## 2. Background (1.5 pages)

Purpose: give a reader what Comparator, nanoda and the challenge statement are, and the shape of the paper's proof.

Claims:
- Comparator's three checks, from its README at d03acab:
  - same statement [STATED v4:L102] = "Prove the same statement as provided in `Challenge`";
  - axioms [STATED v4:L103] = "Use no more axioms than listed in `permitted_axioms`";
  - Lean kernel [STATED v4:L104] = "Be accepted by the Lean kernel". External kernels receive a file containing the solution export.
- nanoda's input [STATED v4:L105] = JSON config + lean4export export file. With enable_nanoda: true, Comparator passes a nanoda-style config.json.
- The challenge statement, quoted at fd4aeeb from /home/checker/math/lean/ComparatorChallenges/SiegelZeros.lean:
  - exists_absolute_real_zero_gap, lines 8-14;
  - WeightedTorusJets.dirichletRealZeroBound_proof, lines 19-25.
  - File sha256 (v4:L007) = bedaac0248a641910f79a380d9702d82c6bfbbfd3760a69d27c72c5d8fb136ce. It is identical at adc7f12 (v4:L007: "unchanged at fd4aeeb").
- The paper's lemmas, with line ranges only (no claim about how they combine):
  - [STATED v4:L106] = Theorem 1, tex 66-73;
  - [STATED v4:L107] = Lemma 2, tex 181-194;
  - [STATED v4:L108] = Lemma 3, tex 252-267;
  - [STATED v4:L109] = Corollary 4, tex 410-420;
  - [STATED v4:L110] = Lemma 6, tex 517-524;
  - [STATED v4:L111] = Lemma 7, tex 598-604.
- The paper's Theorem 1 beside the challenge: [INFERRED v7:L008] = MATCH; Read by J. Reilly, 2026-10-27: MATCH.
- Tool pins:
  - v4:L087: Lean 4.34.1 (5045d005), Mathlib d13f23b, Comparator v4.34.0 d03acab, lean4export v4.34.0 076e8e5;
  - v4:L092: full commits;
  - v4:L088: 3a24072 / f67473b / 37cb87b / 37cb87b+patch, with 3a24072 the official one.

Missing claims: none. Section 2 makes no claim about how the lemmas combine.

Citations: Comparator, nanoda_lib, lean4export, Lean 4, Mathlib, the paper (v6:L143), the 7/8 paper (by title, date 30 September 2026, author OpenAI, path and sha256; v6:L144).

## 3. Statement faithfulness (2.5 pages; rebudgeted 2026-10-27 from 1.5, for the per-challenge reasoning tables)

Purpose: show whether the four family-003 challenge statements match the paper's statements, and say which parts rest on reading and which on Lean.

Table 1 (one row per challenge).

| challenge | file sha256 (fd4aeeb) | finding | read_by (ledger-v7) |
|---|---|---|---|
| QuasiRiemannHypothesis | v4:L001 = 065f8c9a01d28db78c8b1bfc5083b535082a2d2aac2230d563f98b8caa812cc5 | [INFERRED v4:L002] = MATCH (except s = 1, covered by Mathlib's junk value) | Read by J. Reilly, 2026-10-27: MATCH |
| DirichletSevenEighths | v4:L003 = 8fb13ad977bca104591fcbc6ef01a58496e7385053c9b1445f95749afc0eff54 | [INFERRED v4:L004] = MATCH | Read by J. Reilly, 2026-10-27: MATCH |
| HeckeSevenEighths | v4:L005 = cb5e404fa65a502c0a9006b9ad45c28914feb79e4b7b1ffcf05e4af82ed0cfc2 | [INFERRED v4:L006] = MATCH (L-function row by Joe's ruling 2026-10-20; one identification INFERRED) | Read by J. Reilly, 2026-10-27: MATCH (the 6-generator identification re-read and accepted) |
| SiegelZeros | v4:L007 = bedaac0248a641910f79a380d9702d82c6bfbbfd3760a69d27c72c5d8fb136ce | [INFERRED v4:L008] = MATCH | Read by J. Reilly, 2026-10-27: MATCH |

Claims:
- Lean sub-claims of the statement checks: v4:L009 = 34 declarations, all exactly [propext, Classical.choice, Quot.sound].
  - Source: results/2026-10-26-claims-ledger/statement-checks-final-v2.log.
- Non-vacuity lemmas, each with its axioms line = [propext, Classical.choice, Quot.sound]:
  - NonVacuity.hypotheses_satisfiable (v4:L011);
  - NonVacuity.quadChar_LFunction_eq_LSeries (v4:L012);
  - NonVacuity.quadChar_LFunction_one_ne_zero (v4:L013);
  - NonVacuity.specialization (v4:L014).
- Footnotes:
  - NonVacuity.lean source hash (v4:L015), LF sha256 b9fae4da5517a97da50d3fdb5356329f03f00b7ab935a448a999b2c59b24d9f9.
  - The audits were posted on grwtsk/openai-math #29 (v4:L010 = 2026-10-20T16:56:00Z).
  - The Hecke ruling and the one INFERRED identification (v4:L006 value).

Missing claims: none. The readings are INFERRED by design.

Citations: the paper; openai/math fd4aeeb; Mathlib; grwtsk/openai-math #29.

## 4. Two formal routes (1.5 pages)

Purpose: the two checked theorems, OAI's two routes to them, where each gets its spanning statement, and how those statements compare with Corollary 4 (draft: paper/draft/sec4-gap.tex, rewritten 2026-10-27 from v11:L147, L198, L200-L202, L251-L257).

Claims:
- Location of Corollary 4: actual_biquadratic_rectangle_span at InvariantJetLinearMap.lean:471-484, identical at adc7f12 and fd4aeeb (v4:L016 = 09b8bd7fa82365e69caebfad466d039d85084595376766a731945fa5c11a2bdc).
- Its proof invokes the multiplicity estimate at lines 493 and 496 (v4:L099; the two lines are quoted in Section 0).
- Its only use:
  - Within the SiegelZeros tree, the theorem is used only at CharacterGlobalGreedyDeterminantMasterBounds.lean:138 (v4:L017 = 1 use site).
  - After line 138 is replaced, the closure of dirichletRealZeroBound_proof no longer contains it (v4:L018 = absent).
- The separate Jacobsthal copy, at import level only:
  - It depends on its own Geometry.uniform_rectangular_multiplicity and Geometry.source_rectangle_span_of_polynomial_zero_test (v4:L089 = Erdos970 copies). Source reading only.
  - Three configs have a module of that subtree in their solution import closure (v4:L090 = 3 of 416). This is an import closure, not a declaration closure.
- Control scan:
  - v4:L019 = 116314 constants in closure (adc7f12);
  - v4:L094 = 116314 (fd4aeeb, identical block).
- The two checked theorems and OAI's main result (added 2026-10-27):
  - The challenge has Comparator check two theorems (v8:L147). They are not the same Lean proposition: one takes the zero hypotheses curried, the other as a conjunction (v9:L198). They are logically equivalent [INFERRED v9:L199].
  - OAI's lean/formalization.yaml names exists_absolute_real_zero_gap as the main result for the SiegelZeros config; neither it nor lean/docs/003.md names the paper's Theorem 1 [STATED v9:L202].
  - exists_absolute_real_zero_gap is proved through uniform_exclusion_of_local_isolated_bezout and uniform_exclusion_of_actual_cutoff (v9:L201). Its closure (107760 constants) has no 7/8-development constant, no dirichletRealZeroBound_proof and no actual_biquadratic_rectangle_span (v9:L200; v8:L148, v8:L149).
  - So the reroute substitutes Lemma 3 into dirichletRealZeroBound_proof only. The sentence "does not use the multiplicity estimate" names the three lemmas and applies to that theorem.
- CategoryTheory and AlgebraicGeometry names removed by the reroute:
  - v4:L020 = 9936 (6901 + 3035), referenced-names convention (names reachable from the root through types and values, as #find_deps);
  - v4:L021 = 10107 (7048 + 3059), full-dump convention (every declaration in the lean4export dumps).
  - Recommendation: use v4:L020 in the text, because it uses the same reachability convention as v4:L019 and v4:L051. Put v4:L021 in a footnote with its definition.

Missing claims: none.

Citations: openai/math at adc7f12 and fd4aeeb.

## 5. Lemma 3 and Corollary 4 (3 pages)

Purpose: present the Lean proof of the paper's Lemma 3 and Corollary 4, and how it is bridged to OAI's statement of Corollary 4.

Statements (quoted from source, side by side with the paper):
- Lemma 3:
  - Lean: lean-checks/comparator-copy/PaperLemma3/Lemma3.lean:817-825 (v4:L024 = 1ce196f54fa98689bbea6bd74f2abdb110f5cbcca2eecddcca9316b8af465283), equal to lean-checks/Lemma3.lean:816-825 (v4:L022).
  - Paper: [STATED v4:L108] tex 252-267.
  - Match: [INFERRED v7:L145] = MATCH. Read by J. Reilly, 2026-10-27: MATCH.
- Corollary 4:
  - Lean: lean-checks/comparator-copy/PaperLemma3/Bridge.lean:96-109 (v4:L025).
  - Paper: [STATED v4:L109] tex 410-420.
  - Match: [INFERRED v7:L146] = MATCH. Read by J. Reilly, 2026-10-27: MATCH.
- The box Pt is defined at Lemma3.lean:42 (v4:L023 = Pt).
- Copies are identical (v4:L029 = identical).

Proof architecture (v4:L136; comparator copy, line ranges; main proof Lemma3.interpolation 816-985):
- Opening, eq:moments (not one of the six named steps): exists_annihilator 624-661, p5_PtSub 591-612; main proof 829-845.
- Dimension count, zeros of R: four_hull_subset_cube 663-681, exists_vanishing 683-738; main proof 846-885.
- Supporting face and nearest point: exists_lattice_nonvanishing 740-770, exists_nearest 87-148 (with p1_var_ineq 57-85, p1_coord_le_sqd 51-55, p1_dot_self_nonneg 47-49), quarter_mem_face 150-208; main proof 886-909.
- Vertex choice: exists_heavy_vertex 224-299; main proof 910-916.
- Off-face vanishing: closer_point 301-340 (with p2_dot_expand 213-218, p2_dot_self_nonneg 220-222); main proof 917-939.
- Lagrange polynomial Q: exists_int_hyperplane 371-432 (with p3_g 342-352, p3_g_apply 354, p3_clear 356-369), int_comb_ne_zero 434-443, exists_lagrange 471-586 (with p4_linP 445-448, p4_eval_linP 450-455, p4_deg_linP 457-461, p4_rL 463-465, p4_rL_apply 467-469); main proof 940-947.
- Final contradiction: exists_translate 772-812; main proof 948-985.
- Not placed, because several steps share them: zR 29-30, zC 32-33, emb 35-36, sqd 38-39, Pt 41-43, p5_eval_aeval 614-620.

The bridge (each item quoted from Bridge.lean):
- The main theorem has exactly the type of OAI's theorem, by type_of% (v4:L036 = type_of%; v4:L028 = Lemma3.actual_biquadratic_rectangle_span_via_lemma3).
- The embedding is chosen as IsAlgClosed.lift (v4:L037 = IsAlgClosed.lift).
- The kernel vector is c = biquadraticCoefficients (v4:L038 = ![1, a⁻¹, -b⁻¹, -(a * b)⁻¹]). ker A = span {c} is proved inline (v4:L039 = hker; v4:L027).
- bridge_descent does the descent from C to K and the restriction to an injective family (v4:L040 = bridge_descent; v4:L026).
- AlgEquiv.mul_apply (v4:L041 = (e₁ * e₂) x = e₁ (e₂ x)). Quote the source line, Mathlib d13f23b Mathlib/Algebra/Algebra/Equiv.lean:663: `theorem mul_apply (e₁ e₂ : A₁ ≃ₐ[R] A₁) (x : A₁) : (e₁ * e₂) x = e₁ (e₂ x) :=`.

Reused OAI setup lemmas:
- source_same_witness_hyperplane (v4:L042);
- biquadraticCoefficients_linearIndependent (v4:L043).

Axioms:
- Primary: v4:L032 = [propext, Classical.choice, Quot.sound].
- Corroboration: v4:L030 (2026-10-08, same value).
- Footnote: v4:L031 (same value).

Standalone nanoda:
- v4:L033 = 61810 declarations checked.
- Controls: v4:L034 = rejected (exit 1); v4:L035 = rejected (exit 101).
- The run's sandbox is in Section 8 (v4:L124).

Small-N checks:
- v4:L046 = 540 instances, 28 checks each. This covers N = 2, 3 only.

Working drafts with sorry, in a footnote that names them as not cited:
- v4:L044 = working draft (sorry);
- v4:L045 = working draft (sorry).

Missing claims: none.

Citations:
- the paper;
- Mathlib d13f23b;
- nanoda_lib;
- Fischler, Compos. Math. 141 (2005): write "cited by the paper as [Fischler, Theorem 1.1 and Lemma 1.3]" (tex:155). Do not characterize the results; the numbering was not checked against a copy.

## 6. The reroute (1.25 pages; rebudgeted 2026-10-27 from 2)

Purpose: show that substituting the Lean proof of Corollary 4 into OAI's chain gives a proof accepted by Comparator with both kernels, and that the multiplicity estimate drops out.

Primary record: fd4aeeb, 2026-10-27 runs (results/2026-10-27-reroute-fd4aeeb/).

Table 2:

| run | verdict | dependency scan | prebuild | comparator run | guard |
|---|---|---|---|---|---|
| control | v4:L093 = ACCEPT_BOTH; exit 0 | v4:L094 = 116314 constants in closure | v4:L113 = 11min 19.935s; 9243 jobs | v4:L116 = 842 s; max RSS 7707508 kB; cgroup max_usage 7412195328 B; oom_kill 0 | v4:L118 = 0 LIMIT lines; 0 stops |
| reroute | v4:L095 = ACCEPT_BOTH; exit 0 | v4:L096 = 92658 constants in closure | v4:L114 = 1min 39.395s; 9245 jobs | v4:L117 = 659 s; max RSS 7662352 kB; cgroup max_usage 6280855552 B; oom_kill 0 | (same) |

- Footnote on the prebuild difference [INFERRED v4:L115] = incremental rebuild. The reroute ran in the same clone after the control, so lake rebuilt only the two new modules, the patched module and its dependents.

Clone setup (wording: "local clone of fd4aeeb; package directory reused read-only from the original clone; OAI closure built from scratch"):
- v4:L119 = local clone; packages read-only bind mount; write refused.
- v4:L120 = build dir born 22:19:37 (control prebuild start 22:19:09). This is computed from the clone's birth times and reflog, so "built from scratch" is a computed claim.
- The ledger notes on v4:L093 and v4:L095 say "fresh local clone". The paper does not use "fresh clone" alone.

Claims:
- Installed files and patch (v4:L097 = 1 file, +2/-1).
- Footnote: the patch applies at fd4aeeb (v4:L050 = applies (git apply --check exit 0)).
- The rerouted chain still imports the patched HadamardSupport (v4:L052 = imported). Forward pointer to Section 8.

Corroboration at adc7f12 (2026-10-09):
- v4:L047 = 1 file, +2/-1;
- v4:L048 = bedaac0248a641910f79a380d9702d82c6bfbbfd3760a69d27c72c5d8fb136ce;
- v4:L049 = 9244 jobs; ACCEPT_BOTH; exit 0;
- v4:L051 = 92658, with the control v4:L019 = 116314;
- v4:L018 = absent.

Missing claims: none.

Citations: openai/math adc7f12 and fd4aeeb; Comparator; nanoda_lib; Lean 4.

## 7. Corpus context (1.5 pages)

Purpose: place the SiegelZeros result within the full replay of the openai/math corpus, with official and unofficial tools kept apart.

Table 3 (the one table):

| block | official tool set (nanoda 3a24072) | unofficial nanoda builds | independent replay [STATED] |
|---|---|---|---|
| 189 referenced configs | v4:L053 = 187 + 2; v4:L054 = 178 / 9 | v4:L055 = 9 of 9 (f67473b, UNOFFICIAL) | see the all-416 row |
| 227 unreferenced configs | v4:L056 = 212 / 15. v4:L057, as counts: ACCEPT_BOTH 205, LEAN_ACCEPT_NANODA_CRASH 6, TIMEOUT 1, NOT_CHECKED_HERE 15 | see next row | see the all-416 row |
| Catalan, KMedianThreshold | official: NOT_CHECKED_HERE (v4:L057). Lean-kernel Comparator runs here: v4:L121 = 369 s; exit 0 (KMedianThreshold), v4:L122 = 2234 s; exit 0 (Catalan) | v4:L058 = both kernels (unofficial nanoda) | [STATED v4:L067] = 10 |
| ContinuumCoulombHardness | not completed on this machine (memory) | none | mixed; see footnote |
| all 416 (nealmcb) | outcome comparison, COMPUTED here: v5:L141 = 416 compared; 402 agree; 0 disagree; 14 no verdict here | | [STATED v4:L065] = 416/416 (Comparator as shipped); [STATED v4:L066] = 401/416 (nanoda 3a24072 at 1 GiB stack) |
| export sizes | v4:L060 = 146 (0 differ, 14 not comparable); v4:L061 = 11 (13 incl. 2 from extended records) | | |

Claims:
- Failure classes:
  - [INFERRED v4:L062] = RoundTables group (8), Laughlin group (3), KMedianThreshold, Catalan;
  - [INFERRED v4:L063] = KaplanskyFinitelyPresented, GroupRingDeterminant, KaplanskyDirectFiniteness (COMPUTED); MatchingFPRAS, ContingencyTables, LogspaceEquality, RandomizedMeanPayoff, PeriodicGroup (STATED);
  - [INFERRED v4:L064] = SquareDifference.
- Footnotes:
  - the B3 patch [STATED v4:L068] = edd9824f5fd93c86d3f52acea1373a915ccfddf23db33c5e919f03f7c642bc30;
  - the sweep commit [STATED v4:L069] = 8199c74;
  - ContinuumCoulombHardness, the independent-replay cell ("mixed"). All records are nealmcb's, at 1ca7ff2:
    - Comparator accepts: [STATED v4:L132] = accepted; 923.63 s.
    - The standalone kernel-pair sweep on his export: [STATED v4:L133] = lean_rc 1 (454.4 s); nanoda_rc 1 (99.3 s).
    - nanoda retests: [STATED v4:L134] = f67473b: 0 / 130.1 s / 24.23 GiB; 0 / 114.3 s / 24.26 GiB; 134 / 28.6 s; 134 / 28.8 s; 998e0a8: 134 / 32.8 s.
    - The patched build: [STATED v4:L135] = pass 50.0 s 1.8GB; let fix alone: overflow 34 s 4GB (64 MiB), overflow 48 s 13GB (256 MiB).
    - Our side: v4:L059 = DEFERRED (permanent). No memory figures are given for our runs.
  - v4:L125-L128 are SUPERSEDED by v4:L132-L135, which tie the same records to 1ca7ff2.
- v4:L121 and v4:L122 are whole Comparator runs (build, export, checks), not the kernel replay alone.

Missing claims: none.

Citations:
- nealmcb/openai-math-lean-tooling at 1ca7ff2a0280760783ee2b198c0d6f2a1cfeaba4;
- nanoda_lib issues #55, #61, #62;
- openai/math fd4aeeb;
- Zenodo corpus record (v4:L084).

## 8. Threats to validity (1.25 pages)

Purpose: list what could make the results wrong or weaker than stated, with the evidence for each.

Claims:
- Kernel trust: Comparator's guarantees are the three in v4:L102-L104 [STATED]. They hold under its stated assumptions [STATED v4:L137, README lines 28-39, quoted in full in the ledger]. One of them is "The Lean kernel is correct (with `external_kernels` this can be reduced to "At least one of the Lean kernel or the `external_kernels` is correct")".
- Statement faithfulness rests on reading [INFERRED v7:L002, v7:L004, v7:L006, v7:L008, v7:L145, v7:L146; all Read by J. Reilly, 2026-10-27: MATCH]. The non-vacuity lemmas (v4:L011-L014) rule out a vacuous challenge; they do not establish faithfulness.
- The patched HadamardSupport dependency (v4:L052 = imported).
- The paper's analytic sections are out of scope (scope statement).
- Sandbox history:
  - v4:L070 = 5 families denied;
  - v4:L071 = blocked (errno 97);
  - v4:L072 = connected;
  - v4:L073 = AF_PPPOX, AF_ALG;
  - v4:L074 = ~AF_UNIX only;
  - v4:L075 = 2026-10-08 14:18;
  - v4:L076 = 45 families;
  - v4:L077 = 138 / 138 errno 97.
- WSL memory:
  - v4:L078 = ElementaryPositivity, KaplanskyDirectFiniteness, ShortEgyptianFractions;
  - v4:L079 = 20 GB;
  - MemoryMax: v4:L098 = not enforced; v1 cap kills (the test), with v4:L080 for the cap and guard design.
- The superseded metaprogram: v4:L091 = #reroute + addDecl, named as not evidence. results/2026-10-08-lean-main-rerouted.txt is not cited anywhere in the paper.

Per-run sandbox (Table 4). Each cell is the ledger's sandbox column for the cited rows.

| run | rows | sandbox |
|---|---|---|
| 2026-10-08 12:15 first SiegelZeros comparator (08_comparator.sh) | v4:L074 | Comparator README wrapper: systemd-run --user RestrictAddressFamilies=~AF_UNIX (IP open); not cited for any result |
| 2026-10-08 14:18 SiegelZeros comparator with nanoda (29_comparator_nanoda.sh) | v4:L075 | 5-family filter |
| 2026-10-08 Lemma3Bridged axioms | v4:L030 | systemd-run --user, checker, NoNewPrivs; 5-family filter |
| 2026-10-08 NonVacuity lemmas | v4:L011-L014, v4:L138 | sudo -u checker; no systemd-run; no address-family filter |
| 2026-10-08 standalone nanoda on Lemma3Bridged | v4:L033-L035, v4:L124 | sudo -u checker; no systemd-run; no address-family filter |
| 2026-10-09 rerouted comparator and scans, with the control scan (adc7f12) | v4:L018, v4:L019, v4:L049, v4:L051 | systemd-run --user, checker, NoNewPrivs; 5-family filter |
| corpus replay of the 189 | v4:L053-L055 | systemd-run --user, checker, NoNewPrivs; 5-family filter |
| 2026-10-20 statement-check build | v4:L009, v4:L123 | sudo -u checker; no systemd-run; no address-family filter |
| extended replay of the 227 | v4:L056, v4:L057 | systemd-run --user, checker, NoNewPrivs; 5-family filter |
| 2026-10-26 nanoda version matrix | v4:L062-L064 | system unit + setpriv to checker; 5-family filter; 16G v1 cgroup cap (step 5 under the 45-family list) |
| 2026-10-26 axioms re-checks and AlgEquiv.mul_apply | v4:L031, v4:L032, v4:L041 | 45-family list, checker, NoNewPrivs |
| 2026-10-26 Lean-kernel runs on Catalan and KMedianThreshold | v4:L058, v4:L121, v4:L122 | 45-family list + 16G v1 cgroup cap (67d) |
| 2026-10-26/27 fd4aeeb control and reroute | v4:L093-L097, v4:L113-L117 | 45-family list + 16G v1 cgroup cap (67r) |

- Three runs had no address-family filter. All three ran as sudo -u checker with no systemd-run unit:
  - the 2026-10-08 NonVacuity lemmas (v4:L138);
  - the 2026-10-08 standalone nanoda run on Lemma3Bridged (v4:L124);
  - the 2026-10-20 statement-check build (v4:L123).
- The primary SiegelZeros results (v4:L032, v4:L093-L097) ran under the 45-family list.

- What both kernel checks depend on [STATED v5:L142, Comparator README 77-83 and 175-194, lean4export README 1, 23, 27, 29, nanoda README 13]:
  - Shared: the Lake build of Solution in a landrun sandbox (Comparator steps 1 and 3); the lean4export export of Solution (steps 2 and 3), which holds the module and its transitive dependencies, without unsafe declarations or Expr.mdata by default; and Comparator's own statement and axiom checks (steps 4 and 5).
  - Lean kernel only: the replay of the Solution environment into the Lean kernel inside the Comparator process (step 6).
  - nanoda only: a separate process, given a file containing the solution export and a nanoda-style config.json.
  - [INFERRED, v5:L142 note] The environment replayed in step 6 is the one read from the export, given the README's policy of not loading .olean files. The READMEs do not say whether both kernels read the same export file.

Missing claims: none.

Citations: Comparator; grwtsk/openai-math #40 (comment 6431288875); nanoda_lib.

## 9. Artifacts (0.5 page)

Purpose: tell a reader exactly which files and records reproduce each result.

Claims:
- The repository commit to be tagged is TBD at the paper's final version. v4:L086 is cut and will be re-added at tag time (claim-map.tsv).
- Zenodo:
  - v4:L081 = 10.5281/zenodo.23269528;
  - v4:L082 = 10.5281/zenodo.23499651;
  - v4:L083 = 10.5281/zenodo.23523697;
  - v4:L084 = 10.5281/zenodo.23505836;
  - v4:L085 = 10.5281/zenodo.23269527.
  - The final deposit is held until the paper's final version.
- Canonical and comparator-copy files with sha256:
  - PaperLemma3/Lemma3.lean (v4:L024);
  - Bridge.lean (af401514808dde5bb913ce8e87cc5280b704a234ea324897d1a1ced1f218f250, from v4:L025-L028 sources);
  - Lemma3Bridged.lean (6ce38ac1ef33c8b46028205bb043718565b679175b63cc6fbf8089136554cdb4, v4:L029 source);
  - Lemma3.lean (ecdbf400b24f9241cd03cf383bdcd97ed71e4812578e66d7159a846447f7b1a7, v4:L022 source);
  - NonVacuity.lean (v4:L015).
- Clone setup (v4:L119, v4:L120).
- Pins: v4:L087, v4:L088, v4:L092.
- lean-checks/README.md.

- lean-checks/README.md: v4:L139 = c954fe424f8450ebbbadef60ed1649f94cbd84c25223a30389e2480fc5cd8bf9 (committed at 758b44f).

Missing claims:
- The tag commit.

Citations: Zenodo records; the repository.

## 10. AI-use disclosure (0.25 page)

Purpose: say what Claude Code produced, as facts with sources, and leave the human-review account to Joe.

Claims:
- v4:L129 = lean-checks 260 of 260; wsl-comparator 214 of 214; src 22 of 22. These are tracked files with at least one commit carrying a Co-Authored-By: Claude trailer; 174 of the 175 commits carry it. The full list is in v3-evidence/claude-trailer-files.txt.
- v4:L130 = 4 posts: grwtsk/openai-math #40, comment 6291050955 (2026-10-20); nanoda_lib #55, comment 6291244827 (2026-10-20); grwtsk/openai-math #29, comment 6296359378 (2026-10-20); nanoda_lib #61, comment 6431284502 (2026-10-26).
  - docs/log.md records these drafts as written in the session.
  - It records the 2026-10-09 #40 comment, a Lean Zulip post and the 2026-10-26 #40 follow-up with no drafter, so those are not listed.

> JOE WRITES THIS: the human-review sentences (what was reviewed by a person, how, and what was not).

Missing claims: none.

## Appendix candidates (not decided)

- A. Full 189 and 227 per-config tables.
- B. The +2/-1 diff in full (reroute-diff.txt).
- C. The full Lean statements of the bridge lemmas.
- D. The nanoda version matrix (matrix-v3.tsv), UNOFFICIAL.
- E. The sandbox probes (t22-t26) and the 45-family list.
- F. The small-N execution details (v4:L046).
- G. The 34 statement-check axioms outputs (v4:L009).
- H. The two count conventions for Section 4 (v4:L020, v4:L021).
- I. The per-run sandbox table in full, if Table 4 is too long for Section 8.

## Claims used in more than one section (risk of inconsistent restatement)

| ids | sections | what to keep consistent |
|---|---|---|
| v4:L019, v4:L094 | 0, 4, 6 | 116314 and "identical at fd4aeeb" |
| v4:L099 | 0, 4 | lines 493 and 496, quoted the same way |
| v4:L051, v4:L096 | 0, 6 | 92658 and the two matches |
| v4:L093, v4:L095 | 0, 1, 6 | "accepted by Comparator with both kernels", exit 0 |
| v4:L097, v4:L047 | 0, 6 | 1 file, +2/-1 |
| v4:L032 | 0, 5, 8 | nine declarations, standard axioms |
| v7:L145, v7:L146 | 0, 1, 5, 8 | [INFERRED] MATCH; Read by J. Reilly, 2026-10-27: MATCH |
| v7:L002, v7:L004, v7:L006, v7:L008 | 1, 2, 3, 8 | [INFERRED]; Read by J. Reilly, 2026-10-27: MATCH |
| v4:L016, v4:L017, v4:L018 | 0, 4, 6 | "only use" is within the SiegelZeros tree |
| v4:L089, v4:L090 | 1, 4, 7 | import level only; 3 of 416; the exact scope sentence |
| v4:L007, v4:L048 | 2, 3, 6 | the challenge sha256; quoted at fd4aeeb, identical at adc7f12 |
| v4:L108, v4:L109 | 2, 5 | tex line ranges 252-267 and 410-420 |
| v5:L141, v5:L140 | 0, 7 | 416 compared; 402 agree; 14 no verdict here; QuasiRiemannHypothesis closure identical |
| v4:L065, v4:L066 | 0, 7 | [STATED], 416/416 and 401/416 |
| v4:L119, v4:L120 | 6, 9 | the clone wording |
| v4:L052 | 6, 8 | "imported" |
| v4:L059 | 7 | cell text vs ledger value |
| v4:L076 | 0, 8 | 45 families |
| v4:L123, v4:L124, v4:L138 | 3, 5, 8 | the three runs without an address-family filter |

## Citations needed by section (from citations-needed.md; UNCONFIRMED flagged)

| section | works |
|---|---|
| 0 | paper (v6:L143), openai/math, Comparator, nanoda_lib, nealmcb repo at 1ca7ff2 |
| 1 | paper (v6:L143), arXiv:2610.15483 (explicit-constant pointer only) |
| 2 | Comparator README at d03acab, nanoda_lib README at 3a24072, lean4export, Lean 4, Mathlib, paper |
| 3 | paper, openai/math fd4aeeb, Mathlib, grwtsk/openai-math #29 |
| 4 | openai/math adc7f12 and fd4aeeb |
| 5 | paper, Mathlib, nanoda_lib, Fischler 2005 (as "cited by the paper as [Fischler, Theorem 1.1 and Lemma 1.3]") |
| 6 | openai/math adc7f12 and fd4aeeb, Comparator, nanoda_lib, Lean 4 |
| 7 | nealmcb repo at 1ca7ff2 (v4:L132-L135 and v5:L141 read from that commit), nanoda_lib #55, #61, #62, openai/math fd4aeeb, Zenodo corpus record |
| 8 | Comparator README at d03acab, lean4export README at 076e8e5, nanoda_lib README at 3a24072, grwtsk/openai-math #40 |
| 9 | Zenodo records, the repository |
| 10 | none |

- Bastounis–Circelli–Hansen (arXiv:2610.08144, v1, 6 Oct 2026): cite in Section 1 or 8 with this sentence (results/2026-10-27-readings/readings-claude-code.md, reading 7): "Bastounis, Circelli and Hansen [arXiv:2610.08144] argue that a Lean check of an AI autoformalisation need not certify the natural-language proof, and show for OpenAI's Navier–Stokes formalisation that the Lean proof does not correspond to the natural-language proof." Its example concerns a different openai/math paper (Navier–Stokes), not family 003.
- Lu–Zaman–Zhao is not cited in Section 1.
- arXiv:2610.15483 is cited only in the explicit-constant pointer.

## Page estimate

| section | pages |
|---|---|
| 0 | 0.5 |
| 1 | 1.5 |
| 2 | 1.5 |
| 3 | 2.5 |
| 4 | 1.5 |
| 5 | 3.0 |
| 6 | 1.25 |
| 7 | 1.5 |
| 8 | 1.25 |
| 9 | 0.5 |
| 10 | 0.25 |
| total body | 15.25 (over the 15-page target by 0.25 after the rebudget) |
| references | about 1 (outside the body estimate) |

Section 8 grows with Table 4. If it runs over, move Table 4 to appendix I.
