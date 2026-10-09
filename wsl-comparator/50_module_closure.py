"""Read-only: import closures of given modules (same method as 43_bridge_import_closure.py: header-only
import parsing, nested comments stripped, Lean core/Std/Lake resolved from the toolchain sources).

Usage: python3 -I 50_module_closure.py <openai/math lean dir> <toolchain src/lean dir> <module> [<module> ...]
For each root module: closure size, unresolved modules, every PrimeNumberTheoremAnd module in the closure,
whether PrimeNumberTheoremAnd.SiegelZeros.HadamardSupport is in it and which closure modules import it
directly, and any OAI module in the closure that lies outside OAI.NumberTheory.SiegelZeros.
"""
import os, sys

lean, core = sys.argv[1], sys.argv[2]
roots = sys.argv[3:]
pkgs = os.path.join(lean, '.lake', 'packages')
modfile = {}
for base, prefix_dirs in [(lean, ['OAI']), (core, ['Init', 'Lean', 'Std', 'Lake']), (os.path.join(core, 'lake'), ['Lake']),
                          *[(os.path.join(pkgs, p), None) for p in sorted(os.listdir(pkgs))]]:
    tops = prefix_dirs or [d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d)) and not d.startswith('.')]
    for t in tops:
        for dp, dns, fs in os.walk(os.path.join(base, t)):
            dns[:] = [d for d in dns if not d.startswith('.')]
            for f in fs:
                if f.endswith('.lean'):
                    p = os.path.join(dp, f)
                    modfile.setdefault(os.path.relpath(p, base)[:-5].replace(os.sep, '.'), p)
    for f in os.listdir(base):
        if f.endswith('.lean'):
            modfile.setdefault(f[:-5], os.path.join(base, f))


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


cache = {}
def imports(m):
    if m in cache:
        return cache[m]
    p = modfile.get(m)
    if p is None:
        cache[m] = None
        return None
    toks = strip_comments(open(p, encoding='utf-8', errors='replace').read()).split()
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
    cache[m] = out
    return out


def closure(root):
    seen, missing, st = set(), set(), [root]
    while st:
        x = st.pop()
        if x in seen:
            continue
        seen.add(x)
        im = imports(x)
        if im is None:
            missing.add(x); continue
        st += im
    return seen, missing


H = 'PrimeNumberTheoremAnd.SiegelZeros.HadamardSupport'
for r in roots:
    cl, missing = closure(r)
    pnt = sorted(m for m in cl if m.startswith('PrimeNumberTheoremAnd'))
    oai = [m for m in cl if m.startswith('OAI.')]
    outside = sorted(m for m in oai if not m.startswith('OAI.NumberTheory.SiegelZeros.'))
    print(f'\n== {r}')
    print(f'  file: {os.path.relpath(modfile[r], lean) if r in modfile else "NOT FOUND"}')
    print(f'  closure: {len(cl)} modules ({len(oai)} OAI, {sum(m.startswith("Mathlib") for m in cl)} Mathlib, {len(pnt)} PrimeNumberTheoremAnd); unresolved: {sorted(missing)}')
    print(f'  OAI modules outside OAI.NumberTheory.SiegelZeros: {outside}')
    print(f'  {H} in closure: {H in cl}')
    print(f'  closure modules that import it directly: {sorted(m for m in cl if H in (imports(m) or []))}')
    print(f'  PrimeNumberTheoremAnd modules in closure: {pnt}')
