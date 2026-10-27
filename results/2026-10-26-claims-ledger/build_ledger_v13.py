"""Claims ledger v13 (2026-10-27): the seventh reading signed off, and the author's statement on references. Writes ledger-v13.tsv.

Usage: python -I results/2026-10-26-claims-ledger/build_ledger_v13.py <repo root>
Append-only: every ledger-v12.tsv row is copied byte-for-byte; new rows L270-L272.
L270 repeats v12:L258 with read_by set (v12:L258 itself is unchanged, as in v10).
"""
import csv, os, sys

root = sys.argv[1]
OUT = os.path.join(root, 'results', '2026-10-26-claims-ledger')
LOG = 'docs/log.md'


def line_of(path, sub):
    L = open(os.path.join(root, path), 'rb').read().replace(b'\r\n', b'\n').decode('utf-8').split('\n')
    hits = [i + 1 for i, l in enumerate(L) if sub in l]
    assert len(hits) == 1, (path, sub, hits)
    return f'{path}:{hits[0]}'


with open(os.path.join(OUT, 'ledger-v12.tsv'), encoding='utf-8') as f:
    rd = csv.reader(f, delimiter='\t'); cols = next(rd); rows = [dict(zip(cols, r)) for r in rd]
assert [r['id'] for r in rows] == [f'L{k:03d}' for k in range(1, 270)], 'ledger-v12.tsv ids are not L001-L269'
o = {r['id']: r for r in rows}['L258']
sign = line_of(LOG, 'Read by J. Reilly, 2026-10-27: arXiv:2610.08144, cite with the framing sentence of v12:L258.')
n1 = dict(o); n1.update(id='L270', status='FOUND', read_by=f'Read by J. Reilly, 2026-10-27: cite with the framing sentence ({sign})', read_note='',
                        note='supersedes v12:L258 (same claim, value and source; read_by added). ' + o['note'])
stm = line_of(LOG, "Author's statement (J. Reilly, 2026-10-27): the author checked every reference against its source.")
n2 = dict(id='L271', paper_section='10', claim='The author states that he checked every reference against its source.', value="author's statement", unit='statement',
          source=stm, label='STATED', openai_math_commit='n/a', toolchain='n/a', sandbox='n/a', status='FOUND',
          note='source: the author (docs/log.md, 2026-10-27); not checked by Claude Code', read_by='J. Reilly (author statement)', read_note='')
drf = line_of(LOG, "## 2026-10-27: draft abstract, sections 1, 8, 10 (Claude Code, from Joe's point lists); ledger v12")
n3 = dict(id='L272', paper_section='10', claim="The author wrote the content of the abstract, the introduction, Section 8 and Section 10 as point lists, and Claude Code drafted the text from them (docs/log.md, 2026-10-27).",
          value='content: author; drafting: Claude Code', unit='authorship', source=drf, label='COMPUTED', openai_math_commit='n/a', toolchain='n/a', sandbox='n/a', status='FOUND',
          note='the prompts with the point lists are not in the repository; the log entry and the commit (Co-Authored-By trailer) record the drafting', read_by='', read_note='')
p = os.path.join(OUT, 'ledger-v13.tsv')
if os.path.exists(p): sys.exit(f'refusing to overwrite {p}')
with open(p, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t', lineterminator='\n'); w.writerow(cols)
    for r in rows + [n1, n2, n3]: w.writerow([r[c] for c in cols])
print('rows', len(rows) + 3, 'new L270 L271 L272')
