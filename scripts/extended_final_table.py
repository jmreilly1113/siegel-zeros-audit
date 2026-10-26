"""Extended replay, final table for the 227 unreferenced configs (2026-10-26), from the raw records (read-only on results/).

Usage: python -I scripts/extended_final_table.py <repo root> <out dir> [--unofficial=<matrix dir> --suffix=<s>]
  --unofficial: deferred configs with a B3 (37cb87b + patch, 64 MiB) run in <matrix dir>/runs/<C>.B3.log get status
  'run here, unofficial tool set B3' and the measured outcome, wall time and peak RSS; their official outcome stays NOT_CHECKED_HERE.
Reads, under results/2026-10-21-extended-replay/:
  phase0-configs-227.tsv   the 227 configs, group, shipped nanoda setting
  run.log                  every "<config>: outcome <X>; ..." line; the LAST one per config is the final outcome
                           (AtomicGaussian, BallPacking and LipschitzHilbert have earlier outcome lines)
  runs/<C>.result.json     115_classify.py's record: must agree with the last run.log outcome (checked; mismatch = exit 1)
  runs/<C>-axioms.log      #print axioms output (parsed directly, not from result.json)
  runs/<C>-audit-*.log     audit queries for the placeholder configs
  deferred.txt, stops.tsv  the 15 configs without a result, and the stops behind them
WSL memory at the time of each outcome is from platform-change-wsl-24gb.txt: ~16 GB (15,965 MB) before 2026-10-21 13:56:21,
24 GB until 2026-10-22 08:10:32, 20 GB after.
Writes corpus-227.tsv and summary-227.txt into <out dir>; refuses to overwrite.
"""
import collections, csv, json, os, re, sys

root, out = sys.argv[1], sys.argv[2]
OPT = dict(a[2:].split('=', 1) for a in sys.argv[3:] if a.startswith('--') and '=' in a)
UNOFF, SFX = OPT.get('unofficial'), OPT.get('suffix', '')
D = os.path.join(root, 'results', '2026-10-21-extended-replay')
rel = lambda p: os.path.relpath(p, root).replace(os.sep, '/')
outs = [os.path.join(out, f) for f in (f'corpus-227{SFX}.tsv', f'summary-227{SFX}.txt')]
for p in outs:
    if os.path.exists(p): sys.exit(f'refusing to overwrite {p}')
os.makedirs(out, exist_ok=True)

plan = list(csv.DictReader(open(os.path.join(D, 'phase0-configs-227.tsv'), encoding='utf-8'), delimiter='\t'))
assert len(plan) == 227
names = {r['config'] for r in plan}
outc = collections.defaultdict(list)  # config -> [(time, outcome, export sha, bytes)]
for line in open(os.path.join(D, 'run.log'), encoding='utf-8'):
    m = re.match(r'(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) ([A-Za-z0-9]+): outcome ([A-Z_]+)(?:; export sha256/bytes (\S+) (\S+))?', line)
    if m and m.group(2) in names: outcome_t = m.groups(); outc[m.group(2)].append(outcome_t[:1] + outcome_t[2:])
deferred = [l.strip() for l in open(os.path.join(D, 'deferred.txt'), encoding='utf-8') if l.strip() and not l.startswith('#')]
assert len(deferred) == 15 and set(deferred) <= names
stops = list(csv.DictReader(open(os.path.join(D, 'stops.tsv'), encoding='utf-8'), delimiter='\t'))

MEM_LIM = 'memory-limit-configs-20261023.txt'
MCB = 'results/2026-10-25-extended-replay-vs-mcburnett/comparison.txt'
LARGE10 = ['OrdinaryTwoPointCorrelations', 'JointDickman', 'SurfaceImmersion', 'ContinuumCoulombHardness', 'InvariantIsing',
           'FalconerAllDimensions', 'DefocusingNLS', 'PolycyclicRecognition', 'OstmannComplete', 'PattersonFirstMoment']
DEFER = {
    'Catalan': ('memory: nanoda 3a24072 run stopped by the guard twice; high-water 19,565,700 KB and rising under 24 GB WSL; '
                "no verdict from either kernel; Joe 2026-10-23 option 6 (not checked)", f'{rel(D)}/{MEM_LIM}'),
    'MUBSix': ('memory: four runs stopped ~22 min in, before nanoda started (comparator high-water ~18.6-19.0 GB); '
               'Joe 2026-10-23 option 6 (not checked)', f'{rel(D)}/{MEM_LIM}'),
    'KMedianThreshold': ('memory: lone nanoda run stopped by the guard 2026-10-24 16:55:24, nanoda_bin VmHWM 19.84 GB at 513 s and '
                         'still growing; same treatment as Catalan (not checked)', f'{rel(D)}/stops.tsv; {rel(D)}/runs/KMedianThreshold-nanoda.mem.json'),
    'CycleCliqueRamsey': ('memory: second guard stop on its lone build 2026-10-25 13:30:20 (lean processes ~5.5 GB each); '
                          'not checked', f'{rel(D)}/stops.tsv; {rel(D)}/GUARD_STOPPED-14.txt'),
    'UniversalTensorSquares': ('memory: second guard stop on its lone build 2026-10-26 10:20:33 (4 threads; first stop 10:15:28 at 10 threads); '
                               '388 modules unbuilt; not checked', f'{rel(D)}/stops.tsv'),
}
for c in LARGE10:
    DEFER[c] = ("large config not run here (Joe 2026-10-25 ~20:40); STATED accepted by Neal McBurnett's comparator run at identical pins", MCB)
assert set(DEFER) == set(deferred), set(DEFER) ^ set(deferred)


def wsl_mem(t):
    return '16GB-default' if t < '2026-10-21 13:56:21' else ('24GB' if t < '2026-10-22 08:10:32' else '20GB')


def axioms(c):
    p = os.path.join(D, 'runs', f'{c}-axioms.log')
    if not os.path.isfile(p): return 'MISSING', set(), None
    t = open(p, encoding='utf-8').read()
    ax = set()
    decls = re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", t)
    for _, a in decls: ax |= {x.strip() for x in a.split(',') if x.strip()}
    nodep = re.findall(r"'([^']+)' does not depend on any axioms", t)
    ok = 'SANDBOX EXIT CODE: 0' in t
    return ('ok' if ok else 'exit!=0'), ax, len(decls) + len(nodep)


def audit(c):
    res = []
    for k in ('challenge', 'solution'):
        p = os.path.join(D, 'runs', f'{c}-audit-{k}.log')
        if not os.path.isfile(p): continue
        t = open(p, encoding='utf-8').read()
        a = re.search(r'AUDIT axioms \(\d+\): \[([^\]]*)\]', t)
        tg = re.search(r'AUDIT statement\+proof closure: \d+ constants; contains target: (\w+)', t)
        st = re.search(r'AUDIT statement closure: \d+ constants; contains target: (\w+)', t)
        res.append(f"{k}: axioms [{a.group(1) if a else '?'}]; target in statement closure {st.group(1) if st else '?'}; "
                   f"in statement+proof closure {tg.group(1) if tg else '?'}")
    return ' | '.join(res)


cols = ['config', 'group', 'shipped_nanoda', 'status', 'final_outcome', 'final_outcome_time', 'earlier_outcomes', 'nanoda_3a24072_run',
        'rerun_28800s', 'shipped_run', 'f67473b_direct', 'axioms_query', 'axioms_used', 'audit', 'wsl_memory_at_outcome',
        'export_bytes', 'export_sha256', 'deferral_reason', 'evidence'] + (['unofficial_B3', 'official_note'] if UNOFF else [])
rows, problems = [], []
for r in plan:
    c = r['config']; row = dict.fromkeys(cols, '')
    row.update(config=c, group=r['group'], shipped_nanoda=r['shipped_nanoda'])
    rj = os.path.join(D, 'runs', f'{c}.result.json')
    if c in deferred:
        assert not os.path.isfile(rj), c
        row.update(status='DEFERRED', final_outcome='NOT_CHECKED_HERE', deferral_reason=DEFER[c][0], evidence=DEFER[c][1])
        b3 = os.path.join(UNOFF, 'runs', f'{c}.B3.log') if UNOFF else None
        if b3 and os.path.isfile(b3):
            o = [l[9:].strip() for l in open(b3, encoding='utf-8') if l.startswith('OUTCOME:')][-1]
            row['unofficial_B3'] = f'{o} [{rel(b3)}]'
            if o.startswith('pass'):
                row['status'] = 'run here, unofficial tool set B3'
                row['official_note'] = ('official outcome stays NOT_CHECKED_HERE: the official tool set is nanoda 3a24072 (16 MiB) through comparator, '
                    'and that run did not finish (deferral reason). The B3 run is a different nanoda build (37cb87b + nealmcb let/succ patch, 64 MiB), '
                    "run directly on the export (not through comparator); Lean's kernel was not run on this config here.")
        rows.append(row); continue
    d = json.load(open(rj, encoding='utf-8'))
    L = outc.get(c)
    if not L: problems.append(f'{c}: result.json but no outcome line in run.log'); continue
    t, o, sha, nb = L[-1]
    if o != d['outcome']: problems.append(f'{c}: last run.log outcome {o} != result.json {d["outcome"]}')
    if sha not in (None, 'None') and sha != (d.get('export') or {}).get('export_sha256'): problems.append(f'{c}: export sha differs')
    nr = d.get('nanoda_run', {}); rr = d.get('nanoda_run_4x'); sr = d.get('shipped_run', {}); fd = d.get('f67473b_direct')
    aq, ax, nd = axioms(c)
    ev = [rel(os.path.join(D, 'run.log')), rel(rj)] + [rel(x['log'].replace('/mnt/c/Users/Work/dev/siegel', root)) for x in (nr, rr, sr, fd) if x and x.get('log')]
    row.update(status='RESULT', final_outcome=o, final_outcome_time=t,
               earlier_outcomes='; '.join(f'{x[1]} {x[0]}' for x in L[:-1]),
               nanoda_3a24072_run=f"{nr.get('class')} (exit {nr.get('exit')}, {nr.get('wall_s')} s)",
               rerun_28800s=f"{rr['class']} (exit {rr['exit']}, {rr['wall_s']} s)" if rr else '',
               shipped_run=sr.get('class', ''), f67473b_direct=f"{fd['result']} (exit {fd['exit']})" if fd else '',
               axioms_query=f'{aq}, {nd} declarations' if nd is not None else aq, axioms_used=', '.join(sorted(ax)),
               audit=audit(c), wsl_memory_at_outcome=wsl_mem(t),
               export_bytes=(d.get('export') or {}).get('export_bytes') or '', export_sha256=(d.get('export') or {}).get('export_sha256') or '',
               evidence='; '.join(ev))
    rows.append(row)
if problems: sys.exit('PROBLEMS:\n' + '\n'.join(problems))

with open(outs[0], 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, cols, delimiter='\t', lineterminator='\n'); w.writeheader(); w.writerows(rows)

res = [x for x in rows if x['status'] == 'RESULT']
std = {'propext', 'Classical.choice', 'Quot.sound'}
S = []
P = S.append
P('Extended replay, final table of the 227 unreferenced configs (COMPUTED by scripts/extended_final_table.py from the raw records)')
P(f'Command: python -I scripts/extended_final_table.py . {rel(out)}')
P('Official pins: openai/math fd4aeeb, Lean 4.34.1, comparator d03acab, lean4export 076e8e5, nanoda_lib 3a24072 (16 MiB stack).')
P('The f67473b_direct column is UNOFFICIAL (post-fix nanoda on the retained export, outside comparator).')
P('')
P(f"configs 227: results {len(res)}, deferred {len(rows) - len(res)}" + (f" (of which run here on the UNOFFICIAL tool set B3: {sum(1 for x in rows if x['status'] == 'run here, unofficial tool set B3')})" if UNOFF else ''))
P('final outcome (last run.log outcome line; equals result.json for every config): ' + str(dict(collections.Counter(x['final_outcome'] for x in rows))))
P('by group, results / deferred: ' + ', '.join(f"{g} {sum(1 for x in res if x['group'] == g)}/{sum(1 for x in rows if x['group'] == g and x['status'] == 'DEFERRED')}" for g in 'PCUSN'))
P('')
P('Configs with more than one outcome line (the last is final):')
for x in rows:
    if x['earlier_outcomes']: P(f"  {x['config']}: earlier {x['earlier_outcomes']}; final {x['final_outcome']} {x['final_outcome_time']}")
P('')
P('Not ACCEPT_BOTH:')
for x in res:
    if x['final_outcome'] != 'ACCEPT_BOTH':
        P(f"  {x['config']} ({x['group']}): {x['final_outcome']}; 3a24072 run {x['nanoda_3a24072_run']}; 28800 s rerun {x['rerun_28800s'] or '-'}; shipped {x['shipped_run']}; f67473b {x['f67473b_direct'] or '-'}")
P('ACCEPT_BOTH only after the 28800 s rerun: ' + ', '.join(x['config'] for x in res if x['rerun_28800s'].startswith('ACCEPT_BOTH')))
P('')
P('WSL memory when each outcome was recorded: ' + str(dict(collections.Counter(x['wsl_memory_at_outcome'] for x in res))))
P('  outcomes under the ~16 GB default (before 2026-10-21 13:56:21): ' + ', '.join(x['config'] for x in res if x['wsl_memory_at_outcome'] == '16GB-default'))
P('  outcomes under 24 GB (2026-10-21 13:56:21 to 2026-10-22 08:10:32): ' + ', '.join(x['config'] for x in res if x['wsl_memory_at_outcome'] == '24GB'))
P('')
P('Deferred (no result here):')
for x in rows:
    if x['status'] == 'DEFERRED': P(f"  {x['config']} ({x['group']}): {x['deferral_reason']} [{x['evidence']}]")
if UNOFF:
    P('')
    P('Deferred configs run here on the UNOFFICIAL tool set B3 (official outcome unchanged: NOT_CHECKED_HERE):')
    for x in rows:
        if x.get('unofficial_B3'): P(f"  {x['config']}: status '{x['status']}'; B3 {x['unofficial_B3']}")
    P('  ' + 'Note: ' + next((x['official_note'] for x in rows if x.get('official_note')), ''))
P('')
P('#print axioms (runs/<C>-axioms.log, one Lean query per config on the solution theorem(s), in the checker sandbox):')
P(f"  query logs: {sum(1 for x in res if x['axioms_query'].startswith('ok'))} with exit 0 of {len(res)} results; "
  f"declarations queried: {sum(int(re.search(r'(\d+) decl', x['axioms_query']).group(1)) for x in res if 'decl' in x['axioms_query'])}")
P('  axiom sets: ' + str(dict(collections.Counter(x['axioms_used'] for x in res))))
P('  configs using any axiom outside propext, Classical.choice, Quot.sound: ' + str([x['config'] for x in res if set(filter(None, x['axioms_used'].split(', '))) - std]))
P('  (Phase 4.3, phase0-configs-227-summary.txt: no config permits axioms beyond these three.)')
P('Audit queries (placeholder configs, phase4-challenge-placeholders.tsv):')
for x in rows:
    if x['group'] == 'P': P(f"  {x['config']}: {x['audit'] or 'not run (' + (x['deferral_reason'][:40] + '...)' if x['deferral_reason'] else 'no audit log)')}")
open(outs[1], 'w', encoding='utf-8', newline='\n').write('\n'.join(S) + '\n')
print('\n'.join(S))
