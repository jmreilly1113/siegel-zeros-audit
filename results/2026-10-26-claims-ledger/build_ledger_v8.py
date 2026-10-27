"""Claims ledger v8 (2026-10-27). Read-only on the repo; writes ledger-v8.tsv next to this file (refuses to overwrite).

Usage: python -I results/2026-10-26-claims-ledger/build_ledger_v8.py <repo root>
Append-only (id-stability.md): every ledger-v7.tsv row is copied unchanged; new rows take explicit ids from L147 on.
New rows:
  L147-L149  which declarations the SiegelZeros challenge has Comparator check, and the closure of exists_absolute_real_zero_gap
  L150       lean/docs/003.md links the three 7/8 challenges to the 7/8 paper (STATED)
  L151       the HeckeSevenEighths identification in paper wording (INFERRED, read_by empty)
  L152-...   one INFERRED row per reasoning point of the six readings (results/2026-10-27-readings/readings-claude-code.md),
             read_by empty, for Joe to mark
"""
import csv, hashlib, os, sys, collections

root = sys.argv[1]
OUT = os.path.join(root, 'results', '2026-10-26-claims-ledger')
problems = []


def _read(p):
    b = open(os.path.join(root, p), 'rb').read().replace(b'\r\n', b'\n')
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
RR = 'results/2026-10-27-reroute-fd4aeeb/'; RD = 'results/2026-10-27-readings/readings-claude-code.md'
X = 'external/openai-math/'

with open(os.path.join(OUT, 'ledger-v7.tsv'), encoding='utf-8') as f:
    rd = csv.reader(f, delimiter='\t'); cols = next(rd); rows = [dict(zip(cols, r)) for r in rd]
assert [r['id'] for r in rows] == [f'L{k:03d}' for k in range(1, 147)], 'ledger-v7.tsv ids are not L001-L146'
new = []


def row(sec, claim, value, unit, src, label, commit, tc, sb, note='', read_by='', read_note=''):
    i = f'L{147 + len(new):03d}'
    new.append(dict(id=i, paper_section=sec, claim=claim, value=value, unit=unit, source='; '.join(src) if isinstance(src, (list, tuple)) else src,
                    label=label, openai_math_commit=commit, toolchain=tc, sandbox=sb, status='FOUND', note=note, read_by=read_by, read_note=read_note))
    return i


# ---- item 1: declarations checked, and the closure of exists_absolute_real_zero_gap ----
row('2; 6', 'The SiegelZeros challenge has Comparator check two declarations: the challenge file states theorems exists_absolute_real_zero_gap (line 8) and WeightedTorusJets.dirichletRealZeroBound_proof (line 19), and the config theorem_names lists both, for the shipped config and for the nanoda-enabled copy used in the runs.',
    'OAI.SiegelZeros.WeightedTorusJets.exists_absolute_real_zero_gap; OAI.SiegelZeros.WeightedTorusJets.dirichletRealZeroBound_proof', 'theorem_names',
    [L(X + 'lean/ComparatorChallenges/SiegelZeros.lean', 8, 8, 'theorem exists_absolute_real_zero_gap'), L(X + 'lean/ComparatorChallenges/SiegelZeros.lean', 19, 19, 'theorem WeightedTorusJets.dirichletRealZeroBound_proof'),
     L(X + 'lean/ComparatorChallenges/SiegelZeros.json', 4, 7, '"OAI.SiegelZeros.WeightedTorusJets.exists_absolute_real_zero_gap"'), L(X + 'lean/ComparatorChallenges/SiegelZeros.json', 4, 7, '"OAI.SiegelZeros.WeightedTorusJets.dirichletRealZeroBound_proof"'),
     L('wsl-comparator/SiegelZeros-nanoda.json', 4, 7, '"OAI.SiegelZeros.WeightedTorusJets.exists_absolute_real_zero_gap"')],
    'COMPUTED', A_ + ' (challenge file and shipped config; the challenge file is unchanged at fd4aeeb, v7:L007)', NR, NONE,
    note='source text; the shipped config at adc7f12 is the one in external/openai-math; wsl-comparator/SiegelZeros-nanoda.json differs from it only in enable_nanoda')
SCAN = L('lean-checks/ReroutedDeps.lean', 3, 5, 'reporting closure members whose last name component is one of')
for lab, ln in (('control', 5), ('reroute', 4)):
    row('4; 6', f'fd4aeeb {lab}: the dependency scan of exists_absolute_real_zero_gap finds 107760 constants in its closure and no member whose last name component is actual_biquadratic_rectangle_span, uniform_rectangular_multiplicity, source_rectangle_span_of_polynomial_zero_test, actual_biquadratic_rectangle_span_via_lemma3 or interpolation.',
        '107760 constants in closure; matches: []', 'constants in closure',
        [R(RR + f'{lab}-deps.log', 'OAI.SiegelZeros.WeightedTorusJets.exists_absolute_real_zero_gap: 107760 constants in closure; matches: []'), SCAN,
         L('lean-checks/ReroutedDeps.lean', 36, 36, '#find_deps OAI.SiegelZeros.WeightedTorusJets.exists_absolute_real_zero_gap ["uniform_rectangular_multiplicity", "source_rectangle_span_of_polynomial_zero_test", "actual_biquadratic_rectangle_span"')],
        'COMPUTED', F_, TC, SB45, note='same count in the control and the reroute; the scan matches by last name component, over types and values of theorem/def/opaque constants (ReroutedDeps.lean:3-5). It looks for these five names only; other multiplicity lemmas are not searched for')

# ---- item 2: lean/docs/003.md (STATED) ----
D3 = X + 'lean/docs/003.md'
row('2; 3', "openai/math's scope page lean/docs/003.md lists the 7/8 paper as an accompanying paper, states the 7/8 bound for the Riemann zeta function, every Dirichlet L-function and finite-order Hecke L-functions over Q(sqrt(-3)), and links these three results to the challenge files QuasiRiemannHypothesis.lean, DirichletSevenEighths.lean and HeckeSevenEighths.lean.",
    '3: "The following describes the scope of the Lean formalization related to the following accompanying paper(s):"; 5: "[The Quasi-Riemann Hypothesis: A Zero-Free Half-Plane $\\Re(s)>7/8$](../../preprints/The-Quasi-Riemann-Hypothesis-September-30-2026/paper.pdf)"; 10: "The formalization gives $\\theta=7/8$ for the Riemann zeta function and every Dirichlet $L$-function, uniformly over all positive moduli and all characters. It also establishes the same bound for finite-order Hecke $L$-functions over $\\mathbb Q(\\sqrt{-3})$."; 22: "| Riemann zeta $7/8$ bound | [QuasiRiemannHypothesis.lean](../ComparatorChallenges/QuasiRiemannHypothesis.lean) |"; 23: "| Dirichlet $L$-function $7/8$ bound | [DirichletSevenEighths.lean](../ComparatorChallenges/DirichletSevenEighths.lean) |"; 24: "| Finite-order Hecke $L$-function $7/8$ bound | [HeckeSevenEighths.lean](../ComparatorChallenges/HeckeSevenEighths.lean) |"',
    'quote', [L(D3, 3, 3, 'related to the following accompanying paper(s):'), L(D3, 5, 5, 'The-Quasi-Riemann-Hypothesis-September-30-2026/paper.pdf'), L(D3, 10, 10, 'It also establishes the same bound for finite-order Hecke'),
              L(D3, 22, 22, '[QuasiRiemannHypothesis.lean](../ComparatorChallenges/QuasiRiemannHypothesis.lean)'), L(D3, 23, 23, '[DirichletSevenEighths.lean](../ComparatorChallenges/DirichletSevenEighths.lean)'), L(D3, 24, 24, '[HeckeSevenEighths.lean](../ComparatorChallenges/HeckeSevenEighths.lean)')],
    'STATED', A_ + ' (file LF sha256 41e52ed7..., identical to the fd4aeeb copy read 2026-10-27)', NR, NR,
    note='the file does not use the words "main theorem"; the link to thm:main (build/paper.tex:106-111) is by the statement, which says the same three things')

# ---- item 4: the HeckeSevenEighths identification, in paper wording ----
HC = 'docs/statement-check-HeckeSevenEighths.md'
row('3', 'HeckeSevenEighths: the challenge\'s L-function is the paper\'s L_F(s, eta). For Re s > 1 the challenge defines it, by a Lean lemma, as (1/6) times the sum over nonzero alpha in O of chi(alpha) N(alpha)^(-s). The ring O = Z[omega] is a principal ideal domain whose six units act freely on its nonzero elements, so each nonzero ideal has exactly six generators. chi is trivial on units and the norm is unit-invariant, so each ideal contributes six equal terms, and the sum equals the sum over nonzero ideals a of eta(a) (Na)^(-s), with eta(alpha O) = chi(alpha); the rearrangement is valid by absolute convergence. The challenge\'s L-function is holomorphic off {0, 1}, so by the identity theorem the two functions agree on 7/8 < Re s <= 1.',
    'MATCH (each nonzero ideal of O has exactly six generators, on which chi and the norm are constant)', 'finding',
    [L(RD, 88, 99, 'The identification Joe ruled on 2026-10-20'), R(HC, 'Each nonzero ideal has exactly 6 generators'), R(HC, '`HeckeSeries.LFunction_hasSum`'), R(HC, 'By the identity theorem (INFERRED')],
    'INFERRED', F_, TC, NONE, note='replaces the wording "L-function row by Joe\'s ruling 2026-10-20" of v7:L006 for use in Table 1; v7:L006 itself is unchanged and keeps its read_by. Rests on: Lean lemmas of 2026-10-20 (HeckeSeries.LFunction_hasSum, Hecke.differentiableAt_LFunction, HeckeNorm) and the reading in readings-claude-code.md:94-99',
    read_by='')

# ---- item 3: one INFERRED row per reasoning point of the six readings (read_by empty) ----
P = [  # (reading, point, lines a-b, substring in those lines, value)
 ('SiegelZeros', 'quantifier order: the constant c precedes q, chi and beta, so c is absolute', 13, 13, '**Quantifier order:**', 'MATCH'),
 ('SiegelZeros', 'hypotheses: primitive, nonprincipal, real, q >= 3, beta in (0,1); none added, none missing', 14, 21, 'Nothing is added and nothing is missing', 'MATCH'),
 ('SiegelZeros', 'conclusion: c <= (1 - beta) log q, non-strict as in (1.1)', 22, 22, 'non-strict as in (1.1)', 'MATCH'),
 ('SiegelZeros', 'Mathlib meaning: IsPrimitive is conductor = level, and conductor is the least level through which chi factors', 24, 24, 'IsPrimitive is `conductor χ = n`', 'MATCH'),
 ('SiegelZeros', 'Mathlib meaning: (chi a).im = 0 for all a means real-valued; values are 0 or roots of unity, so 0 or +-1', 25, 25, 'means real-valued', 'MATCH'),
 ('SiegelZeros', 'Mathlib meaning: DirichletCharacter.LFunction is ZMod.LFunction, the continuation; it equals the Dirichlet series for Re s > 1 and is entire for chi != 1', 26, 26, '`DirichletCharacter.LFunction` is `ZMod.LFunction χ`', 'MATCH'),
 ('SiegelZeros', 'edge cases: q = 4 (odd) and q = 8 (one even, one odd) are covered', 29, 29, 'q = 4 (χ₋₄, odd) and q = 8', 'MATCH'),
 ('SiegelZeros', 'edge cases: no hypothesis mentions parity, so both parities are included', 30, 30, 'No hypothesis mentions parity', 'MATCH'),
 ('SiegelZeros', 'edge cases: nothing excludes non-prime or even conductors', 31, 31, 'Nothing excludes non-prime or even conductors', 'MATCH'),
 ('QuasiRiemannHypothesis', 'quantifier order: 7/8 is a fixed literal', 41, 41, 'the constant 7/8 is a fixed literal', 'MATCH'),
 ('QuasiRiemannHypothesis', 'hypotheses: only Re s > 7/8; no pole hypothesis', 42, 42, 'only Re s > 7/8', 'MATCH'),
 ('QuasiRiemannHypothesis', 'conclusion: != 0 on the open half-plane Re s > 7/8; the paper excludes the boundary', 43, 43, 'the boundary Re s = 7/8 is not included', 'MATCH'),
 ('QuasiRiemannHypothesis', 'Mathlib meaning: riemannZeta is hurwitzZetaEven 0, the continuation, with a junk value at 1', 44, 44, 'riemannZeta is `hurwitzZetaEven 0`', 'MATCH'),
 ('QuasiRiemannHypothesis', 'edge case s = 1: Mathlib\'s riemannZeta 1 is a nonzero junk value, so the statement asserts a true fact about it and nothing about the pole, which the paper allows', 45, 49, 'riemannZeta 1 = (γ − log 4π)/2', 'MATCH'),
 ('DirichletSevenEighths', 'quantifier order: fixed 7/8, uniform over every q >= 1, chi and s', 56, 56, 'fixed 7/8, uniform over every q ≥ 1', 'MATCH'),
 ('DirichletSevenEighths', 'hypotheses: any modulus q >= 1 and any character, imprimitive ones and q = 1 included, as in the paper\'s definition', 58, 59, 'including imprimitive ones and q = 1', 'MATCH'),
 ('DirichletSevenEighths', 'hypotheses: hpole excludes s = 1 only for the principal character mod q', 60, 60, 'excludes s = 1 only for the principal character mod q', 'MATCH'),
 ('DirichletSevenEighths', 'conclusion: != 0, strict half-plane', 62, 62, '**Conclusion:** `≠ 0`, strict half-plane', 'MATCH'),
 ('DirichletSevenEighths', 'Mathlib meaning: LFunction is the continuation; for q = 1 it is riemannZeta; for chi != 1 it is entire, so its value at s = 1 is genuine', 64, 65, 'For q = 1 it is riemannZeta', 'MATCH'),
 ('DirichletSevenEighths', 'edge cases: imprimitive nonprincipal characters gain zeros only on Re s = 0; the principal pole at 1 is excluded by hpole', 68, 69, 'on Re s = 0, which is outside the half-plane', 'MATCH'),
 ('HeckeSevenEighths', 'quantifier order: fixed 7/8, every Character', 79, 79, 'fixed 7/8; every `Character`', 'MATCH'),
 ('HeckeSevenEighths', 'hypotheses: Character (nonzero modulus, MulChar on O/m trivial on units, zero on non-units) is exactly a ray class character mod m extended by zero, since O is a PID with 6 units', 81, 82, 'exactly the characters of the ray class group mod', 'MATCH'),
 ('HeckeSevenEighths', 'hypotheses: imprimitive characters are included on both sides', 83, 83, 'Imprimitive characters are included on both sides', 'MATCH'),
 ('HeckeSevenEighths', 'hypotheses: the auxiliary period does not matter (HeckeHolo.period_indep)', 84, 84, 'HeckeHolo.period_indep', 'MATCH'),
 ('HeckeSevenEighths', 'hypotheses: hpole excludes s = 1 for the principal character only', 85, 85, 'the principal character only', 'MATCH'),
 ('HeckeSevenEighths', 'conclusion: != 0, strict half-plane', 87, 87, '**Conclusion:** `≠ 0`, strict half-plane', 'MATCH'),
 ('HeckeSevenEighths', 'definitions: the lattice series for Re s > 1, holomorphy off {0, 1} and the norm formula fix the function in 7/8 < Re s <= 1 by the identity theorem', 88, 93, 'By the identity theorem this fixes the function in the strip', 'MATCH'),
 ('HeckeSevenEighths', 'identification: each nonzero ideal has exactly 6 generators; chi and the norm are unit-invariant; so (1/6) times the sum over alpha equals the sum over ideals (absolute convergence)', 94, 99, 'I accept the identification', 'MATCH'),
 ('HeckeSevenEighths', 'the Dedekind factorization is not needed for this match (checked numerically only)', 100, 100, 'is not needed for this match', 'consistent'),
 ('HeckeSevenEighths', 'edge case s = 0 (outside the half-plane): a Gamma(0) = 0 junk value, no effect on the statement', 101, 101, 'Γ(0) = 0 junk value', 'MATCH'),
 ('Lemma3.interpolation', 'A: any surjective C-linear map C^4 -> C^3', 111, 111, '| A |', 'MATCH'),
 ('Lemma3.interpolation', 'kernel: ker A = C c', 112, 112, '| kernel |', 'MATCH'),
 ('Lemma3.interpolation', 'Q-independence: LinearIndependent Q c, c a family of four complex numbers', 113, 113, '| ℚ-independence |', 'MATCH'),
 ('Lemma3.interpolation', 'N, t: N >= 1, integers t_j >= 3(N - 1)', 114, 114, '| N, t |', 'MATCH'),
 ('Lemma3.interpolation', 'budget (3.1): exact and strict', 115, 115, '| budget (3.1) |', 'MATCH (exact, strict)'),
 ('Lemma3.interpolation', 'P_t: separate degrees deg_{z_j} B <= t_j', 116, 116, '| P_t |', 'MATCH'),
 ('Lemma3.interpolation', 'domain: Fin 4 -> Fin N is E_N', 117, 117, '| domain |', 'MATCH'),
 ('Lemma3.interpolation', 'conclusion: evaluation at A(n) is surjective onto C^{E_N}', 118, 118, '| conclusion |', 'MATCH'),
 ('Lemma3.rectangle', 'hypotheses on A: the same as Lemma 3', 128, 128, '| hypotheses on A |', 'MATCH'),
 ('Lemma3.rectangle', 'H, N: naturals with 1 <= H <= N', 129, 129, '| H, N |', 'MATCH'),
 ('Lemma3.rectangle', 'bound alpha_0: 32 H^(2/3) N^(4/3), real exponents', 130, 130, '| bound α₀ |', 'MATCH'),
 ('Lemma3.rectangle', 'bounds alpha_1, alpha_2: 32 H^(-1/3) N^(4/3)', 131, 131, '| bounds α₁, α₂ |', 'MATCH'),
 ('Lemma3.rectangle', 'alpha: in N^3, compared as reals with T_j', 132, 132, '| α |', 'MATCH'),
 ('Lemma3.rectangle', 'rows: (An)_0^a0 (An)_1^a1 (An)_2^a2; Lean indexes from 0, the paper from 1', 133, 133, '| rows |', 'MATCH'),
 ('Lemma3.rectangle', 'conclusion: the rows span all functions on E_N', 134, 134, '| conclusion |', 'MATCH'),
 ('Lemma3.rectangle', 'the remark "the constant 32 is independent of A and H" is the literal 32 in Lean', 135, 135, 'the constant 32 is independent of A and H', 'consistent'),
]
RID = {'SiegelZeros': 'v7:L008', 'QuasiRiemannHypothesis': 'v7:L002', 'DirichletSevenEighths': 'v7:L004', 'HeckeSevenEighths': 'v7:L006', 'Lemma3.interpolation': 'v7:L145', 'Lemma3.rectangle': 'v7:L146'}
first = None
for rdg, pt, a, b, sub, val in P:
    i = row('3' if rdg not in ('Lemma3.interpolation', 'Lemma3.rectangle') else '5', f'Reading point, {rdg}: {pt}.', val, 'reasoning point',
            [L(RD, a, b, sub)], 'INFERRED', F_ if rdg not in ('Lemma3.interpolation', 'Lemma3.rectangle') else NR, TC, NONE,
            note=f'reasoning behind {RID[rdg]}; rests on reading the Lean source against the paper text (readings-claude-code.md:{a}-{b})', read_by='')
    first = first or i

if problems:
    print('PROBLEMS (ledger not written):'); print('\n'.join(problems)); sys.exit(1)
p = os.path.join(OUT, 'ledger-v8.tsv')
if os.path.exists(p): sys.exit(f'refusing to overwrite {p}')
with open(p, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t', lineterminator='\n'); w.writerow(cols)
    for r in rows + new: w.writerow([r[c] for c in cols])
print('rows', len(rows) + len(new), 'new', len(new), new[0]['id'], '-', new[-1]['id'], 'reasoning rows from', first, dict(collections.Counter(r['label'] for r in new)))
