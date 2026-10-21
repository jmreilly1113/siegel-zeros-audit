"""Paper prep Task 3: classify the nanoda reruns of the 9 non-ACCEPT_BOTH configs (read-only on results/).

Usage: python -I scripts/paperprep_task3.py <repo root>
Reads results/2026-10-20-paper-prep/wsl/task3-<config>-{comparator-bigenv,nanoda-direct}.log and the original
corpus logs. Classes (Joe's brief): RESOURCE (nanoda passes now), UNSUPPORTED (nanoda says unsupported),
GENUINE_REJECT (nanoda finished and rejected a declaration). A run that still dies with a stack-overflow abort fits
none of the three; it is reported as NOT_RESOLVED_CRASH, never folded into GENUINE_REJECT.
"""
import glob, os, re, sys

root = sys.argv[1]
W = os.path.join(root, 'results', '2026-10-20-paper-prep', 'wsl')
cfgs = ['OptimalMaxCut', 'UniqueGamesTheorem', 'VertexCover', 'KaplanskyFinitelyPresented', 'GroupRingDeterminant',
        'Laughlin', 'BinPackingGap', 'IndependentSets', 'PerfectCompleteness']
issue55 = {'DirectedFeedback', 'UniqueGamesTheorem', 'BinPackingGap', 'VertexCover', 'IndependentSets', 'MinUncut',
           'PerfectCompleteness', 'OptimalMaxCut', 'Laughlin', 'LaughlinPlanar', 'LaughlinFock', 'Problem355',
           'KMedianThreshold', 'SquareDifference', 'ContinuumCoulombHardness'}  # results/2026-10-19-external-checks-comparison.txt:45-48


def run(path, comparator):
    t = open(path, encoding='utf-8', errors='replace').read()
    st = re.search(r'^INNER ulimit -s: (\S+);.*RUST_MIN_STACK=(\S+)', t, re.M)
    settings = f'ulimit -s {st.group(1)}, RUST_MIN_STACK={st.group(2)}' if st else 'settings line missing'
    code = re.findall(r'COMPARATOR EXIT CODE: (\d+)', t)
    code = int(code[-1]) if code else None
    dur = re.findall(r'DURATION_SECONDS: (\d+)', t)
    crash = re.search(r"thread '([^']+)' \(\d+\) has overflowed its stack", t)
    lean_ok = 'Lean default kernel accepts the solution' in t
    if comparator and 'nanoda kernel accepts the solution' in t and code == 0:
        c = 'RESOURCE'
    elif not comparator and code == 0 and not crash:
        c = 'RESOURCE'
    elif re.search(r'(?i)unsupported|not supported|unimplemented', t):
        c = 'UNSUPPORTED'
    elif crash or 'fatal runtime error: stack overflow' in t:
        c = 'NOT_RESOLVED_CRASH'
    elif code in (124, 137):
        c = 'TIMEOUT'
    else:
        c = 'GENUINE_REJECT?'
    ev = (f"{crash.group(1)} overflowed its stack" if crash else '') + (f'; exit {code}' if code is not None else '; no exit line') \
        + (f'; {dur[-1]} s' if dur else '') + ('; Lean kernel accepts' if comparator and lean_ok else '')
    return c, settings, ev


def original(cfg):
    for p in glob.glob(os.path.join(root, 'results', '2026-10-1[12]-corpus-*', '**', cfg + '-nanoda.log'), recursive=True):
        t = open(p, encoding='utf-8', errors='replace').read()
        m = re.search(r"thread '([^']+)' \(\d+\) has overflowed its stack", t)
        return os.path.relpath(p, root).replace(os.sep, '/'), ('stack overflow (' + m.group(1) + ')' if m else 'see log')
    return '-', '-'


print('config\tcomparator_run\tdirect_run\tclass\tsettings_in_effect\tcomparator_evidence\tdirect_evidence\tin_issue55\toriginal_run')
stop = False
for cfg in cfgs:
    a = run(os.path.join(W, f'task3-{cfg}-comparator-bigenv.log'), True)
    b = run(os.path.join(W, f'task3-{cfg}-nanoda-direct.log'), False)
    cls = a[0] if a[0] == b[0] else f'{a[0]}/{b[0]}'
    stop |= 'GENUINE' in cls
    o = original(cfg)
    print(f'{cfg}\t{a[0]}\t{b[0]}\t{cls}\t{a[1]} | {b[1]}\t{a[2]}\t{b[2]}\t{cfg in issue55}\t{o[0]}: {o[1]}')
print('STOP: a possible GENUINE_REJECT is present' if stop else 'no GENUINE_REJECT: no run finished with a rejection; every non-pass is a stack-overflow abort')
