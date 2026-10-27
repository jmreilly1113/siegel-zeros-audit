# Paper outline (LIPIcs, about 15 pages): generated 2026-10-27 from the claims ledger

Source of claims: results/2026-10-26-claims-ledger/ledger-v2.tsv (98 rows). Other inputs: citations-needed.md, gaps.md and LEDGER.md (same folder), results/2026-10-27-reroute-fd4aeeb/SUMMARY.md, lean-checks/README.md (commit 758b44f). The row-by-row mapping is in paper/claim-map.tsv.

Conventions:
- Every claim cites its ledger id. The value after "=" is copied from the ledger's value column.
- [INFERRED Lxxx] and [STATED Lxxx] stay visible in the prose. Rows without a tag are COMPUTED.
- A "Missing claims" item has no ledger row. It gets no value and is not written into the paper until a row exists.
- Vocabulary:
  - "accepted by Comparator with both kernels" (never "verified");
  - "replay" (never "verification");
  - "matches" for comparisons done by reading;
  - "proved" for Lean proofs only.
  - Lean statements are quoted from source files.
- Numbering note: refs/siegel-paper.tex is amsart with one shared counter (\newtheorem{theorem}{Theorem}; lemma, corollary and remark use [theorem]).
  - The main theorem is therefore Theorem 1 (tex 66-73), and the outline writes "the paper's Theorem 1". The brief said "Theorem 1.1"; the source does not number it that way.
  - The rest follow on the same counter: Lemma 2 (181), Lemma 3 (252), Corollary 4 (410), Remark 5 (434), Lemma 6 (517), Lemma 7 (598).
  - So the brief's "Lemmas 5-7" are Lemmas 6 and 7; item 5 is a remark.

## 0. Title and abstract (0.5 page)

Purpose: state the four results in the abstract, each backed by ledger rows.

Abstract claims:
1. OAI's formal proof reaches Corollary 4 by a multiplicity estimate and does not contain the paper's proof of Lemma 3.
   - OAI's Corollary 4 is actual_biquadratic_rectangle_span at InvariantJetLinearMap.lean:471-484 (L016, LF sha256 = 09b8bd7fa82365e69caebfad466d039d85084595376766a731945fa5c11a2bdc).
   - The control scan of dirichletRealZeroBound_proof finds actual_biquadratic_rectangle_span, uniform_rectangular_multiplicity and source_rectangle_span_of_polynomial_zero_test in its closure (L019 = 116314 constants in closure).
   - Missing claim: "OAI's sources do not contain the paper's proof of Lemma 3". No ledger row. Candidate source: the text search reported in docs/lean-paper-map.md:20; its output is not saved in results/.
2. The paper's Lemma 3 and Corollary 4 are proved in Lean, and the Lean statements match the paper's.
   - Lemma3.interpolation (L022, L024) and Lemma3.rectangle (L025).
   - Axioms of all nine comparator-copy declarations (L032) = [propext, Classical.choice, Quot.sound].
   - Missing claim: the statement match for Lemma 3 and Corollary 4 [would be INFERRED]. No ledger row. Candidate source: docs/lemma3-lean-statement-review.md.
3. A +2/-1 substitution gives a proof of the SiegelZeros challenge that is accepted by Comparator with both kernels at fd4aeeb under the 45-family deny list, and the dependency scan shows it does not use the multiplicity estimate.
   - Diff (L097) = 1 file, +2/-1.
   - Verdict (L095) = ACCEPT_BOTH; exit 0.
   - Scan (L096) = 92658 constants in closure; matches only via_lemma3 and interpolation (L051, same block, identical per L096).
   - Deny list (L076) = 45 families.
4. The corpus replay agrees with an independent replay on a second platform.
   - Export sizes equal for L060 = 146 exports and L061 = 11 (13 incl. 2 from extended records).
   - [STATED L065] nealmcb's comparator run accepts 416/416.
   - Missing claim: outcome-level agreement (each config accepted here is also accepted there). No ledger row. Candidate source: results/2026-10-25-extended-replay-vs-mcburnett/comparison.txt.

Citations: the paper (version label UNCONFIRMED), openai/math at both commits, Comparator, nanoda_lib, nealmcb/openai-math-lean-tooling at 1ca7ff2.

## 1. Introduction (1.5 pages)

Purpose: give the four results and the boundary of what is claimed.

Claims: the four abstract claims, with the same ids as Section 0. Each is restated in one sentence with a forward pointer, not re-derived.

Not claimed (scope statements, no values):
- Nothing about the paper's analytic sections (Section 2 of the paper, Lemma 2).
- No specialist review of the mathematics.
- Statement faithfulness is checked by reading [INFERRED L002, L004, L006, L008].
- The reroute concerns the SiegelZeros chain only. Three further configurations load modules from a separate copy of this code (namespace OAI.Erdos970), with its own multiplicity estimate (L089 = Erdos970 copies; L090 = 3 of 416).
- Nothing about the explicit constant beyond a pointer.

Missing claims:
- The pointer target for the explicit constant. No ledger row. docs/effectivity/ is not in the ledger.

Citations: the paper; arXiv:2610.15483 (context only); Lu–Zaman–Zhao arXiv:2602.03626 (context only, no ledger row).

## 2. Background (1.5 pages)

Purpose: give a reader what Comparator, nanoda and the challenge statement are, and the shape of the paper's proof.

Claims:
- The challenge statement, quoted from external/openai-math/lean/ComparatorChallenges/SiegelZeros.lean (adc7f12):
  - exists_absolute_real_zero_gap, lines 8-14;
  - WeightedTorusJets.dirichletRealZeroBound_proof, lines 19-25.
  - File sha256 (L007) = bedaac0248a641910f79a380d9702d82c6bfbbfd3760a69d27c72c5d8fb136ce, unchanged at fd4aeeb.
- Tool pins:
  - L087: Lean 4.34.1 (5045d005), Mathlib d13f23b, Comparator v4.34.0 d03acab, lean4export v4.34.0 076e8e5;
  - L092: full Comparator and lean4export commits;
  - L088: nanoda pins = 3a24072 / f67473b / 37cb87b / 37cb87b+patch, with 3a24072 the official one.
- The paper's Theorem 1, quoted from refs/siegel-paper.tex:66-73, beside the challenge: [INFERRED L008] = MATCH.

Missing claims:
- Comparator's three checks (build and statement comparison, axiom whitelist, kernel replay). No ledger row. Candidate source: docs/paper/independence.md (a).
- What nanoda is and how it receives declarations (export format). No ledger row. Candidate source: docs/paper/independence.md (a)-(b).
- The paper's proof structure, as STATED rows:
  - Lemma 2 (tex 181-194);
  - Lemma 3 (252-267) and Corollary 4 (410-420);
  - Lemmas 6 and 7 (517-524, 598-604), and how they combine into Theorem 1.
  - No ledger rows for any of these.

Citations: Comparator, nanoda_lib, lean4export, Lean 4, Mathlib, the paper (version label UNCONFIRMED).

## 3. Statement faithfulness (1.5 pages)

Purpose: show that the four family-003 challenge statements match the paper's statements, and say which parts of that rest on reading and which on Lean.

Table 1 (one row per challenge):

| challenge | file sha256 (fd4aeeb) | finding |
|---|---|---|
| QuasiRiemannHypothesis | L001 = 065f8c9a01d28db78c8b1bfc5083b535082a2d2aac2230d563f98b8caa812cc5 | [INFERRED L002] = MATCH (except s = 1, covered by Mathlib's junk value) |
| DirichletSevenEighths | L003 = 8fb13ad977bca104591fcbc6ef01a58496e7385053c9b1445f95749afc0eff54 | [INFERRED L004] = MATCH |
| HeckeSevenEighths | L005 = cb5e404fa65a502c0a9006b9ad45c28914feb79e4b7b1ffcf05e4af82ed0cfc2 | [INFERRED L006] = MATCH (L-function row by Joe's ruling 2026-10-20; one identification INFERRED) |
| SiegelZeros | L007 = bedaac0248a641910f79a380d9702d82c6bfbbfd3760a69d27c72c5d8fb136ce | [INFERRED L008] = MATCH |

Claims:
- Lean sub-claims of the statement checks: L009 = 34 declarations, all exactly [propext, Classical.choice, Quot.sound].
  - Source: results/2026-10-26-claims-ledger/statement-checks-final-v2.log, the v2 log in the ledger folder.
- Non-vacuity lemmas, each with its axioms line = [propext, Classical.choice, Quot.sound]:
  - NonVacuity.hypotheses_satisfiable (L011);
  - NonVacuity.quadChar_LFunction_eq_LSeries (L012);
  - NonVacuity.quadChar_LFunction_one_ne_zero (L013);
  - NonVacuity.specialization (L014).
- Source file NonVacuity.lean (L015), LF sha256 b9fae4da5517a97da50d3fdb5356329f03f00b7ab935a448a999b2c59b24d9f9, in a table footnote.
- The HeckeSevenEighths row needs a footnote on the ruling and the one INFERRED identification (L006 value).

Missing claims: none for this section. The faithfulness readings are INFERRED by design.

Citations: the paper; openai/math fd4aeeb; Mathlib; grwtsk/openai-math #29 only if L010 is placed (see claim-map.tsv).

## 4. The gap (1.5 pages)

Purpose: locate where OAI's proof reaches Corollary 4 and what that route brings in.

Claims:
- Location of Corollary 4: actual_biquadratic_rectangle_span at InvariantJetLinearMap.lean:471-484, identical at adc7f12 and fd4aeeb (L016 = 09b8bd7fa82365e69caebfad466d039d85084595376766a731945fa5c11a2bdc).
- Its only use:
  - Within the SiegelZeros tree, the theorem is used only at CharacterGlobalGreedyDeterminantMasterBounds.lean:138 (L017 = 1 use site).
  - After line 138 is replaced, the closure of dirichletRealZeroBound_proof no longer contains it (L018 = absent).
- The separate Jacobsthal copy, at import level only:
  - The copy in namespace OAI.Erdos970.WeightedTorusJets depends on its own Geometry.uniform_rectangular_multiplicity and Geometry.source_rectangle_span_of_polynomial_zero_test (L089 = Erdos970 copies). Source reading only; no declaration-closure scan was run.
  - Three configs have a module of that subtree in their solution import closure: Jacobsthal, JacobsthalImproved, OstmannPrimes (L090 = 3 of 416). This is an import closure, not a declaration closure.
- Control scan: OAI's unmodified dirichletRealZeroBound_proof depends on actual_biquadratic_rectangle_span, uniform_rectangular_multiplicity and source_rectangle_span_of_polynomial_zero_test.
  - L019 = 116314 constants in closure (adc7f12);
  - L094 = 116314, identical at fd4aeeb.
- CategoryTheory and AlgebraicGeometry names removed by the reroute, two counts:
  - L020 = 9936 (6901 + 3035), referenced-names convention: names reachable from the root through types and values, as #find_deps.
  - L021 = 10107 (7048 + 3059), full-dump convention: every declaration in the lean4export dumps, including unreferenced recursors and constructors.
  - Recommendation: use L020 (9936) in the text. It uses the same reachability convention as the closure scans (L019, L051), so all counts in the section are comparable. Give L021 in a footnote with its definition.

Missing claims: none for this section. The difference between the two closure sizes is not a ledger value; if the text needs it, add a row.

Citations: openai/math at adc7f12 and fd4aeeb.

## 5. Lemma 3 and Corollary 4 (3 pages)

Purpose: present the Lean proof of the paper's Lemma 3 and Corollary 4, and how it is bridged to OAI's statement of Corollary 4.

Statements (quoted from source, side by side with the paper):
- Lemma 3:
  - Lean: lean-checks/comparator-copy/PaperLemma3/Lemma3.lean:817-825, Lemma3.interpolation (L024, sha256 = 1ce196f54fa98689bbea6bd74f2abdb110f5cbcca2eecddcca9316b8af465283). It equals lean-checks/Lemma3.lean:816-825 (L022), which imports Mathlib only.
  - Paper: refs/siegel-paper.tex:252-267.
- Corollary 4:
  - Lean: lean-checks/comparator-copy/PaperLemma3/Bridge.lean:96-109, Lemma3.rectangle (L025).
  - Paper: refs/siegel-paper.tex:410-420.
  - The brief gave 410-429. The statement ends at \end{corollary} on line 420, and lines 422-432 are its proof. The Lean docstring (Bridge.lean:96) also says 410-420.
- The box Pt is defined at Lemma3.lean:42 (L023 = Pt).
- Copies are identical (L029 = identical): PaperLemma3/Lemma3.lean, Lemma3Bridged.lean and Lemma3.lean, by declaration block.

Proof architecture:
- Missing claim: the structure of the Lean proof of Lemma 3 (its sub-lemma groups and how they follow the paper's proof). No ledger row. Candidate source: lean-checks/README.md rows for Lemma3_P1 … Lemma3_P5 and Lemma3Skeleton.

The bridge (each item quoted from Bridge.lean):
- The main theorem has exactly the type of OAI's theorem, by type_of% (L036 = type_of%; L028 = Lemma3.actual_biquadratic_rectangle_span_via_lemma3).
- The embedding K -> C is chosen as IsAlgClosed.lift, not taken as a hypothesis (L037 = IsAlgClosed.lift).
- The kernel vector c is OAI's biquadraticCoefficients (L038 = ![1, a⁻¹, -b⁻¹, -(a * b)⁻¹]). ker A = span {c} is proved inline in bridge_main (L039 = hker; L027).
- bridge_descent does the descent from C to K and the restriction to an injective family (L040 = bridge_descent; L026).
- AlgEquiv.mul_apply (L041 = (e₁ * e₂) x = e₁ (e₂ x)). Quote the source line, Mathlib d13f23b Mathlib/Algebra/Algebra/Equiv.lean:663: `theorem mul_apply (e₁ e₂ : A₁ ≃ₐ[R] A₁) (x : A₁) : (e₁ * e₂) x = e₁ (e₂ x) :=`. It fixes the third row of A as phi(sigma(tau(1, a, b, ab))).

Reused OAI setup lemmas:
- source_same_witness_hyperplane (L042 = source_same_witness_hyperplane);
- biquadraticCoefficients_linearIndependent and its _map form (L043 = biquadraticCoefficients_linearIndependent).

Axioms:
- Primary: all nine comparator-copy declarations, fd4aeeb, deny list (L032 = [propext, Classical.choice, Quot.sound]).
- Corroboration:
  - Lemma3Bridged.lean at adc7f12, 2026-10-08 (L030 = [propext, Classical.choice, Quot.sound]);
  - the 2026-10-26 rerun at fd4aeeb, in a footnote (L031, same value).

Standalone nanoda:
- 3a24072 accepts the export of via_lemma3 (L033 = 61810 declarations checked).
- Controls:
  - with Classical.choice not permitted, rejected (L034 = rejected (exit 1));
  - with rectangle's proof replaced by interpolation's, rejected (L035 = rejected (exit 101)).

Small-N checks:
- Exact execution of the proof of Lemma 3 at N = 2, 3 (L046 = 540 instances, 28 checks each, all pass).
- This confirms the proof steps at N = 2, 3 only.

Working drafts with sorry, in a footnote that names them as not cited:
- Lemma3_Cor4.lean (L044 = working draft (sorry));
- Lemma3_Bridge.lean (L045 = working draft (sorry)).
- The canonical Bridge.lean imports neither.

Missing claims:
- The statement match of Lemma 3 and Corollary 4 against tex 252-267 and 410-420 [would be INFERRED]. Same item as Section 0 claim 2.
- The proof architecture (above).

Citations:
- the paper;
- Mathlib d13f23b;
- nanoda_lib;
- Fischler, Compos. Math. 141 (2005), cited by the paper at tex:155 as "Theorem 1.1 and Lemma 1.3". Its internal numbering is UNCONFIRMED; cite the paper's reference only, or confirm the numbering first.
- arXiv:2610.15483 (context only).

## 6. The reroute (2 pages)

Purpose: show that substituting the Lean proof of Corollary 4 into OAI's chain gives a proof accepted by Comparator with both kernels, and that the multiplicity estimate drops out.

Primary record: fd4aeeb, 2026-10-27 runs (results/2026-10-27-reroute-fd4aeeb/).

Table 2 (control and reroute):

| run | verdict | dependency scan of dirichletRealZeroBound_proof | prebuild | comparator wall | peak memory |
|---|---|---|---|---|---|
| control | L093 = ACCEPT_BOTH; exit 0 | L094 = 116314 constants in closure; identical to the 10-09 block | Missing | Missing | Missing |
| reroute | L095 = ACCEPT_BOTH; exit 0 | L096 = 92658 constants in closure; identical to the 10-09 block | Missing | Missing | Missing |

Claims:
- The installed comparator-copy files have sha256 1ce196f5... and af401514...; the patch (L097) = 1 file, +2/-1.
- The patch applies cleanly at fd4aeeb, and the patched file is byte-identical at adc7f12 and fd4aeeb (L050 = applies (git apply --check exit 0)), in a footnote.
- The rerouted chain still imports the patched PrimeNumberTheoremAnd.SiegelZeros.HadamardSupport (L052 = imported). Forward pointer to Section 8.

Corroboration at adc7f12 (2026-10-09):
- The rerouted clone differs from openai/math in one tracked file (L047 = 1 file, +2/-1), plus the two PaperLemma3 modules.
- The challenge file is unchanged (L048 = bedaac0248a641910f79a380d9702d82c6bfbbfd3760a69d27c72c5d8fb136ce).
- Comparator run (L049 = 9244 jobs; ACCEPT_BOTH; exit 0).
- Rerouted scan (L051 = 92658 constants in closure), with the control (L019 = 116314).
- After line 138 is replaced, the closure no longer contains actual_biquadratic_rectangle_span (L018 = absent).

Clone setup (wording fixed by Joe, docs/paper/methods-notes.md, Update 2026-10-27): "local clone of fd4aeeb; package directory reused read-only from the original clone; OAI closure built from scratch."
- The ledger notes on L093 and L095 say "fresh local clone /home/checker/math-r2; packages bind-mounted read-only from the original clone". The paper must not use "fresh clone" alone.

Missing claims:
- Clone setup: local clone, packages bind-mounted read-only (write test refused), OAI closure built from scratch. Present only as notes on L093 and L095, not as a claim row. Source: results/2026-10-27-reroute-fd4aeeb/SUMMARY.md and run.log.
- Prebuild times for the control and the reroute, and the reason they differ. The reason is INFERRED: the reroute ran in the same clone after the control and rebuilt only the new and patched modules and their dependents. No ledger row. Source: control-prebuild.log, reroute-prebuild.log ("Service runtime").
- Comparator wall times and peak memory for both runs. No ledger row. Source: SUMMARY.md, control-comparator.log, reroute-comparator.log.
- The guard made no stops during the runs. No ledger row. Source: SUMMARY.md.

Citations: openai/math adc7f12 and fd4aeeb; Comparator; nanoda_lib; Lean 4.

## 7. Corpus context (1.5 pages)

Purpose: place the SiegelZeros result within the full replay of the openai/math corpus, with official and unofficial tools kept apart.

Table 3 (the one table):

| block | official tool set (nanoda 3a24072) | unofficial nanoda builds | independent replay [STATED] |
|---|---|---|---|
| 189 referenced configs | L053 = 187 + 2 (187 at fd4aeeb, SiegelZeros and QuasiRiemannHypothesis in the adc7f12 pilot); L054 = 178 / 9 (9 ACCEPT_LEAN_ONLY, nanoda 3a24072 crashes) | L055 = 9 of 9 pass with f67473b (UNOFFICIAL) | [STATED L065] = 416/416 accepted by Comparator as shipped |
| 227 unreferenced configs | L056 = 212 / 15; L057 = {'ACCEPT_BOTH': 205, 'LEAN_ACCEPT_NANODA_CRASH': 6, 'NOT_CHECKED_HERE': 15, 'TIMEOUT': 1} | see Catalan/KMedianThreshold row | [STATED L066] = 401/416 (nanoda 3a24072 at 1 GiB stack) |
| Catalan, KMedianThreshold | official: NOT_CHECKED_HERE (L057) | L058 = both kernels (unofficial nanoda): Lean via the shipped-config comparator, nanoda via B3 | [STATED L067] = 10 (the ten master failures check with the let fix, Nat.succ guard and 64 MiB) |
| ContinuumCoulombHardness | "not completed on this machine (memory)" (L059 = DEFERRED (permanent)) | none | Missing (see below) |
| export sizes | L060 = 146 (0 differ, 14 not comparable); L061 = 11 (13 incl. 2 from extended records) | | |

Claims:
- nanoda failure classes, each with its members:
  - class 1 [INFERRED L062] = RoundTables group (8), Laughlin group (3), KMedianThreshold, Catalan;
  - class 2 [INFERRED L063] = KaplanskyFinitelyPresented, GroupRingDeterminant, KaplanskyDirectFiniteness (COMPUTED); MatchingFPRAS, ContingencyTables, LogspaceEquality, RandomizedMeanPayoff, PeriodicGroup (STATED);
  - class 3 [INFERRED L064] = SquareDifference.
- The patch used for B3 is nealmcb's, sha256 computed here before applying (L068 = edd9824f5fd93c86d3f52acea1373a915ccfddf23db33c5e919f03f7c642bc30) [STATED L068], in a footnote.
- nealmcb's 416-config sweep ran on nanoda master [STATED L069] = 8199c74, in a footnote.
- Jacobsthal, JacobsthalImproved and OstmannPrimes are ACCEPT_BOTH (L090 note). The sentence on their separate copy is in Section 4.
- The 227 table's cell text for ContinuumCoulombHardness follows Joe's wording. The ledger value stays DEFERRED (permanent) (L059).

Missing claims:
- Lean-kernel times for Catalan and KMedianThreshold. No ledger row; L058 gives the status only. Source: results/2026-10-27-reroute-fd4aeeb/optional/README.md, section A.
- nealmcb's ContinuumCoulombHardness figures [would be STATED]: f67473b and 37cb87b-with-patch acceptance, times and memory, and his comparator acceptance. No ledger row. Source: optional/README.md, section B, with URLs at 1ca7ff2.
- ContinuumCoulombHardness guard-stop details (thread counts, MemAvailable). L059 summarises them in its claim text; add a row if the table footnote gives figures.
- Outcome-level agreement with the independent replay. Same item as Section 0 claim 4.

Citations:
- nealmcb/openai-math-lean-tooling at 1ca7ff2a0280760783ee2b198c0d6f2a1cfeaba4;
- nanoda_lib issues #55, #61, #62;
- openai/math fd4aeeb;
- Zenodo corpus record (L084).

## 8. Threats to validity (1.25 pages)

Purpose: list what could make the results wrong or weaker than stated, with the evidence for each.

Claims:
- Kernel trust.
  - Missing claim: what each kernel checks and the components both depend on (exporter, Lean front end for the Lean kernel). No ledger row. Candidate source: docs/paper/independence.md (a)-(c).
- Statement faithfulness rests on reading [INFERRED L002, L004, L006, L008]. The non-vacuity lemmas (L011-L014) rule out a vacuous challenge; they do not establish faithfulness.
- The patched HadamardSupport dependency: the rerouted chain imports PrimeNumberTheoremAnd.SiegelZeros.HadamardSupport, created by OAI's patch (L052 = imported).
- The paper's analytic sections are out of scope (scope statement, no value).
- Sandbox history:
  - Original filter (L070 = 5 families denied).
  - Under it, IP and DNS fail (L071 = blocked (errno 97)), but AF_VSOCK to the Windows host connects (L072 = connected). No route to the internet was tested.
  - AF_PPPOX and AF_ALG were also creatable (L073 = AF_PPPOX, AF_ALG).
  - The first SiegelZeros comparator run used ~AF_UNIX only (L074 = ~AF_UNIX only). The first run under the 5-family filter ended at L075 = 2026-10-08 14:18.
  - From 2026-10-26 16:40, all 45 families are denied (L076 = 45 families).
  - t25 probe (L077 = 138 / 138 errno 97).
  - All primary SiegelZeros results in Sections 5 and 6 (L032, L093-L097) ran under the 45-family list.
- WSL memory:
  - L078 = ElementaryPositivity, KaplanskyDirectFiniteness, ShortEgyptianFractions (the three results recorded before the change to 24 GB);
  - L079 = 20 GB (from 2026-10-22 08:10).
  - MemoryMax is not enforced (L080 = not enforced). The rerun with saved output (L098 = not enforced; v1 cap kills) is the row to cite for the test; L080 carries the cap and guard design.
- The superseded metaprogram: lean-checks/MainRerouted.lean defines elab "#reroute" and adds copies with addDecl (L091 = #reroute + addDecl). Name it as not evidence. Its results file, results/2026-10-08-lean-main-rerouted.txt, is not cited anywhere in the paper.

Missing claims:
- Kernel trust (above).

Citations: Comparator; grwtsk/openai-math #40 (sandbox follow-up, comment 6431288875); nanoda_lib.

## 9. Artifacts (0.5 page)

Purpose: tell a reader exactly which files and records reproduce each result.

Claims:
- Repository commit to be tagged: TBD at the paper's final version.
  - L086 is stale: it records HEAD at ledger time as 3 commits ahead of bb6f197, and origin is now at cd6ddb7. It needs a new row at tag time.
  - Earlier tags (L086): reviewer-packet-v1 (8d265cd), -v1.1 (d182d03), -v2-preliminary (9bf7d0b), -v3 (d1aff7a).
- Zenodo:
  - L081 = 10.5281/zenodo.23269528;
  - L082 = 10.5281/zenodo.23499651;
  - L083 = 10.5281/zenodo.23523697;
  - L084 = 10.5281/zenodo.23505836 (corpus replay);
  - concept DOI L085 = 10.5281/zenodo.23269527.
  - The final deposit is held until the paper's final version.
- Canonical and comparator-copy files with sha256:
  - PaperLemma3/Lemma3.lean (L024 = 1ce196f54fa98689bbea6bd74f2abdb110f5cbcca2eecddcca9316b8af465283);
  - Bridge.lean (af401514808dde5bb913ce8e87cc5280b704a234ea324897d1a1ced1f218f250, from L025-L028 sources);
  - Lemma3Bridged.lean (6ce38ac1ef33c8b46028205bb043718565b679175b63cc6fbf8089136554cdb4, L029 source);
  - Lemma3.lean (ecdbf400b24f9241cd03cf383bdcd97ed71e4812578e66d7159a846447f7b1a7, L022 source);
  - NonVacuity.lean (L015).
- Toolchain and nanoda pins: L087, L088, L092.
- lean-checks/README.md: the role of each Lean file.

Missing claims:
- The tag commit (above).
- lean-checks/README.md has no ledger row (committed at 758b44f). Add one if the paper cites the README's role table.

Citations: Zenodo records; the repository.

## 10. AI-use disclosure (0.25 page)

Purpose: say what Claude Code produced, as facts with sources, and leave the human-review account to Joe.

Claims: none. The ledger has no row about authorship of the Lean files or run scripts.

Missing claims (candidate sources, no values given):
- Which Lean files in lean-checks/ Claude Code wrote. Candidate sources: docs/log.md; git history (Co-Authored-By trailers).
- Which run scripts in wsl-comparator/ and src/ Claude Code wrote. Same candidate sources.
- Which public posts were drafted by Claude Code (for example the #61 and #40 comments). Candidate source: docs/log.md.

> JOE WRITES THIS: the human-review sentences (what was reviewed by a person, how, and what was not).

## Appendix candidates (not decided)

- A. Full 189 and 227 per-config tables (corpus-227-v3.tsv and the 189 summary).
- B. The +2/-1 diff in full (reroute-diff.txt).
- C. The full Lean statements of the bridge lemmas (bridge_descent, bridge_main, via_lemma3).
- D. The nanoda version matrix (matrix-v3.tsv), UNOFFICIAL.
- E. The sandbox probes (t22-t26) and the 45-family list.
- F. The small-N execution details (L046).
- G. The statement-check sub-claims, all 34 axioms outputs (L009).
- H. The two count conventions for Section 4 (L020, L021) with the counting script.

## Claims used in more than one section (risk of inconsistent restatement)

| ids | sections | what to keep consistent |
|---|---|---|
| L019, L094 | 0, 4, 6 | 116314 and "identical at fd4aeeb" |
| L051, L096 | 0, 6 | 92658 and the two matches |
| L095, L093 | 0, 1, 6 | "accepted by Comparator with both kernels", exit 0 |
| L097, L047 | 0, 6 | 1 file, +2/-1, at both commits |
| L032 | 0, 5, 8 | the nine declarations, standard axioms |
| L016, L017, L018 | 0, 4, 6 | "only use" is within the SiegelZeros tree |
| L089, L090 | 1, 4, 7 | import level only; "3 of 416"; the exact scope sentence |
| L002, L004, L006, L008 | 1, 3, 8 | always [INFERRED] |
| L007, L048 | 2, 3, 6 | the challenge sha256 |
| L052 | 6, 8 | "imported" (the dependency, not a claim about its correctness) |
| L065 | 0, 7 | [STATED], 416/416 |
| L059 | 7, 8 (via memory) | cell text vs ledger value |
| L076 | 0, 8 | 45 families |
| L091 | 5 (draft footnote), 8 | not evidence |

## Citations needed by section (from citations-needed.md; UNCONFIRMED flagged)

| section | works |
|---|---|
| 0 | paper (**version label UNCONFIRMED**), openai/math, Comparator, nanoda_lib, nealmcb repo at 1ca7ff2 |
| 1 | paper (**version label UNCONFIRMED**), arXiv:2610.15483, Lu–Zaman–Zhao |
| 2 | Comparator (full commit now confirmed, L092), nanoda_lib, lean4export (full commit now confirmed, L092), Lean 4, Mathlib, paper |
| 3 | paper, openai/math fd4aeeb, Mathlib, grwtsk/openai-math #29 (only if L010 is placed) |
| 4 | openai/math adc7f12 and fd4aeeb |
| 5 | paper, Mathlib, nanoda_lib, Fischler 2005 (**internal theorem and lemma numbers UNCONFIRMED**), arXiv:2610.15483 |
| 6 | openai/math adc7f12 and fd4aeeb, Comparator, nanoda_lib, Lean 4 |
| 7 | nealmcb repo at 1ca7ff2, nanoda_lib #55, #61, #62, openai/math fd4aeeb, Zenodo corpus record |
| 8 | Comparator, grwtsk/openai-math #40, nanoda_lib |
| 9 | Zenodo records, the repository |
| 10 | none |

- Not to be cited: Bastounis–Circelli–Hansen (arXiv:2610.08144). No local copy; all details UNCONFIRMED; no ledger row uses it.
- The Comparator and lean4export UNCONFIRMED entries in the citations table are resolved by the appended update in citations-needed.md and by L092.

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
