"""nanoda version matrix (2026-10-26, UNOFFICIAL): matrix.tsv from our run logs plus cells STATED by Neal McBurnett's public results.

Usage: python -I scripts/nanoda_matrix.py <repo root> <matrix dir> [<output name>, default matrix.tsv]
COMPUTED cells come from our logs only:
  3a24072 @16 MiB (official): the 189 from results/2026-10-20-paper-prep-3/corpus-189.tsv (+ its log path); the 227 from
      results/2026-10-21-extended-replay/runs/<C>.result.json (nanoda_run, comparator with enable_nanoda=true)
  3a24072 @1 GiB (B1), 37cb87b (B2), 37cb87b+patch @64 MiB (B3): <matrix dir>/runs/<C>.<B>.log OUTCOME line (140_matrix_run.sh)
      KaplanskyFinitelyPresented / GroupRingDeterminant @1 GiB also: results/2026-10-20-nanoda-discrepancy/R3/<C>.R3.log
  f67473b: results/2026-10-20-nanoda-postfix-f67473b/outcomes.tsv (through comparator) and the extended f67473b-direct logs
STATED cells quote nealmcb's issue text or files (URL at a pinned commit). INFERRED cells say so. Empty = nobody ran it.
Writes matrix.tsv; refuses to overwrite.
"""
import csv, json, os, re, sys

root, M = sys.argv[1], sys.argv[2]
R = os.path.join(root, 'results')
rel = lambda p: os.path.relpath(p, root).replace(os.sep, '/')
out = os.path.join(M, sys.argv[3] if len(sys.argv) > 3 else 'matrix.tsv')
if os.path.exists(out): sys.exit(f'refusing to overwrite {out}')
NT = 'https://github.com/nealmcb/openai-math-lean-tooling/blob/1ca7ff2a0280760783ee2b198c0d6f2a1cfeaba4/results/'
I55, I55c = 'https://github.com/ammkrn/nanoda_lib/issues/55', 'https://github.com/ammkrn/nanoda_lib/issues/55#issuecomment-6208777323'
I61, I61c = 'https://github.com/ammkrn/nanoda_lib/issues/61', 'https://github.com/ammkrn/nanoda_lib/issues/61#issuecomment-6402528075'
I62 = 'https://github.com/ammkrn/nanoda_lib/issues/62'
SS, TS, AB = NT + 'nanoda-stack-size-2026-10-25.txt', NT + 'nanoda-repro/three-stack-failures.md', NT + 'nanoda-ab-let.jsonl'

C189 = ['OptimalMaxCut', 'UniqueGamesTheorem', 'VertexCover', 'KaplanskyFinitelyPresented', 'GroupRingDeterminant', 'Laughlin',
        'BinPackingGap', 'IndependentSets', 'PerfectCompleteness']
C227 = ['KaplanskyDirectFiniteness', 'LaughlinPlanar', 'LaughlinFock', 'SquareDifference', 'DirectedFeedback', 'MinUncut']
EXTRA = [('KMedianThreshold', '227'), ('Catalan', '227'), ('ContinuumCoulombHardness', '227'), ('LogspaceEquality', '189'), ('RandomizedMeanPayoff', '189')]
ROWS = [(c, '189') for c in C189] + [(c, '227') for c in C227] + EXTRA
COLS = ['3a24072@16MiB (official)', '3a24072@1GiB (B1)', 'f67473b@16MiB', '37cb87b@16MiB (B2)', '37cb87b+patch@64MiB (B3)']

# STATED / INFERRED cells (Neal's published results; quoted, not re-measured)
ROUND = 'RoundTables group'
ST = {
    ('OptimalMaxCut', 1): f'STATED: fails at 1 GiB ("nanoda exits with an error after 30 to 60 s at a 1 GiB stack", {ROUND}) [{I55}]',
    ('VertexCover', 1): f'STATED: fails at 1 GiB ({ROUND}, 30-60 s) [{I55}]',
    ('BinPackingGap', 1): f'STATED: fails at 1 GiB ({ROUND}, 30-60 s) [{I55}]',
    ('IndependentSets', 1): f'STATED: fails at 1 GiB ({ROUND}, 30-60 s) [{I55}]',
    ('PerfectCompleteness', 1): f'STATED: fails at 1 GiB ({ROUND}, 30-60 s) [{I55}]',
    ('UniqueGamesTheorem', 1): f'STATED: stack overflow at 1 GiB (131 s, 25.1 GiB); 16 GiB stack: 31-bit index panic after 1,874 s, 285 GiB [{I55}]',
    ('Laughlin', 1): f'STATED: killed at 151 GiB (1 GiB-stack build) [{I55}]',
    ('LaughlinPlanar', 1): f'STATED: reached 175 GiB, ended by a 4 h timeout [{I55}]',
    ('LaughlinFock', 1): f'STATED: abort at 127 GiB [{I55}]',
    ('DirectedFeedback', 1): f'STATED: stack overflow at 1 GiB (131 s, 24.6 GiB) [{I55}]',
    ('MinUncut', 1): f'STATED: fails at 1 GiB ({ROUND}, 30-60 s) [{I55}]',
    ('SquareDifference', 1): f'STATED: "nanoda exits with an error" (1 GiB-stack build) [{I55}]',
    ('ContinuumCoulombHardness', 1): f'STATED: "nanoda exits with an error" (1 GiB-stack build) [{I55}]',
    ('ContinuumCoulombHardness', 2): f'STATED: accepted, 130 s, ~24 GiB [{I61}]',
    ('Catalan', 1): f'STATED: panic "index 2147483648 exceeds 31-bit capacity" after 2,014 s, 259 GiB (1 GiB stack) [{I55}]',
    ('KMedianThreshold', 1): f'STATED: "nanoda exits with an error" (1 GiB-stack build) [{I55}]',
    ('Catalan', 2): f'STATED: among the 14 of 15 that pass on f67473b [{I55c}]',
    ('KMedianThreshold', 2): f'STATED: among the 14 of 15 that pass on f67473b [{I55c}]',
    ('ContinuumCoulombHardness', 3): f'STATED: overflows on master; let fix alone overflows at 64 MiB (34 s, 4 GB) and 256 MiB (48 s, 13 GB) [{I61}; {SS}]',
    ('ContinuumCoulombHardness', 4): f'STATED: pass 50.0 s, 1.8 GB (let fix + Nat.succ guard, 64 MiB, 4 threads) [{SS}]',
    ('LogspaceEquality', 2): f'STATED: accepted 19 s, 0.8 GB (16 MiB, 4 threads) [{TS}]',
    ('LogspaceEquality', 3): f'STATED: abort (stack overflow) at 16 MiB [{TS}]; also rc 134 on 8199c74 [{AB}]',
    ('LogspaceEquality', 4): f'STATED: pass 21.3 s, 1.7 GB [{SS}]',
    ('RandomizedMeanPayoff', 3): f'STATED: one of the ten that fail on master [{I61c}]; rc 134 on 8199c74 base [{AB}]',
    ('RandomizedMeanPayoff', 4): f'STATED: passes with let fix + guard at 16 MiB, so at 64 MiB [{SS}]',
}
for c in ['OptimalMaxCut', 'UniqueGamesTheorem', 'VertexCover', 'BinPackingGap', 'IndependentSets', 'PerfectCompleteness']:
    ST[(c, 3)] = (f'INFERRED pass: STATED rc 0 on master 8199c74 (9 commits before 37cb87b; base and patched, 8 threads) [{AB}], and not among the '
                  f'ten #61 names as failing on master [{I61c}]; nobody ran 37cb87b on it')
    ST[(c, 4)] = f'(not run on 37cb87b+patch; STATED rc 0 on 8199c74 + let fix + guard at 16 MiB [{AB}])'
ST[('SquareDifference', 3)] = (f'(not run here yet) STATED: fails on master at any stack, 8 GiB stack still running at 34 min, 96 GB [{SS}; {I62}]')


def ours(c, b):
    p = os.path.join(M, 'runs', f'{c}.{b}.log')
    if not os.path.isfile(p): return None
    o = [l for l in open(p, encoding='utf-8') if l.startswith('OUTCOME:')]
    return f'COMPUTED: {o[-1][9:].strip()} [{rel(p)}]' if o else None


t189 = {r['config']: r for r in csv.DictReader(open(os.path.join(R, '2026-10-20-paper-prep-3', 'corpus-189.tsv'), encoding='utf-8'), delimiter='\t')}
pf = {r['config']: r for r in csv.DictReader(open(os.path.join(R, '2026-10-20-nanoda-postfix-f67473b', 'outcomes.tsv'), encoding='utf-8'), delimiter='\t')} \
    if os.path.isfile(os.path.join(R, '2026-10-20-nanoda-postfix-f67473b', 'outcomes.tsv')) else {}
rows = []
for c, s in ROWS:
    cell = [''] * 5
    if s == '189':
        t = t189[c]; lp = t['log_paths'].split('; ')[0]
        cell[0] = f"COMPUTED: {t['nanoda_3a24072']} (through comparator) [{lp}]"
        if c in pf:
            cell[2] = f"COMPUTED: {pf[c].get('outcome') or pf[c].get('postfix_outcome') or list(pf[c].values())[1]} (through comparator) [results/2026-10-20-nanoda-postfix-f67473b/{c}-postfix.log]"
        r3 = os.path.join(R, '2026-10-20-nanoda-discrepancy', 'R3', f'{c}.R3.log')
        if os.path.isfile(r3): cell[1] = f'COMPUTED 2026-10-20: exit 0 (R3, direct) [{rel(r3)}]'
    else:
        rj = os.path.join(R, '2026-10-21-extended-replay', 'runs', f'{c}.result.json')
        if os.path.isfile(rj):
            d = json.load(open(rj, encoding='utf-8')); nr = d['nanoda_run']; fd = d.get('f67473b_direct')
            cell[0] = f"COMPUTED: {nr['class']} (through comparator, exit {nr['exit']}, {nr['wall_s']} s) [{rel(rj)}]"
            if fd:
                mj = json.load(open(os.path.join(R, '2026-10-21-extended-replay', 'runs', f'{c}-f67473b-direct.mem.json'), encoding='utf-8'))
                lg = open(os.path.join(R, '2026-10-21-extended-replay', 'runs', f'{c}-f67473b-direct.log'), encoding='utf-8').read()
                w = re.search(r'DURATION_SECONDS: (\d+)', lg).group(1)
                cell[2] = f"COMPUTED: {fd['result']} (direct, exit {fd['exit']}, {w} s, peak {mj['peak_hwm_kb']} kB) [results/2026-10-21-extended-replay/runs/{c}-f67473b-direct.log]"
        else:
            cell[0] = {'KMedianThreshold': 'not run here: deferred (memory; 3a24072 run stopped at 19.84 GB and growing)',
                       'Catalan': 'not run here: deferred (memory; 3a24072 run stopped at 19.6 GB and rising)'}.get(c, 'not run here (deferred, Joe 2026-10-25)')
    for i, b in ((1, 'B1'), (3, 'B2'), (4, 'B3')):
        o = ours(c, b)
        if o: cell[i] = (cell[i] + ' | ' if cell[i] else '') + o
    for (cc, i), v in ST.items():
        if cc == c and not (i in (1, 3, 4) and ours(c, {1: 'B1', 3: 'B2', 4: 'B3'}[i])):
            cell[i] = (cell[i] + ' | ' if cell[i] else '') + v
        elif cc == c and i == 1:  # keep Neal's 1 GiB statement next to our B1 run
            cell[i] = cell[i] + ' | ' + v
    rows.append([c, s] + cell)
with open(out, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t', lineterminator='\n'); w.writerow(['config', 'set'] + COLS); w.writerows(rows)
print(open(out, encoding='utf-8').read())
