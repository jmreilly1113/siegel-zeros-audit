"""Corpus checks, phase 2 (read-only): schema survey of every lean/ComparatorChallenges/*.json.

Usage: python3 -I 62_corpus_configs.py <openai/math lean dir> <out.tsv>
Key names are taken from the files themselves (SiegelZeros.json shows: challenge_module, solution_module,
theorem_names, definition_names, permitted_axioms, enable_nanoda); every key found anywhere is tabulated.
"""
import collections, glob, json, os, sys
import yaml

lean, out = sys.argv[1], sys.argv[2]
y = yaml.safe_load(open(os.path.join(lean, 'formalization.yaml'), encoding='utf-8'))
referenced = {e['comparator_config'] for e in y['status']['main_results']}
STD = {'propext', 'Classical.choice', 'Quot.sound'}
paths = sorted(glob.glob(os.path.join(lean, 'ComparatorChallenges', '*.json')))
cfgs, bad = {}, []
for p in paths:
    rel = os.path.relpath(p, lean).replace(os.sep, '/')
    try:
        cfgs[rel] = json.load(open(p, encoding='utf-8'))
    except Exception as e:
        bad.append((rel, repr(e)))
key_count = collections.Counter(k for c in cfgs.values() for k in c)
print(f'config files: {len(paths)}; parsed: {len(cfgs)}; parse errors: {bad}')
print('keys (number of configs containing each):')
for k, n in key_count.most_common():
    print(f'  {k:<22} {n}')
keys = [k for k, _ in key_count.most_common()]
nanoda = collections.Counter('absent' if 'enable_nanoda' not in c else str(c['enable_nanoda']).lower() for c in cfgs.values())
print(f'enable_nanoda: {dict(nanoda)}')
ax = collections.Counter(tuple(sorted(c.get('permitted_axioms', []))) for c in cfgs.values())
print('permitted_axioms sets:')
for a, n in ax.most_common():
    print(f'  {n:>4}  {list(a)}')
nonstd = {r: c.get('permitted_axioms') for r, c in cfgs.items() if set(c.get('permitted_axioms', [])) - STD}
print(f'configs permitting axioms beyond propext/Classical.choice/Quot.sound: {len(nonstd)}')
for r, a in sorted(nonstd.items()):
    print(f'  {r}: {a}  referenced={r in referenced}')
rare = [k for k, n in key_count.items() if n <= 5]
print(f'keys in at most 5 configs: {rare}')
for k in rare:
    for r, c in sorted(cfgs.items()):
        if k in c:
            print(f'  {k} in {r}: {json.dumps(c[k])[:200]}')
cm = [r for r, c in cfgs.items() if c.get('challenge_module') != 'ComparatorChallenges.' + os.path.basename(r)[:-5]]
print(f'configs whose challenge_module is not ComparatorChallenges.<file stem>: {len(cm)} {cm[:10]}')
ch_missing = [r for r, c in cfgs.items() if not os.path.isfile(os.path.join(lean, *c.get('challenge_module', '').split('.')) + '.lean')]
sol_missing = [r for r, c in cfgs.items() if not os.path.isfile(os.path.join(lean, *c.get('solution_module', '').split('.')) + '.lean')]
print(f'challenge module file missing: {len(ch_missing)} {ch_missing[:10]}')
print(f'solution module file missing: {len(sol_missing)} {sol_missing[:10]}')
print(f'theorem_names count: total {sum(len(c.get("theorem_names", [])) for c in cfgs.values())}; '
      f'configs with 0 theorem names: {[r for r, c in cfgs.items() if not c.get("theorem_names")]}')
print(f'definition_names nonempty: {sum(1 for c in cfgs.values() if c.get("definition_names"))}')
with open(out, 'w', encoding='utf-8') as fh:
    fh.write('# Phase 2 config schema survey (computed from the JSON files at adc7f12).\n')
    fh.write('\t'.join(['config', 'referenced_by_yaml', 'challenge_module', 'solution_module', 'n_theorems', 'theorem_names',
                        'n_definitions', 'definition_names', 'permitted_axioms', 'nonstandard_axioms', 'enable_nanoda', 'other_keys']) + '\n')
    for r, c in sorted(cfgs.items()):
        other = {k: v for k, v in c.items() if k not in ('challenge_module', 'solution_module', 'theorem_names', 'definition_names', 'permitted_axioms', 'enable_nanoda')}
        fh.write('\t'.join([r, str(r in referenced), c.get('challenge_module', ''), c.get('solution_module', ''),
                            str(len(c.get('theorem_names', []))), ','.join(c.get('theorem_names', [])),
                            str(len(c.get('definition_names', []))), ','.join(c.get('definition_names', [])),
                            ','.join(c.get('permitted_axioms', [])), ','.join(sorted(set(c.get('permitted_axioms', [])) - STD)),
                            'absent' if 'enable_nanoda' not in c else str(c['enable_nanoda']).lower(),
                            json.dumps(other) if other else '']) + '\n')
