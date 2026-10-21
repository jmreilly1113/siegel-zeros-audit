"""Paper prep 4, Task 2c: catalog and static-scan summaries at fd4aeeb, from the rerun outputs (read-only).

Usage: python -I scripts/section55_summaries.py <out dir>   (the dir holding the fd4aeeb rerun outputs and nanoda-settings.tsv)
"""
import ast, collections, csv, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
out = sys.argv[1]
P = lambda n: os.path.join(out, n)
cat = open(P('corpus-catalog-fd4aeeb-findings.txt'), encoding='utf-8').read()
scan = open(P('corpus-static-scan-fd4aeeb-findings.txt'), encoding='utf-8').read()
chal = open(P('corpus-challenge-scan-fd4aeeb.txt'), encoding='utf-8').read()
ref = {r['config'] for r in csv.DictReader(open(P('nanoda-settings.tsv'), encoding='utf-8'), delimiter='\t')
       if r['commit'] == 'fd4aeeb' and r['referenced_by_yaml_at_commit'] == 'True'}
assert len(ref) == 189
nr = ast.literal_eval(re.search(r'on disk but not referenced: (\[.*?\])', cat).group(1))
missing = ast.literal_eval(re.search(r'referenced but not on disk: (\[.*?\])', cat).group(1))
srcbad = ast.literal_eval(re.search(r'not resolving: (\[.*?\])', cat).group(1))
C = ['Paper prep 4, Task 2: catalog consistency at fd4aeeb (COMPUTED; Phase 1 rerun 2026-10-21, script 61_corpus_catalog.py unchanged)',
     'Inputs: results/2026-10-21-paper-prep-4/corpus-catalog-fd4aeeb-findings.txt and .tsv (run against /home/checker/math at fd4aeeb, clean).',
     'The original Phase 1 run (results/2026-10-11-corpus-catalog*.tsv/-findings.txt) was at adc7f12; this rerun replaces nothing.', '']
C += [l for l in cat.splitlines() if re.match(r'^(yaml version|entries:|configs on disk|sources:)', l)]
C.append(f'yaml/config/file mismatches: entries whose config or file is missing: '
         f'{re.search(r"entries: (\d+); config exists (\d+); file exists (\d+)", cat).groups()} (entries, config exists, file exists) -> none missing')
C.append('  declaration matches are HEURISTIC text matches: ' + re.search(r'declaration keyword\+name text match \(heuristic\) (\d+); full-name namespace match \(heuristic\) (\d+)', cat).group(0))
C += [l.strip() for l in cat.splitlines() if 'full-name heuristic miss' in l]
C.append(f'configs on disk not referenced: {len(nr)} (= 416 - 189)')
C.append(f'references with no config on disk: {len(missing)} {missing}')
C.append(f'unresolved sources[].id paths: {len(srcbad)} {srcbad}')
C.append('withdrawn-manuscript check (yaml lines matching each title):')
C += ['  ' + l.strip() for l in cat.splitlines() if l.startswith('withdrawn')]
C.append('  preprint folders that still exist for those titles (not referenced by the yaml):')
C += ['  ' + l.strip()[:300] for l in cat.splitlines() if 'preprints/ folders matching' in l]
C.append(f'configs referenced by more than one yaml entry: {re.search(r"configs referenced by more than one entry: (\d+)", cat).group(1)}')
open(P('catalog-summary.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(C) + '\n')

hits = {m.group(1).strip(): (int(m.group(2)), int(m.group(3))) for m in re.finditer(r'^  (\S.*?)\s+(\d+) hits in (\d+) files$', scan, re.M)}
confs = {m.group(1).strip(): int(m.group(2)) for m in re.finditer(r'^  (\S.*?)\s+(\d+) configs$', scan, re.M)}
unres = re.findall(r'^  ComparatorChallenges/(\w+)\.json: \[', scan, re.M)
S = ['Paper prep 4, Task 2: static scan at fd4aeeb (HEURISTIC; Phase 3 rerun 2026-10-21, scripts 63/64 unchanged; comments stripped,',
     'string literals not stripped; a hit is a review pointer, not a finding).',
     'Inputs: corpus-static-scan-fd4aeeb-findings.txt, corpus-static-scan-fd4aeeb.tsv, -challenges.tsv, corpus-challenge-scan-fd4aeeb.txt.',
     'The original Phase 3 run (results/2026-10-11-corpus-static-scan*) was at adc7f12.', '',
     re.search(r'^A\. files scanned.*$', scan, re.M).group(0), '',
     'Solution side: hits, and configs (of 416; of the 189 referenced) whose solution import closure reaches a hit:']
tsv = [r for r in csv.DictReader((l for l in open(P('corpus-static-scan-fd4aeeb.tsv'), encoding='utf-8') if not l.startswith('#')), delimiter='\t')]
for k, (h, f) in hits.items():
    refc = {c for r in tsv if r['pattern'] == k for c in (r['configs'].split(',') if r['configs'] else []) if c.split('/')[-1].replace('.json', '') in ref}
    S.append(f'  {k:32s} {h:3d} hits in {f:3d} files; configs reaching a hit: {confs.get(k, "?")} of 416, {len(refc)} of 189 referenced')
S.append(f'  closure mapping: computed for 416 configs; unresolved imports for {len(unres)}: {unres} '
         f'(referenced: {[u for u in unres if u in ref]}). For those, the mapping is incomplete; for all others it is the import-header closure.')
S.append('  The 5 "unsafe" hits are Aesop rule attributes (e.g. @[aesop ... unsafe apply]) in carleson ToMathlib files that no solution closure reaches (as in the adc7f12 run).')
S.append('')
S.append('Challenge side (416 challenge files), placeholder scan (corpus-challenge-scan-fd4aeeb.txt):')
for l in chal.splitlines():
    if l.startswith('  '):
        n = re.search(r'(\w+)\.lean', l).group(1)
        S.append(f'  {l.strip()}   [referenced at fd4aeeb: {n in ref}]')
S.append('  In referenced challenge files the only nonstandard placeholder is HarmonicGrowth (axiom mainStatement). NavierStokesVelocity '
         "(sorried def half) is NOT referenced by formalization.yaml at fd4aeeb; DefocusingNLS and ElementaryPositivity (sorried defs) are not referenced "
         'and their sorries are the intended definition_names stubs.')
mB = re.search(r"sorry count == named theorems\+definitions: (\d+); differs: (\[.*\])", scan)
S.append(f'  sorry count == named theorems + definitions in {mB.group(1)} of 416; differs (file, sorries, theorem names, definition names): {mB.group(2)}')
S.append('')
ch = [r for r in csv.DictReader((l for l in open(P('corpus-static-scan-fd4aeeb-challenges.tsv'), encoding='utf-8') if not l.startswith('#')), delimiter='\t')]
haz = [h for h in ch[0].keys() if h not in ('config', 'lines', 'custom_decls', 'theorem_decls', 'sorry', 'n_theorem_names', 'n_definition_names', 'sorry_eq_named')]
S.append('Challenge-file junk-value hazard pointers (number of challenge files with >= 1 occurrence; HEURISTIC):')
for h in haz:
    a = sum(1 for r in ch if int(r[h]) > 0)
    b = sum(1 for r in ch if int(r[h]) > 0 and r['config'].split('/')[-1][:-5] in ref)
    S.append(f'  {h:45s} all 416: {a:3d}; referenced 189: {b:3d}')
open(P('static-scan-summary.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(S) + '\n')

tx = lambda s: (s.replace('_', r'\_').replace('#', r'\#').replace('&', r'\&').replace('⁻¹', r'$^{-1}$')
                .replace('ℕ', r'$\mathbb{N}$').replace('"- "', '``$-$\'\''))
T = ['% Generated by scripts/section55_summaries.py (fd4aeeb rerun); do not edit by hand. HEURISTIC text scan.',
     r'\begin{tabular}{@{}lrrr@{}}', r'\toprule', r'Pattern (solution side) & Hits & Files & Referenced configs reached \\', r'\midrule']
for k, (h, f) in hits.items():
    refc = {c for r in tsv if r['pattern'] == k for c in (r['configs'].split(',') if r['configs'] else []) if c.split('/')[-1].replace('.json', '') in ref}
    T.append(f'{tx(k)} & {h} & {f} & {len(refc)} \\\\')
T += [r'\bottomrule', r'\end{tabular}', '', r'\begin{tabular}{@{}lrr@{}}', r'\toprule', r'Challenge-file hazard pointer & All 416 & Referenced 189 \\', r'\midrule']
for h in haz:
    a = sum(1 for r in ch if int(r[h]) > 0); b = sum(1 for r in ch if int(r[h]) > 0 and r['config'].split('/')[-1][:-5] in ref)
    T.append(f'{tx(h)} & {a} & {b} \\\\')
T += [r'\bottomrule', r'\end{tabular}']
open(P('tables-5-5.tex'), 'w', encoding='utf-8', newline='\n').write('\n'.join(T) + '\n')
print('\n'.join(C)); print(); print('\n'.join(S))
