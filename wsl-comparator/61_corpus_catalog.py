"""Corpus checks, phase 1 (read-only, no build): consistency of lean/formalization.yaml.

Usage: python3 -I 61_corpus_catalog.py <openai/math lean dir> <out.tsv>
Checks per status.main_results entry: config exists, file exists, declaration found in the file
(HEURISTIC text match: the last name component after a theorem/lemma/def/abbrev/instance/structure
keyword, and whether the enclosing namespaces seen in the file can produce the full name).
Also: configs on disk not referenced, references with no config, sources[].id paths, withdrawn titles.
"""
import glob, os, re, sys
import yaml

lean, out = sys.argv[1], sys.argv[2]
y = yaml.safe_load(open(os.path.join(lean, 'formalization.yaml'), encoding='utf-8'))
mr = y['status']['main_results']
print(f'yaml version {y.get("version")}; sources {len(y.get("sources", []))}; main_results {len(mr)}; '
      f'distinct configs {len({e.get("comparator_config") for e in mr})}; review status {y.get("review")}')

decl_kw = r'(?:theorem|lemma|def|abbrev|instance|structure|inductive|class|opaque|axiom)'


def namespaces_and_decls(src):
    """Return list of full names (namespace prefix + declared name) found by a line-based heuristic."""
    names, stack = [], []
    for line in src.split('\n'):
        s = line.strip()
        m = re.match(r'^namespace\s+(\S+)', s)
        if m:
            stack.append(('ns', m.group(1).split('.'))); continue
        if re.match(r'^(noncomputable\s+)?section\b', s):
            stack.append(('sec', None)); continue
        if re.match(r'^end\b', s) and stack:
            stack.pop(); continue
        m = re.match(r'^(?:@\[[^\]]*\]\s*)?(?:(?:private|protected|noncomputable|nonrec|unsafe|partial)\s+)*' + decl_kw + r'\s+([^\s:({\[]+)', s)
        if m:
            pre = [p for k, parts in stack if k == 'ns' for p in parts]
            n = m.group(1)
            names.append(n[7:] if n.startswith('_root_.') else '.'.join(pre + [n]))
    return names


rows = []
for e in mr:
    cfg, decl, f = e.get('comparator_config'), e.get('declaration'), e.get('file')
    cfg_ok = os.path.isfile(os.path.join(lean, cfg)) if cfg else False
    fp = os.path.join(lean, f) if f else ''
    file_ok = os.path.isfile(fp)
    last = decl.split('.')[-1] if decl else ''
    text_hit = full_hit = False
    if file_ok:
        src = open(fp, encoding='utf-8', errors='replace').read()
        text_hit = re.search(decl_kw + r'\s+(?:[\w.]*\.)?' + re.escape(last) + r'\b', src) is not None
        full_hit = decl in namespaces_and_decls(src)
    rows.append((cfg, decl, f, cfg_ok, file_ok, text_hit, full_hit))

with open(out, 'w', encoding='utf-8') as fh:
    fh.write('# Phase 1 catalog consistency. decl_text_match and decl_fullname_match are HEURISTIC text matches, not elaboration.\n')
    fh.write('comparator_config\tdeclaration\tfile\tconfig_exists\tfile_exists\tdecl_text_match\tdecl_fullname_match\n')
    for r in rows:
        fh.write('\t'.join(map(str, r)) + '\n')

def count(i): return sum(1 for r in rows if r[i])
print(f'entries: {len(rows)}; config exists {count(3)}; file exists {count(4)}; '
      f'declaration keyword+name text match (heuristic) {count(5)}; full-name namespace match (heuristic) {count(6)}')
for r in rows:
    if not (r[3] and r[4] and r[5]):
        print(f'  PROBLEM: {r}')
for r in rows:
    if r[3] and r[4] and r[5] and not r[6]:
        print(f'  full-name heuristic miss (text match found): {r[1]} in {r[2]}')

on_disk = {os.path.relpath(p, lean).replace(os.sep, '/') for p in glob.glob(os.path.join(lean, 'ComparatorChallenges', '*.json'))}
referenced = {r[0] for r in rows}
print(f'configs on disk: {len(on_disk)}; referenced: {len(referenced)}')
print(f'  on disk but not referenced: {sorted(on_disk - referenced)}')
print(f'  referenced but not on disk: {sorted(referenced - on_disk)}')
multi = {c: [r[1] for r in rows if r[0] == c] for c in referenced}
print(f'  configs referenced by more than one entry: {sum(1 for v in multi.values() if len(v) > 1)}')
for c, v in sorted(multi.items()):
    if len(v) > 1:
        print(f'    {c}: {v}')

srcs = y.get('sources', [])
bad = []
for s in srcs:
    p = os.path.normpath(os.path.join(lean, s['id'])) if not s['id'].startswith('http') else None
    if p is None or not os.path.isfile(p):
        bad.append(s['id'])
print(f'sources: {len(srcs)}; id resolves to an existing file: {len(srcs) - len(bad)}; not resolving: {bad}')

withdrawn = [('Weil classes on split abelian eightfolds', r'weil.*eightfold|eightfold.*weil'),
             ('Kuga-Satake algebraicity', r'kuga.?satake'),
             ('rational Hodge for products of K3 surfaces', r'hodge.*k3|k3.*hodge')]
raw = open(os.path.join(lean, 'formalization.yaml'), encoding='utf-8').read()
for title, pat in withdrawn:
    hits = [l.strip() for l in raw.split('\n') if re.search(pat, l, re.I)]
    print(f'withdrawn "{title}": yaml lines matching /{pat}/i: {len(hits)} {hits[:3]}')
pre = os.path.normpath(os.path.join(lean, '..', 'preprints'))
for title, pat in withdrawn:
    d = [x for x in os.listdir(pre) if re.search(pat, x, re.I)]
    print(f'  preprints/ folders matching: {d}')
