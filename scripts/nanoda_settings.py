"""Paper prep 4, Task 1: the nanoda setting of every Comparator config file (read-only).

Usage: python -I scripts/nanoda_settings.py <tree at fd4aeeb> <tree at adc7f12> <out dir>
  <tree at X>: a directory with lean/ComparatorChallenges/*.json and lean/formalization.yaml from `git archive X`.
Parses each config with json.load and records every key whose name contains "nanoda" (case-insensitive), so the
actual key name is reported rather than assumed.
"""
import collections, json, os, re, sys

t_fd, t_adc, out = sys.argv[1:4]


def refs(tree):
    t = open(os.path.join(tree, 'lean', 'formalization.yaml'), encoding='utf-8').read()
    return {m.group(1).split('/')[-1][:-5] for m in re.finditer(r'comparator_config:\s*["\']?([^\s"\']+)', t)}


def scan(tree):
    d = os.path.join(tree, 'lean', 'ComparatorChallenges')
    rows = []
    for f in sorted(os.listdir(d)):
        if not f.endswith('.json'):
            continue
        c = json.load(open(os.path.join(d, f), encoding='utf-8'))
        keys = [k for k in c if 'nanoda' in k.lower()]
        if not keys:
            setting, key = 'absent', ''
        else:
            assert len(keys) == 1, (f, keys)
            key = keys[0]
            v = c[key]
            setting = 'true' if v is True else 'false' if v is False else f'other:{v!r}'
        rows.append((f[:-5], key, setting))
    return rows


os.makedirs(out, exist_ok=True)
S = ['Paper prep 4, Task 1: nanoda setting of every Comparator config (COMPUTED; scripts/nanoda_settings.py; json.load)']
with open(os.path.join(out, 'nanoda-settings.tsv'), 'w', encoding='utf-8', newline='\n') as tsv:
    tsv.write('commit\tconfig\treferenced_by_yaml_at_commit\tkey\tsetting\n')
    for label, tree in [('fd4aeeb', t_fd), ('adc7f12', t_adc)]:
        rows, ref = scan(tree), refs(tree)
        for n, k, s in rows:
            tsv.write(f'{label}\t{n}\t{n in ref}\t{k}\t{s}\n')
        allc = collections.Counter(s for _, _, s in rows)
        refc = collections.Counter(s for n, _, s in rows if n in ref)
        keys = collections.Counter(k for _, k, _ in rows)
        S.append(f'\n== {label}: {len(rows)} config files in lean/ComparatorChallenges/; {len(ref)} referenced by formalization.yaml')
        S.append(f'   key names found: {dict(keys)}')
        S.append(f'   (i) all config files: ' + ', '.join(f'{k} {v}' for k, v in sorted(allc.items())))
        S.append(f'   (ii) referenced configs: ' + ', '.join(f'{k} {v}' for k, v in sorted(refc.items())))
        on = [n for n, _, s in rows if s == 'true']
        S.append(f'   configs with nanoda on: {on}')
        S.append(f'   configs with no nanoda key: {[n for n, _, s in rows if s == "absent"]}')
        S.append(f'   referenced configs missing on disk: {sorted(ref - {n for n, _, _ in rows})}')
        S.append(f'   explicit "enable_nanoda": false: {allc.get("false", 0)} of {len(rows)} config files -> '
                 f'{"MATCHES 402 of 405" if (allc.get("false", 0), len(rows)) == (402, 405) else "no match"}')
        off_all = allc.get('false', 0) + allc.get('absent', 0)
        off_ref = refc.get('false', 0) + refc.get('absent', 0)
        S.append(f'   "402 of 405 ship with nanoda off": (i) off {off_all} of {len(rows)} -> {"MATCH" if (off_all, len(rows)) == (402, 405) else "no match"}; '
                 f'(ii) off {off_ref} of {sum(refc.values())} -> {"MATCH" if (off_ref, sum(refc.values())) == (402, 405) else "no match"}')
open(os.path.join(out, 'nanoda-settings-summary.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(S) + '\n')
print('\n'.join(S))
