# Paper outline (LIPIcs, about 15 pages): from the claims ledger, v3 (2026-10-27)

Source of claims: results/2026-10-26-claims-ledger/ledger-v3.tsv (130 rows: the 98 v2 rows unchanged, plus L099-L130).
- Other inputs: citations-needed.md, gaps.md, LEDGER.md and id-stability.md (same folder); results/2026-10-27-reroute-fd4aeeb/SUMMARY.md; lean-checks/README.md (commit 758b44f).
- The row-by-row mapping is in paper/claim-map.tsv.
- Ids are append-only (id-stability.md). This outline uses v2/v3 ids. Those differ from v1 for L050-L090.

Conventions:
- Every claim cites its ledger id. The value after "=" is copied from the ledger's value column. The exception is L057, which is rendered as counts at Joe's request.
- [INFERRED Lxxx] and [STATED Lxxx] stay visible in the prose. Rows without a tag are COMPUTED.
- **BLOCKED** marks a claim that rests on a statement-match row whose read_by does not include Joe. Blocked rows: L002, L004, L006, L008, L100, L101. A blocked claim is not written as prose until Joe's reading is recorded.
- A "Missing claims" item has no ledger row. It gets no value.
- Vocabulary:
  - "accepted by Comparator with both kernels" (never "verified");
  - "replay" (never "verification");
  - "the paper's Theorem 1" (the source numbers it Theorem 1, L106);
  - "matches" for comparisons done by reading;
  - "proved" for Lean proofs only.
  - Lean statements are quoted from source files.
- Numbering: amsart with one shared counter (L106-L111 note). The results are Theorem 1, Lemma 2, Lemma 3, Corollary 4, Remark 5, Lemma 6, Lemma 7.

## 0. Title and abstract (0.5 page)

Purpose: state the four results in the abstract, each backed by ledger rows.

Abstract claims:
1. OAI's formal proof of Corollary 4 goes through a multiplicity estimate (uniform_rectangular_multiplicity), not the paper's argument for Lemma 3.
   - The control scan of dirichletRealZeroBound_proof finds actual_biquadratic_rectangle_span, uniform_rectangular_multiplicity and source_rectangle_span_of_polynomial_zero_test in its closure (L019 = 116314 constants in closure).
   - Inside OAI's proof of actual_biquadratic_rectangle_span, line 493 applies Geometry.source_rectangle_span_of_polynomial_zero_test and line 496 applies Geometry.uniform_rectangular_multiplicity (L099). Value = 493-494: "apply Geometry.source_rectangle_span_of_polynomial_zero_test φ.toRingHom / ![1, a, b, a * b] σ.toRingHom τ.toRingHom H N n hninj hn"; 496-497: "apply Geometry.uniform_rectangular_multiplicity (Nat.succ_le_iff.mpr hH) hHN / (biquadraticCoefficients (φ a) (φ b)) hc D' F hF".
2. The paper's Lemma 3 and Corollary 4 are proved in Lean, and the Lean statements match the paper's.
   - Lemma3.interpolation (L022, L024) and Lemma3.rectangle (L025).
   - Axioms of all nine comparator-copy declarations (L032) = [propext, Classical.choice, Quot.sound].
   - **BLOCKED:** the statement match [INFERRED L100] = PENDING JOE READING and [INFERRED L101] = PENDING JOE READING. Until Joe's reading is recorded, the abstract can only say "proved in Lean".
3. A +2/-1 substitution gives a proof of the SiegelZeros challenge that is accepted by Comparator with both kernels at fd4aeeb under the 45-family deny list. The dependency scan shows it does not use the multiplicity estimate.
   - Diff (L097) = 1 file, +2/-1.
   - Verdict (L095) = ACCEPT_BOTH; exit 0.
   - Scan (L096) = 92658 constants in closure; matches only via_lemma3 and interpolation (L051).
   - Deny list (L076) = 45 families.
4. The corpus replay agrees with an independent replay on a second platform.
   - Outcomes (L112) = 160 compared; 159 agree; 0 disagree; 1 no verdict here (PlanarPacking, TIMEOUT); nanoda 3a24072 crashed here on 6 (DirectedFeedback, KaplanskyDirectFiniteness, LaughlinFock, LaughlinPlanar, MinUncut, SquareDifference).
   - Export sizes equal for L060 = 146 exports and L061 = 11 (13 incl. 2 from extended records).
   - [STATED L065] nealmcb's comparator run accepts 416/416.
   - The abstract must say what L112 covers: 160 of the 212 extended-replay results. It does not cover the 189.

Missing claims:
- Outcome-level comparison for the 189 and for the 52 extended-replay results not in comparison.txt. No ledger row.

Citations: the paper (version label UNCONFIRMED); openai/math at both commits; Comparator; nanoda_lib; nealmcb/openai-math-lean-tooling at 1ca7ff2.

## 1. Introduction (1.5 pages)

Purpose: give the four results and the boundary of what is claimed.

Claims:
- The four abstract claims, with the same ids as Section 0. Each is restated in one sentence with a forward pointer.
- Claim 2 stays BLOCKED as in Section 0.

Not claimed (scope statements, no values):
- Nothing about the paper's analytic sections (Lemma 2, L107).
- No specialist review of the mathematics.
- Statement faithfulness is checked by reading [INFERRED L002, L004, L006, L008; all BLOCKED].
- The reroute concerns the SiegelZeros chain only. Three further configurations load modules from a separate copy of this code (namespace OAI.Erdos970), with its own multiplicity estimate (L089 = Erdos970 copies; L090 = 3 of 416).
- Nothing about the explicit constant beyond a pointer to arXiv:2610.15483.

Missing claims: none.

Citations: the paper; arXiv:2610.15483 (the explicit-constant pointer only).

## 2. Background (1.5 pages)

Purpose: give a reader what Comparator, nanoda and the challenge statement are, and the shape of the paper's proof.

Claims:
- Comparator's three checks, from its README at d03acab:
  - same statement [STATED L102] = "Prove the same statement as provided in `Challenge`";
  - axioms [STATED L103] = "Use no more axioms than listed in `permitted_axioms`";
  - Lean kernel [STATED L104] = "Be accepted by the Lean kernel". External kernels receive a file containing the solution export.
- nanoda's input [STATED L105] = JSON config + lean4export export file. With enable_nanoda: true, Comparator passes a nanoda-style config.json.
- The challenge statement, quoted at fd4aeeb from /home/checker/math/lean/ComparatorChallenges/SiegelZeros.lean:
  - exists_absolute_real_zero_gap, lines 8-14;
  - WeightedTorusJets.dirichletRealZeroBound_proof, lines 19-25.
  - File sha256 (L007) = bedaac0248a641910f79a380d9702d82c6bfbbfd3760a69d27c72c5d8fb136ce. It is identical at adc7f12 (L007: "unchanged at fd4aeeb").
- The paper's proof structure, each quoted from refs/siegel-paper.tex:
  - [STATED L106] = Theorem 1, tex 66-73;
  - [STATED L107] = Lemma 2, tex 181-194;
  - [STATED L108] = Lemma 3, tex 252-267;
  - [STATED L109] = Corollary 4, tex 410-420;
  - [STATED L110] = Lemma 6, tex 517-524;
  - [STATED L111] = Lemma 7, tex 598-604.
- The paper's Theorem 1 beside the challenge: [INFERRED L008] = MATCH. **BLOCKED.**
- Tool pins:
  - L087: Lean 4.34.1 (5045d005), Mathlib d13f23b, Comparator v4.34.0 d03acab, lean4export v4.34.0 076e8e5;
  - L092: full commits;
  - L088: 3a24072 / f67473b / 37cb87b / 37cb87b+patch, with 3a24072 the official one.

Missing claims:
- How Lemmas 2, 3, 6 and 7 and Corollary 4 combine into Theorem 1 (the paper's Section 6, "Completion of the proof", from tex 663). No ledger row. Needed only if the section states the combination.

Citations: Comparator, nanoda_lib, lean4export, Lean 4, Mathlib, the paper (version label UNCONFIRMED).

## 3. Statement faithfulness (1.5 pages)

Purpose: show whether the four family-003 challenge statements match the paper's statements, and say which parts rest on reading and which on Lean.

Table 1 (one row per challenge). The whole findings column is **BLOCKED** until Joe's reading is recorded.

| challenge | file sha256 (fd4aeeb) | finding | read_by (ledger-v3) |
|---|---|---|---|
| QuasiRiemannHypothesis | L001 = 065f8c9a01d28db78c8b1bfc5083b535082a2d2aac2230d563f98b8caa812cc5 | [INFERRED L002] = MATCH (except s = 1, covered by Mathlib's junk value) | Claude Code; Joe approved the finding (docs/log.md:619) |
| DirichletSevenEighths | L003 = 8fb13ad977bca104591fcbc6ef01a58496e7385053c9b1445f95749afc0eff54 | [INFERRED L004] = MATCH | Claude Code; Joe approved the finding (docs/log.md:619) |
| HeckeSevenEighths | L005 = cb5e404fa65a502c0a9006b9ad45c28914feb79e4b7b1ffcf05e4af82ed0cfc2 | [INFERRED L006] = MATCH (L-function row by Joe's ruling 2026-10-20; one identification INFERRED) | Claude Code; Joe ruled on the LFunction row only (docs/log.md:658) |
| SiegelZeros | L007 = bedaac0248a641910f79a380d9702d82c6bfbbfd3760a69d27c72c5d8fb136ce | [INFERRED L008] = MATCH | Claude Code |

Claims:
- Lean sub-claims of the statement checks: L009 = 34 declarations, all exactly [propext, Classical.choice, Quot.sound].
  - Source: results/2026-10-26-claims-ledger/statement-checks-final-v2.log.
- Non-vacuity lemmas, each with its axioms line = [propext, Classical.choice, Quot.sound]:
  - NonVacuity.hypotheses_satisfiable (L011);
  - NonVacuity.quadChar_LFunction_eq_LSeries (L012);
  - NonVacuity.quadChar_LFunction_one_ne_zero (L013);
  - NonVacuity.specialization (L014).
- Footnotes:
  - NonVacuity.lean source hash (L015), LF sha256 b9fae4da5517a97da50d3fdb5356329f03f00b7ab935a448a999b2c59b24d9f9.
  - The audits were posted on grwtsk/openai-math #29 (L010 = 2026-10-20T16:56:00Z).
  - The Hecke ruling and the one INFERRED identification (L006 value).

Missing claims: none. The readings are INFERRED by design and BLOCKED on Joe.

Citations: the paper; openai/math fd4aeeb; Mathlib; grwtsk/openai-math #29.

## 4. The gap (1.5 pages)

Purpose: locate where OAI's proof reaches Corollary 4 and what that route brings in.

Claims:
- Location of Corollary 4: actual_biquadratic_rectangle_span at InvariantJetLinearMap.lean:471-484, identical at adc7f12 and fd4aeeb (L016 = 09b8bd7fa82365e69caebfad466d039d85084595376766a731945fa5c11a2bdc).
- Its proof invokes the multiplicity estimate at lines 493 and 496 (L099; the two lines are quoted in Section 0).
- Its only use:
  - Within the SiegelZeros tree, the theorem is used only at CharacterGlobalGreedyDeterminantMasterBounds.lean:138 (L017 = 1 use site).
  - After line 138 is replaced, the closure of dirichletRealZeroBound_proof no longer contains it (L018 = absent).
- The separate Jacobsthal copy, at import level only:
  - It depends on its own Geometry.uniform_rectangular_multiplicity and Geometry.source_rectangle_span_of_polynomial_zero_test (L089 = Erdos970 copies). Source reading only.
  - Three configs have a module of that subtree in their solution import closure (L090 = 3 of 416). This is an import closure, not a declaration closure.
- Control scan:
  - L019 = 116314 constants in closure (adc7f12);
  - L094 = 116314 (fd4aeeb, identical block).
- CategoryTheory and AlgebraicGeometry names removed by the reroute:
  - L020 = 9936 (6901 + 3035), referenced-names convention (names reachable from the root through types and values, as #find_deps);
  - L021 = 10107 (7048 + 3059), full-dump convention (every declaration in the lean4export dumps).
  - Recommendation: use L020 in the text, because it uses the same reachability convention as L019 and L051. Put L021 in a footnote with its definition.

Missing claims: none.

Citations: openai/math at adc7f12 and fd4aeeb.

## 5. Lemma 3 and Corollary 4 (3 pages)

Purpose: present the Lean proof of the paper's Lemma 3 and Corollary 4, and how it is bridged to OAI's statement of Corollary 4.

Statements (quoted from source, side by side with the paper):
- Lemma 3:
  - Lean: lean-checks/comparator-copy/PaperLemma3/Lemma3.lean:817-825 (L024 = 1ce196f54fa98689bbea6bd74f2abdb110f5cbcca2eecddcca9316b8af465283), equal to lean-checks/Lemma3.lean:816-825 (L022).
  - Paper: [STATED L108] tex 252-267.
  - Match: [INFERRED L100] = PENDING JOE READING. **BLOCKED.** read_by: Claude Code (docs/log.md:277).
- Corollary 4:
  - Lean: lean-checks/comparator-copy/PaperLemma3/Bridge.lean:96-109 (L025).
  - Paper: [STATED L109] tex 410-420.
  - Match: [INFERRED L101] = PENDING JOE READING. **BLOCKED.** read_by: none recorded.
- The box Pt is defined at Lemma3.lean:42 (L023 = Pt).
- Copies are identical (L029 = identical).

Proof architecture:
- Missing claim: the structure of the Lean proof of Lemma 3 (its sub-lemma groups and how they follow the paper's proof). No ledger row. Candidate source: lean-checks/README.md rows for Lemma3_P1 … Lemma3_P5 and Lemma3Skeleton.

The bridge (each item quoted from Bridge.lean):
- The main theorem has exactly the type of OAI's theorem, by type_of% (L036 = type_of%; L028 = Lemma3.actual_biquadratic_rectangle_span_via_lemma3).
- The embedding is chosen as IsAlgClosed.lift (L037 = IsAlgClosed.lift).
- The kernel vector is c = biquadraticCoefficients (L038 = ![1, a⁻¹, -b⁻¹, -(a * b)⁻¹]). ker A = span {c} is proved inline (L039 = hker; L027).
- bridge_descent does the descent from C to K and the restriction to an injective family (L040 = bridge_descent; L026).
- AlgEquiv.mul_apply (L041 = (e₁ * e₂) x = e₁ (e₂ x)). Quote the source line, Mathlib d13f23b Mathlib/Algebra/Algebra/Equiv.lean:663: `theorem mul_apply (e₁ e₂ : A₁ ≃ₐ[R] A₁) (x : A₁) : (e₁ * e₂) x = e₁ (e₂ x) :=`.

Reused OAI setup lemmas:
- source_same_witness_hyperplane (L042);
- biquadraticCoefficients_linearIndependent (L043).

Axioms:
- Primary: L032 = [propext, Classical.choice, Quot.sound].
- Corroboration: L030 (2026-10-08, same value).
- Footnote: L031 (same value).

Standalone nanoda:
- L033 = 61810 declarations checked.
- Controls: L034 = rejected (exit 1); L035 = rejected (exit 101).
- The run's sandbox is in Section 8 (L124).

Small-N checks:
- L046 = 540 instances, 28 checks each. This covers N = 2, 3 only.

Working drafts with sorry, in a footnote that names them as not cited:
- L044 = working draft (sorry);
- L045 = working draft (sorry).

Missing claims:
- The proof architecture (above).

Citations:
- the paper;
- Mathlib d13f23b;
- nanoda_lib;
- Fischler, Compos. Math. 141 (2005), cited by the paper at tex:155. Its internal theorem numbering is UNCONFIRMED; cite the paper's reference only, or confirm the numbering first.

## 6. The reroute (2 pages)

Purpose: show that substituting the Lean proof of Corollary 4 into OAI's chain gives a proof accepted by Comparator with both kernels, and that the multiplicity estimate drops out.

Primary record: fd4aeeb, 2026-10-27 runs (results/2026-10-27-reroute-fd4aeeb/).

Table 2:

| run | verdict | dependency scan | prebuild | comparator run | guard |
|---|---|---|---|---|---|
| control | L093 = ACCEPT_BOTH; exit 0 | L094 = 116314 constants in closure | L113 = 11min 19.935s; 9243 jobs | L116 = 842 s; max RSS 7707508 kB; cgroup max_usage 7412195328 B; oom_kill 0 | L118 = 0 LIMIT lines; 0 stops |
| reroute | L095 = ACCEPT_BOTH; exit 0 | L096 = 92658 constants in closure | L114 = 1min 39.395s; 9245 jobs | L117 = 659 s; max RSS 7662352 kB; cgroup max_usage 6280855552 B; oom_kill 0 | (same) |

- Footnote on the prebuild difference [INFERRED L115] = incremental rebuild. The reroute ran in the same clone after the control, so lake rebuilt only the two new modules, the patched module and its dependents.

Clone setup (wording: "local clone of fd4aeeb; package directory reused read-only from the original clone; OAI closure built from scratch"):
- L119 = local clone; packages read-only bind mount; write refused.
- L120 = build dir born 22:19:37 (control prebuild start 22:19:09). This is computed from the clone's birth times and reflog, so "built from scratch" is a computed claim.
- The ledger notes on L093 and L095 say "fresh local clone". The paper does not use "fresh clone" alone.

Claims:
- Installed files and patch (L097 = 1 file, +2/-1).
- Footnote: the patch applies at fd4aeeb (L050 = applies (git apply --check exit 0)).
- The rerouted chain still imports the patched HadamardSupport (L052 = imported). Forward pointer to Section 8.

Corroboration at adc7f12 (2026-10-09):
- L047 = 1 file, +2/-1;
- L048 = bedaac0248a641910f79a380d9702d82c6bfbbfd3760a69d27c72c5d8fb136ce;
- L049 = 9244 jobs; ACCEPT_BOTH; exit 0;
- L051 = 92658, with the control L019 = 116314;
- L018 = absent.

Missing claims: none.

Citations: openai/math adc7f12 and fd4aeeb; Comparator; nanoda_lib; Lean 4.

## 7. Corpus context (1.5 pages)

Purpose: place the SiegelZeros result within the full replay of the openai/math corpus, with official and unofficial tools kept apart.

Table 3 (the one table):

| block | official tool set (nanoda 3a24072) | unofficial nanoda builds | independent replay [STATED] |
|---|---|---|---|
| 189 referenced configs | L053 = 187 + 2; L054 = 178 / 9 | L055 = 9 of 9 (f67473b, UNOFFICIAL) | see the all-416 row |
| 227 unreferenced configs | L056 = 212 / 15. L057, as counts: ACCEPT_BOTH 205, LEAN_ACCEPT_NANODA_CRASH 6, TIMEOUT 1, NOT_CHECKED_HERE 15 | see next row | outcomes compared for 160: L112 (COMPUTED here from his STATED records) |
| Catalan, KMedianThreshold | official: NOT_CHECKED_HERE (L057). Lean-kernel Comparator runs here: L121 = 369 s; exit 0 (KMedianThreshold), L122 = 2234 s; exit 0 (Catalan) | L058 = both kernels (unofficial nanoda) | [STATED L067] = 10 |
| ContinuumCoulombHardness | "not completed on this machine (memory)" (L059 = DEFERRED (permanent)) | none | [STATED L125] = accepted; 923.63 s. [STATED L128] = pass 50.0 s 1.8GB with the patch at 64 MiB |
| all 416 (nealmcb) | | | [STATED L065] = 416/416 (Comparator as shipped); [STATED L066] = 401/416 (nanoda 3a24072 at 1 GiB stack) |
| export sizes | L060 = 146 (0 differ, 14 not comparable); L061 = 11 (13 incl. 2 from extended records) | | |

Claims:
- Failure classes:
  - [INFERRED L062] = RoundTables group (8), Laughlin group (3), KMedianThreshold, Catalan;
  - [INFERRED L063] = KaplanskyFinitelyPresented, GroupRingDeterminant, KaplanskyDirectFiniteness (COMPUTED); MatchingFPRAS, ContingencyTables, LogspaceEquality, RandomizedMeanPayoff, PeriodicGroup (STATED);
  - [INFERRED L064] = SquareDifference.
- Footnotes:
  - the B3 patch [STATED L068] = edd9824f5fd93c86d3f52acea1373a915ccfddf23db33c5e919f03f7c642bc30;
  - the sweep commit [STATED L069] = 8199c74;
  - ContinuumCoulombHardness, nealmcb's other records: [STATED L126] = lean 1; nanoda 1 (99.3 s); [STATED L127] = the f67473b retests and ~24 GiB.
  - L125-L128 come from local transcriptions. Their agreement with commit 1ca7ff2 is UNCONFIRMED (no network).
- L121 and L122 are whole Comparator runs (build, export, checks), not the kernel replay alone.

Missing claims:
- The guard-stop details for ContinuumCoulombHardness (MemAvailable at each stop). L059's claim text gives only the thread counts. Needed only if the table footnote gives figures.
- The outcome comparison for the 189 and the other 52 (Section 0).

Citations:
- nealmcb/openai-math-lean-tooling at 1ca7ff2a0280760783ee2b198c0d6f2a1cfeaba4;
- nanoda_lib issues #55, #61, #62;
- openai/math fd4aeeb;
- Zenodo corpus record (L084).

## 8. Threats to validity (1.25 pages)

Purpose: list what could make the results wrong or weaker than stated, with the evidence for each.

Claims:
- Kernel trust: Comparator's guarantees are the three in L102-L104 [STATED]. Its own assumptions (README lines 28-39) are not a ledger row (Missing, below).
- Statement faithfulness rests on reading [INFERRED L002, L004, L006, L008, L100, L101; all BLOCKED]. The non-vacuity lemmas (L011-L014) rule out a vacuous challenge; they do not establish faithfulness.
- The patched HadamardSupport dependency (L052 = imported).
- The paper's analytic sections are out of scope (scope statement).
- Sandbox history:
  - L070 = 5 families denied;
  - L071 = blocked (errno 97);
  - L072 = connected;
  - L073 = AF_PPPOX, AF_ALG;
  - L074 = ~AF_UNIX only;
  - L075 = 2026-10-08 14:18;
  - L076 = 45 families;
  - L077 = 138 / 138 errno 97.
- WSL memory:
  - L078 = ElementaryPositivity, KaplanskyDirectFiniteness, ShortEgyptianFractions;
  - L079 = 20 GB;
  - MemoryMax: L098 = not enforced; v1 cap kills (the test), with L080 for the cap and guard design.
- The superseded metaprogram: L091 = #reroute + addDecl, named as not evidence. results/2026-10-08-lean-main-rerouted.txt is not cited anywhere in the paper.

Per-run sandbox (Table 4). Each cell is the ledger's sandbox column for the cited rows.

| run | rows | sandbox |
|---|---|---|
| 2026-10-08 12:15 first SiegelZeros comparator (08_comparator.sh) | L074 | Comparator README wrapper: systemd-run --user RestrictAddressFamilies=~AF_UNIX (IP open); not cited for any result |
| 2026-10-08 14:18 SiegelZeros comparator with nanoda (29_comparator_nanoda.sh) | L075 | 5-family filter |
| 2026-10-08 Lemma3Bridged axioms | L030 | systemd-run --user, checker, NoNewPrivs; 5-family filter |
| 2026-10-08 NonVacuity lemmas | L011-L014 | lake env lean as checker in the comparator-checked clone (32_nonvacuity.sh) |
| 2026-10-08 standalone nanoda on Lemma3Bridged | L033-L035, L124 | sudo -u checker; no systemd-run; no address-family filter |
| 2026-10-09 rerouted comparator and scans, with the control scan (adc7f12) | L018, L019, L049, L051 | systemd-run --user, checker, NoNewPrivs; 5-family filter |
| corpus replay of the 189 | L053-L055 | systemd-run --user, checker, NoNewPrivs; 5-family filter |
| 2026-10-20 statement-check build | L009, L123 | sudo -u checker; no systemd-run; no address-family filter |
| extended replay of the 227 | L056, L057 | systemd-run --user, checker, NoNewPrivs; 5-family filter |
| 2026-10-26 nanoda version matrix | L062-L064 | system unit + setpriv to checker; 5-family filter; 16G v1 cgroup cap (step 5 under the 45-family list) |
| 2026-10-26 axioms re-checks and AlgEquiv.mul_apply | L031, L032, L041 | 45-family list, checker, NoNewPrivs |
| 2026-10-26 Lean-kernel runs on Catalan and KMedianThreshold | L058, L121, L122 | 45-family list + 16G v1 cgroup cap (67d) |
| 2026-10-26/27 fd4aeeb control and reroute | L093-L097, L113-L117 | 45-family list + 16G v1 cgroup cap (67r) |

- The table shows two runs with no address-family filter: the 10-08 standalone nanoda and the 10-20 statement checks. The primary SiegelZeros results (L032, L093-L097) ran under the 45-family list.

Missing claims:
- Comparator's stated assumptions (README lines 28-39, including "The Lean kernel is correct"), and the components both kernels depend on. No ledger row. The README copy is in v3-evidence/.
- Whether 32_nonvacuity.sh used a systemd-run unit. The ledger does not say.

Citations: Comparator; grwtsk/openai-math #40 (comment 6431288875); nanoda_lib.

## 9. Artifacts (0.5 page)

Purpose: tell a reader exactly which files and records reproduce each result.

Claims:
- The repository commit to be tagged is TBD at the paper's final version. L086 is cut and will be re-added at tag time (claim-map.tsv).
- Zenodo:
  - L081 = 10.5281/zenodo.23269528;
  - L082 = 10.5281/zenodo.23499651;
  - L083 = 10.5281/zenodo.23523697;
  - L084 = 10.5281/zenodo.23505836;
  - L085 = 10.5281/zenodo.23269527.
  - The final deposit is held until the paper's final version.
- Canonical and comparator-copy files with sha256:
  - PaperLemma3/Lemma3.lean (L024);
  - Bridge.lean (af401514808dde5bb913ce8e87cc5280b704a234ea324897d1a1ced1f218f250, from L025-L028 sources);
  - Lemma3Bridged.lean (6ce38ac1ef33c8b46028205bb043718565b679175b63cc6fbf8089136554cdb4, L029 source);
  - Lemma3.lean (ecdbf400b24f9241cd03cf383bdcd97ed71e4812578e66d7159a846447f7b1a7, L022 source);
  - NonVacuity.lean (L015).
- Clone setup (L119, L120).
- Pins: L087, L088, L092.
- lean-checks/README.md.

Missing claims:
- The tag commit.
- A ledger row for lean-checks/README.md (committed at 758b44f).

Citations: Zenodo records; the repository.

## 10. AI-use disclosure (0.25 page)

Purpose: say what Claude Code produced, as facts with sources, and leave the human-review account to Joe.

Claims:
- L129 = lean-checks 260 of 260; wsl-comparator 214 of 214; src 22 of 22. These are tracked files with at least one commit carrying a Co-Authored-By: Claude trailer; 174 of the 175 commits carry it. The full list is in v3-evidence/claude-trailer-files.txt.
- L130 = 4 posts: grwtsk/openai-math #40, comment 6291050955 (2026-10-20); nanoda_lib #55, comment 6291244827 (2026-10-20); grwtsk/openai-math #29, comment 6296359378 (2026-10-20); nanoda_lib #61, comment 6431284502 (2026-10-26).
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
- F. The small-N execution details (L046).
- G. The 34 statement-check axioms outputs (L009).
- H. The two count conventions for Section 4 (L020, L021).
- I. The per-run sandbox table in full, if Table 4 is too long for Section 8.

## Claims used in more than one section (risk of inconsistent restatement)

| ids | sections | what to keep consistent |
|---|---|---|
| L019, L094 | 0, 4, 6 | 116314 and "identical at fd4aeeb" |
| L099 | 0, 4 | lines 493 and 496, quoted the same way |
| L051, L096 | 0, 6 | 92658 and the two matches |
| L093, L095 | 0, 1, 6 | "accepted by Comparator with both kernels", exit 0 |
| L097, L047 | 0, 6 | 1 file, +2/-1 |
| L032 | 0, 5, 8 | nine declarations, standard axioms |
| L100, L101 | 0, 1, 5, 8 | BLOCKED; PENDING JOE READING |
| L002, L004, L006, L008 | 1, 2, 3, 8 | [INFERRED], BLOCKED |
| L016, L017, L018 | 0, 4, 6 | "only use" is within the SiegelZeros tree |
| L089, L090 | 1, 4, 7 | import level only; 3 of 416; the exact scope sentence |
| L007, L048 | 2, 3, 6 | the challenge sha256; quoted at fd4aeeb, identical at adc7f12 |
| L108, L109 | 2, 5 | tex line ranges 252-267 and 410-420 |
| L112 | 0, 7 | 160 compared, not the whole corpus |
| L065, L066 | 0, 7 | [STATED], 416/416 and 401/416 |
| L119, L120 | 6, 9 | the clone wording |
| L052 | 6, 8 | "imported" |
| L059 | 7 | cell text vs ledger value |
| L076 | 0, 8 | 45 families |
| L124, L123 | 5, 8 | the two runs without an address-family filter |

## Citations needed by section (from citations-needed.md; UNCONFIRMED flagged)

| section | works |
|---|---|
| 0 | paper (**version label UNCONFIRMED**), openai/math, Comparator, nanoda_lib, nealmcb repo at 1ca7ff2 |
| 1 | paper (**version label UNCONFIRMED**), arXiv:2610.15483 (explicit-constant pointer only) |
| 2 | Comparator README at d03acab, nanoda_lib README at 3a24072, lean4export, Lean 4, Mathlib, paper |
| 3 | paper, openai/math fd4aeeb, Mathlib, grwtsk/openai-math #29 |
| 4 | openai/math adc7f12 and fd4aeeb |
| 5 | paper, Mathlib, nanoda_lib, Fischler 2005 (**internal theorem and lemma numbers UNCONFIRMED**) |
| 6 | openai/math adc7f12 and fd4aeeb, Comparator, nanoda_lib, Lean 4 |
| 7 | nealmcb repo at 1ca7ff2 (**L125-L128: agreement of the local transcriptions with 1ca7ff2 UNCONFIRMED**), nanoda_lib #55, #61, #62, openai/math fd4aeeb, Zenodo corpus record |
| 8 | Comparator, grwtsk/openai-math #40, nanoda_lib |
| 9 | Zenodo records, the repository |
| 10 | none |

- Bastounis–Circelli–Hansen (arXiv:2610.08144): pending Joe's reading. No local copy; all details UNCONFIRMED; no ledger row uses it.
- Lu–Zaman–Zhao is not cited in Section 1.
- arXiv:2610.15483 is cited only in the explicit-constant pointer.

## Page estimate

| section | pages |
|---|---|
| 0 | 0.5 |
| 1 | 1.5 |
| 2 | 1.5 |
| 3 | 1.5 |
| 4 | 1.5 |
| 5 | 3.0 |
| 6 | 2.0 |
| 7 | 1.5 |
| 8 | 1.25 |
| 9 | 0.5 |
| 10 | 0.25 |
| total body | 15.0 |
| references | about 1 (outside the body estimate) |

Section 8 grows with Table 4. If it runs over, move Table 4 to appendix I.
