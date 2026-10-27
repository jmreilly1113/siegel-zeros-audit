"""Claims ledger v10 (2026-10-27): Joe's sign-off of the 47 reasoning rows. Writes ledger-v10.tsv (refuses to overwrite).

Usage: python -I results/2026-10-26-claims-ledger/build_ledger_v10.py <repo root>
Append-only. Per Joe's instruction ("Don't edit the old rows"), every ledger-v9.tsv row is copied byte-for-byte,
status included; the old rows v9:L203 and v8:L152-L197 are NOT marked superseded. Each new row L204-L250 repeats one of
them (claim, value, source, label) with read_by "Read by J. Reilly, 2026-10-27: agree" and a note naming the row it
supersedes. Cite the new rows from here on.
"""
import csv, os, sys

root = sys.argv[1]
OUT = os.path.join(root, 'results', '2026-10-26-claims-ledger')
LOG = 'docs/log.md'; MK = 'results/2026-10-27-readings/reasoning-marks.tsv'
SIGN = 'Read by J. Reilly, 2026-10-27: reasoning rows v9:L203 and v8:L152–L197, all agree.'


def line_of(path, sub):
    L = open(os.path.join(root, path), 'rb').read().replace(b'\r\n', b'\n').decode('utf-8').split('\n')
    hits = [i + 1 for i, l in enumerate(L) if sub in l]
    assert len(hits) == 1, (path, sub, hits)
    return f'{path}:{hits[0]}'


with open(os.path.join(OUT, 'ledger-v9.tsv'), encoding='utf-8') as f:
    rd = csv.reader(f, delimiter='\t'); cols = next(rd); rows = [dict(zip(cols, r)) for r in rd]
assert [r['id'] for r in rows] == [f'L{k:03d}' for k in range(1, 204)]
byid = {r['id']: r for r in rows}
marks = {r['id']: r for r in csv.DictReader(open(os.path.join(root, MK), encoding='utf-8'), delimiter='\t')}
logref = line_of(LOG, SIGN)
olds = [('v9', 'L203')] + [('v8', f'L{k:03d}') for k in range(152, 198)]
new = []
for k, (ver, old) in enumerate(olds):
    o = byid[old]; m = marks[f'{ver}:{old}']
    assert o['label'] == 'INFERRED' and o['read_by'] == '' and m['mark'] == 'agree' and m['note'].startswith('Read by J. Reilly, 2026-10-27'), old
    n = dict(o)
    n['id'] = f'L{204 + k:03d}'
    n['status'] = 'FOUND'
    n['read_by'] = f'Read by J. Reilly, 2026-10-27: agree ({logref}; {MK}, row {ver}:{old})'
    n['read_note'] = ''
    n['note'] = f'supersedes {ver}:{old} (same claim, value and source; read_by added). ' + o['note']
    new.append(n)
p = os.path.join(OUT, 'ledger-v10.tsv')
if os.path.exists(p): sys.exit(f'refusing to overwrite {p}')
with open(p, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t', lineterminator='\n'); w.writerow(cols)
    for r in rows + new: w.writerow([r[c] for c in cols])
print('rows', len(rows) + len(new), 'new', new[0]['id'], '-', new[-1]['id'], '(from', olds[0], 'to', olds[-1], ')')
