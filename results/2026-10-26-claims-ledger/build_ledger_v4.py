"""Claims ledger v4 (2026-10-27). Read-only on the repo; writes ledger-v4.tsv next to this file (refuses to overwrite).

Usage: python -I results/2026-10-26-claims-ledger/build_ledger_v4.py <repo root>

Append-only, as in v3 (id-stability.md):
  - every ledger-v3.tsv row is copied with its id and all fields; the only change allowed is the status of a row that a new
    row supersedes, which becomes "SUPERSEDED by v4:Lxxx" (value and source are kept);
  - new rows take explicit ids from L131 on.
Sources are resolved as in build_ledger.py: R(path, substring) -> path:LINE; L(path, a, b, substring) -> path:a-b (LF sha256).
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
NC = '1ca7ff2a0280760783ee2b198c0d6f2a1cfeaba4'
NEAL = f'https://github.com/nealmcb/openai-math-lean-tooling/blob/{NC}/'
LG = 'results/2026-10-26-claims-ledger/'; EV = LG + 'v3-evidence/'
NCmp = 'results/2026-10-27-neal-comparison/'; NX = NCmp + 'neal-1ca7ff2-extracts.txt'
PL = 'lean-checks/comparator-copy/PaperLemma3/Lemma3.lean'

with open(os.path.join(OUT, 'ledger-v3.tsv'), encoding='utf-8') as f:
    rd = csv.reader(f, delimiter='\t'); cols = next(rd); rows = [dict(zip(cols, r)) for r in rd]
assert [r['id'] for r in rows] == [f'L{k:03d}' for k in range(1, 131)], 'ledger-v3.tsv ids are not L001-L130'
byid = {r['id']: r for r in rows}
new = []


def row(i, sec, claim, value, unit, src, label, commit, tc, sb, status='FOUND', note='', read_by='', read_note=''):
    new.append(dict(id=i, paper_section=sec, claim=claim, value=value, unit=unit,
                    source='; '.join(src) if isinstance(src, (list, tuple)) else src, label=label, openai_math_commit=commit,
                    toolchain=tc, sandbox=sb, status=status, note=note, read_by=read_by, read_note=read_note))


def supersede(old, by):
    r = byid[old]; assert r['status'] == 'FOUND', (old, r['status']); r['status'] = f'SUPERSEDED by v4:{by}'


# ---- item 2: outcome comparison against nealmcb at 1ca7ff2, all our recorded results ----
SM = NCmp + 'summary.txt'
row('L131', '0; 7', "Outcome-level comparison with nealmcb's Comparator results at 1ca7ff2 (results/cmp-all/all.jsonl, one record per config), against all our recorded results: the 189 (187 at fd4aeeb, SiegelZeros and QuasiRiemannHypothesis in the adc7f12 pilot) and the 227 (final outcome, with the optional Lean-kernel runs on Catalan and KMedianThreshold). Verdict compared: Comparator with the Lean kernel accepts the config.",
    '416 compared; 402 agree; 0 disagree; 14 no verdict here (ContinuumCoulombHardness, CycleCliqueRamsey, DefocusingNLS, FalconerAllDimensions, InvariantIsing, JointDickman, MUBSix, OrdinaryTwoPointCorrelations, OstmannComplete, PattersonFirstMoment, PolycyclicRecognition, SurfaceImmersion, UniversalTensorSquares: NOT_CHECKED_HERE; PlanarPacking: TIMEOUT); 0 no verdict there; 0 no verdict on either side',
    'configs', [R(SM, 'configs: ours 416, his 416, union 416, in both 416'), R(SM, "by class: {'agree': 402, 'no verdict here': 14}"), R(SM, 'disagree: []'), R(SM, "no verdict here: [('ContinuumCoulombHardness'"),
                R(SM, 'no verdict there: []'), R(SM, 'no verdict either side: []'), R(SM, "his outcomes: {'accepted': 416}"), NCmp + 'outcomes.tsv (one row per config)', NEAL + 'results/cmp-all/all.jsonl'],
    'COMPUTED', F_ + ' (ours: 187 + 227; SiegelZeros and QuasiRiemannHypothesis at ' + A_ + ')', TC, NR,
    note='his side is STATED (all.jsonl at 1ca7ff2, sha256 6753e7de...; his STATUS.md is dated 2026-10-13). Agreement for the 189: 189 of 189; for the 227: 213 of 227. Catalan and KMedianThreshold agree only through the optional Lean-kernel runs. The pilot pair is compared across commits (ours adc7f12, his fd4aeeb). His records for ArtinParabolicIntersections and TraceIdealTransportSupport have the nanoda flag set; all others are Lean kernel only')
supersede('L112', 'L131')

# ---- item 2: nealmcb's ContinuumCoulombHardness rows, re-tied to 1ca7ff2 (STATED) ----
TT = f'nealmcb pins (MANIFEST.txt at {NC[:7]})'
row('L132', '7', 'nealmcb at 1ca7ff2: Comparator as shipped (Lean kernel, nanoda flag false) accepts ContinuumCoulombHardness, check time 923.63 s.', 'accepted; 923.63 s', 'verdict',
    [NEAL + 'results/cmp-all/all.jsonl#L416', NEAL + 'results/cmp-all/STATUS.md#L7', R(NX, 'results/cmp-all/all.jsonl:416:{"config": "ContinuumCoulombHardness"'), R(NX, "results/cmp-all/STATUS.md:7:last driver line: ['ContinuumCoulombHardness accepted None 923.63']")],
    'STATED', F_, TT, 'nealmcb sandbox (landrun)', note='replaces v3:L125, whose agreement with 1ca7ff2 was UNCONFIRMED; the record is present at 1ca7ff2')
row('L133', '7', 'nealmcb at 1ca7ff2: on his ContinuumCoulombHardness export (1,081,490,385 bytes), the kernel-pair sweep records exit 1 for the Lean kernel replay (454.4 s) and exit 1 for nanoda 3a24072 (99.3 s), with no verdict text.', 'lean_rc 1 (454.4 s); nanoda_rc 1 (99.3 s)', 'exit codes',
    [NEAL + 'results/kernel-pair-sweep.jsonl#L372', R(NX, 'results/kernel-pair-sweep.jsonl:372:{"config": "ContinuumCoulombHardness"')], 'STATED', F_, TT, 'nealmcb',
    note='replaces v3:L126 (which gave only the nanoda time); the cause of exit 1 is not recorded in the line')
row('L134', '7', 'nealmcb at 1ca7ff2: nanoda retests of ContinuumCoulombHardness (4 threads, 30G cap): f67473b exit 0 at 130.1 s and 24.23 GiB, and exit 0 at 114.3 s and 24.26 GiB (two builds); exit 134 at 28.6 s and 28.8 s (a third f67473b build); 998e0a8 exit 134 at 32.8 s. His REPORT.md gives "130 s and 24 GiB on f67473b".',
    'f67473b: 0 / 130.1 s / 24.23 GiB; 0 / 114.3 s / 24.26 GiB; 134 / 28.6 s; 134 / 28.8 s; 998e0a8: 134 / 32.8 s', 'exit code, time, memory',
    [NEAL + 'results/nanoda-retest.jsonl#L9', NEAL + 'results/nanoda-retest.jsonl#L18', NEAL + 'results/nanoda-retest.jsonl#L25', NEAL + 'results/nanoda-retest.jsonl#L28', NEAL + 'results/nanoda-retest.jsonl#L31', NEAL + 'REPORT.md#L534',
     R(NX, 'results/nanoda-retest.jsonl:9:'), R(NX, 'results/nanoda-retest.jsonl:31:'), R(NX, 'REPORT.md:534:')], 'STATED', F_, 'nanoda f67473b (three builds) / 998e0a8', 'nealmcb',
    note='replaces v3:L127; the ~24 GiB figure is now tied to nanoda-retest.jsonl:9 (rss_gib 24.23) and REPORT.md:534 at 1ca7ff2, not only to #61. The builds are his scratch paths nanoda-master, nanoda-alpha, nanoda-i57 (all f67473b) and nanoda-pr59 (998e0a8)')
row('L135', '7', 'nealmcb at 1ca7ff2: with the let fix and the Nat.succ guard at STACK_SIZE 64 MiB, nanoda 37cb87b passes ContinuumCoulombHardness at 50.0 s and 1.8 GB; with the let fix alone it overflows at 64 MiB (34 s, 4 GB) and 256 MiB (48 s, 13 GB).',
    'pass 50.0 s 1.8GB; let fix alone: overflow 34 s 4GB (64 MiB), overflow 48 s 13GB (256 MiB)', 'result',
    [NEAL + 'results/nanoda-stack-size-2026-10-25.txt#L19', NEAL + 'results/nanoda-stack-size-2026-10-25.txt#L12', R(NX, 'results/nanoda-stack-size-2026-10-25.txt:19:'), R(NX, 'results/nanoda-stack-size-2026-10-25.txt:12:')],
    'STATED', F_, 'nanoda 37cb87b (+ patch)', 'nealmcb', note='replaces v3:L128; same text as the copy in comparison.txt')
for o, n in (('L125', 'L132'), ('L126', 'L133'), ('L127', 'L134'), ('L128', 'L135')): supersede(o, n)

# ---- item 3: structure of the Lean proof of Lemma 3 (comparator copy) ----
G = [  # (group, [(declaration, a, b, substring)], interpolation body lines, body step comment)
    ('opening, eq:moments (not one of the six steps)', [('exists_annihilator', 624, 661, 'theorem exists_annihilator'), ('p5_PtSub', 591, 612, 'def p5_PtSub')], (829, 845), '-- Step 1: the annihilating weights `v`.'),
    ('dimension count, zeros of R (eq:zeros)', [('four_hull_subset_cube', 663, 681, 'theorem four_hull_subset_cube'), ('exists_vanishing', 683, 738, 'theorem exists_vanishing')], (846, 885), '-- Step 3: `R`.'),
    ('supporting face and nearest point', [('exists_lattice_nonvanishing', 740, 770, 'theorem exists_lattice_nonvanishing'), ('exists_nearest', 87, 148, 'theorem exists_nearest'), ('p1_var_ineq', 57, 85, 'lemma p1_var_ineq'),
                                           ('p1_coord_le_sqd', 51, 55, 'lemma p1_coord_le_sqd'), ('p1_dot_self_nonneg', 47, 49, 'lemma p1_dot_self_nonneg'), ('quarter_mem_face', 150, 208, 'theorem quarter_mem_face')], (886, 909), '-- Step 4: lattice points where `R ∘ A` does not vanish.'),
    ('vertex choice (eq:vertex)', [('exists_heavy_vertex', 224, 299, 'theorem exists_heavy_vertex')], (910, 916), '-- Steps 7–8: the vertex `u`.'),
    ('off-face vanishing (eq:distance, eq:offface)', [('closer_point', 301, 340, 'theorem closer_point'), ('p2_dot_expand', 213, 218, 'theorem p2_dot_expand'), ('p2_dot_self_nonneg', 220, 222, 'theorem p2_dot_self_nonneg')], (917, 939), '-- Steps 9–11: `R` vanishes at `m + n − u` for `n ∈ S` off the face.'),
    ('Lagrange polynomial Q', [('exists_int_hyperplane', 371, 432, 'theorem exists_int_hyperplane'), ('p3_g', 342, 352, 'def p3_g'), ('p3_g_apply', 354, 354, 'theorem p3_g_apply'), ('p3_clear', 356, 369, 'theorem p3_clear'),
                               ('int_comb_ne_zero', 434, 443, 'theorem int_comb_ne_zero'), ('exists_lagrange', 471, 586, 'theorem exists_lagrange'), ('p4_linP', 445, 448, 'def p4_linP'), ('p4_eval_linP', 450, 455, 'theorem p4_eval_linP'),
                               ('p4_deg_linP', 457, 461, 'theorem p4_deg_linP'), ('p4_rL', 463, 465, 'def p4_rL'), ('p4_rL_apply', 467, 469, 'theorem p4_rL_apply')], (940, 947), '-- Step 12: the integer hyperplane'),
    ('final contradiction (B = Q R(z + A(m - u)))', [('exists_translate', 772, 812, 'theorem exists_translate')], (948, 985), '-- Step 15: `B = Q · R(z + A(m − u)) ∈ 𝒫_t`.'),
]
SHARED = [('zR', 29, 30, 'def zR'), ('zC', 32, 33, 'def zC'), ('emb', 35, 36, 'def emb'), ('sqd', 38, 39, 'def sqd'), ('Pt', 41, 43, 'def Pt'), ('p5_eval_aeval', 614, 620, 'theorem p5_eval_aeval')]
src = []; parts = []
for g, ds, (a, b), cm in G:
    for d in ds: src.append(L(PL, d[1], d[2], d[3]))
    src.append(L(PL, a, a, cm))
    parts.append(f'{g}: ' + ', '.join(f'{d[0]} {d[1]}-{d[2]}' for d in ds) + f'; main proof {a}-{b}')
for d in SHARED: src.append(L(PL, d[1], d[2], d[3]))
src.append(L(PL, 816, 817, 'theorem interpolation'))
parts.append('not placed (shared by several steps): ' + ', '.join(f'{d[0]} {d[1]}-{d[2]}' for d in SHARED))
row('L136', '5', 'Structure of the Lean proof of Lemma 3 in the comparator copy PaperLemma3/Lemma3.lean: each sub-lemma with its line range (docstring to last line), grouped under the paper\'s proof steps (tex 268-408); Lemma3.interpolation (816-985) calls each group in order at its "-- Step" comments.',
    ' | '.join(parts), 'declarations', src, 'COMPUTED', NR, TC, NONE,
    note='grouping by the step comments in the main proof (829-962) and by where each helper is used (a helper is placed in the group of the only sub-lemma that uses it). exists_annihilator and p5_PtSub give the weights v of eq:moments, which opens the proof and is not one of the six named steps. zR, zC, emb, Pt are used across groups; sqd by both the nearest-point and off-face groups; p5_eval_aeval by exists_lattice_nonvanishing and exists_translate')

# ---- item 4: Comparator's stated assumptions (README lines 28-39) ----
CR = EV + 'comparator-README-d03acab.md'
row('L137', '8', "Comparator's stated assumptions (README lines 28-39 at d03acab), quoted.",
    '"Given the following assumptions: 1. The transitive closure of imports of `Challenge.lean` as well as `lakefile.toml`/`lakefile.lean` are controlled by you or trustworthy. 2. You have not previously tried to compile the `Solution` file or any other potentially adversarial files (as that might compromise your `Challenge` file to make it seem like you are looking for a different proof than you actually are) 3. You have the `landrun` and `lean4export` binary in `PATH` 4. `landrun` works correctly on your system and `Solution.lean` does not exploit any bugs in `landrun` that allow a process to escape its sandbox 5. The Lean kernel is correct (with `external_kernels` this can be reduced to "At least one of the Lean kernel or the `external_kernels` is correct") 6. You are not running this under a privileged user"',
    'tool documentation', ['/root/tools/comparator/README.md lines 28-39 (clone d03acab154d269c06e60e4de7e4cc85deebff94b; README unmodified, ' + R(EV + 'tool-readmes.txt', 'clone /root/tools/comparator HEAD d03acab') + ')',
                           L(CR, 28, 28, 'Given the following assumptions:'), L(CR, 29, 30, 'The transitive closure of imports of `Challenge.lean`'), L(CR, 37, 38, '5. The Lean kernel is correct'), L(CR, 39, 39, '6. You are not running this under a privileged user')],
    'STATED', NR, 'Comparator d03acab (v4.34.0)', NR, note='quoted with line breaks joined; the copy in v3-evidence/ has the same sha256 as the clone README (cfdf0ff6...)')

# ---- item 5: the NonVacuity run's sandbox (closes the Section 8 missing item) ----
row('L138', '8', 'Sandbox of the 2026-10-08 NonVacuity run (L011-L014): wsl-comparator/32_nonvacuity.sh runs lake env lean as checker via sudo -u checker; no systemd-run unit and no RestrictAddressFamilies filter.',
    'sudo -u checker; no systemd-run; no address-family filter', 'sandbox',
    [R('wsl-comparator/32_nonvacuity.sh', "sudo -u checker -H bash -lc 'export PATH=\"$HOME/.elan/bin:$PATH\"; cd $HOME/math/lean; date; time lake env lean"), R('results/2026-10-08-lean-nonvacuity.txt', 'wsl-comparator/32_nonvacuity.sh')], 'COMPUTED', A_, TC, NR,
    note='the script is first committed in 447ad02 (2026-10-09 08:50), after the run (2026-10-08 14:28), and is unchanged since; that the committed text is the text that ran is INFERRED')

# ---- item 7: lean-checks/README.md ----
row('L139', '9', 'lean-checks/README.md (the role of each Lean file) is committed at 758b44f74a208791c4c59b898d1ba104122ae7d0 and unchanged since; LF sha256 of the file.', 'c954fe424f8450ebbbadef60ed1649f94cbd84c25223a30389e2480fc5cd8bf9', 'sha256',
    [L('lean-checks/README.md', 1, 1, '# lean-checks/: what each Lean file is'), 'git log -- lean-checks/README.md (one commit, 758b44f)'], 'COMPUTED', NR, NR, NR,
    note='the source entry gives the sha256 of the working-tree file after LF normalisation; git show 758b44f:lean-checks/README.md has the same sha256')

# ---- write ----
if problems:
    print('PROBLEMS (ledger not written):'); print('\n'.join(problems)); sys.exit(1)
assert [r['id'] for r in new] == [f'L{k:03d}' for k in range(131, 131 + len(new))]
assert new[-1]['source'].split(' (LF sha256 ')[1].startswith('c954fe424f8450ebbbadef60ed1649f94cbd84c25223a30389e2480fc5cd8bf9'), 'README sha256 changed'
p = os.path.join(OUT, 'ledger-v4.tsv')
if os.path.exists(p): sys.exit(f'refusing to overwrite {p}')
allrows = rows + new
with open(p, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t', lineterminator='\n'); w.writerow(cols)
    for r in allrows: w.writerow([r[c] for c in cols])
print('rows', len(allrows), 'new', len(new), 'new by label', dict(collections.Counter(r['label'] for r in new)), 'status', dict(collections.Counter(r['status'] for r in allrows)))
