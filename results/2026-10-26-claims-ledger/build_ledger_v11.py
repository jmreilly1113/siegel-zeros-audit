"""Claims ledger v11 (2026-10-27): the two formal routes. Writes ledger-v11.tsv (refuses to overwrite).

Usage: python -I results/2026-10-26-claims-ledger/build_ledger_v11.py <repo root>
Append-only: every ledger-v10.tsv row is copied byte-for-byte (old rows are not edited, as in v10); new rows L251-L257.
L251 supersedes v9:L199 (its note says so; v9:L199 itself is unchanged).
"""
import csv, hashlib, os, sys, collections

root = sys.argv[1]
OUT = os.path.join(root, 'results', '2026-10-26-claims-ledger')
problems = []


def _read(p):
    full = os.path.join(root, p) if not p.startswith('\\\\') else p
    b = open(full, 'rb').read().replace(b'\r\n', b'\n')
    return b, b.decode('utf-8', 'replace').split('\n')


def R(path, sub, nth=1):
    _, L = _read(path)
    hits = [i + 1 for i, l in enumerate(L) if sub in l]
    if len(hits) < nth:
        problems.append(f'R not found: {path} :: {sub!r}'); return f'{path}:?'
    return f'{path}:{hits[nth - 1]}'


def L(path, a, b, sub):
    raw, lines = _read(path)
    if sub not in '\n'.join(lines[a - 1:b]): problems.append(f'L mismatch: {path}:{a}-{b} :: {sub!r}')
    return f'{path}:{a}-{b} (LF sha256 {hashlib.sha256(raw).hexdigest()})'


A_ = 'adc7f1241b42e322a6451854ab7e4b4c146bf78a'; F_ = 'fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb'
TC = 'Lean 4.34.1 / Mathlib d13f23b / Comparator d03acab / lean4export 076e8e5'
NR = 'n/a'; NONE = 'none (no run; source text)'
SB45 = '45-family RestrictAddressFamilies (every family of kernel 5.15.167.4; 75d/140d/67d), checker, NoNewPrivs'
W = '\\\\wsl.localhost\\Ubuntu-24.04\\home\\checker\\math\\lean\\OAI\\NumberTheory\\SiegelZeros\\'
ACT = W + 'Structure\\ArithmeticCutoffTransport.lean'; RDT = W + 'Determinants\\RectangleDeterminant.lean'; SB = W + 'Selection\\SelectionBridge.lean'
BZ = W + 'Intersection\\BezoutBoundary.lean'; DIR = W + 'Selection\\Directions.lean'; OMG = W + 'Structure\\OmegaIndependence.lean'
TR = 'results/2026-10-27-two-routes/'; BR = 'lean-checks/comparator-copy/PaperLemma3/Bridge.lean'
IJ = 'lean-build/OAI/NumberTheory/SiegelZeros/Structure/InvariantJetLinearMap.lean'

with open(os.path.join(OUT, 'ledger-v10.tsv'), encoding='utf-8') as f:
    rd = csv.reader(f, delimiter='\t'); cols = next(rd); rows = [dict(zip(cols, r)) for r in rd]
assert [r['id'] for r in rows] == [f'L{k:03d}' for k in range(1, 251)], 'ledger-v10.tsv ids are not L001-L250'
new = []


def row(i, sec, claim, value, unit, src, label, commit, tc, sb, note='', read_by=''):
    assert i == f'L{251 + len(new):03d}', i
    new.append(dict(id=i, paper_section=sec, claim=claim, value=value, unit=unit, source='; '.join(src),
                    label=label, openai_math_commit=commit, toolchain=tc, sandbox=sb, status='FOUND', note=note, read_by=read_by, read_note=''))


# item 1
EQ = TR + 'equivalence.log'; CE = 'lean-checks/ChallengeEquivalence.lean'
row('L251', '2; 3', 'The two SiegelZeros challenge statements, copied verbatim from SiegelZeros.lean:9-14 and 20-25 as Props in a Mathlib-only file, are equivalent: ChallengeEquivalence.statements_equivalent proves ExistsAbsoluteRealZeroGap <-> DirichletRealZeroBound.',
    "[propext, Classical.choice, Quot.sound]", 'axioms',
    [L(CE, 1, 1, 'import Mathlib'), L(CE, 11, 17, 'def ExistsAbsoluteRealZeroGap : Prop :='), L(CE, 20, 26, 'def DirichletRealZeroBound : Prop :='), L(CE, 28, 28, 'theorem statements_equivalent : ExistsAbsoluteRealZeroGap ↔ DirichletRealZeroBound := by'),
     R(EQ, "'ChallengeEquivalence.statements_equivalent' depends on axioms: [propext, Classical.choice, Quot.sound]"), R(EQ, 'LEAN EXIT CODE: 0'), R(EQ, 'HEAD fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb, tracked changes 0')],
    'COMPUTED', F_, TC, SB45, note='supersedes v9:L199 (INFERRED: logically equivalent, not the same type); v9:L199 is unchanged. `XR_L=/home/checker/math/lean bash wsl-comparator/75r_sbx.sh 1800 4 "lake env lean /tmp/tr/ChallengeEquivalence.lean"`, no build. The two Props are not the same type; the proof uncurries the three zero hypotheses')

# item 2: the spanning hypothesis of the main route, quoted from source
row('L252', '4', "The main route's spanning hypothesis is W50.ActualCutoffSpanning H N d a ha (Structure/ArithmeticCutoffTransport.lean:356-366): with L = rootField a sqrtTwo, the rows W60.weightedRow of the theta values theta(u, v, n_j), theta(-u, v, n_j), theta(-u, -v, n_j) of the integral roots u, v over the box exponents n_j (j : Fin (N^4)) span L^(N^4) when restricted to the weighted cutoff W62.cutoff H (sourceCutoff H N). W28.actualCutoffSpanning_of_localBezout (lines 488-514) proves it for 0 < H <= N and squarefree d != 1, 2 from W22.LocalIsolatedBezoutStatement C: it maps to C with rowSpan_top_of_field_map, reindexes by boxEnumeration, and applies actual_complex_cutoff_spanning. The cutoff is {a : a.coords 0 + H a.coords 1 + H a.coords 2 <= C} (Selection/SelectionBridge.lean:464-466, 412-417) with C = sourceCutoff H N = floor(96 H^(2/3) N^(4/3)) (Determinants/RectangleDeterminant.lean:39-40).",
    'rowSpan over L of weighted theta rows, cutoff weight a0 + H a1 + H a2 <= floor(96 H^(2/3) N^(4/3)); from LocalIsolatedBezoutStatement via actual_complex_cutoff_spanning', 'statement',
    [L(ACT, 356, 366, 'def ActualCutoffSpanning (H N : ℕ) (d : ℤ) (a : ℂ) (ha : a ^ 2 = (d : ℂ)) : Prop :='), L(ACT, 366, 366, '(W62.cutoff H (sourceCutoff H N)) = ⊤'),
     L(ACT, 488, 514, 'theorem actualCutoffSpanning_of_localBezout'), L(ACT, 503, 503, 'apply rowSpan_top_of_field_map'), L(ACT, 507, 507, '(actual_complex_cutoff_spanning hBezout H N hH hHN d hd hd1 hd2 a ha)'),
     L(SB, 412, 417, 'a.coords 0 + H * a.coords 1 + H * a.coords 2'), L(SB, 464, 466, 'def cutoff (H C : ℕ) : Finset (Index H) :='), L(RDT, 39, 40, '⌊96 * (H : ℝ) ^ (2 / 3 : ℝ) * (N : ℝ) ^ (4 / 3 : ℝ)⌋₊')],
    'COMPUTED', F_, NR, 'read-only source reading of the clean fd4aeeb clone')
row('L253', '4', "actual_complex_cutoff_spanning (ArithmeticCutoffTransport.lean:429-447) gets the complex cutoff span from actual_cutoff_spanning_of_localBezout (lines 296-304), which combines cutoff_span_of_rectangularAssertion (RectangleDeterminant.lean:48) with actual_rectangularAssertion_of_localBezout (lines 277-282). RectangularAssertion v H N (RectangleDeterminant.lean:31-37) is a zero test with Corollary 4's bounds: a box polynomial p with every mixed invariant of order a, a 0 <= 32 H^(2/3) N^(4/3) and a 1, a 2 <= 32 H^(-1/3) N^(4/3), vanishing at 1 is zero. The directions are ![1, a, b, a*b], ![1, -a, b, -(a*b)], ![1, -a, -b, a*b] (Selection/Directions.lean:21-22), and the coefficient vector is omegaCoefficients = ![1, 1/a, -(1/b), -(1/(a*b))] (Structure/OmegaIndependence.lean:21).",
    'RectangularAssertion bounds: 32 * H^(2/3) * N^(4/3) and 32 * H^(-(1/3)) * N^(4/3) (the same as Corollary 4); proved via the local Bezout statement', 'statement',
    [L(ACT, 429, 447, 'theorem actual_complex_cutoff_spanning'), L(ACT, 444, 444, 'have hspan := actual_cutoff_spanning_of_localBezout hBezout'), L(ACT, 296, 304, 'theorem actual_cutoff_spanning_of_localBezout'),
     L(ACT, 303, 304, 'cutoff_span_of_rectangularAssertion (fun i => (basis i).val) hH'), L(ACT, 277, 282, 'theorem actual_rectangularAssertion_of_localBezout'),
     L(RDT, 31, 37, 'def RectangularAssertion (v : Fin 3 → Fin 4 → K) (H N : ℕ) : Prop :='), L(RDT, 34, 34, '(a 0 : ℝ) ≤ 32 * (H : ℝ) ^ (2 / 3 : ℝ) * (N : ℝ) ^ (4 / 3 : ℝ) →'),
     L(RDT, 35, 35, '(a 1 : ℝ) ≤ 32 * (H : ℝ) ^ (-(1 / 3 : ℝ)) * (N : ℝ) ^ (4 / 3 : ℝ) →'), L(RDT, 48, 48, 'theorem cutoff_span_of_rectangularAssertion'),
     L(DIR, 21, 22, '![![1, a, b, a*b], ![1, -a, b, -(a*b)], ![1, -a, -b, a*b]]'), L(OMG, 21, 21, 'def omegaCoefficients (a b : K) : Fin 4 → K := ![1, 1 / a, -(1 / b), -(1 / (a * b))]')],
    'COMPUTED', F_, NR, 'read-only source reading of the clean fd4aeeb clone',
    note='so the main route does not use actual_biquadratic_rectangle_span, but it does prove a Corollary-4-shaped zero test with the same constants, by the local Bezout statement')
row('L254', '4', "Comparison of the main route's spanning statement with Lemma3.rectangle and with OAI's actual_biquadratic_rectangle_span, by reading the source. Rows: all three use products of the three conjugate linear forms of n with exponents a 0, a 1, a 2 (main route: theta(u,v,n), theta(-u,v,n), theta(-u,-v,n); after mapping to C these are the rows of A = the directions matrix, whose kernel is spanned by omegaCoefficients). Exponents: Lemma3.rectangle and actual_biquadratic_rectangle_span use the rectangle a 0 <= 32 H^(2/3) N^(4/3), a 1, a 2 <= 32 H^(-1/3) N^(4/3); the main route uses the weighted cutoff a 0 + H a 1 + H a 2 <= floor(96 H^(2/3) N^(4/3)), which contains that rectangle (32 H^(2/3)U + 2 H 32 H^(-1/3) U = 96 H^(2/3) U). Field: Lemma3.rectangle spans over C; actual_biquadratic_rectangle_span over the number field K; the main route over L = rootField a sqrtTwo, reached from C by rowSpan_top_of_field_map. Plausibility: Lemma3.rectangle, applied with A = the directions matrix and c = omegaCoefficients (Q-independent by actual_omega_independent), plus the inclusion of the rectangle in the cutoff, plus OAI's own rowSpan_top_of_field_map and boxEnumeration reindexing (a descent like bridge_descent), would plausibly give ActualCutoffSpanning without the local Bezout statement. Differences: rectangle versus weighted cutoff index sets (Index H, Fin (N^4)), span form versus the zero-test form RectangularAssertion, and the field.",
    'plausible; differences: index set (rectangle vs weighted cutoff, which contains it), form (span vs zero test), field (C vs L), indexing', 'finding',
    [L(BR, 96, 109, 'theorem rectangle'), L(IJ, 471, 484, 'theorem actual_biquadratic_rectangle_span'), L(ACT, 356, 366, 'def ActualCutoffSpanning'), L(RDT, 31, 37, 'def RectangularAssertion'),
     L(SB, 412, 417, 'a.coords 0 + H * a.coords 1 + H * a.coords 2'), L(RDT, 39, 40, '⌊96 * (H : ℝ) ^ (2 / 3 : ℝ) * (N : ℝ) ^ (4 / 3 : ℝ)⌋₊'), L(ACT, 382, 382, 'theorem rowSpan_top_of_field_map'), L(ACT, 414, 414, 'theorem actual_omega_independent'),
     L(BR, 147, 155, 'theorem bridge_descent')],
    'INFERRED', F_, TC, NONE, note='no proof was written or run; "plausibly" rests on reading the statements. Not read in detail: W40.rowEntry and the proof of cutoff_span_of_rectangularAssertion', read_by='')

# item 3
CTL = TR + 'routes-control.log'; RER = TR + 'routes-reroute-2.log'
row('L255', '4', 'In the main route, uniform_exclusion_of_local_isolated_bezout obtains the spanning hypothesis of uniform_exclusion_of_actual_cutoff from W28.actualCutoffSpanning_of_localBezout (BezoutBoundary.lean:16-19); the closure of exists_absolute_real_zero_gap contains actualCutoffSpanning_of_localBezout, actual_complex_cutoff_spanning, actual_cutoff_spanning_of_localBezout, actual_rectangularAssertion_of_localBezout and cutoff_span_of_rectangularAssertion.',
    'actualCutoffSpanning_of_localBezout (BezoutBoundary.lean:18)', 'proof step',
    [L(BZ, 16, 19, 'exact W28.actualCutoffSpanning_of_localBezout hBezout H N (by omega) hHN'), R(CTL, 'OAI.SiegelZeros.WeightedTorusJets.W28.actualCutoffSpanning_of_localBezout,'), R(CTL, 'OAI.SiegelZeros.WeightedTorusJets.W28.actual_rectangularAssertion_of_localBezout,'), R(CTL, 'OAI.SiegelZeros.WeightedTorusJets.W28.cutoff_span_of_rectangularAssertion,')],
    'COMPUTED', F_, TC, SB45)
row('L256', '4', 'Shared names: exists_good_mass_for_actual_zeros_normalized (W63), false_of_eventual_exists_pivot_master and exists_actual_character_pivot_master (W50) are in the closure of exists_absolute_real_zero_gap and in neither the control nor the rerouted closure of dirichletRealZeroBound_proof. The second route matches only the three Corollary 4 lemmas in the control and none of the probed names in the reroute.',
    'main route: all three; dirichletRealZeroBound_proof: none (control and reroute)', 'membership',
    [R(CTL, 'OAI.SiegelZeros.WeightedTorusJets.W63.exists_good_mass_for_actual_zeros_normalized]'), R(CTL, 'OAI.SiegelZeros.SiegelZerosAwei.W50.false_of_eventual_exists_pivot_master,'), R(CTL, 'OAI.SiegelZeros.SiegelZerosAwei.W50.exists_actual_character_pivot_master,'),
     R(CTL, 'OAI.SiegelZeros.WeightedTorusJets.dirichletRealZeroBound_proof: 116314 constants in closure; CategoryTheory 9454; AlgebraicGeometry 3035; matches: [OAI.SiegelZeros.WeightedTorusJets.actual_biquadratic_rectangle_span,'),
     R(RER, 'OAI.SiegelZeros.WeightedTorusJets.dirichletRealZeroBound_proof: 92658 constants in closure; CategoryTheory 2553; AlgebraicGeometry 0; matches: []'), L('lean-checks/RouteCompare.lean', 42, 42, '#route_compare OAI.SiegelZeros.WeightedTorusJets.dirichletRealZeroBound_proof')],
    'COMPUTED', F_, TC, SB45, note='matching by last name component (RouteCompare.lean, as ReroutedDeps.lean). So the two routes do not share these three steps by name; whether they share other Lemma 6 or Lemma 7 machinery was not tested')
row('L257', '4', 'CategoryTheory and AlgebraicGeometry names (first name component) in the closures, by the v7:L020 convention (names reachable from the root through types and values, as #find_deps): exists_absolute_real_zero_gap 9434 and 3024 in both clones; dirichletRealZeroBound_proof 9454 and 3035 in the control, 2553 and 0 in the reroute. The control minus reroute difference, 6901 and 3035, equals v7:L020.',
    'exists_absolute_real_zero_gap: CategoryTheory 9434, AlgebraicGeometry 3024; dirichletRealZeroBound_proof: 9454/3035 (control), 2553/0 (reroute); difference 6901 + 3035', 'names',
    [R(CTL, 'OAI.SiegelZeros.WeightedTorusJets.exists_absolute_real_zero_gap: 107760 constants in closure; CategoryTheory 9434; AlgebraicGeometry 3024'),
     R(RER, 'OAI.SiegelZeros.WeightedTorusJets.exists_absolute_real_zero_gap: 107760 constants in closure; CategoryTheory 9434; AlgebraicGeometry 3024'),
     R(CTL, 'dirichletRealZeroBound_proof: 116314 constants in closure; CategoryTheory 9454; AlgebraicGeometry 3035'), R(RER, 'dirichletRealZeroBound_proof: 92658 constants in closure; CategoryTheory 2553; AlgebraicGeometry 0'),
     R('results/2026-10-09-route-declaration-overlap.txt', '6901'), L('lean-checks/RouteCompare.lean', 3, 6, 'whose first name component')],
    'COMPUTED', F_, TC, SB45, note='the rerouted-clone run needed its package directory bind-mounted read-only again (routes-reroute-2.log); the first attempt (routes-reroute.log) failed with lake trying to clone Mathlib, which the sandbox blocked')

if problems:
    print('PROBLEMS (ledger not written):'); print('\n'.join(ascii(x) for x in problems)); sys.exit(1)
p = os.path.join(OUT, 'ledger-v11.tsv')
if os.path.exists(p): sys.exit(f'refusing to overwrite {p}')
with open(p, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t', lineterminator='\n'); w.writerow(cols)
    for r in rows + new: w.writerow([r[c] for c in cols])
print('rows', len(rows) + len(new), 'new', [r['id'] for r in new], dict(collections.Counter(r['label'] for r in new)))
