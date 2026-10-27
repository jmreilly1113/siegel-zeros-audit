"""Claims ledger v16 (2026-10-27): the repository tag of the paper's final version. Writes ledger-v16.tsv (refuses to overwrite).

Usage: python -I results/2026-10-26-claims-ledger/build_ledger_v16.py <repo root>
Append-only: every ledger-v15.tsv row is copied byte-for-byte; new row L275.
The tag paper-v1 is created on the commit that adds this file; a row cannot name the hash of the commit that contains it, so the
hash is recorded after tagging, in docs/log.md (`git rev-parse paper-v1^{commit}`).
"""
import csv, os, sys
root = sys.argv[1]
OUT = os.path.join(root, 'results', '2026-10-26-claims-ledger')
with open(os.path.join(OUT, 'ledger-v15.tsv'), encoding='utf-8') as f:
    rd = csv.reader(f, delimiter='\t'); cols = next(rd); rows = [dict(zip(cols, r)) for r in rd]
assert [r['id'] for r in rows] == [f'L{k:03d}' for k in range(1, 275)]
n = dict(id='L275', paper_section='9', claim='The repository state of the paper\'s final version is tagged paper-v1 (Joe, 2026-10-27: "tag name paper-v1"); the tag is created on the commit that adds ledger-v16.tsv.',
         value='paper-v1', unit='git tag', source='git tag paper-v1 (annotated, created after this ledger is committed); hash recorded in docs/log.md after tagging',
         label='COMPUTED', openai_math_commit='n/a', toolchain='n/a', sandbox='n/a', status='FOUND',
         note='the row is written before the tag exists; docs/log.md records `git rev-parse paper-v1^{commit}` after tagging', read_by='', read_note='')
p = os.path.join(OUT, 'ledger-v16.tsv')
if os.path.exists(p): sys.exit(f'refusing to overwrite {p}')
with open(p, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t', lineterminator='\n'); w.writerow(cols)
    for r in rows + [n]: w.writerow([r[c] for c in cols])
print('rows', len(rows) + 1, 'new L275')
