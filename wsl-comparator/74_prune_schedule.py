"""Item 4 planning (read-only): batch-and-prune schedule for the 172 remainder configs, peak disk inside WSL on C:.

Usage: python3 -I 74_prune_schedule.py <openai/math lean dir at fd4aeeb> <toolchain src/lean dir> [schedule json to write]
Model (all module sets COMPUTED with the header-only import parser of 71_main_plan.py; sizes partly estimated):
- Disk unit is GiB of allocated blocks (st_blocks), the same unit as `df -BG`.
- A module's build output is every file under .lake/build/lib/lean and .lake/build/ir with its path stem.
  Built modules use their measured size. Unbuilt modules use a least-squares fit size ~ a + b*(closure size) + c*(source
  bytes) over the built OAI modules (INFERRED estimate; fit quality printed).
- Pruning removes only OAI build outputs. Package builds (Mathlib etc.) are never pruned. The pilot closures
  (SiegelZeros, QuasiRiemannHypothesis, EditApproximation) are always kept.
- Order: headline batch first (15 configs), then the remainder batches. After each batch (after its replay, shipped
  reruns and queries), prune every OAI module not in a kept closure and not needed by any later batch.
- Batching: greedy. Each step adds the config with the fewest new bytes given what is present plus the batch so far
  (ties: most shared modules), until the batch's new bytes would exceed a budget B. Several B are tried; the schedule
  with the lowest peak is reported (ties: fewer batches).
"""
import json, os, sys
import yaml

lean, core = sys.argv[1], sys.argv[2]
pkgs = os.path.join(lean, '.lake', 'packages')
GiB = 1024 ** 3
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


ccache = {}
def closure(m):
    if m in ccache: return ccache[m]
    st, seen = [m], set()
    while st:
        x = st.pop()
        if x in seen: continue
        seen.add(x); st += imports(x) or []
    ccache[m] = frozenset(seen)
    return ccache[m]


# measured build-output sizes of OAI modules
build = os.path.join(lean, '.lake', 'build')
size = {}
for sub in ('lib/lean', 'ir'):
    root = os.path.join(build, sub)
    for dp, dns, fs in os.walk(root):
        rel = os.path.relpath(dp, root)
        for f in fs:
            m = ('' if rel == '.' else rel.replace(os.sep, '.') + '.') + f.split('.')[0]
            size[m] = size.get(m, 0) + os.lstat(os.path.join(dp, f)).st_blocks * 512
built = {m for m in size if modpkg.get(m) == 'openai-math' and
         os.path.isfile(os.path.join(build, 'lib', 'lean', *m.split('.')) + '.olean')}
oai_bytes_now = sum(size[m] for m in size if modpkg.get(m) == 'openai-math')

def feats(m):
    return (1.0, float(sum(1 for x in closure(m) if modpkg.get(x) not in (None, 'core'))), float(os.path.getsize(modfile[m])))

# least squares (normal equations, 3x3) on built OAI modules: exploratory floating-point estimate
X = [feats(m) for m in sorted(built)]; Y = [float(size[m]) for m in sorted(built)]
A = [[sum(x[i] * x[j] for x in X) for j in range(3)] for i in range(3)]
bv = [sum(x[i] * y for x, y in zip(X, Y)) for i in range(3)]
M = [row[:] + [bv[i]] for i, row in enumerate(A)]
for c in range(3):
    p = max(range(c, 3), key=lambda r: abs(M[r][c])); M[c], M[p] = M[p], M[c]
    for r in range(3):
        if r != c:
            f = M[r][c] / M[c][c]; M[r] = [a - f * b for a, b in zip(M[r], M[c])]
coef = [M[i][3] / M[i][i] for i in range(3)]
pred = [sum(c * xi for c, xi in zip(coef, x)) for x in X]
ybar = sum(Y) / len(Y)
r2 = 1 - sum((y - q) ** 2 for y, q in zip(Y, pred)) / sum((y - ybar) ** 2 for y in Y)
tot_err = (sum(pred) - sum(Y)) / sum(Y)

scache = {}
def msize(m):
    if m not in scache:
        scache[m] = size[m] if m in built else max(0.0, sum(c * xi for c, xi in zip(coef, feats(m))))
    return scache[m]

y = yaml.safe_load(open(os.path.join(lean, 'formalization.yaml'), encoding='utf-8'))
ref = sorted({e['comparator_config'] for e in y['status']['main_results']})
cfgs = {r: json.load(open(os.path.join(lean, r), encoding='utf-8')) for r in ref}
def need(r):
    c = cfgs[r]; s = set()
    for root in [c['solution_module'], c['challenge_module']] + c.get('solution_imports', []):
        s |= closure(root)
    return frozenset(m for m in s if modpkg.get(m) == 'openai-math')
def pkg_need(r):
    c = cfgs[r]; s = set()
    for root in [c['solution_module'], c['challenge_module']] + c.get('solution_imports', []):
        s |= closure(root)
    return {m for m in s if modpkg.get(m) not in (None, 'core', 'openai-math')}

head = ['ComparatorChallenges/' + n + '.json' for n in (
    'DirichletSevenEighths HeckeSevenEighths OptimalMaxCut UniqueGamesTheorem VertexCover MatrixFields MatrixMultiplication '
    'MahlerConjecture SymmetricMahlerEquality SymmetricPolar ExactFourier UniformFourier EuclideanFiveColor PlaneColoring '
    'HarmonicGrowth').split()]
pilot = ['ComparatorChallenges/' + n + '.json' for n in ('SiegelZeros', 'QuasiRiemannHypothesis', 'EditApproximation')]
rest = [r for r in ref if r not in head and r not in pilot]
assert len(head) == 15 and all(h in cfgs for h in head) and len(rest) == 172, (len(rest),)
for p in pilot:
    cfgs.setdefault(p, json.load(open(os.path.join(lean, p), encoding='utf-8')))
print('pilot configs referenced by the yaml at this commit: ' + ', '.join(f"{p.split('/')[-1][:-5]} {p in ref}" for p in pilot))
N = {r: need(r) for r in cfgs}
kept = frozenset().union(*(N[p] for p in pilot))
H = frozenset().union(*(N[h] for h in head))

# fixed part of WSL disk use: df used minus OAI build outputs minus the temporary /home/checker/mainsrc copy
sv = os.statvfs('/'); used_now = (sv.f_blocks - sv.f_bfree) * sv.f_frsize
mainsrc = 0
for dp, dns, fs in os.walk('/home/checker/mainsrc'):
    for f in fs:
        try: mainsrc += os.lstat(os.path.join(dp, f)).st_blocks * 512
        except OSError: pass
pkg_new = {m for r in ref for m in pkg_need(r) if not os.path.isfile(os.path.join(pkgs, modpkg[m], '.lake', 'build', 'lib', 'lean', *m.split('.')) + '.olean')}
fixed = used_now - oai_bytes_now - mainsrc

print(f'WSL / used now {used_now / GiB:.1f} GiB = OAI build outputs {oai_bytes_now / GiB:.1f} + temporary mainsrc {mainsrc / GiB:.1f} + fixed {fixed / GiB:.1f} (OS, toolchain, packages, sources)')
print(f'OAI modules built now: {len(built)}; package modules still to build (never pruned): {len(pkg_new)}')
print(f'size model (INFERRED): bytes = {coef[0]:.0f} + {coef[1]:.0f}*closure + {coef[2]:.2f}*source_bytes; R^2 {r2:.3f}; '
      f'error of summed prediction over built modules {tot_err * 100:+.1f}%')
print(f'mean measured size per built OAI module {oai_bytes_now / max(1, len(built)) / 2**20:.2f} MiB')


def gb(s): return sum(msize(m) for m in s) / GiB

def schedule(B):
    batches, todo = [], list(rest)
    present = set(built) | set(H)   # after the headline build
    future_all = frozenset().union(*(N[r] for r in rest))
    present = {m for m in present if m in kept or m in future_all}  # prune after headline replay
    while todo:
        cur, cn = [], set()
        while todo:
            have = present | cn
            best = min(todo, key=lambda r: (sum(msize(m) for m in N[r] - have), -len(N[r] & have), r))
            if cur and sum(msize(m) for m in (cn | N[best]) - present) > B * GiB: break
            cur.append(best); cn |= N[best]; todo.remove(best)
        batches.append((cur, frozenset(cn)))
        present |= cn
        later = frozenset().union(*(N[r] for r in todo)) if todo else frozenset()
        present = {m for m in present if m in kept or m in later}
    return batches

def simulate(batches, verbose=False):
    pk = sum(msize(m) for m in pkg_new) / GiB
    base = fixed / GiB + pk
    present = set(built)
    rows = []
    peak_h = base + gb(present | H)
    present |= H
    future = [b[1] for b in batches]
    allf = frozenset().union(*future)
    present = {m for m in present if m in kept or m in allf}
    after_h = base + gb(present)
    peak = peak_h
    for i, (cs, need_i) in enumerate(batches):
        newm = need_i - present
        present |= need_i
        p = base + gb(present)
        later = frozenset().union(*future[i + 1:]) if i + 1 < len(future) else frozenset()
        present = {m for m in present if m in kept or m in later}
        rows.append((i + 1, cs, len(newm), gb(newm), p, base + gb(present)))
        peak = max(peak, p)
    return peak, peak_h, after_h, rows

print(f'\nno pruning, everything built: {fixed / GiB + sum(msize(m) for m in pkg_new) / GiB + gb(set(built) | H | frozenset().union(*(N[r] for r in rest))):.1f} GiB')
results = []
for B in (1, 2, 3, 4, 6, 8, 10, 15, 20, 30, 1000):
    bs = schedule(B)
    pk, ph, ah, rows = simulate(bs)
    results.append((round(pk, 1), len(bs), B, bs))
    print(f'budget {B:>4} GiB new per batch: {len(bs):>3} batches, peak {pk:.1f} GiB (headline-phase peak {ph:.1f}, after headline prune {ah:.1f})')
pk, nb, B, bs = min(results, key=lambda t: (t[0], t[1]))
pk, ph, ah, rows = simulate(bs)
print(f'\n== chosen: budget {B} GiB, {nb} batches, peak WSL disk use {pk:.1f} GiB')
print(f'headline batch: peak {ph:.1f} GiB; after its replay and prune {ah:.1f} GiB (kept: pilot closures and modules later batches need)')
print('batch | configs | new OAI modules | new GiB | WSL used after build | after prune')
for i, cs, nm, ng, p, a in rows:
    print(f'{i:>5} | {len(cs):>3} | {nm:>6} | {ng:>6.1f} | {p:>6.1f} | {a:>6.1f} | ' + ' '.join(c.split('/')[-1][:-5] for c in cs))
big = sorted(((gb(N[r] - built - H), r) for r in rest), reverse=True)[:5]
print('\nlargest single remainder configs (GiB of OAI outputs not already built): ' + ', '.join(f'{r.split("/")[-1][:-5]} {g:.1f}' for g, r in big))
if len(sys.argv) > 3:
    json.dump({'budget_gib': B, 'peak_gib': round(pk, 1), 'kept_configs': pilot,
               'batches': [cs for cs, _ in bs]}, open(sys.argv[3], 'w'), indent=1)
    print(f'schedule written to {sys.argv[3]}')
