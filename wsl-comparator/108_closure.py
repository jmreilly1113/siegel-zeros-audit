"""Read-only: repo files in the import closure of comparator configs (parser copied from 50_module_closure.py).

Usage: python3 -I 108_closure.py <openai/math lean dir> <config.json> [<config.json> ...]
Roots per config: solution_module, challenge_module, solution_imports. Only modules whose source lies in the repo
(lean/OAI/**, lean/ComparatorChallenges/**, lean/*.lean) are followed; anything else (Mathlib, other lake packages,
Lean core) is a leaf and counted as external. Prints one line per config with counts, then every repo path
(relative to the repo root, i.e. 'lean/...') of the union, sorted, prefixed 'PATH '.
"""
import json, os, sys

lean = sys.argv[1]
modfile = {}
for top in ('OAI', 'ComparatorChallenges'):
    for dp, dns, fs in os.walk(os.path.join(lean, top)):
        dns[:] = [d for d in dns if not d.startswith('.')]
        for f in fs:
            if f.endswith('.lean'):
                p = os.path.join(dp, f)
                modfile[os.path.relpath(p, lean)[:-5].replace(os.sep, '.')] = p
for f in os.listdir(lean):
    if f.endswith('.lean'):
        modfile[f[:-5]] = os.path.join(lean, f)


def strip_comments(src):
    out, i, depth, n = [], 0, 0, len(src)
    while i < n:
        if src.startswith('/-', i):
            depth += 1; i += 2; continue
        if depth and src.startswith('-/', i):
            depth -= 1; i += 2; out.append(' '); continue
        if depth:
            i += 1; continue
        if src.startswith('--', i):
            j = src.find('\n', i)
            i = n if j < 0 else j
            continue
        out.append(src[i]); i += 1
    return ''.join(out)


def imports(m):
    toks = strip_comments(open(modfile[m], encoding='utf-8', errors='replace').read()).split()
    out, i = [], 0
    while i < len(toks) and toks[i] in ('module', 'prelude'):
        i += 1
    while i < len(toks):
        j = i
        while j < len(toks) and toks[j] in ('public', 'meta', 'private'):
            j += 1
        if j < len(toks) and toks[j] == 'import':
            j += 1
            if j < len(toks) and toks[j] == 'all':
                j += 1
            out.append(toks[j]); i = j + 1
        else:
            break
    return out


union = set()
for cfgp in sys.argv[2:]:
    c = json.load(open(cfgp, encoding='utf-8'))
    roots = [c['solution_module'], c['challenge_module']] + c.get('solution_imports', [])
    seen, ext, st = set(), set(), list(roots)
    while st:
        x = st.pop()
        if x in seen or x in ext:
            continue
        if x not in modfile:
            ext.add(x); continue
        seen.add(x)
        st.extend(imports(x))
    paths = {os.path.relpath(modfile[m], os.path.dirname(lean)).replace(os.sep, '/') for m in seen}
    union |= paths
    print(f'CONFIG {os.path.basename(cfgp)}: roots {roots}; repo modules {len(seen)}; external leaf modules {len(ext)}')
union.add('lean/' + 'lake-manifest.json'); union.add('lean/lakefile.lean'); union.add('lean/lean-toolchain')
for p in sorted(union):
    print('PATH ' + p)
