"""Extended replay, Phase 6: corpus-416.tsv, summary-416.txt, tables-extended.tex (new files only; refuses to overwrite).

Usage: python -I scripts/extended_tables.py <repo root> <extended-replay dir> [<issue copy>] [--partial]
The 189 referenced rows are taken unchanged from results/2026-10-20-paper-prep-3/corpus-189.tsv (same columns, same
values), with only new columns appended; for them peak memory, build disk and export hash were not logged (MISSING) and
wall time is the logged DURATION_SECONDS of the final corpus nanoda run (results/2026-10-21-paper-prep-4/cost.tsv).
The 227 rows come from <dir>/runs/<config>.result.json (115_classify.py). The issue copy (untracked) is cited by sha256 only.
--partial: allow fewer than 227 results (pilot/progress tables, written with a -partial-<n> suffix).
"""
import csv, hashlib, json, os, re, statistics, sys

sys.stdout.reconfigure(encoding='utf-8')
root, D = sys.argv[1], sys.argv[2]
args = [a for a in sys.argv[3:] if not a.startswith('--')]
issue = args[0] if args else None
partial = '--partial' in sys.argv
R = os.path.join(root, 'results')
rel = lambda p: os.path.relpath(p, root).replace(os.sep, '/')
plan = list(csv.DictReader(open(os.path.join(D, 'phase0-configs-227.tsv'), encoding='utf-8'), delimiter='\t'))
res = {}
for r in plan:
    p = os.path.join(D, 'runs', r['config'] + '.result.json')
    if os.path.isfile(p): res[r['config']] = json.load(open(p, encoding='utf-8'))
n_done = len(res)
if not partial: assert n_done == 227, f'{n_done} results; use --partial'
sfx = '' if n_done == 227 and not partial else f'-partial-{n_done}'
outs = {k: os.path.join(D, f'{k}{sfx}.{e}') for k, e in (('corpus-416', 'tsv'), ('summary-416', 'txt'), ('tables-extended', 'tex'))}
for p in outs.values():
    if os.path.exists(p): sys.exit(f'refusing to overwrite {p}')

t189p = os.path.join(R, '2026-10-20-paper-prep-3', 'corpus-189.tsv')
t189 = list(csv.DictReader(open(t189p, encoding='utf-8'), delimiter='\t'))
cols189 = list(t189[0].keys())
assert len(t189) == 189
ns = {r['config']: r['setting'] or 'absent' for r in csv.DictReader(open(os.path.join(R, '2026-10-21-paper-prep-4', 'nanoda-settings.tsv'), encoding='utf-8'), delimiter='\t') if r['commit'] == 'fd4aeeb'}
cost = {}
for r in csv.DictReader(open(os.path.join(R, '2026-10-21-paper-prep-4', 'cost.tsv'), encoding='utf-8'), delimiter='\t'):
    if r['kind'] == 'replay nanoda-3a24072+Lean' and r['wall_seconds'] != 'MISSING':
        cost[r['config']] = r['wall_seconds']  # the 187 fd4aeeb runs and the 3 pilot runs; one per config
NEW = ['referenced', 'group', 'shipped_nanoda', 'outcome', 'final_label', 'wall_time_s', 'peak_rss_sum_kb', 'peak_hwm_kb', 'build_disk_kb',
       'export_sha256', 'export_bytes', 'axioms']
rows = []
for r in t189:
    lab = 'ACCEPT_BOTH' if r['nanoda_3a24072'] == 'ACCEPT' else ('crash at 3a24072, pass at f67473b' if r['nanoda_f67473b'] == 'ACCEPT' else 'OTHER')
    oc = 'ACCEPT_BOTH' if lab == 'ACCEPT_BOTH' else 'LEAN_ACCEPT_NANODA_CRASH'
    rows.append(dict(r) | {'referenced': 'y', 'group': '', 'shipped_nanoda': ns[r['config']], 'outcome': oc, 'final_label': lab,
                           'wall_time_s': cost.get(r['config'], 'MISSING'), 'peak_rss_sum_kb': 'MISSING', 'peak_hwm_kb': 'MISSING',
                           'build_disk_kb': 'MISSING', 'export_sha256': 'MISSING', 'export_bytes': 'MISSING', 'axioms': 'MISSING'})


def nanoda_cell(j):
    nr = j.get('nanoda_run_4x') or j['nanoda_run']
    c = nr.get('class')
    return {'ACCEPT_BOTH': 'ACCEPT', 'NANODA_CRASH': 'CRASH (' + nr.get('reason', '')[:60] + ')', 'NANODA_UNSUPPORTED': 'UNSUPPORTED',
            'NANODA_REJECT': 'REJECT', 'NOT_RUN': ''}.get(c, c or '')


for r in plan:
    n = r['config']; j = res.get(n)
    if j is None: continue
    nr = j.get('nanoda_run_4x') or j['nanoda_run']
    m = (j.get('mem') or {}).get('nanoda-4x' if j.get('nanoda_run_4x') else 'nanoda') or {}
    sr = j['shipped_run']
    lean = 'ACCEPT' if nr.get('lean_accepts') or sr.get('class') == 'ACCEPT_LEAN' else ({'NOT_RUN': ''}.get(nr.get('class'), 'NOT ACCEPTED'))
    logs = [v['log'] for v in (j['nanoda_run'], j['shipped_run'], j.get('nanoda_run_4x') or {}) if v.get('log')]
    fd = j.get('f67473b_direct')
    ax = j.get('axioms') or {}
    axs = sorted({a for v in ax.get('per_decl', {}).values() for a in v})
    rows.append({c: '' for c in cols189} | {
        'config': n, 'family': '', 'commit_run_at': 'fd4aeeb', 'lean_kernel': lean, 'nanoda_3a24072': nanoda_cell(j),
        'nanoda_f67473b': ('ACCEPT' if fd and fd['result'] == 'pass' else (fd['result'] if fd else '')),
        'log_paths': ';'.join(l.replace('/mnt/c/Users/Work/dev/siegel/', '') for l in logs),
        'binary_hashes': 'nanoda 3a24072 897971d7e99f1ac2... (manifest-extended.json)' + ('; f67473b be15131c173f1b80... (113 log)' if fd else ''),
        'notes': j.get('reason', ''), 'stage': 'extended-replay 2026-10-21',
        'referenced': 'n', 'group': r['group'], 'shipped_nanoda': ns[n], 'outcome': j['outcome'], 'final_label': j['final_label'],
        'wall_time_s': nr.get('wall_s') if nr.get('wall_s') is not None else 'MISSING',
        'peak_rss_sum_kb': m.get('peak_rss_sum_kb') or 'MISSING', 'peak_hwm_kb': m.get('peak_hwm_kb') or 'MISSING',
        'build_disk_kb': j.get('build_disk_kb') if j.get('build_disk_kb') is not None else 'MISSING',
        'export_sha256': (j.get('export') or {}).get('export_sha256') or 'MISSING', 'export_bytes': (j.get('export') or {}).get('export_bytes') or 'MISSING',
        'axioms': ','.join(axs) if ax.get('per_decl') else 'MISSING'})
with open(outs['corpus-416'], 'w', encoding='utf-8', newline='\n') as f:
    f.write('\t'.join(cols189 + NEW) + '\n')
    for r in rows: f.write('\t'.join(str(r[c]) for c in cols189 + NEW) + '\n')

# ---- summary
OUT6 = ['ACCEPT_BOTH', 'LEAN_ACCEPT_NANODA_CRASH', 'LEAN_ACCEPT_NANODA_UNSUPPORTED', 'COMPARATOR_REJECT', 'BUILD_FAIL', 'TIMEOUT']
cnt = lambda rs: {o: sum(1 for r in rs if r['outcome'] == o) for o in OUT6}
ref = [r for r in rows if r['referenced'] == 'y']; unr = [r for r in rows if r['referenced'] == 'n']
S = [f'Extended replay summary{" (PARTIAL: " + str(n_done) + " of 227 unreferenced configs)" if sfx else ""} (COMPUTED; scripts/extended_tables.py)',
     f'Rows: {len(rows)} = {len(ref)} referenced (corpus-189.tsv, unchanged) + {len(unr)} unreferenced (runs/*.result.json).', '',
     'Outcome counts:' + ''.join(f'\t{o}' for o in OUT6) + '\ttotal']
for lab, rs in [('referenced 189', ref), ('unreferenced', unr)] + [(f'  group {g}', [r for r in unr if r['group'] == g]) for g in 'PCUSN'] + [('all', rows)]:
    c = cnt(rs); S.append(f'{lab}' + ''.join(f'\t{c[o]}' for o in OUT6) + f'\t{len(rs)}')
    assert sum(c.values()) == len(rs), lab
for o in OUT6:
    assert cnt(rows)[o] == cnt(ref)[o] + cnt(unr)[o]
    assert cnt(unr)[o] == sum(cnt([r for r in unr if r['group'] == g])[o] for g in 'PCUSN')
assert cnt(ref) == {'ACCEPT_BOTH': 180, 'LEAN_ACCEPT_NANODA_CRASH': 9, 'LEAN_ACCEPT_NANODA_UNSUPPORTED': 0, 'COMPARATOR_REJECT': 0, 'BUILD_FAIL': 0, 'TIMEOUT': 0}
if not sfx: assert len(rows) == 416 and len(ref) + len(unr) == 416
S.append('ASSERTIONS OK: each row sums to its population; groups sum to the unreferenced total; referenced + unreferenced = all;'
         ' referenced counts equal results/2026-10-20-paper-prep-3/summary.txt (180 + 9 = 189).')
fl = {}
for r in rows: fl[r['final_label']] = fl.get(r['final_label'], 0) + 1
S.append('Final labels (all rows): ' + '; '.join(f'{k} {v}' for k, v in sorted(fl.items())))
S.append('')
itxt = open(issue, encoding='utf-8').read() if issue and os.path.isfile(issue) else None
ish = hashlib.sha256(open(issue, 'rb').read()).hexdigest() if itxt is not None else None
S.append(f'Non-ACCEPT_BOTH configs, cross-referenced against ammkrn/nanoda_lib#55 (saved untracked copy, sha256 {ish or "NOT AVAILABLE"}):')
for r in rows:
    if r['outcome'] == 'ACCEPT_BOTH': continue
    hit = (re.search(r'\b' + re.escape(r['config']) + r'\b', itxt) is not None) if itxt is not None else None
    S.append(f'  {r["config"]}\t{"referenced" if r["referenced"] == "y" else "group " + r["group"]}\t{r["outcome"]}\t{r["final_label"]}\t'
             f'named in #55 copy: {hit}\t{(r.get("notes") or "")[:140]}')
S.append('')
num = lambda xs: sorted(int(x) for x in xs if str(x) not in ('MISSING', '', 'None'))


def dist(xs, unit):
    xs = num(xs)
    if not xs: return 'MISSING'
    p90 = xs[min(len(xs) - 1, int(round(0.9 * (len(xs) - 1))))]
    return f'n {len(xs)}; min {xs[0]} {unit}; median {statistics.median(xs):g}; p90 {p90}; max {xs[-1]} {unit}'


S.append('Distributions over the unreferenced rows (nanoda run; 111_memsample.py; INFERRED: the sampler adds ~4-8 s per run, phase1-method-test.txt):')
S.append('  wall time: ' + dist([r['wall_time_s'] for r in unr], 's'))
S.append('  peak RSS sum: ' + dist([r['peak_rss_sum_kb'] for r in unr], 'KB'))
S.append('  peak single-process HWM: ' + dist([r['peak_hwm_kb'] for r in unr], 'KB'))
S.append('  build disk (du of lean/.lake/build after prebuild minus before): ' + dist([r['build_disk_kb'] for r in unr], 'KB'))
S.append('  export bytes: ' + dist([r['export_bytes'] for r in unr], 'B'))
S.append('  referenced 189 wall time (earlier corpus runs, uninstrumented): ' + dist([r['wall_time_s'] for r in ref], 's'))
open(outs['summary-416'], 'w', encoding='utf-8', newline='\n').write('\n'.join(S) + '\n')

# ---- tex
tx = lambda s: str(s).replace('\\', r'\textbackslash{}').replace('_', r'\_').replace('&', r'\&').replace('#', r'\#').replace('%', r'\%')
T = ['% Generated by scripts/extended_tables.py; do not edit by hand.' + (f' PARTIAL ({n_done} of 227).' if sfx else ''),
     r'\begin{tabular}{@{}lrrrrrrr@{}}', r'\toprule',
     r'Population & Both & Crash & Unsupp. & Reject & Build fail & Timeout & Total \\', r'\midrule']
for lab, rs in [('Referenced', ref)] + [(f'Unreferenced, group {g}', [r for r in unr if r['group'] == g]) for g in 'PCUSN'] + [('Unreferenced', unr), ('All config files', rows)]:
    c = cnt(rs); T.append(f'{lab} & ' + ' & '.join(str(c[o]) for o in OUT6) + f' & {len(rs)} \\\\')
T += [r'\bottomrule', r'\end{tabular}', '', r'\begin{tabular}{@{}lllp{6cm}@{}}', r'\toprule', r'Config & Population & Final label & Cause \\', r'\midrule']
for r in rows:
    if r['outcome'] != 'ACCEPT_BOTH':
        T.append(f'{tx(r["config"])} & {"ref." if r["referenced"] == "y" else "group " + r["group"]} & {tx(r["final_label"])} & {tx((r.get("notes") or "")[:90])} \\\\')
T += [r'\bottomrule', r'\end{tabular}']
tm = os.path.join(D, 'timing', 'timing-summary.tsv')
if os.path.isfile(tm):
    tr = list(csv.DictReader(open(tm, encoding='utf-8'), delimiter='\t'))
    T += ['', r'\begin{tabular}{@{}lrrrrr@{}}', r'\toprule', r'Config & off (s) & on (s) & on$-$off (s) & HWM off (MB) & HWM on (MB) \\', r'\midrule']
    for r in tr:
        T.append(f'{tx(r["config"])} & {r["median_off_s"]} & {r["median_on_s"]} & {r["median_diff_s"]} & {r["median_hwm_off_mb"]} & {r["median_hwm_on_mb"]} \\\\')
    T += [r'\bottomrule', r'\end{tabular}']
T += ['', r'\begin{tabular}{@{}ll@{}}', r'\toprule', r'Measure (unreferenced, nanoda run) & Distribution \\', r'\midrule',
      f'Wall time & {tx(dist([r["wall_time_s"] for r in unr], "s"))} \\\\',
      f'Peak single-process memory & {tx(dist([r["peak_hwm_kb"] for r in unr], "KB"))} \\\\',
      f'Peak summed memory & {tx(dist([r["peak_rss_sum_kb"] for r in unr], "KB"))} \\\\',
      f'Build disk & {tx(dist([r["build_disk_kb"] for r in unr], "KB"))} \\\\', r'\bottomrule', r'\end{tabular}']
open(outs['tables-extended'], 'w', encoding='utf-8', newline='\n').write('\n'.join(T) + '\n')
print('\n'.join(S))
