"""Part B planning (read-only): referenced configs, headline batch and build estimates at upstream main.

Usage: python3 -I 71_main_plan.py <main src lean dir> <adc7f12 clone lean dir> <toolchain src/lean dir> <changed modules file>
- <main src lean dir>: `git archive origin/main lean` unpacked; its .lake is a symlink to the adc7f12 clone's .lake
  (same manifest, so the same packages). A module counts as already built if the adc7f12 clone has its .olean and
  neither it nor anything in its closure is in <changed modules file> (modules whose source differs between commits).
- Header-only import parser, as in 50_module_closure.py / 65_build_estimate.py.
"""
import collections, glob, json, os, re, sys
import yaml

lean, old, core, changed_path = sys.argv[1:5]
changed = {l.strip() for l in open(changed_path) if l.strip()}
pkgs = os.path.join(old, '.lake', 'packages')
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
    """Closure of one module (memoized, iterative)."""
    if m in ccache: return ccache[m]
    order, st, seen = [], [m], set()
    while st:
        x = st.pop()
        if x in seen: continue
        seen.add(x); order.append(x); st += imports(x) or []
    ccache[m] = frozenset(seen)
    return ccache[m]


def built(m):
    pkg = modpkg.get(m)
    if pkg == 'core': return True
    base = old if pkg == 'openai-math' else os.path.join(pkgs, pkg)
    return os.path.isfile(os.path.join(base, '.lake', 'build', 'lib', 'lean', *m.split('.')) + '.olean')


stale_memo = {}
def stale(m):
    if m in stale_memo: return stale_memo[m]
    r = m in changed or any(x in changed for x in closure(m))
    stale_memo[m] = r; return r


y = yaml.safe_load(open(os.path.join(lean, 'formalization.yaml'), encoding='utf-8'))
mr = y['status']['main_results']
ref = sorted({e['comparator_config'] for e in mr})
print(f'main formalization.yaml: version {y.get("version")}; main_results {len(mr)}; distinct configs {len(ref)}; sources {len(y.get("sources", []))}')
missing = [r for r in ref if not os.path.isfile(os.path.join(lean, r))]
print(f'referenced configs missing on disk: {missing}')
cfgs = {r: json.load(open(os.path.join(lean, r), encoding='utf-8')) for r in ref}

def cfg_closure(r):
    c = cfgs[r] if r in cfgs else json.load(open(os.path.join(lean, r), encoding='utf-8'))
    s = set()
    for root in [c['solution_module'], c['challenge_module']] + c.get('solution_imports', []):
        s |= closure(root)
    return s

def to_build(mods):
    nc = {m for m in mods if modpkg.get(m) not in (None, 'core')}
    tb = {m for m in nc if not built(m) or stale(m)}
    return nc, tb

# headline batch from lean/docs/NNN.md comparator links
fams = ['003', '102', '107', '087', '130', '124', '158', '159', '180', '182']
print('\n== headline families (configs linked from lean/docs/NNN.md)')
batch = []
for f in fams:
    p = os.path.join(lean, 'docs', f + '.md')
    txt = open(p, encoding='utf-8').read() if os.path.isfile(p) else ''
    links = sorted(set(re.findall(r'ComparatorChallenges/([A-Za-z0-9_]+)\.(?:lean|json)', txt)))  # docs link the challenge .lean; the config has the same stem
    title = txt.split('\n', 1)[0][:100] if txt else '(no docs file)'
    print(f'  {f}: {title}')
    for l in links:
        r = f'ComparatorChallenges/{l}.json'
        nb = len(to_build(cfg_closure(r))[1]) if os.path.isfile(os.path.join(lean, r)) else -1
        print(f'      {r}  referenced_by_yaml={r in cfgs}  exists={os.path.isfile(os.path.join(lean, r))}  modules_to_build_alone={nb}')
        if r not in batch: batch.append(r)
for extra in ('ComparatorChallenges/HarmonicGrowth.json', 'ComparatorChallenges/NavierStokesVelocity.json'):
    print(f'  extra {extra}: referenced_by_yaml={extra in cfgs} exists={os.path.isfile(os.path.join(lean, extra))}')
pilot = ['ComparatorChallenges/SiegelZeros.json', 'ComparatorChallenges/QuasiRiemannHypothesis.json', 'ComparatorChallenges/EditApproximation.json']
for p in pilot:
    nc, tb = to_build(cfg_closure(p))
    print(f'  pilot {p}: closure needs rebuild of {len(tb)} modules (stale or unbuilt) -> {"unchanged, excluded" if not tb else "CHANGED"}')
# scope = yaml-referenced configs only: the headline batch keeps only referenced configs; others are listed separately
not_ref = [r for r in batch if r not in cfgs]
headline = [r for r in batch if r in cfgs and (r not in pilot or to_build(cfg_closure(r))[1])]
for extra in ('ComparatorChallenges/HarmonicGrowth.json', 'ComparatorChallenges/NavierStokesVelocity.json'):
    if extra in cfgs and extra not in headline:
        headline.append(extra)
    elif extra not in cfgs and extra not in not_ref:
        not_ref.append(extra)
print('\nlinked from the headline families or named extra, but NOT referenced by formalization.yaml (outside scope; listed separately):')
for r in not_ref:
    print(f'  {r}: modules to build alone {len(to_build(cfg_closure(r))[1])}')

def summarize(label, sel):
    union = set()
    for r in sel:
        union |= cfg_closure(r)
    nc, tb = to_build(union)
    oai = {m for m in tb if modpkg[m] == 'openai-math'}
    st = {m for m in tb if built(m) and stale(m)}
    print(f'\n== {label}: {len(sel)} configs; union {len(nc)} non-core modules; to build {len(tb)} '
          f'(OAI {len(oai)}, other packages {len(tb) - len(oai)}; of these {len(st)} are built but stale)')
    by = collections.Counter(modpkg[m] for m in tb)
    print('   to build by package: ' + ', '.join(f'{p} {n}' for p, n in by.most_common()))
    n = len(tb); runs = len(sel)
    print(f'   INFERRED estimate (pilot rates: 2.2 s/module at 4 threads, 3.8 MB/module, 9-17 min per comparator run): '
          f'build ~{n*2.2/3600:.1f} h ({n*1.1/3600:.1f}-{n*4.4/3600:.1f} h), disk ~{n*3.8/1000:.0f} GB; '
          f'replay of {runs} nanoda runs ~{runs*9/60:.0f}-{runs*17/60:.0f} h')
    return union, tb

print(f'\nchanged modules (source differs adc7f12 -> main): {sorted(changed)}')
u_all, tb_all = summarize('all referenced configs at main', ref)
u_head, tb_head = summarize('headline batch', headline)
rest = [r for r in ref if r not in headline and r not in pilot]
u_rest, tb_rest = summarize('remainder (referenced, minus headline and pilot)', rest)
shared = tb_head & u_rest
print(f'\n== pruning: of the {len(tb_head)} modules the headline batch would build, {len(shared)} are also in the remainder\'s closures; '
      f'{len(tb_head) - len(shared)} are used only by headline configs')
stale_any = {m for m in u_all if built(m) and stale(m)}
print(f'built-but-stale modules among referenced closures: {len(stale_any)} {sorted(stale_any)[:10]}')
print('\nheadline configs: ' + ', '.join(r.split('/')[-1] for r in headline))
