"""Read-only feasibility check for plan step 3d (comparator run on the rerouted proof).

1. Lists the OAI identifiers used by the bridge part of lean-checks/Lemma3Bridged.lean (lines from
   "Corollary 4 from Lemma 3" to "end Lemma3") and the OAI module that declares each.
2. Prints the full import closure (all packages) of the modules the comparator copy of our code will
   import: Mathlib and OAI.NumberTheory.SiegelZeros.Structure.InvariantJetLinearMap.
3. Checks that no module in that closure is one of the rerouted chain modules or Main.

Usage: python3 -I 43_bridge_import_closure.py <openai/math lean dir> <path to Lemma3Bridged.lean> <toolchain src/lean dir>
Reads only. Run against the checker's comparator-checked clone (pinned at adc7f12, with .lake/packages).
"""
import os, re, sys

lean, bridged, core = sys.argv[1], sys.argv[2], sys.argv[3]
pkgs = os.path.join(lean, '.lake', 'packages')

# module -> file, over the OAI tree, the Lake packages of the clone, and the Lean toolchain's own sources
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
                    m = os.path.relpath(p, base)[:-5].replace(os.sep, '.')
                    modfile.setdefault(m, p)
    for f in os.listdir(base):  # root-level module files such as Mathlib.lean
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


def imports(m):
    p = modfile.get(m)
    if p is None:
        return None
    src = open(p, encoding='utf-8', errors='replace').read()
    # only the module header counts: strip comments (block comments nest), then read
    # `[module] [prelude] ([public] [meta] import X)*`
    src = strip_comments(src)
    toks = src.split()
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
            out.append(toks[j])
            i = j + 1
        else:
            break
    return out


def closure(roots):
    seen, missing, st = set(), set(), list(roots)
    while st:
        x = st.pop()
        if x in seen:
            continue
        seen.add(x)
        im = imports(x)
        if im is None:
            missing.add(x)
            continue
        st += im
    return seen, missing


P = 'OAI.NumberTheory.SiegelZeros.'
forbidden = [P + 'Characters.CharacterGlobalGreedyDeterminantMasterBounds',
             P + 'EntireFunctions.RealZeroUniformMasterBound',
             P + 'Characters.DirichletRealZeroBound',
             P + 'Characters.DirichletRealZeroBoundProof',
             P + 'Main']
roots = ['Mathlib', P + 'Structure.InvariantJetLinearMap']

# 1. OAI identifiers used by the bridge region
src = open(bridged, encoding='utf-8').read().split('\n')
a = next(i for i, l in enumerate(src) if l.startswith('/-! ## Corollary 4 from Lemma 3'))
b = next(i for i, l in enumerate(src) if l.startswith('end Lemma3'))
region = '\n'.join(src[a:b + 1])
region_nc = strip_comments(region)
region_nc = re.sub(r'--[^\n]*', ' ', region_nc)
idents = set(re.findall(r"[A-Za-z_][A-Za-z0-9_'.]*", region_nc))
oai_decl = {}
for m, p in modfile.items():
    if not m.startswith(P):
        continue
    s = open(p, encoding='utf-8', errors='replace').read()
    for n in re.findall(r"^\s*(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+)*(?:theorem|lemma|def|abbrev|structure|class|inductive|instance)\s+([A-Za-z_][A-Za-z0-9_'.]*)", s, re.M):
        oai_decl.setdefault(n.split('.')[-1], set()).add(m)
used = sorted(i for i in idents if i.split('.')[-1] in oai_decl and i[0].islower() or i in ('OAI',))
print(f'bridge region: lean-checks/Lemma3Bridged.lean lines {a + 1}-{b + 1}')
print('identifiers in the bridge region whose last component is declared somewhere in OAI SiegelZeros:')
cl, missing = closure(roots)
for i in used:
    if i == 'OAI':
        continue
    mods = sorted(oai_decl[i.split('.')[-1]])
    print(f'  {i}: declared in {len(mods)} module(s); in closure: {[m for m in mods if m in cl]}; outside: {[m for m in mods if m not in cl][:4]}')

# 2. closure
print(f'\nimport roots of the comparator copy of our code: {roots}')
print(f'full import closure: {len(cl)} modules ({sum(m.startswith("OAI.") for m in cl)} OAI, '
      f'{sum(m.startswith("Mathlib") for m in cl)} Mathlib, {sum(not m.startswith(("OAI.", "Mathlib")) for m in cl)} other); unresolved: {sorted(missing)}')
print('non-Mathlib modules in the closure:')
for m in sorted(cl):
    if not m.startswith('Mathlib'):
        print('  ' + m)

# 3. check
bad = [f for f in forbidden if f in cl]
print(f'\nforbidden modules in closure: {bad}')
print('CHECK ' + ('PASSED' if not bad and not missing else 'FAILED'))
