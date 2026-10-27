"""Claims ledger for the cs.LO paper (2026-10-26). Read-only on the repo; writes ledger.tsv next to this file.

Usage: python -I results/2026-10-26-claims-ledger/build_ledger.py <repo root>
Every source of kind R/L is resolved and checked mechanically:
  R(path, substring, nth=1)          -> "path:LINE", the line of the nth occurrence of substring (exit 1 if absent)
  L(path, a, b, substring)           -> "path:a-b (LF sha256 ...)", substring must occur within lines a..b of a Lean source
  U(url)                             -> recorded as given (pinned URL)
Lines are 1-based, counted after normalising CRLF to LF; sha256 of Lean sources is of the LF bytes.
"""
import hashlib, os, re, sys

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
    seg = '\n'.join(lines[a - 1:b])
    if sub not in seg: problems.append(f'L mismatch: {path}:{a}-{b} :: {sub!r}')
    return f'{path}:{a}-{b} (LF sha256 {hashlib.sha256(raw).hexdigest()})'


def U(url): return url


A_ = 'adc7f1241b42e322a6451854ab7e4b4c146bf78a'; F_ = 'fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb'
TC = 'Lean 4.34.1 / Mathlib d13f23b / Comparator d03acab / lean4export 076e8e5'
TCN = TC + ' / nanoda 3a24072 (STACK_SIZE 16 MiB)'
SB0 = 'comparator README wrapper: systemd-run --user RestrictAddressFamilies=~AF_UNIX (IP open)'
SB5 = 'systemd-run --user, checker, NoNewPrivs; RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET (5-family; AF_VSOCK/AF_ALG/AF_PPPOX not denied)'
SB5C = 'system unit + setpriv to checker; 5-family RestrictAddressFamilies; 16G v1 cgroup cap (140_matrix_run.sh)'
SB45 = '45-family RestrictAddressFamilies (every family of kernel 5.15.167.4; 75d/140d/67d), checker, NoNewPrivs'
NONE = 'none (no run; source text)'
NR = 'n/a'
NEAL = 'https://github.com/nealmcb/openai-math-lean-tooling/blob/1ca7ff2a0280760783ee2b198c0d6f2a1cfeaba4/'
I55 = 'https://github.com/ammkrn/nanoda_lib/issues/55'
I61c = 'https://github.com/ammkrn/nanoda_lib/issues/61#issuecomment-6402528075'
I55n = 'https://github.com/ammkrn/nanoda_lib/issues/55#issuecomment-6293743601'
I55f = 'https://github.com/ammkrn/nanoda_lib/issues/55#issuecomment-6208777323'
I55a = 'https://github.com/ammkrn/nanoda_lib/issues/55#issuecomment-6293428329'
I62 = 'https://github.com/ammkrn/nanoda_lib/issues/62'
WSLM = '\\\\wsl.localhost\\Ubuntu-24.04\\home\\checker\\math\\lean\\'
IJ = 'lean-build/OAI/NumberTheory/SiegelZeros/Structure/InvariantJetLinearMap.lean'
BR = 'lean-checks/comparator-copy/PaperLemma3/Bridge.lean'
PL = 'lean-checks/comparator-copy/PaperLemma3/Lemma3.lean'
LB = 'lean-checks/Lemma3Bridged.lean'
LG = 'results/2026-10-26-claims-ledger/'
MX = 'results/2026-10-26-nanoda-version-matrix/'
XR = 'results/2026-10-21-extended-replay/'
rows = []


def row(sec, claim, value, unit, src, label, commit, tc, sb, status='FOUND', note=''):
    rows.append([sec, claim, value, unit, '; '.join(src) if isinstance(src, (list, tuple)) else src, label, commit, tc, sb, status, note])


# ---------------- Section 3: statement faithfulness ----------------
for ch, cp, ln in (('QuasiRiemannHypothesis', 'docs/statement-check-QuasiRiemannHypothesis.md', None),
                   ('DirichletSevenEighths', 'docs/statement-check-DirichletSevenEighths.md', None),
                   ('HeckeSevenEighths', 'docs/statement-check-HeckeSevenEighths.md', None)):
    h = {'QuasiRiemannHypothesis': '065f8c9a01d28db78c8b1bfc5083b535082a2d2aac2230d563f98b8caa812cc5',
         'DirichletSevenEighths': '8fb13ad977bca104591fcbc6ef01a58496e7385053c9b1445f95749afc0eff54',
         'HeckeSevenEighths': 'cb5e404fa65a502c0a9006b9ad45c28914feb79e4b7b1ffcf05e4af82ed0cfc2'}[ch]
    row('3', f'The family-003 challenge file lean/ComparatorChallenges/{ch}.lean at openai/math fd4aeeb has this sha256, and the StatementChecks copy used for the checks is byte-identical to it.',
        h, 'sha256', [R(LG + 'challenge-copies.tsv', ch), R('results/2026-10-20-statement-checks/lean-sources.sha256', ch)],
        'COMPUTED', F_, NR, NR)
    row('3', f'{ch}: the Lean challenge statement matches the paper statement (finding of the statement check).',
        'MATCH' + (' (L-function row by Joe\'s ruling 2026-10-20; one identification INFERRED)' if ch == 'HeckeSevenEighths' else
                   ' (except s = 1, covered by Mathlib\'s junk value)' if ch == 'QuasiRiemannHypothesis' else ''), 'finding',
        [R('docs/statement-check-summary.md', f'**{ch}:**'), cp,
         R(LG + 'statement-checks-final-v2.log', 'depends on axioms')], 'INFERRED', F_, TC, NR, 'FOUND',
        'rests on: reading of Lean statement against paper text (argument in ' + cp + '); Lean sub-claims (non-vacuity, series identities, holomorphy) are COMPUTED in statement-checks-final-v2.log')
row('3', 'The SiegelZeros challenge file (adc7f12) has this sha256; it is unchanged at fd4aeeb.',
    'bedaac0248a641910f79a380d9702d82c6bfbbfd3760a69d27c72c5d8fb136ce', 'sha256',
    [R('results/2026-10-08-lean-comparator-wsl.txt', 'sha256 ComparatorChallenges/SiegelZeros.lean'), R(LG + 'challenge-copies.tsv', 'SiegelZeros')], 'COMPUTED', f'{A_} and {F_}', NR, NR)
row('3', 'SiegelZeros: the challenge statement matches Theorem 1 of the paper (hypotheses primitive, nonprincipal, real, q >= 3, beta in (0,1)).',
    'MATCH', 'finding', [R('docs/paper-map.md', 'Lean statement fidelity'), R('results/2026-10-08-lean-type-compare.txt', 'Challenge')],
    'INFERRED', A_, TC, NR, 'FOUND', 'rests on: reading of Lean statement against paper text (docs/paper-map.md); type equality challenge vs solution is COMPUTED in results/2026-10-08-lean-type-compare.txt')
row('3', 'All 34 #print axioms outputs of the statement-check build are exactly [propext, Classical.choice, Quot.sound].',
    '34', 'declarations', [R(LG + 'statement-checks-final-v2.log', "HeckeNorm.norm_coordinateElement' depends on axioms"),
                            'copied 2026-10-26 from WSL /lean-build-final-v2.log (sha256 2f3d3814b84337a0a402791f260ac39bb7e6b753a0242a4c7ce135360ff00388), written 2026-10-20 12:51'],
    'COMPUTED', F_, TC, 'statement-checks lake build (not sandboxed by systemd-run)', 'FOUND',
    'the v1 log results/2026-10-20-statement-checks/lean-build-final.log has 32 (no HeckeNorm); docs cite the v2 path in results/, which never existed there')
row('3', 'The four statement audits were posted publicly on grwtsk/openai-math #29.', '2026-10-20T16:56:00Z', 'timestamp',
    U('https://github.com/grwtsk/openai-math/issues/29#issuecomment-6296359378'), 'COMPUTED', F_, NR, NR, 'FOUND',
    'comment id 6296359378 by the project account, read via API 2026-10-26, created = updated (not edited)')
NV = 'lean-checks/NonVacuity.lean'
for name, what in (('hypotheses_satisfiable', 'for every odd prime p, the quadratic character mod p satisfies all hypotheses of the challenge (q = p >= 3, primitive, nonprincipal, real)'),
                   ('quadChar_LFunction_eq_LSeries', 'the L-function of the quadratic character equals its Dirichlet series for Re s > 1'),
                   ('quadChar_LFunction_one_ne_zero', 'L(1, chi_p) != 0 for the quadratic character mod an odd prime p'),
                   ('specialization', 'the challenge theorem specialises to an explicit statement about the quadratic characters (an exists c > 0, for all odd primes p, ...)')):
    row('3', f'NonVacuity.{name}: {what}.', "[propext, Classical.choice, Quot.sound]", 'axioms',
        [R('results/2026-10-08-lean-nonvacuity.txt', f"'NonVacuity.{name}' depends on axioms"), R(NV, f'theorem {name}')],
        'COMPUTED', A_, TC, 'lake env lean as checker in the comparator-checked clone (32_nonvacuity.sh)', 'FOUND',
        'results file records NonVacuity.lean sha256 b9fae4da...; it equals the current LF file sha256 (next row)')
row('3', 'NonVacuity.lean source file (the file whose lemmas are listed above).', 'see sha256', 'file', L(NV, 58, 60, 'hypotheses_satisfiable'), 'COMPUTED', A_, NR, NR)

# ---------------- Section 4: OAI route vs paper ----------------
row('4', "OAI's Corollary 4, actual_biquadratic_rectangle_span, is stated at InvariantJetLinearMap.lean:471-484 (identical file at adc7f12 and fd4aeeb).",
    '09b8bd7fa82365e69caebfad466d039d85084595376766a731945fa5c11a2bdc', 'sha256 (LF)',
    [L(IJ, 471, 484, 'theorem actual_biquadratic_rectangle_span'), L(WSLM + 'OAI\\NumberTheory\\SiegelZeros\\Structure\\InvariantJetLinearMap.lean', 471, 484, 'theorem actual_biquadratic_rectangle_span')],
    'COMPUTED', f'{A_} (lean-build) and {F_} (WSL clone)', NR, NR, 'FOUND', 'both sources carry the same LF sha256 if the claim holds; checked by the ledger script')
row('4', 'Within the SiegelZeros tree, actual_biquadratic_rectangle_span is used only at CharacterGlobalGreedyDeterminantMasterBounds.lean:138 (text search of all OAI .lean sources).',
    '1', 'use sites (SiegelZeros tree)', [R(LG + 'only-use-search.txt', 'SiegelZeros/Characters/CharacterGlobalGreedyDeterminantMasterBounds.lean:138')], 'COMPUTED', F_, NR, 'read-only grep, no sandbox', 'FOUND',
    'the search also finds a separate copy of the code under OAI/NumberTheory/Jacobsthal/Siegel/ (theorem at InvariantJetLinearMap.lean:481, used at CharacterGlobalGreedyDeterminantMasterBounds.lean:140); that tree is a different family, not the SiegelZeros chain')
row('4', 'Scan-based: after replacing line 138, the closure of dirichletRealZeroBound_proof no longer contains actual_biquadratic_rectangle_span (so line 138 was its only use in that closure).',
    'absent', 'match', [R('results/2026-10-09-lean-rerouted-comparator-deps.txt', 'dirichletRealZeroBound_proof: 92658 constants'), R('results/2026-10-09-rerouted-comparator-diff.txt', '+  have hspan := Lemma3.actual_biquadratic_rectangle_span_via_lemma3')],
    'COMPUTED', A_, TC, SB5)
row('4', "Control scan: OAI's unmodified route 2 (dirichletRealZeroBound_proof) depends on actual_biquadratic_rectangle_span, uniform_rectangular_multiplicity and source_rectangle_span_of_polynomial_zero_test.",
    '116314', 'constants in closure', R('results/2026-10-09-lean-rerouted-comparator-deps.txt', 'dirichletRealZeroBound_proof: 116314 constants'), 'COMPUTED', A_, TC, SB5)
row('4', 'Rerouting removes from route 2 these referenced names in the CategoryTheory and AlgebraicGeometry namespaces (referenced-names convention: names reachable from the root through types and values, as #find_deps).',
    '9936 (6901 + 3035)', 'declarations', R('results/2026-10-09-route-declaration-overlap.txt', 'top-level namespaces of the removed names (20 largest): CategoryTheory 6901'), 'COMPUTED', A_, 'lean4export v4.34.0 dumps; src/route_overlap.py (Python 3.14.6)', NR)
row('4', 'The same removal counted over the full lean4export dumps (full-dump convention: every declaration in the dump, incl. unreferenced recursors/constructors).',
    '10107 (7048 + 3059)', 'declarations', R('results/2026-10-09-route-declaration-overlap.txt', 'top-level namespaces of the removed names (20 largest): CategoryTheory 7048'), 'COMPUTED', A_, 'lean4export v4.34.0 dumps; src/route_overlap.py (Python 3.14.6)', NR)

# ---------------- Section 5: Lemma 3 and Corollary 4 ----------------
row('5', 'Lemma3.interpolation (the paper\'s Lemma 3) is stated at lean-checks/Lemma3.lean:816-825 (docstring at 816); the file imports Mathlib only.',
    'Lemma3.interpolation', 'declaration', [L('lean-checks/Lemma3.lean', 816, 825, 'theorem interpolation'), R('lean-checks/Lemma3.lean', 'import Mathlib')], 'COMPUTED', NR, TC, NONE)
row('5', 'Pt t, the box of polynomials with degreeOf j <= t j, is defined at Lemma3.lean:42.', 'Pt', 'definition', L('lean-checks/Lemma3.lean', 42, 43, 'def Pt'), 'COMPUTED', NR, TC, NONE)
row('5', 'The comparator copy PaperLemma3/Lemma3.lean equals lean-checks/Lemma3.lean through "end Lemma3", and is the file installed for the accepted rerouted comparator run.',
    '1ce196f54fa98689bbea6bd74f2abdb110f5cbcca2eecddcca9316b8af465283', 'sha256', [L(PL, 817, 825, 'theorem interpolation'), R('results/2026-10-09-rerouted-comparator-diff.txt', '1ce196f54fa98689bbea6bd74f2abdb110f5cbcca2eecddcca9316b8af465283')], 'COMPUTED', A_, NR, NR)
for nm, a, b, sub in (('rectangle', 96, 109, 'theorem rectangle'), ('bridge_descent', 147, 155, 'theorem bridge_descent'),
                      ('bridge_main', 196, 211, 'theorem bridge_main'), ('actual_biquadratic_rectangle_span_via_lemma3', 288, 290, 'type_of% @OAI.SiegelZeros.WeightedTorusJets.actual_biquadratic_rectangle_span')):
    row('5', f'Lemma3.{nm} is stated in the canonical comparator copy Bridge.lean (installed for the accepted rerouted run, sha256 af401514...).', f'Lemma3.{nm}', 'declaration',
        [L(BR, a, b, sub), R('results/2026-10-09-rerouted-comparator-diff.txt', 'af401514808dde5bb913ce8e87cc5280b704a234ea324897d1a1ced1f218f250')], 'COMPUTED', A_, TC, NONE)
row('5', 'Copies are identical: interpolation (PaperLemma3/Lemma3.lean 817-985 = Lemma3Bridged.lean 818-986 = Lemma3.lean 817-985), rectangle (Bridge.lean 97-143 = Lemma3Bridged.lean 1066-1112), bridge_main (Bridge.lean 198-286 = Lemma3Bridged.lean 1167-1255), bridge_descent and via_lemma3 likewise.',
    'identical', 'declaration text', [L(PL, 817, 985, 'theorem interpolation'), L(LB, 1066, 1112, 'theorem rectangle'), L(LB, 1167, 1255, 'theorem bridge_main'), L(BR, 198, 286, 'theorem bridge_main')],
    'COMPUTED', NR, NR, NONE, 'FOUND', 'block comparison by the ledger session 2026-10-26 (statement + proof, byte-equal after LF normalisation); bridge_main statement also equals OAI 471-484 character for character apart from the name')
row('5', 'Axioms of interpolation, rectangle and via_lemma3 (Lemma3Bridged.lean, OAI adc7f12, 2026-10-08).', '[propext, Classical.choice, Quot.sound]', 'axioms',
    [R('results/2026-10-08-lean-lemma3-bridge.txt', "'Lemma3.interpolation' depends on axioms"), R('results/2026-10-08-lean-lemma3-bridge.txt', "'Lemma3.rectangle' depends on axioms"), R('results/2026-10-08-lean-lemma3-bridge.txt', "'Lemma3.actual_biquadratic_rectangle_span_via_lemma3' depends on axioms")],
    'COMPUTED', A_, TC, SB5, 'FOUND', 'recorded file hash 04a49750... is the CRLF form of the LF file 6ce38ac1... (results/2026-10-09-lean-checks-line-endings.txt)')
row('5', 'Fresh run, 2026-10-26 21:43: the same three axioms lines for Lemma3Bridged.lean (LF 6ce38ac1...) at openai/math fd4aeeb under the 45-family deny list.', '[propext, Classical.choice, Quot.sound]', 'axioms',
    [R(LG + 'axioms-rectangle-2026-10-26.txt', "'Lemma3.rectangle' depends on axioms"), R(LG + 'axioms-rectangle-2026-10-26.txt', "'Lemma3.interpolation' depends on axioms"), R(LG + 'axioms-rectangle-2026-10-26.txt', "'Lemma3.actual_biquadratic_rectangle_span_via_lemma3' depends on axioms")],
    'COMPUTED', F_, TC, SB45)
row('5', 'Axioms of interpolation, rectangle and via_lemma3 compiled from the comparator copy (PaperLemma3/Bridge.lean itself), fd4aeeb, deny list.', '', 'axioms', 'pending: separate step after the ledger (axioms-comparator-copy-2026-10-26.txt)', 'COMPUTED', F_, TC, SB45, 'PENDING')
row('5', 'Standalone nanoda 3a24072 check of the export of via_lemma3: accepted.', '61810', 'declarations checked', R('results/2026-10-08-lean-lemma3-nanoda.txt', 'Checked 61810 declarations'), 'COMPUTED', A_, TCN, 'nanoda direct as checker (36_nanoda_lemma3.sh)')
row('5', 'Negative control (a): the same export with Classical.choice not permitted is rejected.', 'rejected (exit 1)', 'verdict', [R('results/2026-10-08-lean-lemma3-nanoda.txt', 'unpermitted axiom "Classical.choice"'), R('results/2026-10-08-lean-lemma3-nanoda.txt', 'nanoda exit 1')], 'COMPUTED', A_, TCN, 'nanoda direct as checker')
row('5', "Negative control (b): the export with rectangle's proof replaced by interpolation's proof is rejected.", 'rejected (exit 101)', 'verdict', [R('results/2026-10-08-lean-lemma3-nanoda.txt', 'assertion failed: self.def_eq(u, v)'), R('results/2026-10-08-lean-lemma3-nanoda.txt', 'nanoda exit 101')], 'COMPUTED', A_, TCN, 'nanoda direct as checker', 'FOUND', 'rejection is a kernel def_eq assertion on the tampered proof')
row('5', 'Bridge: via_lemma3 has exactly the type of OAI\'s theorem, by type_of%.', 'type_of%', 'construction', L(BR, 288, 290, 'type_of%'), 'COMPUTED', NR, TC, NONE)
row('5', 'Bridge: the embedding K -> C is chosen as IsAlgClosed.lift (not a hypothesis).', 'IsAlgClosed.lift', 'construction', L(BR, 214, 214, 'IsAlgClosed.lift'), 'COMPUTED', NR, TC, NONE)
row('5', 'c = biquadraticCoefficients (phi a) (phi b) = (1, (phi a)^-1, -(phi b)^-1, -(phi a phi b)^-1) (OAI definition).', '![1, a⁻¹, -b⁻¹, -(a * b)⁻¹]', 'definition', L(IJ, 321, 322, 'def biquadraticCoefficients'), 'COMPUTED', A_, TC, NONE)
row('5', 'Bridge: ker A = span {c} is proved inline in bridge_main.', 'hker', 'proof step', L(BR, 231, 254, 'LinearMap.ker A = Submodule.span ℂ {c}'), 'COMPUTED', NR, TC, NONE)
row('5', 'Bridge: bridge_descent does both the descent from C to K and the restriction to an injective family.', 'bridge_descent', 'lemma', L(BR, 147, 155, 'theorem bridge_descent'), 'COMPUTED', NR, TC, NONE)
row('5', '(sigma * tau) x = sigma (tau x) in Mathlib d13f23b (AlgEquiv.mul_apply), so the third row of A is phi(sigma(tau(1, a, b, ab))).', '(e₁ * e₂) x = e₁ (e₂ x)', '#check output',
    'MISSING: the #check @AlgEquiv.mul_apply output (2026-10-26, Mathlib d13f23b, via stdin) was printed to the session only, not saved to results/', 'COMPUTED', F_, TC, SB45, 'MISSING')
row('5', "The bridge reuses OAI's source_same_witness_hyperplane (the basis D of ker biquadraticForm with rows phi(1,a,b,ab), phi(sigma ...), phi((sigma*tau) ...)).", 'source_same_witness_hyperplane', 'OAI lemma', L(IJ, 447, 455, 'theorem source_same_witness_hyperplane'), 'COMPUTED', A_, TC, NONE)
row('5', "The bridge's c is linearly independent over Q by OAI's biquadraticCoefficients_linearIndependent (and its _map form).", 'biquadraticCoefficients_linearIndependent', 'OAI lemma', [L(IJ, 380, 397, 'theorem biquadraticCoefficients_linearIndependent'), L(IJ, 424, 430, 'theorem biquadraticCoefficients_linearIndependent_map')], 'COMPUTED', A_, TC, NONE)
row('5', 'Lemma3_Cor4.lean is a working draft: its interpolation is proved by sorry (line 31), so its rectangle (identical text to the canonical one) depends on sorryAx; the canonical Bridge.lean does not import it.',
    'working draft (sorry)', 'file role', [L('lean-checks/Lemma3_Cor4.lean', 22, 31, 'by sorry'), L(BR, 1, 3, 'import OAI.NumberTheory.SiegelZeros.PaperLemma3.Lemma3'), R('results/2026-10-08-lean-lemma3-cor4-piece.txt', 'Lemma3_Cor4')], 'COMPUTED', NR, TC, NONE)
row('5', 'Lemma3_Bridge.lean is a working draft: its rectangle is proved by sorry (line 20); the canonical Bridge.lean does not import it.',
    'working draft (sorry)', 'file role', [L('lean-checks/Lemma3_Bridge.lean', 7, 20, 'sorry'), R('results/2026-10-08-lean-lemma3-bridge-piece.txt', 'Lemma3_Bridge')], 'COMPUTED', NR, TC, NONE)
row('5', 'Exact execution of the proof of Lemma 3 at N = 2, 3 (src/lemma3_construct.py): 423 + 46 + 71 = 540 instances, 28 checks each, all pass.', '540', 'instances',
    [R('results/2026-10-08-lemma3-construct-N2-summary.txt', 'instances: 423, all checks passed: 423'), R('results/2026-10-08-lemma3-construct-N2-generic4d-summary.txt', 'instances: 46, all checks passed: 46'),
     R('results/2026-10-08-lemma3-construct-N3-summary.txt', 'instances: 71, all checks passed: 71'), R('results/2026-10-08-lemma3-construct-N2-summary.txt', 'checks per instance: {28: 423}')],
    'COMPUTED', NR, 'Python Fraction (exact)', NR, 'FOUND', 'confirms the proof steps at N = 2, 3 only, not the lemma in general')

# ---------------- Section 6: the reroute ----------------
row('6', 'The rerouted clone differs from openai/math in 1 tracked file, +2/-1 (an import and the term at line 138), plus the two untracked PaperLemma3 modules.', '1 file, +2/-1', 'diff',
    [R('results/2026-10-09-rerouted-comparator-diff.txt', '# Result: existing files changed = 1 file, 2 lines added, 1 removed'), R('results/2026-10-09-rerouted-comparator-diff.txt', '1 file changed, 2 insertions(+), 1 deletion(-)')], 'COMPUTED', A_, NR, NR)
row('6', 'The challenge file is unchanged in the rerouted run.', 'bedaac0248a641910f79a380d9702d82c6bfbbfd3760a69d27c72c5d8fb136ce', 'sha256', R('results/2026-10-09-lean-comparator-rerouted-nanoda.txt', 'challenge file sha256: bedaac02'), 'COMPUTED', A_, NR, NR)
row('6', 'Rerouted comparator run: 9244 jobs built; nanoda and Lean kernels accept; exit 0.', '9244 jobs; ACCEPT_BOTH; exit 0', 'verdict',
    [R('results/2026-10-09-lean-comparator-rerouted-nanoda.txt', '/9244]'), R('results/2026-10-09-lean-comparator-rerouted-nanoda.txt', 'nanoda kernel accepts the solution'), R('results/2026-10-09-lean-comparator-rerouted-nanoda.txt', 'Lean default kernel accepts the solution'), R('results/2026-10-09-lean-comparator-rerouted-nanoda.txt', 'COMPARATOR EXIT CODE: 0')],
    'COMPUTED', A_, TCN, SB5 + ' (48_comparator_rerouted_nanoda.sh); before the 45-family deny list', 'FOUND', 'run 2026-10-09 09:07-09:32')
row('6', 'The reroute has not been run at openai/math fd4aeeb or under the 45-family deny list.', 'not run', 'run', 'MISSING: NEW RUN NEEDED (see gaps.md)', 'COMPUTED', F_, TCN, SB45, 'MISSING')
row('6', 'The reroute patch applies cleanly at fd4aeeb; the patched file is byte-identical at adc7f12 and fd4aeeb.', 'applies (git apply --check exit 0)', 'check', [R(LG + 'patch-apply-check.txt', 'git apply --check exit 0'), R(LG + 'patch-apply-check.txt', 'target at fd4aeeb sha256')], 'COMPUTED', F_, 'git apply (no build)', 'read-only scratch repo')
row('6', 'Rerouted dependency scan: dirichletRealZeroBound_proof closure, matches only via_lemma3 and interpolation; none of the three OAI lemmas.', '92658', 'constants in closure',
    [R('results/2026-10-09-lean-rerouted-comparator-deps.txt', 'dirichletRealZeroBound_proof: 92658 constants in closure; matches: [Lemma3.actual_biquadratic_rectangle_span_via_lemma3'), R('results/2026-10-09-lean-rerouted-comparator-deps.txt', ' Lemma3.interpolation]')], 'COMPUTED', A_, TC, SB5)
row('6', 'The rerouted chain still imports the patched PrimeNumberTheoremAnd.SiegelZeros.HadamardSupport.', 'imported', 'dependency', R('results/2026-10-09-pnt-hadamard-dependency.txt', 'clone /home/checker/math-rerouted'), 'COMPUTED', A_, TC, NR)

# ---------------- Section 7: corpus context ----------------
CS = 'results/2026-10-20-corpus-summary-final.md'
row('7', 'Of the 189 configs referenced by formalization.yaml, 187 were replayed at fd4aeeb and 2 (SiegelZeros, QuasiRiemannHypothesis) in the pilot at adc7f12.', '187 + 2', 'configs', [R(CS, '187 were replayed at fd4aeeb'), R(CS, 'The other 2, SiegelZeros and QuasiRiemannHypothesis')], 'COMPUTED', f'{F_}; pilot {A_}', TCN, SB5)
row('7', 'At fd4aeeb, both kernels accept 178 of the 187; 9 are ACCEPT_LEAN_ONLY (nanoda 3a24072 crashes).', '178 / 9', 'configs', [R(CS, '| **All, fd4aeeb** | **178** | **9** | **187** |'), R(CS, '- **ACCEPT_LEAN_ONLY (9):**')], 'COMPUTED', F_, TCN, SB5)
row('7', 'All 9 ACCEPT_LEAN_ONLY configs pass with nanoda f67473b through comparator (UNOFFICIAL).', '9 of 9', 'configs', R('results/2026-10-20-nanoda-postfix-f67473b/SUMMARY.txt', '9 of 9 POSTFIX_ACCEPT_BOTH'), 'COMPUTED', F_, TC + ' / nanoda f67473b (16 MiB)', SB5)
X3 = MX + 'extended-replay-227/summary-227-v3.txt'
row('7', 'Extended replay of the 227 unreferenced configs (official tool set, nanoda 3a24072): 212 results, 15 not checked here.', '212 / 15', 'configs', R(X3, 'configs 227: results 212, deferred 15'), 'COMPUTED', F_, TCN, SB5)
row('7', 'Official final outcomes of the 227: ACCEPT_BOTH 205, LEAN_ACCEPT_NANODA_CRASH 6, TIMEOUT 1, NOT_CHECKED_HERE 15.', "{'ACCEPT_BOTH': 205, 'LEAN_ACCEPT_NANODA_CRASH': 6, 'NOT_CHECKED_HERE': 15, 'TIMEOUT': 1}", 'outcomes', R(X3, "{'ACCEPT_BOTH': 205, 'LEAN_ACCEPT_NANODA_CRASH': 6"), 'COMPUTED', F_, TCN, SB5)
row('7', 'Catalan and KMedianThreshold (official: NOT_CHECKED_HERE) were accepted here by both kernels: Lean via the shipped-config comparator, nanoda via the UNOFFICIAL B3 build.', 'both kernels (unofficial nanoda)', 'status',
    [R(X3, "  Catalan: status 'both kernels accepted here"), R(X3, "  KMedianThreshold: status 'both kernels accepted here")], 'COMPUTED', F_, TC + ' / nanoda 37cb87b + nealmcb patch (STACK_SIZE 64 MiB) [B3]', SB45 + ' + 16G cap')
row('7', 'ContinuumCoulombHardness could not be built here (guard stopped the build at 4 and 2 threads); permanently deferred; results STATED by nealmcb.', 'DEFERRED (permanent)', 'status', R(X3, 'ContinuumCoulombHardness (U)'), 'COMPUTED', F_, TC, SB45)
row('7', 'Export sizes equal nealmcb\'s for 146 extended-replay exports (0 differ, 14 not comparable).', '146', 'exports', R('results/2026-10-25-extended-replay-vs-mcburnett/comparison.txt', 'export bytes vs Neal: same 146 different 0 not comparable 14'), 'COMPUTED', F_, NR, NR)
row('7', 'Export sizes equal nealmcb\'s (results/nanoda-ab-let.jsonl) to the byte for the 11 configs run in the 2026-10-26 matrix (plus MatchingFPRAS and ContingencyTables, 13 in all).', '11 (13 incl. 2 from extended records)', 'exports', [R(MX + 'FINAL.md', 'all 13 sizes match to the byte'), U(NEAL + 'results/nanoda-ab-let.jsonl')], 'COMPUTED', F_, NR, NR)
for cls, members, sub in (('1', 'RoundTables group (8), Laughlin group (3), KMedianThreshold, Catalan', '1. **Recursion in 3a24072'),
                          ('2', 'KaplanskyFinitelyPresented, GroupRingDeterminant, KaplanskyDirectFiniteness (COMPUTED); MatchingFPRAS, ContingencyTables, LogspaceEquality, RandomizedMeanPayoff, PeriodicGroup (STATED)', '2. **Deep but finite Nat recursion.**'),
                          ('3', 'SquareDifference', '3. **The let bug: SquareDifference.**')):
    row('7', f'nanoda failure class {cls}: members and evidence (matrix-v3.tsv cells, COMPUTED or STATED per cell).', members, 'configs',
        [R(MX + 'FINAL.md', sub), R(MX + 'FINAL.md', '**Class 1 evidence, stated precisely.**') if cls == '1' else R(MX + 'SUMMARY.md', f'### Class {cls}'), MX + 'matrix-v3.tsv'],
        'INFERRED', F_, 'nanoda 3a24072 / 3a24072@1GiB / f67473b / 37cb87b / 37cb87b+patch@64MiB', SB5C + '; step 5 under ' + SB45, 'FOUND',
        'rests on: per-config outcomes across nanoda builds (COMPUTED or STATED cells); class membership is an interpretation of those outcomes, measured by backtrace only for RoundTables (STATED, #55)')
row('7', "nealmcb's comparator run, as shipped, accepts all 416 configs at fd4aeeb.", '416/416', 'configs', U(NEAL + 'results/cmp-all/STATUS.md (lines 3, 5)'), 'STATED', F_, 'nealmcb pins (MANIFEST.txt at 1ca7ff2)', 'nealmcb sandbox (landrun)')
row('7', "nealmcb: nanoda accepts 401 of 416 exports; the 401 used 3a24072 built with a 1 GiB stack (his correction).", '401/416', 'configs', [U(I55), U(I55n)], 'STATED', F_, 'nanoda 3a24072 @ 1 GiB stack', 'nealmcb')
row('7', 'nealmcb: on nanoda master ten openai/math configs fail; with the let fix, the Nat.succ guard and STACK_SIZE 64 MiB all ten check.', '10', 'configs', [U(I61c), U(NEAL + 'results/nanoda-stack-size-2026-10-25.txt')], 'STATED', F_, 'nanoda 37cb87b (+ patch)', 'nealmcb')
row('7', "nealmcb's patch nanoda-let-fvar-and-succ-guard-37cb87b.patch (used for B3 here).", 'edd9824f5fd93c86d3f52acea1373a915ccfddf23db33c5e919f03f7c642bc30', 'sha256', [U(NEAL + 'tools/patches/nanoda-let-fvar-and-succ-guard-37cb87b.patch'), R(MX + 'MANIFEST.txt', 'patch sha256 edd9824f')], 'STATED', NR, NR, NR, 'FOUND', 'sha256 COMPUTED here before applying (MANIFEST.txt)')
row('7', "nealmcb's 416-config sweep ran on nanoda master 8199c74 (nine commits before 37cb87b).", '8199c74', 'commit', U(NEAL + 'tools/cloud_nanoda_let_sweep.sh (line 4)'), 'STATED', F_, NR, NR)

# ---------------- Section 8: threats to validity ----------------
NC = 'results/2026-10-26-network-check/'
row('8', 'Original sandbox: RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET in a systemd-run user unit (67/75/107, 29/48).', '5 families denied', 'property', [R('wsl-comparator/67_corpus_run.sh', 'RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET'), R(NC + 'README.md', 'Unit properties tested')], 'COMPUTED', NR, NR, SB5)
row('8', 'Under that filter TCP/UDP over IPv4 and IPv6 and DNS fail inside the unit (2026-10-26 test).', 'blocked (errno 97)', 'probe', R(NC + 't22_net.out', 'PROBE tcp connect 1.1.1.1:443: blocked'), 'COMPUTED', NR, NR, SB5)
row('8', 'Under that filter AF_VSOCK was not denied, and a connection to the Windows host (CID 2, port 50000) succeeded; no route to the internet was tested.', 'connected', 'probe', R(NC + 't22_net.out', 'PROBE vsock connect host CID 2: ALLOWED'), 'COMPUTED', NR, NR, SB5)
row('8', 'The old filter also left AF_PPPOX and AF_ALG creatable.', 'AF_PPPOX, AF_ALG', 'families', R(NC + 't25_old_vs_new.out', 'FAM 24 STREAM=OK'), 'COMPUTED', NR, NR, SB5)
row('8', 'The first SiegelZeros comparator run (2026-10-08 12:15, 08_comparator.sh) used the comparator README wrapper (~AF_UNIX only); IP was open under it.', '~AF_UNIX only', 'property', [R('results/2026-10-08-lean-comparator-wsl.txt', 'RestrictAddressFamilies=~AF_UNIX --user'), R('wsl-comparator/28_netblock_probe.log', 'tcp 1.1.1.1:443: OPEN')], 'COMPUTED', A_, TC, SB0)
row('8', 'The first SiegelZeros comparator run under the 5-family filter is the nanoda run of 2026-10-08 (29_comparator_nanoda.sh, ended 14:18).', '2026-10-08 14:18', 'date', [R('results/2026-10-08-lean-comparator-nanoda-netblock.txt', 'Run ended 14:18:02 EDT 2026-10-08'), R('results/2026-10-08-lean-comparator-nanoda-netblock.txt', 'RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET')], 'COMPUTED', A_, TCN, SB5)
row('8', 'From 2026-10-26 16:40 the deny list names all 45 families of kernel 5.15.167.4 (RestrictAddressFamilies=none is rejected by systemd-run 255).', '45 families', 'property', [R(NC + 'README.md', 'Update 2026-10-26 16:40: full deny list'), R(NC + 't24_none.out', 'Failed to set unit properties: Invalid argument')], 'COMPUTED', NR, NR, SB45)
row('8', 't25 all-families probe: inside the new unit all 138 socket() calls (families 1..46 x STREAM/DGRAM/RAW) fail with errno 97, in user and system units.', '138 / 138 errno 97', 'calls', [R(NC + 't25_allfamilies.out', '(a) families probed 46; not all-97: none'), R(NC + 't25_allfamilies.out', '(b) families probed 46; not all-97: none')], 'COMPUTED', NR, NR, SB45)
row('8', 'No SiegelZeros comparator run exists under the 45-family deny list (only the rectangle/interpolation axioms re-check).', 'none', 'run', 'MISSING: covered by the NEW RUN NEEDED reroute item (gaps.md)', 'COMPUTED', F_, TCN, SB45, 'MISSING')
row('8', 'WSL memory changed from the ~16 GB default (15,965 MB) to 24 GB at 2026-10-21 13:56:21; three extended-replay results were recorded before it.', 'ElementaryPositivity, KaplanskyDirectFiniteness, ShortEgyptianFractions', 'configs',
    [R(XR + 'platform-change-wsl-24gb.txt', 'Configs completed before the change at 16 GB'), R(XR + 'run.log', 'stopped by hand for the WSL memory change'), R(X3, 'outcomes under the ~16 GB default')], 'COMPUTED', F_, NR, NR)
row('8', 'WSL memory changed from 24 GB to 20 GB at 2026-10-22 08:10.', '20 GB', 'memory', R(XR + 'platform-change-wsl-24gb.txt', 'Second change, 2026-10-22 08:10'), 'COMPUTED', F_, NR, NR)
row('8', 'systemd 255 does not enforce MemoryMax in this cgroup-hybrid WSL; the cap is set on the unit\'s own v1 memory cgroup instead (140/140d/67d); the guard 69_corpus_guard.sh stops builds below a MemAvailable floor.', 'not enforced', 'behaviour',
    [R('wsl-comparator/140_matrix_run.sh', 'does not enforce'), R('wsl-comparator/69_corpus_guard.sh', 'MemAvailable < MEM_MB'), R(MX + 'MANIFEST.txt', "systemd's MemoryMax is not enforced")], 'COMPUTED', NR, NR, 'n/a', 'FOUND', 'the 600 MB-under-200M test output itself was printed to the session; the record is the script header and MANIFEST.txt')

# ---------------- Section 9: artifacts ----------------
Z = LG + 'zenodo/'
for rid, ver, what in (('23269528', 'reviewer-packet-v1', 'reviewer packet v1 zip (GitHub tag reviewer-packet-v1)'), ('23499651', 'reviewer-packet-v2-preliminary', 'reviewer packet v2 preliminary zip (tag reviewer-packet-v2-preliminary)'),
                       ('23523697', 'reviewer-packet-v3', 'reviewer packet v3 zip (tag reviewer-packet-v3)'), ('23505836', 'corpus-replay-2026-10-20', 'corpus replay zip (repo commit 60552ee)')):
    row('9', f'Zenodo record 10.5281/zenodo.{rid} ({ver}): {what}.', f'10.5281/zenodo.{rid}', 'DOI', [R(Z + f'r{rid}.json', f'"doi": "10.5281/zenodo.{rid}"'), U(f'https://zenodo.org/api/records/{rid}')], 'COMPUTED', A_ if rid != '23505836' else F_, NR, NR, 'FOUND',
        'record JSON fetched read-only 2026-10-26 16:02 (before the GitHub-only network rule) and copied into the ledger')
row('9', 'Concept DOI of the reviewer packets.', '10.5281/zenodo.23269527', 'DOI', R(Z + 'r23523697.json', '"conceptdoi": "10.5281/zenodo.23269527"'), 'COMPUTED', NR, NR, NR)
row('9', 'Repository HEAD (local, 3 commits ahead of origin bb6f197) and tags reviewer-packet-v1 (8d265cd), -v1.1 (d182d03), -v2-preliminary (9bf7d0b), -v3 (d1aff7a).', 'see note', 'commit', 'git rev-parse HEAD / git tag (2026-10-26)', 'COMPUTED', NR, NR, NR, 'FOUND', 'HEAD at ledger time is recorded in LEDGER.md; tags listed with object ids')
row('9', 'Toolchain pins: Lean 4.34.1 (5045d005), Mathlib d13f23b, Comparator v4.34.0 d03acab, lean4export v4.34.0 076e8e5.', 'see claim', 'pins',
    [R('results/2026-10-11-corpus-provenance.txt', 'comparator: afa65e57'), R('results/2026-10-11-corpus-provenance.txt', 'lean4export: 8c5d64ba'), R('results/2026-10-08-lean-comparator-wsl.txt', 'commit 5045d0056413266e57c625dcd7c365b10e377c52')], 'COMPUTED', F_, TC, NR)
row('9', 'nanoda pins: 3a24072 official; f67473b, 37cb87b and 37cb87b + nealmcb patch @ 64 MiB unofficial (binaries and hashes).', '3a24072 / f67473b / 37cb87b / 37cb87b+patch', 'pins', [R(MX + 'MANIFEST.txt', '  official  nanoda_lib 3a2407216ee84a75f9e1aead6803d0578be06ae7'), R(MX + 'MANIFEST.txt', '  B3        B2')], 'COMPUTED', NR, NR, NR)

# ---------------- write ----------------
cols = ['id', 'paper_section', 'claim', 'value', 'unit', 'source', 'label', 'openai_math_commit', 'toolchain', 'sandbox', 'status', 'note']
if problems:
    print('PROBLEMS (ledger not written):'); print('\n'.join(problems)); sys.exit(1)
import csv
p = os.path.join(OUT, 'ledger.tsv')
if os.path.exists(p): sys.exit(f'refusing to overwrite {p}')
with open(p, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t', lineterminator='\n'); w.writerow(cols)
    for k, r in enumerate(rows, 1): w.writerow([f'L{k:03d}'] + r)
import collections
print('rows', len(rows), 'status', dict(collections.Counter(r[9] for r in rows)), 'label', dict(collections.Counter(r[5] for r in rows)))
