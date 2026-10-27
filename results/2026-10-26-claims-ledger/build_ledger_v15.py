"""Claims ledger v15 (2026-10-27): the arXiv:2610.15483 citation with its author, by Joe's decision. Writes ledger-v15.tsv.

Usage: python -I results/2026-10-26-claims-ledger/build_ledger_v15.py <repo root>
Append-only: every ledger-v14.tsv row is copied byte-for-byte; new row L274 supersedes v12:L268 (which is unchanged).
"""
import csv, os, sys
root = sys.argv[1]
OUT = os.path.join(root, 'results', '2026-10-26-claims-ledger')
def line_of(path, sub):
    L = open(os.path.join(root, path), 'rb').read().replace(b'\r\n', b'\n').decode('utf-8').split('\n')
    hits = [i + 1 for i, l in enumerate(L) if sub in l]
    assert len(hits) == 1, (path, sub, hits)
    return f'{path}:{hits[0]}'
with open(os.path.join(OUT, 'ledger-v14.tsv'), encoding='utf-8') as f:
    rd = csv.reader(f, delimiter='\t'); cols = next(rd); rows = [dict(zip(cols, r)) for r in rd]
assert [r['id'] for r in rows] == [f'L{k:03d}' for k in range(1, 274)]
o = {r['id']: r for r in rows}['L268']
n = dict(o)
n.update(id='L274', status='FOUND',
         claim='Citation identity of arXiv:2610.15483: v1, dated October 11, 2026, DOI 10.48550/arXiv.2610.15483, author as listed on the abstract page.',
         value='arXiv:2610.15483 v1 (October 11, 2026); doi:10.48550/arXiv.2610.15483; author as listed by arXiv',
         source=o['source'] + '; ' + line_of('paper/draft/refs-sources/arxiv-2610.15483.json', '"authors"') + '; ' + line_of('docs/log.md', 'arXiv:2610.15483: "A bibliography entry for an arXiv paper normally carries the author as arXiv lists them'),
         note='supersedes v12:L268 (whose note said "cite by arXiv number only"). By Joe\'s decision of 2026-10-27 the bibliography entry carries the author; the text cites the work by a citation key', read_by='', read_note='')
p = os.path.join(OUT, 'ledger-v15.tsv')
if os.path.exists(p): sys.exit(f'refusing to overwrite {p}')
with open(p, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t', lineterminator='\n'); w.writerow(cols)
    for r in rows + [n]: w.writerow([r[c] for c in cols])
print('rows', len(rows) + 1, 'new L274')
