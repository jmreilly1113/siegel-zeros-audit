"""Classify headline-batch runs from their logs (75_headline_batch.sh). Usage: python3 -I 75_classify.py <results dir>

Per run (raw class, from fixed log lines; the decisive line is printed as evidence):
  TIMEOUT          exit code 124 or 137 (coreutils timeout), prebuild or comparator
  BUILD_FAIL       prebuild exited nonzero, or the comparator log has a Lean/Lake `error:` before any kernel ran
  AXIOM_VIOLATION  "Illegal axiom detected"
  NANODA_UNSUPPORTED  nanoda ran, did not accept, and the log says unsupported / not supported / unimplemented
  NANODA_REJECT    nanoda ran and did not accept (any other reason)
  ACCEPT_BOTH      nanoda run: both kernels accept, "Your solution is okay!", exit 0
  ACCEPT_LEAN      shipped run (nanoda disabled): Lean kernel accepts, "Your solution is okay!", exit 0
  GUARD_STOPPED    no exit code in the log and the batch was stopped by a guard (not a proof outcome)
  OTHER            anything else, including a nanoda crash (stack overflow, abort) that is not a verdict on the proof
Per config: the nanoda run's class, except ACCEPT_LEAN_ONLY when the nanoda run is not ACCEPT_BOTH but the shipped
run is ACCEPT_LEAN; a prebuild TIMEOUT/BUILD_FAIL is reported when there is no comparator run.
"""
import os, re, sys

out = sys.argv[1]


def code(txt, key):
    m = re.findall(key + r' EXIT CODE: (\d+)', txt)
    return int(m[-1]) if m else None


def line(txt, pat):
    for l in txt.splitlines():
        if re.search(pat, l): return l.strip()[:200]
    return ''


def run_class(path, nanoda):
    if not os.path.isfile(path): return 'NOT_RUN', ''
    t = open(path, encoding='utf-8', errors='replace').read()
    c = code(t, 'COMPARATOR')
    ok = 'Your solution is okay!' in t and c == 0
    if c is None:  # the run did not finish (killed): never a verdict
        if os.path.isfile(os.path.join(out, 'GUARD_STOPPED.txt')) or os.path.isfile('/home/checker/corpus/GUARD_STOPPED'):
            return 'GUARD_STOPPED', 'no COMPARATOR EXIT CODE line; guard stop'
        return 'OTHER', 'no COMPARATOR EXIT CODE line (run did not finish)'
    if c in (124, 137): return 'TIMEOUT', f'COMPARATOR EXIT CODE: {c}'
    if 'Illegal axiom detected' in t: return 'AXIOM_VIOLATION', line(t, 'Illegal axiom detected')
    if nanoda and 'Running nanoda kernel' in t and 'nanoda kernel accepts the solution' not in t             and re.search(r'overflowed its stack|fatal runtime error|nanoda exited with 13[4-9]', t):
        return 'OTHER', 'nanoda crashed (' + (line(t, r'overflowed its stack|fatal runtime error') or line(t, 'nanoda exited')) +             ('); Lean kernel accepted in the same run' if 'Lean default kernel accepts the solution' in t else ')')
    if nanoda and 'Running nanoda kernel' in t and 'nanoda kernel accepts the solution' not in t:
        e = line(t, r'(?i)unsupported|not supported|unimplemented')
        if e: return 'NANODA_UNSUPPORTED', e
        return 'NANODA_REJECT', line(t, r'(?i)nanoda.*(reject|error|fail)|error') or line(t, 'Running nanoda kernel')
    if nanoda and ok and 'nanoda kernel accepts the solution' in t and 'Lean default kernel accepts the solution' in t:
        return 'ACCEPT_BOTH', 'nanoda kernel accepts; Lean default kernel accepts; Your solution is okay!; exit 0'
    if not nanoda and ok and 'Lean default kernel accepts the solution' in t:
        return 'ACCEPT_LEAN', 'Lean default kernel accepts; Your solution is okay!; exit 0'
    if 'Running nanoda kernel' not in t and 'Lean default kernel' not in t and re.search(r'(?m)^error|: error:|error: ', t):
        return 'BUILD_FAIL', line(t, r'^error|: error:|error: ')
    return 'OTHER', line(t, r'(?i)error|exception|fail') or f'COMPARATOR EXIT CODE: {c}'


def prebuild_class(path):
    if not os.path.isfile(path): return 'NOT_RUN', ''
    t = open(path, encoding='utf-8', errors='replace').read()
    c = code(t, 'SANDBOX')
    secs = line(t, 'PREBUILD_SECONDS')
    if c in (124, 137): return 'TIMEOUT', f'SANDBOX EXIT CODE: {c}; {secs}'
    if c == 0: return 'OK', secs
    return 'BUILD_FAIL', (line(t, r'error') or f'SANDBOX EXIT CODE: {c}') + f'; {secs}'


plan = [l.rstrip('\n').split('\t') for l in open(os.path.join(out, 'plan.tsv'))][1:]
print('config\tin_sample\tprebuild\tnanoda_run\tshipped_run\tconfig_outcome\tevidence')
for n, tg, ins in plan:
    pb, pbe = prebuild_class(os.path.join(out, n + '.prebuild.log'))
    nr, nre = run_class(os.path.join(out, n + '-nanoda.log'), True)
    sr, sre = run_class(os.path.join(out, n + '-shipped.log'), False)
    if nr == 'NOT_RUN':
        oc, ev = (pb, pbe) if pb != 'OK' else ('NOT_RUN', '')
    elif nr != 'ACCEPT_BOTH' and sr == 'ACCEPT_LEAN':
        oc, ev = 'ACCEPT_LEAN_ONLY', f'nanoda: {nre} | shipped: {sre}'
    else:
        oc, ev = nr, nre + (f' | shipped: {sr}: {sre}' if sr != 'NOT_RUN' else '')
    print(f'{n}\t{ins}\t{pb}\t{nr}\t{sr}\t{oc}\t{ev}')
for f in sorted(os.listdir(out)):
    if f.endswith('-shipped.log') and f[:-12] not in {p[0] for p in plan}:
        sr, sre = run_class(os.path.join(out, f), False)
        print(f'{f[:-12]}\tTrue\t(pilot build)\t(pilot: see 2026-10-11-corpus-pilot)\t{sr}\t{sr}\t{sre}')
