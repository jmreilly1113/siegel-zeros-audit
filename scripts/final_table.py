"""Paper prep 3, Task 1: final corpus table from the raw per-config run logs (read-only on results/).

Usage: python -I scripts/final_table.py <repo root> <tree at fd4aeeb> <tree at adc7f12> <out dir>
  <tree at X>: a directory holding lean/formalization.yaml, lean/docs/*.md and lean/ComparatorChallenges/*
  from `git archive X lean/...` of github.com/openai/math (read-only extracts; nothing is modified).

Reads only per-config logs (no outcomes.tsv, no summary file):
  pilot (adc7f12)       results/2026-10-11-corpus-pilot/<C>-nanoda.log
  headline, remainder   results/2026-10-11-corpus-headline/<C>-{nanoda,shipped}.log, .../2026-10-12-corpus-remainder/batch-*/...
  nanoda f67473b        results/2026-10-20-nanoda-postfix-f67473b/<C>-postfix.log
  SiegelZeros extra     results/2026-10-20-paper-prep/wsl/task4-SiegelZeros-posthoc.log (fd4aeeb, post-hoc)
                        results/2026-10-20-paper-prep-2/wsl/task3-SiegelZeros-adc7f12-shipped.log (adc7f12, full block)
  closure diff          results/2026-10-20-paper-prep-2/wsl/task3-closure-diffstat.txt
Stopped/interrupted logs and the guard-stopped headline attempt dirs are not final runs and are skipped.
Writes corpus-189.tsv, summary.txt, tables.tex into <out dir>.
"""
import collections, json, os, re, sys

root, t_fd, t_adc, out = sys.argv[1:5]
R = os.path.join(root, 'results')
rel = lambda p: os.path.relpath(p, root).replace(os.sep, '/')
H3A = '897971d7e99f1ac2ce3d43131d291a63858badf41cab409f70b99dbd04e0b714'
ISSUE55 = {'DirectedFeedback', 'UniqueGamesTheorem', 'BinPackingGap', 'VertexCover', 'IndependentSets', 'MinUncut',
           'PerfectCompleteness', 'OptimalMaxCut', 'Laughlin', 'LaughlinPlanar', 'LaughlinFock', 'Problem355',
           'KMedianThreshold', 'SquareDifference', 'ContinuumCoulombHardness'}  # nanoda_lib #55 as of 2026-10-19


def yaml_refs(tree):
    t = open(os.path.join(tree, 'lean', 'formalization.yaml'), encoding='utf-8').read()
    e = [m.group(1).split('/')[-1][:-5] for m in re.finditer(r'comparator_config:\s*["\']?([^\s"\']+)', t)]
    return e, set(e)


def families(tree):
    fam = collections.defaultdict(set)
    d = os.path.join(tree, 'lean', 'docs')
    for f in sorted(os.listdir(d)):
        if re.fullmatch(r'\d{3}\.md', f):
            for m in re.finditer(r'ComparatorChallenges/([A-Za-z0-9]+)\.(?:lean|json)', open(os.path.join(d, f), encoding='utf-8').read()):
                fam[m.group(1)].add(f[:3])
    return fam


def challenge_name(tree, cfg):
    c = json.load(open(os.path.join(tree, 'lean', 'ComparatorChallenges', cfg + '.json'), encoding='utf-8'))
    return c['challenge_module'].split('.')[-1]


def parse(path):
    t = open(path, encoding='utf-8', errors='replace').read()
    m = re.search(r'== clone: HEAD ([0-9a-f]{40})', t)
    code = re.findall(r'COMPARATOR EXIT CODE: (\d+)', t)
    nanoda = ''
    if 'Running nanoda kernel' in t or 'nanoda' in os.path.basename(path) or 'postfix' in path:
        if 'nanoda kernel accepts the solution' in t:
            nanoda = 'ACCEPT'
        elif re.search(r'overflowed its stack|fatal runtime error|nanoda exited with 13[4-9]', t):
            nanoda = 'CRASH (stack overflow)'
        elif 'nanoda kernel rejected' in t:
            nanoda = 'REJECT'
    lean = 'ACCEPT' if 'Lean default kernel accepts the solution' in t else ('REJECT' if 'Lean default kernel rejected' in t else '')
    okay = 'Your solution is okay!' in t and code and code[-1] == '0'
    shas = sorted(set(re.findall(r'\b([0-9a-f]{64})\b', t)))
    return dict(commit=m.group(1) if m else '', code=code[-1] if code else '', nanoda=nanoda, lean=lean, okay=okay,
                shas=shas, path=rel(path))


final_pat = re.compile(r'^([A-Za-z0-9]+)-(nanoda|shipped|postfix)\.log$')
runs = collections.defaultdict(list)   # config -> list of (stage, kind, parsed)
stage_dirs = [('pilot', os.path.join(R, '2026-10-11-corpus-pilot')), ('headline', os.path.join(R, '2026-10-11-corpus-headline'))]
rem = os.path.join(R, '2026-10-12-corpus-remainder')
stage_dirs += [('remainder/' + b, os.path.join(rem, b)) for b in sorted(os.listdir(rem)) if b.startswith('batch-')]
stage_dirs += [('postfix-f67473b', os.path.join(R, '2026-10-20-nanoda-postfix-f67473b'))]
for stage, d in stage_dirs:
    for f in sorted(os.listdir(d)):
        m = final_pat.match(f)
        if m:
            runs[m.group(1)].append((stage, m.group(2), parse(os.path.join(d, f))))
extra = {'SiegelZeros': [('paper-prep posthoc (fd4aeeb)', 'nanoda', parse(os.path.join(R, '2026-10-20-paper-prep', 'wsl', 'task4-SiegelZeros-posthoc.log'))),
                         ('paper-prep-2 adc7f12 full block', 'shipped', parse(os.path.join(R, '2026-10-20-paper-prep-2', 'wsl', 'task3-SiegelZeros-adc7f12-shipped.log')))]}
cd = open(os.path.join(R, '2026-10-20-paper-prep-2', 'wsl', 'task3-closure-diffstat.txt'), encoding='utf-8').read()
closure_empty = '(diff --stat exit 0; empty output = no changes)' in cd and not re.search(r'\d+ files? changed', cd)
closure_cfgs = set(re.findall(r'CONFIG ([A-Za-z0-9]+)\.json', cd))

entries_fd, ref_fd = yaml_refs(t_fd)
entries_adc, ref_adc = yaml_refs(t_adc)
fam = families(t_fd)
rows, problems = [], []
cnt = collections.Counter()
for cfg in sorted(ref_fd):
    rs = runs.get(cfg, [])
    corpus = [r for r in rs if not r[0].startswith('postfix')]
    nan = [p for s, k, p in corpus if k == 'nanoda']
    shp = [p for s, k, p in corpus if k == 'shipped']
    pf = [p for s, k, p in rs if k == 'postfix']
    if len(nan) != 1:
        problems.append(f'{cfg}: {len(nan)} final nanoda-enabled corpus logs')
        continue
    n = nan[0]
    commits = sorted({p['commit'] for p in nan + shp if p['commit']})
    lean_ok = n['lean'] == 'ACCEPT' and all(p['lean'] == 'ACCEPT' and p['okay'] for p in shp)
    n3 = n['nanoda']
    nf = pf[0]['nanoda'] if pf else ''
    fams = ','.join(sorted(fam.get(challenge_name(t_fd, cfg), set()) | fam.get(cfg, set()))) or '(none linked)'
    stage = [s for s, k, p in corpus if k == 'nanoda'][0]
    hashes = [f'nanoda 3a24072: not recorded in the per-config log (official binary sha256 {H3A[:16]}... per results/2026-10-11-corpus-provenance.txt and the 2026-10-20 logs)']
    if pf:
        hashes.append('nanoda f67473b: ' + ', '.join(s for s in pf[0]['shas'] if s.startswith('be15131c')))
    notes = []
    if cfg in ('SiegelZeros', 'QuasiRiemannHypothesis'):
        notes.append(f'run at adc7f12 (pilot); paper-prep-2 Task 3: git diff --stat adc7f12..fd4aeeb over this config\'s closure is '
                     f'{"EMPTY" if closure_empty and cfg in closure_cfgs else "NOT CHECKED"} (results/2026-10-20-paper-prep-2/wsl/task3-closure-diffstat.txt, controls in ../task3-diffstat-controls.txt)')
    if cfg == 'SiegelZeros':
        for s, k, p in extra['SiegelZeros']:
            notes.append(f'{s}: commit {p["commit"][:7]}, Lean {p["lean"] or "-"}, nanoda {p["nanoda"] or "not enabled"}, exit {p["code"]} ({p["path"]})')
    if n3 != 'ACCEPT' and nf == 'ACCEPT':
        notes.append(f'in nanoda_lib #55: {"yes" if cfg in ISSUE55 else "no"}')
    if not lean_ok:
        problems.append(f'{cfg}: Lean kernel not accepted in every final run')
    cls = 'nanoda 3a24072 accepts' if n3 == 'ACCEPT' else ('crash at 3a24072, pass at f67473b' if n3.startswith('CRASH') and nf == 'ACCEPT' else 'OTHER')
    cnt['Lean accepts'] += lean_ok
    cnt[cls] += 1
    rows.append([cfg, fams, ','.join(c[:7] for c in commits), 'ACCEPT' if lean_ok else 'NOT ACCEPT', n3, nf,
                 '; '.join([n['path']] + [p['path'] for p in shp] + [p['path'] for p in pf]), ' | '.join(hashes), ' | '.join(notes), stage])

os.makedirs(out, exist_ok=True)
with open(os.path.join(out, 'corpus-189.tsv'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('config\tfamily\tcommit_run_at\tlean_kernel\tnanoda_3a24072\tnanoda_f67473b\tlog_paths\tbinary_hashes\tnotes\tstage\n')
    for r in rows:
        f.write('\t'.join(r) + '\n')

nine = [r for r in rows if r[4].startswith('CRASH')]
S = []
S.append('Paper prep 3, Task 1: final corpus table (COMPUTED from raw per-config logs by scripts/final_table.py)')
S.append(f'Population: configs referenced by lean/formalization.yaml at fd4aeeb: {len(ref_fd)} (from {len(entries_fd)} main_results entries).')
S.append(f'Rows written: {len(rows)}; problems: {problems or "none"}')
S.append('')
S.append('Counts over the referenced configs:')
S.append(f'  Lean kernel accepts (every final run of the config): {cnt["Lean accepts"]}')
S.append(f'  nanoda 3a24072 accepts: {cnt["nanoda 3a24072 accepts"]}  (of which run at adc7f12 in the pilot: '
         f'{sum(1 for r in rows if r[2] == "adc7f12" and r[4] == "ACCEPT")})')
S.append(f'  crash at nanoda 3a24072, pass at nanoda f67473b: {cnt["crash at 3a24072, pass at f67473b"]}')
S.append(f'  other: {cnt["OTHER"]}')
assert cnt['Lean accepts'] == len(ref_fd) == 189, 'Lean count != 189'
assert cnt['nanoda 3a24072 accepts'] + cnt['crash at 3a24072, pass at f67473b'] == 189 and cnt['OTHER'] == 0, 'nanoda classes do not sum to 189'
S.append(f'  ASSERTION OK: Lean accepts = 189; nanoda 3a24072 accepts + (crash at 3a24072, pass at f67473b) = '
         f'{cnt["nanoda 3a24072 accepts"]} + {cnt["crash at 3a24072, pass at f67473b"]} = 189.')
S.append('  Commit split: ' + ', '.join(f'{k}: {v}' for k, v in sorted(collections.Counter(r[2] for r in rows).items())))
S.append('  Binary hashes: per-config corpus logs do not record the nanoda 3a24072 hash; the f67473b logs record '
         'be15131c173f1b803e3e51239604dbf44489d8be25fe675419ba9a0c9b47ada5 in all 9.')
S.append('')
S.append('Unreferenced (not in the 189):')
ed = [p for s, k, p in runs.get('EditApproximation', []) if k == 'nanoda']
el = os.path.join(t_adc, 'lean', 'ComparatorChallenges', 'EditApproximation.lean')
nlines = sum(1 for _ in open(el, encoding='utf-8'))
for p in ed:
    S.append(f'  EditApproximation: commit {p["commit"][:7]}, Lean {p["lean"]}, nanoda 3a24072 {p["nanoda"]}, exit {p["code"]} ({p["path"]}); '
             f'challenge file ComparatorChallenges/EditApproximation.lean: {nlines} lines at adc7f12 '
             f'({"same" if sum(1 for _ in open(os.path.join(t_fd, "lean", "ComparatorChallenges", "EditApproximation.lean"), encoding="utf-8")) == nlines else "different"} at fd4aeeb); '
             f'referenced by the yaml at adc7f12: {"EditApproximation" in ref_adc}, at fd4aeeb: {"EditApproximation" in ref_fd}')
S.append('')
fd_run = {c for c, rs in runs.items() if any(p['commit'].startswith('fd4aeeb') and k in ('nanoda', 'shipped') and not s.startswith('postfix') for s, k, p in rs)}
any_stage = {c for c, rs in runs.items() if any(not s.startswith('postfix') and k in ('nanoda', 'shipped') for s, k, p in rs)}
S.append('Reconciliation with other figures in circulation:')
S.append(f'  178 = distinct configs referenced by the yaml at adc7f12; 185 = its main_results entries (configs vs entries): '
         f'{len(ref_adc)} / {len(entries_adc)}.')
S.append(f'  187 = configs replayed at fd4aeeb (headline + remainder): {len(fd_run)}; the two others of the 189 '
         f'({", ".join(sorted(ref_fd - fd_run))}) ran at adc7f12.')
S.append(f'  190 = configs run in any stage: {len(any_stage)} = 189 referenced + {", ".join(sorted(any_stage - ref_fd))}.')
S.append(f'  178 ACCEPT_BOTH (corpus table, nanoda 3a24072 at fd4aeeb) = {sum(1 for r in rows if r[4] == "ACCEPT" and "fd4aeeb" in r[2])} '
         f'here; with the 2 pilot configs, nanoda 3a24072 accepts {cnt["nanoda 3a24072 accepts"]} of the 189.')
open(os.path.join(out, 'summary.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(S) + '\n')

tex = [r'% Generated by scripts/final_table.py; do not edit by hand.',
       r'\begin{tabular}{@{}lr@{}}', r'\toprule', r'Configs referenced by \texttt{formalization.yaml} at fd4aeeb & ' + str(len(ref_fd)) + r' \\',
       r'\midrule',
       r'Lean kernel accepts & ' + str(cnt['Lean accepts']) + r' \\',
       r'nanoda 3a24072 accepts & ' + str(cnt['nanoda 3a24072 accepts']) + r' \\',
       r'\quad of which run at adc7f12 (pilot) & ' + str(sum(1 for r in rows if r[2] == 'adc7f12' and r[4] == 'ACCEPT')) + r' \\',
       r'crash at nanoda 3a24072, pass at f67473b & ' + str(cnt['crash at 3a24072, pass at f67473b']) + r' \\',
       r'\bottomrule', r'\end{tabular}', '',
       r'\begin{tabular}{@{}lccc@{}}', r'\toprule', r'Config & In nanoda \#55 & nanoda 3a24072 & nanoda f67473b \\', r'\midrule']
for r in nine:
    tex.append(f'{r[0]} & {"yes" if r[0] in ISSUE55 else "no"} & crash (stack overflow) & {r[5].lower()} \\\\')
tex += [r'\bottomrule', r'\end{tabular}']
open(os.path.join(out, 'tables.tex'), 'w', encoding='utf-8', newline='\n').write('\n'.join(tex) + '\n')
print('\n'.join(S))
