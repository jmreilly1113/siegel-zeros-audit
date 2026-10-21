"""Extended replay: classify ONE config from its logs and write <runs>/<config>.result.json. Run after every step.

Usage: python3 -I 115_classify.py <runs dir> <config> <group> <shipped nanoda setting>
Exit code 0 = final result written (or already present: never rewritten); 2 = not final (a run has no exit-code line:
stopped; rerun on resume); 4 = crash with a retained export: run the f67473b direct check, then classify again; 3 = STOP
(condition (a) or (b); <runs>/STOP.txt written). Outcomes (exactly one):
  ACCEPT_BOTH | LEAN_ACCEPT_NANODA_CRASH | LEAN_ACCEPT_NANODA_UNSUPPORTED | COMPARATOR_REJECT (reason) | BUILD_FAIL | TIMEOUT
STOP (a): the Lean kernel accepts and nanoda rejects with an error that is neither a crash nor a resource failure.
STOP (b): Comparator accepted (outcome ACCEPT_BOTH or LEAN_ACCEPT_*) and #print axioms of a theorem_names/definition_names
entry lists anything beyond propext, Classical.choice, Quot.sound, or sorryAx.
Run-level rules follow 75_classify.py (same log lines); the crash signature list adds Rust panics and allocation failures.
"""
import json, os, re, sys

runs, n, group, shipped = sys.argv[1:5]
STD = {'propext', 'Classical.choice', 'Quot.sound'}
CRASH = r'overflowed its stack|fatal runtime error|nanoda exited with 13[4-9]|panicked at|memory allocation of \d+ bytes failed|out of memory|Cannot allocate memory'
P = lambda s: os.path.join(runs, n + s)
rd = lambda p: open(p, encoding='utf-8', errors='replace').read() if os.path.isfile(p) else None


def code(t, key):
    m = re.findall(key + r' EXIT CODE: (\d+)', t or '')
    return int(m[-1]) if m else None


def first(t, pat):
    for l in (t or '').splitlines():
        if re.search(pat, l): return l.strip()[:240]
    return ''


def mem(path):
    try:
        j = json.load(open(path))
        return {k: j.get(k) for k in ('peak_rss_sum_kb', 'peak_hwm_kb', 'peak_hwm_proc', 'samples', 'unit_cgroup', 'error')}
    except (OSError, ValueError):
        return None


def run(path, nanoda):
    t = rd(path)
    if t is None: return {'class': 'NOT_RUN'}
    c = code(t, 'COMPARATOR'); d = first(t, 'DURATION_SECONDS'); r = {'log': path, 'exit': c, 'wall_s': int(d.split()[-1]) if d else None}
    lean_ok = 'Lean default kernel accepts the solution' in t
    nan_ran = 'Running nanoda kernel' in t
    nan_ok = 'nanoda kernel accepts the solution' in t
    ok = 'Your solution is okay!' in t and c == 0
    r.update(lean_accepts=lean_ok, nanoda_ran=nan_ran, nanoda_accepts=nan_ok)
    if c is None: r['class'] = 'UNFINISHED'
    elif c in (124, 137): r['class'] = 'TIMEOUT'
    elif 'Illegal axiom detected' in t: r.update({'class': 'COMPARATOR_REJECT', 'reason': 'disallowed axiom: ' + first(t, 'Illegal axiom detected')})
    elif 'do not match' in t and not ok:
        r.update({'class': 'COMPARATOR_REJECT', 'reason': 'statement mismatch: ' + first(t, 'do not match')})
    elif nanoda and nan_ran and not nan_ok and re.search(CRASH, t):
        r.update({'class': 'NANODA_CRASH', 'reason': first(t, CRASH)})
    elif nanoda and nan_ran and not nan_ok and re.search(r'(?i)unsupported|not supported|unimplemented', t):
        r.update({'class': 'NANODA_UNSUPPORTED', 'reason': first(t, r'(?i)unsupported|not supported|unimplemented')})
    elif nanoda and nan_ran and not nan_ok:
        r.update({'class': 'NANODA_REJECT', 'reason': first(t, r'(?i)nanoda.*(reject|error|fail)|error') or 'nanoda did not accept'})
    elif nanoda and ok and nan_ok and lean_ok: r['class'] = 'ACCEPT_BOTH'
    elif not nanoda and ok and lean_ok: r['class'] = 'ACCEPT_LEAN'
    elif not nan_ran and not lean_ok and re.search(r'(?m)^error|: error:|error: ', t):
        r.update({'class': 'BUILD_FAIL', 'reason': first(t, r'^error|: error:|error: ')})
    else: r.update({'class': 'COMPARATOR_REJECT', 'reason': 'other: ' + (first(t, r'(?i)error|exception|fail|reject') or f'exit {c}')})
    return r


if os.path.isfile(P('.result.json')):
    print(f'{n}: result.json exists; not rewritten'); sys.exit(0)
res = {'config': n, 'group': group, 'shipped_nanoda': shipped}
pb = rd(P('.prebuild.log')); pb4 = rd(P('.prebuild-4x.log'))
res['prebuild'] = {'exit': code(pb, 'SANDBOX'), 'seconds': (first(pb, 'PREBUILD_SECONDS').split() or [None])[-1]}
if pb4: res['prebuild_4x'] = {'exit': code(pb4, 'SANDBOX'), 'seconds': (first(pb4, 'PREBUILD_SECONDS').split() or [None])[-1]}
try:
    dk = dict(l.strip().split('\t') for l in open(P('.disk.tsv')) if '\t' in l)
    res['build_disk_kb'] = int(dk['build_kb_after_prebuild']) - int(dk['build_kb_before'])
    res['disk'] = dk
except (OSError, KeyError, ValueError):
    res['build_disk_kb'] = None
nr, sr, n4 = run(P('-nanoda.log'), True), run(P('-shipped.log'), False), run(P('-nanoda-4x.log'), True)
res['nanoda_run'], res['shipped_run'] = nr, sr
if n4['class'] != 'NOT_RUN': res['nanoda_run_4x'] = n4
res['mem'] = {k: mem(P(f'-{k}.mem.json')) for k in ('nanoda', 'shipped', 'nanoda-4x') if os.path.isfile(P(f'-{k}.mem.json'))}
try:
    ex = json.load(open(P('-nanoda.mem.json'))).get('export') or {}
    res['export'] = {k: ex.get(k) for k in ('export_sha256', 'export_bytes', 'copied_to', 'error')}
except (OSError, ValueError):
    res['export'] = None


def final():
    pbc = res['prebuild']['exit']
    if pbc is None and pb is not None: return None  # prebuild stopped
    if pbc in (124, 137):
        if not pb4: return ('TIMEOUT', 'prebuild timed out at 14400 s (4x rerun pending)')
        if res['prebuild_4x']['exit'] in (124, 137): return ('TIMEOUT', 'prebuild timed out at 14400 s and at 57600 s')
        if res['prebuild_4x']['exit'] != 0: return ('BUILD_FAIL', 'prebuild 4x: ' + first(pb4, r'error'))
    elif pbc is not None and pbc != 0: return ('BUILD_FAIL', first(pb, r'error:') or first(pb, r'error') or f'SANDBOX EXIT CODE {pbc}')
    if pb is None: return None
    r = n4 if nr['class'] == 'TIMEOUT' and n4['class'] != 'NOT_RUN' else nr
    if r['class'] in ('NOT_RUN', 'UNFINISHED'): return None
    if nr['class'] == 'TIMEOUT' and n4['class'] == 'NOT_RUN': return ('TIMEOUT', 'comparator timed out at 7200 s (4x rerun pending)')
    if r['class'] == 'TIMEOUT': return ('TIMEOUT', 'comparator timed out at 7200 s and at 28800 s')
    if r['class'] == 'ACCEPT_BOTH': return ('ACCEPT_BOTH', '')
    if sr['class'] in ('NOT_RUN', 'UNFINISHED') and r['class'] in ('NANODA_CRASH', 'NANODA_UNSUPPORTED', 'NANODA_REJECT'): return None
    lean = r.get('lean_accepts') or sr['class'] == 'ACCEPT_LEAN'
    if r['class'] == 'NANODA_CRASH' and lean: return ('LEAN_ACCEPT_NANODA_CRASH', r['reason'])
    if r['class'] == 'NANODA_UNSUPPORTED' and lean: return ('LEAN_ACCEPT_NANODA_UNSUPPORTED', r['reason'])
    if r['class'] == 'NANODA_REJECT' and lean: return ('STOP_A', r['reason'])
    if r['class'] in ('NANODA_CRASH', 'NANODA_UNSUPPORTED', 'NANODA_REJECT'):
        return ('COMPARATOR_REJECT', f'other: Lean kernel did not accept (shipped run {sr["class"]}: {sr.get("reason", "")}); nanoda {r["class"]}')
    return (r['class'], r.get('reason', ''))


f = final()
if f is None:
    json.dump(res | {'final': False}, open(P('.partial.json'), 'w'), indent=1); sys.exit(2)
res['outcome'], res['reason'] = f
# f67473b direct rerun of a crash, on the retained export
fd = rd(P('-f67473b-direct.log'))
if res['outcome'] == 'LEAN_ACCEPT_NANODA_CRASH' and fd is None and (res.get('export') or {}).get('copied_to') and (res['export'] or {}).get('export_sha256'):
    json.dump(res | {'final': False, 'pending': 'f67473b direct run'}, open(P('.partial.json'), 'w'), indent=1); sys.exit(4)
if fd is not None:
    c = code(fd, 'NANODA')
    res['f67473b_direct'] = {'log': P('-f67473b-direct.log'), 'exit': c, 'result': 'pass' if c == 0 else ('fail: ' + (first(fd, CRASH) or first(fd, r'(?i)error|panic') or f'exit {c}') if c is not None else 'UNFINISHED')}
res['final_label'] = ('crash at 3a24072, pass at f67473b' if res.get('f67473b_direct', {}).get('result') == 'pass' else
                      'crash at 3a24072, fail at f67473b' if 'f67473b_direct' in res else res['outcome']) if res['outcome'] == 'LEAN_ACCEPT_NANODA_CRASH' else res['outcome']
# #print axioms (Phase 4.1)
ax = rd(P('-axioms.log'))
axr = {'log': P('-axioms.log'), 'exit': code(ax, 'SANDBOX'), 'per_decl': {}}
if ax:
    for m in re.finditer(r"'([^']+)' depends on axioms: \[([^\]]*)\]", ax, re.S):
        axr['per_decl'][m.group(1)] = [a.strip() for a in m.group(2).replace('\n', ' ').split(',') if a.strip()]
    for m in re.finditer(r"'([^']+)' does not depend on any axioms", ax):
        axr['per_decl'][m.group(1)] = []
res['axioms'] = axr
for side in ('challenge', 'solution'):
    a = rd(P(f'-audit-{side}.log'))
    if a is not None:
        res[f'audit_{side}'] = {'log': P(f'-audit-{side}.log'), 'exit': code(a, 'SANDBOX'), 'lines': [l.strip() for l in a.splitlines() if 'AUDIT' in l][:40]}
stop = []
if res['outcome'] == 'STOP_A':
    stop.append(f'(a) Lean kernel accepts, nanoda rejects without a crash signature: {res["reason"]}')
accepted = res['outcome'] == 'ACCEPT_BOTH' or res['outcome'].startswith('LEAN_ACCEPT_')
if accepted:
    for d, axs in axr['per_decl'].items():
        bad = sorted(set(axs) - STD)
        if bad: stop.append(f'(b) {d} depends on {bad}')
    if not axr['per_decl']: res['axioms_note'] = 'no #print axioms output parsed (query exit %s)' % axr['exit']
res['final'] = True
json.dump(res, open(P('.result.json'), 'w'), indent=1)
if os.path.isfile(P('.partial.json')): os.remove(P('.partial.json'))
if stop:
    open(os.path.join(runs, 'STOP.txt'), 'a').write(f'{n}: ' + '; '.join(stop) + '\n'); sys.exit(3)
sys.exit(0)
