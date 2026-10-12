"""Prune OAI build outputs that no later batch needs (approved by Joe 2026-10-11: run the plan without waiting).

Usage: python3 -I 76_prune.py <lean dir> <toolchain src/lean dir> <schedule json> <batches done> <keep-configs file> [--apply]
- <batches done>: number of remainder batches whose runs, shipped reruns and queries have finished (0 = only the
  headline batch has finished).
- Kept: OAI modules in the import closure of (a) every config listed in <keep-configs file> (one config path per line:
  the pilot configs plus every config whose outcome was not ACCEPT_BOTH, so rule-6 checks can still use its build), and
  (b) every config in the remaining batches.
- Deleted (only with --apply): every file under lean/.lake/build/lib/lean and lean/.lake/build/ir whose path stem is an
  OAI or ComparatorChallenges module outside the kept set. Package builds (.lake/packages) are never touched.
Prints the counts and bytes; with --apply, also the deleted module names.
"""
import json, os, sys

lean, core, sched_path, done, keep_path = sys.argv[1:6]
apply = '--apply' in sys.argv[6:]
done = int(done)
pkgs = os.path.join(lean, '.lake', 'packages')
modfile, modpkg = {}, {}
for base, tops, pkg in [(lean, ['OAI', 'ComparatorChallenges'], 'openai-math'), (core, ['Init', 'Lean', 'Std'], 'core'),
                        (os.path.join(core, 'lake'), ['Lake'], 'core')] + [(os.path.join(pkgs, p), None, p) for p in sorted(os.listdir(pkgs))]:
    tops = tops or [d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d)) and not d.startswith('.')]
    for t in tops:
        for dp, dns, fs in os.walk(os.path.join(base, t)):
            dns[:] = [d for d in dns if not d.startswith('.')]
            for f in fs:
                if f.endswith('.lean'):
                    m = os.path.relpath(os.path.join(dp, f), base)[:-5].replace(os.sep, '.')
                    if m not in modfile:
                        modfile[m] = os.path.join(dp, f); modpkg[m] = pkg
    for f in os.listdir(base):
        if f.endswith('.lean') and f[:-5] not in modfile:
            modfile[f[:-5]] = os.path.join(base, f); modpkg[f[:-5]] = pkg


def strip_comments(src):
    out, i, depth, n = [], 0, 0, len(src)
    while i < n:
        if src.startswith('/-', i): depth += 1; i += 2; continue
        if depth and src.startswith('-/', i): depth -= 1; i += 2; out.append(' '); continue
        if depth: i += 1; continue
        if src.startswith('--', i):
            j = src.find('\n', i); i = n if j < 0 else j; continue
        out.append(src[i]); i += 1
    return ''.join(out)


cache = {}
def imports(m):
    if m in cache: return cache[m]
    p = modfile.get(m)
    if p is None: cache[m] = None; return None
    toks = strip_comments(open(p, encoding='utf-8', errors='replace').read()[:200000]).split()
    out, i = [], 0
    while i < len(toks) and toks[i] in ('module', 'prelude'): i += 1
    while i < len(toks):
        j = i
        while j < len(toks) and toks[j] in ('public', 'meta', 'private'): j += 1
        if j < len(toks) and toks[j] == 'import':
            j += 1
            if j < len(toks) and toks[j] == 'all': j += 1
            out.append(toks[j]); i = j + 1
        else: break
    cache[m] = out; return out


def closure(roots):
    seen, st = set(), list(roots)
    while st:
        x = st.pop()
        if x in seen: continue
        seen.add(x); st += imports(x) or []
    return seen


def need(r):
    c = json.load(open(os.path.join(lean, r), encoding='utf-8'))
    return {m for m in closure([c['solution_module'], c['challenge_module']] + c.get('solution_imports', []))
            if modpkg.get(m) == 'openai-math'}


sched = json.load(open(sched_path))
keep_cfgs = [l.strip() for l in open(keep_path) if l.strip() and not l.startswith('#')]
later = [r for b in sched['batches'][done:] for r in b]
keep = set()
for r in keep_cfgs + later:
    keep |= need(r)

build = os.path.join(lean, '.lake', 'build')
files = {}
for sub in ('lib/lean', 'ir'):
    root = os.path.join(build, sub)
    for dp, dns, fs in os.walk(root):
        rel = os.path.relpath(dp, root)
        for f in fs:
            m = ('' if rel == '.' else rel.replace(os.sep, '.') + '.') + f.split('.')[0]
            files.setdefault(m, []).append(os.path.join(dp, f))
present = {m for m in files if modpkg.get(m) == 'openai-math'}
drop = sorted(present - keep)
nbytes = sum(os.lstat(p).st_blocks * 512 for m in drop for p in files[m])
print(f'batches done {done} of {len(sched["batches"])}; kept configs {len(keep_cfgs)} + later configs {len(later)}; '
      f'kept OAI modules {len(keep)}; present {len(present)}; to prune {len(drop)} modules, {nbytes / 1024**3:.2f} GiB; apply={apply}')
if apply:
    for m in drop:
        for p in files[m]:
            os.remove(p)
        print('pruned ' + m)
