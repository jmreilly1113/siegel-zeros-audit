"""Read-only: count declared constant names in lean4export (format 3.1.0) dumps, by kind.

For each dump: theorem/def/opaque/axiom/quot names, and for each inductive block its type, constructor and
recursor names. Also reports whether given root names are present, and how many names start with a given
prefix (e.g. Rerouted. or challenge_).
Usage: python3 -I 54_export_name_counts.py <dump.ndjson> [<dump.ndjson> ...]
"""
import json, sys

for path in sys.argv[1:]:
    names, kinds, ids = {}, {}, []
    for line in open(path, encoding='utf-8'):
        if line.startswith('{"in"'):
            o = json.loads(line)
            if isinstance(o.get('str'), dict):
                p = o['str']['pre']
                names[o['in']] = (names[p] + '.' if p in names else '') + o['str']['str']
            elif 'num' in o:  # numeric name component
                p = o['num']['pre']
                names[o['in']] = (names[p] + '.' if p in names else '') + str(o['num']['i'])
            continue
        for k in ('thm', 'def', 'opaque', 'axiom', 'quot'):
            if line.startswith('{"%s"' % k):
                v = json.loads(line)[k]
                ids.append((k, v['name']))
                break
        else:
            if line.startswith('{"inductive"'):
                v = json.loads(line)['inductive']
                for t in v['types']:
                    ids.append(('inductive', t['name']))
                for c in v['ctors']:
                    ids.append(('ctor', c['name']))
                for r in v['recs']:
                    ids.append(('rec', r['name']))
    full = [(k, names.get(i, f'?{i}')) for k, i in ids]
    by = {}
    for k, _ in full:
        by[k] = by.get(k, 0) + 1
    uniq = {n for _, n in full}
    print(f'== {path}')
    print(f'  declared names: {len(full)} (unique {len(uniq)}); by kind: {dict(sorted(by.items()))}')
    print(f'  without ctors/recs: {sum(v for k, v in by.items() if k not in ("ctor", "rec"))}')
    print(f'  unresolved name ids: {sum(1 for _, n in full if n.startswith("?"))}')
    for pre in ('Rerouted.', 'challenge_', 'Lemma3.', 'OAI.'):
        print(f'  names starting {pre!r}: {sum(1 for n in uniq if n.startswith(pre))}')
