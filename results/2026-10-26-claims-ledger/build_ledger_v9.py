"""Claims ledger v9 (2026-10-27). Read-only on the repo; writes ledger-v9.tsv next to this file (refuses to overwrite).

Usage: python -I results/2026-10-26-claims-ledger/build_ledger_v9.py <repo root>
Append-only (id-stability.md): every ledger-v8.tsv row is copied unchanged, except that v8:L151 gets status
"SUPERSEDED by v9:L203" (value and source kept); new rows take explicit ids from L198 on.
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
X = 'external/openai-math/'
W = '\\\\wsl.localhost\\Ubuntu-24.04\\home\\checker\\math\\lean\\'
SZ = W + 'OAI\\NumberTheory\\SiegelZeros\\'
CM = 'results/2026-10-27-closure-modules/'
SC = 'statement-checks/StatementChecks/'; V2 = 'results/2026-10-26-claims-ledger/statement-checks-final-v2.log'

with open(os.path.join(OUT, 'ledger-v8.tsv'), encoding='utf-8') as f:
    rd = csv.reader(f, delimiter='\t'); cols = next(rd); rows = [dict(zip(cols, r)) for r in rd]
assert [r['id'] for r in rows] == [f'L{k:03d}' for k in range(1, 198)], 'ledger-v8.tsv ids are not L001-L197'
byid = {r['id']: r for r in rows}
new = []


def row(i, sec, claim, value, unit, src, label, commit, tc, sb, note='', read_by=''):
    assert i == f'L{198 + len(new):03d}', i
    new.append(dict(id=i, paper_section=sec, claim=claim, value=value, unit=unit, source='; '.join(src) if isinstance(src, (list, tuple)) else src,
                    label=label, openai_math_commit=commit, toolchain=tc, sandbox=sb, status='FOUND', note=note, read_by=read_by, read_note=''))


CH = X + 'lean/ComparatorChallenges/SiegelZeros.lean'
# ---- a: the two challenge theorems ----
row('L198', '2; 3', 'The SiegelZeros challenge file states two theorems with the same constant, hypotheses on q and chi, and conclusion. They differ in how the zero hypotheses are taken: exists_absolute_real_zero_gap (lines 8-14) takes 0 < beta, beta < 1 and chi.LFunction beta = 0 as three successive implications; dirichletRealZeroBound_proof (lines 19-25) takes them as one conjunction and writes DirichletCharacter.LFunction chi beta. They also sit in different namespace blocks (WeightedTorusJets opened at line 6 for the first; WeightedTorusJets.dirichletRealZeroBound_proof inside SiegelZeros for the second).',
    'line 13: "∀ β : ℝ, 0 < β → β < 1 → χ.LFunction (β : ℂ) = 0 →"; lines 23-24: "∀ β : ℝ, (0 < β ∧ β < 1 ∧ DirichletCharacter.LFunction χ (β : ℂ) = 0) →"', 'source text',
    [L(CH, 8, 14, 'theorem exists_absolute_real_zero_gap :'), L(CH, 13, 13, '∀ β : ℝ, 0 < β → β < 1 → χ.LFunction (β : ℂ) = 0 →'), L(CH, 19, 25, 'theorem WeightedTorusJets.dirichletRealZeroBound_proof :'),
     L(CH, 23, 24, '(0 < β ∧ β < 1 ∧ DirichletCharacter.LFunction χ (β : ℂ) = 0) →'), L(CH, 6, 6, 'namespace WeightedTorusJets')],
    'COMPUTED', A_ + ' (file unchanged at fd4aeeb, v7:L007)', NR, NONE)
row('L199', '2; 3', 'The two challenge theorems are not the same Lean proposition (their types differ: three curried implications versus one conjunction), but they are logically equivalent by uncurrying (and_imp), with chi.LFunction and DirichletCharacter.LFunction chi the same function by dot notation.',
    'not the same type; logically equivalent', 'finding', [L(CH, 13, 13, 'χ.LFunction (β : ℂ) = 0 →'), L(CH, 24, 24, '(0 < β ∧ β < 1 ∧ DirichletCharacter.LFunction χ (β : ℂ) = 0) →')],
    'INFERRED', A_, TC, NONE, note='rests on reading the two statements; no Lean proof of the equivalence was run')

# ---- b: the closure of exists_absolute_real_zero_gap, and its proof ----
CL = CM + 'exists-gap-closure-modules.log'
row('L200', '4', 'fd4aeeb: the closure of exists_absolute_real_zero_gap (107760 constants) contains no constant defined in a module under OAI.NumberTheory.DirichletL (the 7/8 development, Dirichlet and Hecke) and none whose name contains seven_eighths, SevenEighths or QuasiRiemann. It does not contain dirichletRealZeroBound_proof, dirichlet_real_zero_bound or actual_biquadratic_rectangle_span. It contains uniform_exclusion_of_local_isolated_bezout and uniform_exclusion_of_actual_cutoff. Its only OAI module prefix is OAI.NumberTheory.SiegelZeros (3097 constants); it has no PrimeNumberTheoremAnd constant.',
    '107760 constants; 0 from the 7/8 development; dirichletRealZeroBound_proof false; dirichlet_real_zero_bound false; actual_biquadratic_rectangle_span false; uniform_exclusion_of_local_isolated_bezout true; uniform_exclusion_of_actual_cutoff true', 'closure members',
    [R(CL, 'OAI.SiegelZeros.WeightedTorusJets.exists_absolute_real_zero_gap: 107760 constants in closure'), R(CL, 'members from OAI.NumberTheory.DirichletL or named *seven_eighths*/*SevenEighths*/*QuasiRiemann*: 0 []'),
     R(CL, 'member OAI.SiegelZeros.WeightedTorusJets.dirichletRealZeroBound_proof: false'), R(CL, 'member OAI.SiegelZeros.WeightedTorusJets.dirichlet_real_zero_bound: false'),
     R(CL, 'member OAI.SiegelZeros.WeightedTorusJets.actual_biquadratic_rectangle_span: false'), R(CL, 'member OAI.SiegelZeros.SiegelZerosAwei.W50.uniform_exclusion_of_local_isolated_bezout: true'),
     R(CL, 'member OAI.SiegelZeros.SiegelZerosAwei.W50.uniform_exclusion_of_actual_cutoff: true'), R(CL, '(OAI.NumberTheory.SiegelZeros, 3097)'), R(CL, 'LEAN EXIT CODE: 0'),
     L('lean-checks/ClosureModules.lean', 1, 8, 'the dependency closure of a root constant, with the module each member is defined in'), R(CM + 'clone-head.txt', 'HEAD fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb')],
    'COMPUTED', F_, TC, SB45, note='query lean-checks/ClosureModules.lean (`bash wsl-comparator/75d_sbx.sh 1800 4 "lake env lean /tmp/cm/ClosureModules.lean"`, no build; the clone was built 2026-10-26 21:43). Same closure size as v8:L148 by a separate query. The prefix list in the log has no other OAI and no PrimeNumberTheoremAnd entry')
row('L201', '4', "OAI's proof of exists_absolute_real_zero_gap (Conclusions/Theorem.lean:11-19) is `exact SiegelZerosAwei.W50.uniform_exclusion_of_local_isolated_bezout (W22.localIsolatedBezout_of_actual_regular_selection ℂ)`. That theorem (Intersection/BezoutBoundary.lean:13-19) concludes UniformSiegelZeroExclusion by applying uniform_exclusion_of_actual_cutoff, with its spanning hypothesis supplied by W28.actualCutoffSpanning_of_localBezout. uniform_exclusion_of_actual_cutoff (Estimates/GeometricBoundary.lean:18-48) argues by contradiction: it takes W63.exists_good_mass_for_actual_zeros_normalized, fixes H := 86713344, takes a contrary sequence of genuine zeros, and closes with false_of_eventual_exists_pivot_master and exists_actual_character_pivot_master. UniformSiegelZeroExclusion (Model.lean:8-14) has the same text as the challenge statement.",
    'exists_absolute_real_zero_gap -> uniform_exclusion_of_local_isolated_bezout (Bezout) -> uniform_exclusion_of_actual_cutoff -> W63.exists_good_mass_for_actual_zeros_normalized, H := 86713344, false_of_eventual_exists_pivot_master, exists_actual_character_pivot_master', 'proof trace',
    [L(SZ + 'Conclusions\\Theorem.lean', 11, 19, 'exact SiegelZerosAwei.W50.uniform_exclusion_of_local_isolated_bezout'), L(SZ + 'Conclusions\\Theorem.lean', 19, 19, '(W22.localIsolatedBezout_of_actual_regular_selection ℂ)'),
     L(SZ + 'Intersection\\BezoutBoundary.lean', 13, 19, 'apply uniform_exclusion_of_actual_cutoff'), L(SZ + 'Intersection\\BezoutBoundary.lean', 18, 18, 'W28.actualCutoffSpanning_of_localBezout'),
     L(SZ + 'Estimates\\GeometricBoundary.lean', 18, 48, 'obtain ⟨C, hC, hC4, hmassAll⟩ := W63.exists_good_mass_for_actual_zeros_normalized'), L(SZ + 'Estimates\\GeometricBoundary.lean', 26, 26, 'let H : ℕ := 86713344'),
     L(SZ + 'Estimates\\GeometricBoundary.lean', 32, 32, 'apply false_of_eventual_exists_pivot_master'), L(SZ + 'Estimates\\GeometricBoundary.lean', 44, 44, 'apply exists_actual_character_pivot_master'),
     L(SZ + 'Model.lean', 8, 14, 'def UniformSiegelZeroExclusion : Prop :=')],
    'COMPUTED', F_, NR, 'read-only source reading of the clean fd4aeeb clone',
    note='for comparison, dirichletRealZeroBound_proof (Characters/DirichletRealZeroBoundProof.lean:17-24) is `exact WeightedTorusJets.dirichlet_real_zero_bound`, proved at Characters/DirichletRealZeroBound.lean:14-36 from source_real_zero_uniform_master_bound; that is the route that reaches Corollary 4 (v7:L019, v7:L099)')

# ---- c: OAI's statement of which theorem is the main result ----
FY = W + 'formalization.yaml'
row('L202', '2; 4', "OAI's catalogue lean/formalization.yaml lists, under status.main_results, the SiegelZeros config with declaration OAI.SiegelZeros.WeightedTorusJets.exists_absolute_real_zero_gap in OAI/NumberTheory/SiegelZeros/Conclusions/Theorem.lean (fd4aeeb lines 1585-1587; adc7f12 lines 1498-1500). lean/docs/003.md describes the formalized result as one constant c > 0 for every primitive nonprincipal real character of conductor q >= 3 (line 14) and links \"Uniform real-zero gap\" to SiegelZeros.lean (line 25). Neither file names the paper's Theorem 1, and neither names dirichletRealZeroBound_proof.",
    '1585: "- comparator_config: ComparatorChallenges/SiegelZeros.json"; 1586: "declaration: OAI.SiegelZeros.WeightedTorusJets.exists_absolute_real_zero_gap"; 1587: "file: OAI/NumberTheory/SiegelZeros/Conclusions/Theorem.lean"; 003.md 25: "| Uniform real-zero gap | [SiegelZeros.lean](../ComparatorChallenges/SiegelZeros.lean) |"', 'quote',
    [L(FY, 3, 3, 'version: "v0.4"'), L(FY, 972, 972, 'main_results:'), L(FY, 1585, 1587, 'declaration: OAI.SiegelZeros.WeightedTorusJets.exists_absolute_real_zero_gap'),
     L(X + 'lean/formalization.yaml', 1498, 1500, 'declaration: OAI.SiegelZeros.WeightedTorusJets.exists_absolute_real_zero_gap'),
     L(X + 'lean/docs/003.md', 14, 14, 'There is one constant $c>0$ such that every primitive nonprincipal real Dirichlet character of conductor $q\\ge3$'), L(X + 'lean/docs/003.md', 25, 25, '| Uniform real-zero gap | [SiegelZeros.lean](../ComparatorChallenges/SiegelZeros.lean) |')],
    'STATED', F_ + ' and ' + A_, NR, NR, note='searched: Conclusions, the SiegelZeros solution tree and lean/docs/003.md for "Theorem 1", "main theorem" and "thm:main" (no match); formalization.yaml has no theorem-number field. formalization.yaml itself differs between the commits; this entry does not')

# ---- L151 again, with the Lean sources ----
o = byid['L151']; assert o['status'] == 'FOUND'; o['status'] = 'SUPERSEDED by v9:L203'
row('L203', '3', o['claim'], o['value'], o['unit'],
    o['source'].split('; ') + [L(SC + 'HeckeSeries.lean', 373, 374, 'theorem LFunction_hasSum {s : ℂ} (hs : 1 < s.re) :'), L(SC + 'HeckeSeries.lean', 374, 374, "HasSum (fun q : ℤ × ℤ => a' χ q / ((Qf q.1 q.2 : ℝ) : ℂ) ^ s / 6) (LFunction χ s)"),
                               R(V2, "'StatementChecks.HeckeSeries.LFunction_hasSum' depends on axioms: [propext, Classical.choice, Quot.sound]"),
                               L(SC + 'Hecke.lean', 29, 30, 'theorem differentiableAt_LFunction (χ : Character) {s : ℂ} (h0 : s ≠ 0) (h1 : s ≠ 1) :'),
                               R(V2, "'StatementChecks.Hecke.differentiableAt_LFunction' depends on axioms: [propext, Classical.choice, Quot.sound]"),
                               R(V2, "'StatementChecks.HeckeHolo.coord_surj' depends on axioms")],
    'INFERRED', o['openai_math_commit'], o['toolchain'], o['sandbox'],
    note=o['note'] + '. v9 adds the Lean sources: the (1/6)-sum form is StatementChecks.HeckeSeries.LFunction_hasSum (HeckeSeries.lean:373-374), a HasSum over (x, y) in Z x Z of a\'(chi)(x, y) / (x^2 - xy + y^2)^s / 6, not literally a sum over alpha in O; the step from (x, y) to alpha = x + y*omega uses that every element of O is x + y*omega (HeckeHolo.coord_surj) and is part of the INFERRED reading. Holomorphy off {0, 1} is StatementChecks.Hecke.differentiableAt_LFunction (Hecke.lean:29-30). Both are standard-axiom only in the v2 build log. The six-generator identification itself is not formalized in Lean',
    read_by='')

if problems:
    print('PROBLEMS (ledger not written):'); print('\n'.join(problems)); sys.exit(1)
p = os.path.join(OUT, 'ledger-v9.tsv')
if os.path.exists(p): sys.exit(f'refusing to overwrite {p}')
with open(p, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t', lineterminator='\n'); w.writerow(cols)
    for r in rows + new: w.writerow([r[c] for c in cols])
print('rows', len(rows) + len(new), 'new', [r['id'] for r in new], dict(collections.Counter(r['label'] for r in new)))
