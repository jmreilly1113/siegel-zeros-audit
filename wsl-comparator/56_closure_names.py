"""Read-only: from a lean4export (format 3.1.0) dump, write two name lists and reproduce #find_deps.

1. Full dump set: every declared name (thm, def, opaque, axiom, quot, and each inductive block's types,
   constructors and recursors).
2. Referenced-only set: the closure of the root under the same rule as the #find_deps elab in
   lean-checks/Lemma3Bridged.lean and ReroutedDeps.lean. Start at the root. For theorem/def/opaque, follow
   constants in the type and the value; for everything else (inductive type, constructor, recursor, quot,
   axiom), follow constants in the type only. "Constants in an expression" means `.const` nodes, as in
   Lean's Expr.getUsedConstants: projections contribute nothing, metadata is looked through.
   The root itself is counted, as #find_deps does.

Writes <outdir>/<label>.full.txt.gz and <outdir>/<label>.referenced.txt.gz (sorted names, one per line) and
prints counts, plus the kinds of the declarations that are in the dump but not referenced.
Usage: python3 -I 56_closure_names.py <dump.ndjson> <root name> <label> <outdir>
"""
import gzip, json, os, sys
from array import array

path, root_name, label, outdir = sys.argv[1:5]

names = {}                # name id -> string
decl = {}                 # name id -> (kind, type expr, value expr or -1)
CH = 3
child = array('i')        # CH slots per expression id, -1 = none
cname = array('i')        # const name id per expression id, -1 = not a const node


def ensure(n):
    while len(cname) <= n:
        grow = max(1024, len(cname))
        cname.extend([-1] * grow)
        child.extend([-1] * (grow * CH))


def set_children(i, kids):
    ensure(i)
    for j, k in enumerate(kids):
        child[i * CH + j] = k


for line in open(path, encoding='utf-8'):
    c = line[2:6]
    if line.startswith('{"in"'):
        o = json.loads(line)
        if isinstance(o.get('str'), dict):
            p = o['str']['pre']; names[o['in']] = (names[p] + '.' if p in names else '') + o['str']['str']
        elif 'num' in o:
            p = o['num']['pre']; names[o['in']] = (names[p] + '.' if p in names else '') + str(o['num']['i'])
        continue
    if line.startswith('{"app"'):
        o = json.loads(line); a = o['app']; set_children(o['ie'], (a['fn'], a['arg'])); continue
    if line.startswith('{"const"'):
        o = json.loads(line); ensure(o['ie']); cname[o['ie']] = o['const']['name']; continue
    if line.startswith('{"forallE"'):
        o = json.loads(line); a = o['forallE']; set_children(o['ie'], (a['type'], a['body'])); continue
    if line.startswith('{"ie"'):
        o = json.loads(line); i = o['ie']
        if 'lam' in o:
            set_children(i, (o['lam']['type'], o['lam']['body']))
        elif 'letE' in o:
            a = o['letE']; set_children(i, (a['type'], a['value'], a['body']))
        elif 'mdata' in o:
            set_children(i, (o['mdata']['expr'],))
        elif 'proj' in o:
            set_children(i, (o['proj']['struct'],))
        else:
            ensure(i)
        continue
    if line.startswith(('{"bvar"', '{"fvar"', '{"mvar"', '{"natVal"', '{"strVal"', '{"sort"', '{"il"', '{"meta"')):
        continue
    for k in ('thm', 'def', 'opaque'):
        if line.startswith('{"%s"' % k):
            v = json.loads(line)[k]; decl[v['name']] = (k, v['type'], v['value']); break
    else:
        for k in ('axiom', 'quot'):
            if line.startswith('{"%s"' % k):
                v = json.loads(line)[k]; decl[v['name']] = (k, v['type'], -1); break
        else:
            if line.startswith('{"inductive"'):
                v = json.loads(line)['inductive']
                for t in v['types']:
                    decl[t['name']] = ('inductive', t['type'], -1)
                for t in v['ctors']:
                    decl[t['name']] = ('ctor', t['type'], -1)
                for t in v['recs']:
                    decl[t['name']] = ('rec', t['type'], -1)

by_name = {s: i for i, s in names.items()}
root = by_name[root_name]
assert root in decl, f'root {root_name} not declared in dump'

visited = bytearray(len(cname))
seen = {root}
work = [root]


def consts_of(e, out):
    st = [e]
    while st:
        x = st.pop()
        if x < 0 or visited[x]:
            continue
        visited[x] = 1
        n = cname[x]
        if n >= 0:
            out.append(n)
        b = x * CH
        for j in range(CH):
            k = child[b + j]
            if k >= 0:
                st.append(k)


while work:
    d = work.pop()
    if d not in decl:
        continue
    kind, ty, val = decl[d]
    found = []
    consts_of(ty, found)
    if kind in ('thm', 'def', 'opaque') and val >= 0:
        consts_of(val, found)
    for n in found:
        if n not in seen:
            seen.add(n); work.append(n)

full = sorted(names[i] for i in decl)
ref = sorted(names[i] for i in seen)
os.makedirs(outdir, exist_ok=True)
for suffix, lst in (('full', full), ('referenced', ref)):
    with gzip.open(os.path.join(outdir, f'{label}.{suffix}.txt.gz'), 'wt', encoding='utf-8', compresslevel=9) as f:
        f.write('\n'.join(lst) + '\n')
not_decl = [names[i] for i in seen if i not in decl]
rest = [i for i in decl if i not in seen]
kinds = {}
for i in rest:
    kinds[decl[i][0]] = kinds.get(decl[i][0], 0) + 1
print(f'== {label}: {path} root {root_name}')
print(f'  full dump set: {len(full)}; referenced-only set: {len(ref)}; referenced but not declared in dump: {len(not_decl)} {not_decl[:5]}')
print(f'  in dump but not referenced: {len(rest)}; by kind: {dict(sorted(kinds.items()))}')
