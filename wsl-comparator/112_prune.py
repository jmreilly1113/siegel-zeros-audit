"""Extended replay: per-config prune of openai/math build outputs (Joe's brief: prune each config's build after it is
saved, unless its outcome is not ACCEPT_BOTH). Same header-import parsing as 76_prune.py.

Usage: python3 -I 112_prune.py <lean dir> <keep-configs file> [--apply]
Kept: every OAI/ComparatorChallenges module in the import closure of each config listed in <keep-configs file>
(one config path per line, relative to <lean dir>, e.g. ComparatorChallenges/X.json). Deleted (only with --apply):
every file under .lake/build/lib/lean/{OAI,ComparatorChallenges} and .lake/build/ir/{OAI,ComparatorChallenges} whose
module is outside the kept set. .lake/packages is never touched. Prints one summary line, then deleted module count.
"""
import json, os, sys

lean, keep_path = sys.argv[1:3]
apply = '--apply' in sys.argv[3:]
TOPS = ('OAI', 'ComparatorChallenges')


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


def imports(m):
    p = os.path.join(lean, *m.split('.')) + '.lean'
    if not os.path.isfile(p): return []
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
    return out


keep = set()
cfgs = [l.strip() for l in open(keep_path) if l.strip() and not l.startswith('#')] if os.path.isfile(keep_path) else []
for r in cfgs:
    c = json.load(open(os.path.join(lean, r), encoding='utf-8'))
    st = [c['solution_module'], c['challenge_module']] + c.get('solution_imports', [])
    while st:
        x = st.pop()
        if x in keep or x.split('.')[0] not in TOPS: continue
        keep.add(x); st += imports(x)
nfiles = nbytes = 0; mods = set()
for sub in ('lib/lean', 'ir'):
    for t in TOPS:
        base = os.path.join(lean, '.lake', 'build', sub)
        for dp, dns, fs in os.walk(os.path.join(base, t)):
            for f in fs:
                rel = os.path.relpath(os.path.join(dp, f), base)
                d, b = os.path.split(rel)
                m = os.path.join(d, b.split('.')[0]).replace(os.sep, '.')
                if m in keep: continue
                p = os.path.join(dp, f)
                nfiles += 1; nbytes += os.path.getsize(p); mods.add(m)
                if apply: os.remove(p)
print(f'{"deleted" if apply else "would delete"} {nfiles} files, {nbytes / 2**30:.2f} GiB, {len(mods)} modules; kept closure of '
      f'{len(cfgs)} configs ({len(keep)} modules)')
