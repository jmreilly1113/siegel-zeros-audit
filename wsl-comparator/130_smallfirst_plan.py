#!/usr/bin/env python3
"""130 (2026-10-25): write a copy of the plan with the pending configs reordered cheapest project first.

Usage: python3 -I 130_smallfirst_plan.py <plan tsv> <out dir> <lean dir> <new plan tsv>
Why: the 100 configs still pending at 16:17 need ~38,200 unbuilt modules, and 10 of them need ~23,600. In the phase-3
order these sit among the cheap ones, and each blocks the main lane for hours. Configs are grouped by project (first
three components of solution_module, the unit the phase-3 order keeps together so shared builds are reused). A
project's cost is the size of the union of its pending configs' unbuilt closures (128_closure.py). Projects go
cheapest first; within a project the phase-3 order is kept. Done and deferred configs follow, in phase-3 order (114f
skips them). Comment lines are kept at the top, and one is added. The input plan is not modified.
"""
import json, os, subprocess, sys

plan, out, lean, new = sys.argv[1:5]
W = os.path.dirname(os.path.abspath(__file__))
lines = open(plan).read().splitlines()
com = [l for l in lines if l.startswith('#')]
body = [l for l in lines if not l.startswith('#')]
hdr, rows = body[0], [l.split('\t') for l in body[1:] if l.strip()]
defer = set(open(os.path.join(out, 'deferred.txt')).read().split())
done = lambda n: os.path.exists(os.path.join(out, 'runs', n + '.result.json'))
pend = [r for r in rows if not done(r[1]) and r[1] not in defer]
cl = {}
res = subprocess.run(['python3', '-I', os.path.join(W, '128_closure.py'), lean] + [r[1] for r in pend],
                     capture_output=True, text=True, check=True).stdout
for l in res.splitlines():
    f = l.split(); cl[f[0]] = set(f[2:])
proj, porder = {}, []
for r in pend:
    m = json.load(open(os.path.join(lean, 'ComparatorChallenges', r[1] + '.json')))['solution_module']
    p = '.'.join(m.split('.')[:3])
    if p not in proj: proj[p] = []; porder.append(p)
    proj[p].append(r)
cost = {p: len(set().union(*(cl[r[1]] for r in proj[p]))) for p in porder}
ps = sorted(porder, key=lambda p: (cost[p], porder.index(p)))
seq = [r for p in ps for r in proj[p]]
rest = [r for r in rows if r not in pend]
with open(new, 'w') as f:
    for l in com: f.write(l + '\n')
    f.write('# 2026-10-25 (130_smallfirst_plan.py): pending configs reordered cheapest project first (union of unbuilt '
            'closures); within a project the phase-3 order is kept; done and deferred configs follow.\n')
    f.write(hdr + '\n')
    for r in seq + rest: f.write('\t'.join(r) + '\n')
print('pending', len(pend), 'projects', len(ps), 'rows', len(seq + rest))
for p in ps: print(f'{cost[p]:6d} {p}: {" ".join(r[1] for r in proj[p])}')
