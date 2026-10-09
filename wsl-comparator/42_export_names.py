# Reconstruct declaration names in a lean4export ndjson file; report which declared constants have a
# last name component equal to one of the given strings. Usage: 42_export_names.py export.ndjson s1 s2 ...
import json, sys
names, decl_ids = {}, []
for l in open(sys.argv[1]):
    o = json.loads(l)
    if 'str' in o and isinstance(o['str'], dict):
        p = o['str']['pre']; names[o['in']] = (names[p] + '.' if p in names else '') + o['str']['str']
    else:
        for k in ('thm', 'def', 'opaque', 'axiom', 'quot', 'inductive'):
            if k in o:
                v = o[k]
                if isinstance(v, dict) and 'name' in v: decl_ids.append(v['name'])
                elif k == 'inductive':
                    for t in v.get('types', []): decl_ids.append(t['name'])
decls = {names.get(i, f'?{i}') for i in decl_ids}
print(f'  declarations in export: {len(decls)}')
for s in sys.argv[2:]:
    hits = sorted(d for d in decls if d.split('.')[-1] == s)
    print(f'  last component "{s}": {hits}')
