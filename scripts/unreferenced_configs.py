"""Paper prep 4 follow-up, item 3: classify the config files on disk that formalization.yaml does not reference (read-only).

Usage: python -I scripts/unreferenced_configs.py <openai/math clone at fd4aeeb> <out dir>
Writes <out dir>/unreferenced-configs.tsv and unreferenced-configs-summary.txt (and preprints-fd4aeeb.txt, the folder list used).
Counts are COMPUTED. Group roles are INFERRED: the yaml links a main result to a file, not to a manuscript, so the
manuscript match is a HEURISTIC on names (every CamelCase word of >= 4 letters in the config name, cut to its first
5 letters, must occur among the words of a preprints/ folder name, cut the same way).
"""
import collections, hashlib, json, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
clone, out = sys.argv[1:3]
L = os.path.join(clone, 'lean')
ypath = os.path.join(L, 'formalization.yaml')
y = open(ypath, encoding='utf-8').read()
ref = set(re.findall(r'comparator_config: ComparatorChallenges/(\w+)\.json', y))
srcs = set(re.findall(r'id: \.\./preprints/([^/]+)/', y))
pp = sorted(os.listdir(os.path.join(clone, 'preprints')))
C = {f[:-5]: json.load(open(os.path.join(L, 'ComparatorChallenges', f), encoding='utf-8'))
     for f in sorted(os.listdir(os.path.join(L, 'ComparatorChallenges'))) if f.endswith('.json')}
U = sorted(set(C) - ref)
assert len(C) == 416 and len(ref) == 189 and len(U) == 227

# Placeholder challenges: from the fd4aeeb challenge scan (sorry outside a theorem, or a declared axiom).
scan = open(os.path.join(out, 'corpus-challenge-scan-fd4aeeb.txt'), encoding='utf-8').read()
placeholder = set(re.findall(r'^  (?:sorry outside theorem/lemma|axiom declaration): (\w+)\.lean', scan, re.M))

proj = lambda n: '.'.join(C[n]['solution_module'].split('.')[:3])
refproj = collections.defaultdict(list)
for n in ref:
    refproj[proj(n)].append(n)
refmod = {C[n]['solution_module']: n for n in ref}
stem = lambda w: w.lower()[:5]
W = lambda n: {stem(w) for w in re.findall(r'[A-Z][a-z]+|[a-z]+', n) if len(w) >= 4}
PW = {p: {stem(w) for w in re.findall(r'[A-Za-z]+', p)} for p in pp}
match = {n: [p for p in pp if W(n) and W(n) <= PW[p]] for n in C}

GROUPS = [
    ('P', 'placeholder challenge statement (sorried definition or declared axiom in the challenge file)',
     'unfinished or stub statement; not a completed formalization', lambda n: n in placeholder),
    ('C', 'shares its solution project directory (OAI.<Area>.<Project>) with a referenced config',
     'companion result, variant or corollary of a catalogued formalization', lambda n: proj(n) in refproj),
    ('U', 'name matches the title of a manuscript that is not a formalization.yaml source',
     'formalization of a manuscript not (yet) entered in the catalog', lambda n: any(p not in srcs for p in match[n])),
    ('S', 'name matches only titles of manuscripts that are formalization.yaml sources',
     'further result of an already catalogued manuscript', lambda n: bool(match[n])),
    ('N', 'no name match to any manuscript title', 'role not determinable from names', lambda n: True),
]
grp = {}
for n in U:
    grp[n] = next(g for g, _, _, f in GROUPS if f(n))

os.makedirs(out, exist_ok=True)
with open(os.path.join(out, 'preprints-fd4aeeb.txt'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(pp) + '\n')
with open(os.path.join(out, 'unreferenced-configs.tsv'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('config\tgroup\tconfig_path\tsolution_module\tsolution_file\treferenced_configs_same_project\tmatched_preprints\tmatched_preprint_is_yaml_source\n')
    for n in U:
        f.write('\t'.join([n, grp[n], f'lean/ComparatorChallenges/{n}.json', C[n]['solution_module'],
                           'lean/' + C[n]['solution_module'].replace('.', '/') + '.lean', ','.join(sorted(refproj.get(proj(n), []))),
                           ';'.join(match[n]), ';'.join(str(p in srcs) for p in match[n])]) + '\n')

sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
S = ['Paper prep 4 follow-up, item 3: the 227 config files not referenced by formalization.yaml at fd4aeeb',
     f'Command: python -I scripts/unreferenced_configs.py <clone> results/2026-10-21-paper-prep-4; clone at fd4aeeb, clean; '
     f'formalization.yaml sha256 {sha(ypath)}; preprints/ folders {len(pp)} (listed in preprints-fd4aeeb.txt), yaml sources {len(srcs)}.',
     'Counts COMPUTED; roles INFERRED; manuscript matching HEURISTIC (see the script docstring). Groups are exclusive, assigned in the order shown.', '']
cnt = collections.Counter(grp.values())
for g, crit, role, _ in GROUPS:
    ex = [n for n in U if grp[n] == g][:2]
    S.append(f'{g}  {cnt[g]:3d}  criterion (COMPUTED): {crit}')
    S.append(f'          role (INFERRED): {role}')
    for n in ex:
        extra = (f'; same project as referenced {",".join(sorted(refproj[proj(n)]))}' if g == 'C' else
                 f'; matched manuscript {match[n][0]}' if g in 'US' else '')
        S.append(f'          e.g. lean/ComparatorChallenges/{n}.json -> lean/{C[n]["solution_module"].replace(".", "/")}.lean{extra}')
S.append(f'   {sum(cnt.values()):3d}  total')
S.append('')
S.append('Checks for the other roles named in the brief (COMPUTED):')
S.append(f'  superseded versions: configs referenced at adc7f12 but not at fd4aeeb: 0 (see nanoda-settings.tsv); unreferenced configs sharing a '
         f'theorem name with a referenced config: {sum(1 for n in U for t in C[n]["theorem_names"] if t in {t for r in ref for t in C[r]["theorem_names"]})}; '
         f'sharing the exact solution module with a referenced config: {[(n, refmod[C[n]["solution_module"]]) for n in U if C[n]["solution_module"] in refmod]}.')
S.append(f'  tests or examples: config names containing Test/Example/Sanity/Smoke/Demo/Toy/Stub/Draft: '
         f'{[n for n in U if re.search(r"Test|Example|Sanity|Smoke|Demo|Toy|Stub|Draft", n)]}.')
readme = open(os.path.join(L, 'ComparatorChallenges', 'README.md'), encoding='utf-8').read()
sup = re.findall(r'`(\w+Support)\.json`', readme)
S.append(f'  supporting-result comparisons listed in ComparatorChallenges/README.md: {len(sup)}; referenced by the yaml: '
         f'{sum(s in ref for s in sup)}; among the 227: {[s for s in sup if s in U]}.')
S.append(f'  placeholders found by the challenge scan but referenced (not in the 227): {sorted(placeholder & ref)}.')
cal = sum(1 for n in ref if match[n])
S.append(f'  heuristic calibration: the same name match finds some manuscript title for {cal} of the 189 referenced configs '
         f'({sum(1 for n in ref if any(p in srcs for p in match[n]))} of them a yaml source), and for {sum(1 for n in U if match[n])} of the 227.')
S.append('  INFERRED context: history.md (fd4aeeb) says 300 of 719 top-line results are formalized; the yaml catalogs 189 configs for '
         '173 sources, which fits many on-disk configs belonging to manuscripts the catalog does not yet list (groups U and N).')
open(os.path.join(out, 'unreferenced-configs-summary.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(S) + '\n')
print('\n'.join(S))
