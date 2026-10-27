"""Claims ledger v7 (2026-10-27): Joe's sign-off of the six statement readings. Writes ledger-v7.tsv (refuses to overwrite).

Usage: python -I results/2026-10-26-claims-ledger/build_ledger_v7.py <repo root>
Append-only (id-stability.md):
  - every ledger-v6.tsv row is copied unchanged, except: read_by/read_note of v6:L002, L004, L006, L008 (whose value is
    already MATCH) are filled; v6:L100 and v6:L101 (value PENDING JOE READING) get status "SUPERSEDED by v7:Lxxx";
  - new rows L145 (Lemma 3) and L146 (Corollary 4) carry the value MATCH.
"""
import csv, os, sys, collections

root = sys.argv[1]
OUT = os.path.join(root, 'results', '2026-10-26-claims-ledger')
problems = []


def R(path, sub, nth=1):
    L = open(os.path.join(root, path), 'rb').read().replace(b'\r\n', b'\n').decode('utf-8', 'replace').split('\n')
    hits = [i + 1 for i, l in enumerate(L) if sub in l]
    if len(hits) < nth:
        problems.append(f'R not found: {path} :: {sub!r}'); return f'{path}:?'
    return f'{path}:{hits[nth - 1]}'


LOG = 'docs/log.md'; RD = 'results/2026-10-27-readings/readings-claude-code.md'
SIGN = 'Read by J. Reilly, 2026-10-27: MATCH'
with open(os.path.join(OUT, 'ledger-v6.tsv'), encoding='utf-8') as f:
    rd = csv.reader(f, delimiter='\t'); cols = next(rd); rows = [dict(zip(cols, r)) for r in rd]
assert [r['id'] for r in rows] == [f'L{k:03d}' for k in range(1, 145)], 'ledger-v6.tsv ids are not L001-L144'
byid = {r['id']: r for r in rows}

for i, logkey, rdkey in (('L002', 'QuasiRiemannHypothesis challenge vs the 7/8', '### 2. QuasiRiemannHypothesis'),
                         ('L004', 'DirichletSevenEighths challenge vs the 7/8', '### 3. DirichletSevenEighths'),
                         ('L006', 'HeckeSevenEighths challenge vs the 7/8', '### 4. HeckeSevenEighths'),
                         ('L008', 'SiegelZeros challenge vs Theorem 1 (tex 66-73): Read by J. Reilly', '### 1. SiegelZeros')):
    r = byid[i]; assert r['label'] == 'INFERRED' and r['value'].startswith('MATCH'), i
    r['read_note'] = f"earlier: read_by {r['read_by']}; {r['read_note']}"
    r['read_by'] = f'{SIGN} ({R(LOG, logkey)}; reading notes {R(RD, rdkey)})'

new = []
for i, old, sec, rdkey, logkey in (('L145', 'L100', 'Lemma3.interpolation (comparator copy) matches the paper\'s Lemma 3, tex 252-267, clause by clause.', '## Reading 5: Lemma3.interpolation vs tex 252-267', 'Lemma3.interpolation vs tex 252-267: Read by J. Reilly'),
                                   ('L146', 'L101', "Lemma3.rectangle (comparator copy) matches the paper's Corollary 4, tex 410-420.", '## Reading 6: Lemma3.rectangle vs tex 410-420', 'Lemma3.rectangle vs tex 410-420: Read by J. Reilly')):
    o = byid[old]; assert o['value'] == 'PENDING JOE READING' and o['status'] == 'FOUND', old
    o['status'] = f'SUPERSEDED by v7:{i}'
    n = dict(o); n.update(id=i, claim=sec, value='MATCH', status='FOUND',
                         source=o['source'] + '; ' + R(RD, rdkey) + '; ' + R(LOG, logkey),
                         note='replaces v6:' + old + ' (value was PENDING JOE READING)',
                         read_by=f'{SIGN} ({R(LOG, logkey)}; reading notes {R(RD, rdkey)})',
                         read_note=f"earlier: read_by {o['read_by']}")
    new.append(n)

if problems:
    print('PROBLEMS (ledger not written):'); print('\n'.join(problems)); sys.exit(1)
p = os.path.join(OUT, 'ledger-v7.tsv')
if os.path.exists(p): sys.exit(f'refusing to overwrite {p}')
with open(p, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t', lineterminator='\n'); w.writerow(cols)
    for r in rows + new: w.writerow([r[c] for c in cols])
print('rows', len(rows) + len(new), 'new', len(new), 'status', dict(collections.Counter(r['status'] for r in rows + new)))
for r in rows + new:
    if r['read_by']: print(r['id'], r['value'][:20], '|', r['read_by'][:110])
