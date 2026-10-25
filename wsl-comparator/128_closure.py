#!/usr/bin/env python3
"""128 helper (2026-10-25): unbuilt OAI/ComparatorChallenges modules in the import closure of each config.

Usage: python3 -I 128_closure.py <lean dir> <config> [<config> ...]
For each config (ComparatorChallenges/<config>.json: solution_module, challenge_module, solution_imports, as 114f's
prebuild targets) prints one line: "<config> <n unbuilt> <module> <module> ...". A module counts as built when its
.olean exists and is not older than its .lean source (an approximation of lake's trace check). Header-import parsing
is copied from 112_prune.py (strip_comments, imports); .lake/packages modules are not followed.
"""
import json, os, sys

lean = sys.argv[1]
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
            if j < len(toks): out.append(toks[j])
            i = j + 1
        else: break
    return out


def built(m):
    s = os.path.join(lean, *m.split('.')) + '.lean'
    o = os.path.join(lean, '.lake', 'build', 'lib', 'lean', *m.split('.')) + '.olean'
    return os.path.exists(o) and os.path.getmtime(o) >= os.path.getmtime(s)


for cfg in sys.argv[2:]:
    c = json.load(open(os.path.join(lean, 'ComparatorChallenges', cfg + '.json')))
    stack, seen = [c['solution_module'], c['challenge_module']] + c.get('solution_imports', []), set()
    while stack:
        m = stack.pop()
        if m in seen or m.split('.')[0] not in TOPS: continue
        if not os.path.isfile(os.path.join(lean, *m.split('.')) + '.lean'): continue
        seen.add(m); stack.extend(imports(m))
    todo = sorted(m for m in seen if not built(m))
    print(cfg, len(todo), *todo)
