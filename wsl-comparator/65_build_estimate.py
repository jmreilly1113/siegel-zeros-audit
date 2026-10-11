"""Corpus checks, phase 4 estimate (read-only): what a full build would compile.

For the 405 configs (and separately the 178 referenced by formalization.yaml): the union of import closures of
solution modules (plus solution_imports) and challenge modules, split by package, and how many of those
modules already have an .olean in this clone. Same header-only import parser as 50_module_closure.py.
Usage: python3 -I 65_build_estimate.py <openai/math lean dir> <toolchain src/lean dir>
"""
import glob, json, os, sys
from collections import Counter
import yaml

lean, core = sys.argv[1], sys.argv[2]
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
        seen.add(x)
        st += imports(x) or []
    return seen


def olean_exists(m):
    pkg = modpkg.get(m)
    if pkg == 'core': return True
    base = lean if pkg == 'openai-math' else os.path.join(pkgs, pkg)
    return os.path.isfile(os.path.join(base, '.lake', 'build', 'lib', 'lean', *m.split('.')) + '.olean')


y = yaml.safe_load(open(os.path.join(lean, 'formalization.yaml'), encoding='utf-8'))
ref = {e['comparator_config'] for e in y['status']['main_results']}
cfgs = {os.path.relpath(p, lean).replace(os.sep, '/'): json.load(open(p, encoding='utf-8'))
        for p in sorted(glob.glob(os.path.join(lean, 'ComparatorChallenges', '*.json')))}
for label, sel in (('all 405 configs', set(cfgs)), ('178 yaml-referenced configs', ref)):
    union, per_cfg = set(), {}
    for r in sel:
        c = cfgs[r]
        s = closure([c['solution_module'], c['challenge_module']] + c.get('solution_imports', []))
        per_cfg[r] = s; union |= s
    known = {m for m in union if m in modfile}
    unknown = union - known
    by = Counter(modpkg[m] for m in known if modpkg[m] != 'core')
    built = Counter(modpkg[m] for m in known if modpkg[m] != 'core' and olean_exists(m))
    tot = sum(by.values()); tb = sum(built.values())
    print(f'\n== {label}: union of closures {len(union)} modules (non-core {tot}; unresolved {len(unknown)}); already built {tb}; to build {tot - tb}')
    for p, n in by.most_common():
        print(f'  {p:<30} {n:>6} modules, built {built.get(p, 0):>6}, to build {n - built.get(p, 0):>6}')
    sizes = sorted((sum(1 for m in s if modpkg.get(m) == 'openai-math'), r) for r, s in per_cfg.items())
    print(f'  OAI modules per config: min {sizes[0]}, median {sizes[len(sizes)//2]}, max {sizes[-1]}')
    if unknown:
        print(f'  unresolved examples: {sorted(unknown)[:8]}')
