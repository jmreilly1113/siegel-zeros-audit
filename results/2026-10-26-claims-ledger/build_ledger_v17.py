"""Claims ledger v17 (2026-10-27): the paper's title and author block. Writes ledger-v17.tsv (refuses to overwrite).

Usage: python -I results/2026-10-26-claims-ledger/build_ledger_v17.py <repo root>
Append-only: every ledger-v16.tsv row is copied byte-for-byte; new row L276.
ledger-v16.tsv and ledger-v17.tsv are added in the same commit, which carries the tag paper-v1 (v16:L275).
"""
import csv, os, sys
root = sys.argv[1]
OUT = os.path.join(root, 'results', '2026-10-26-claims-ledger')
with open(os.path.join(OUT, 'ledger-v16.tsv'), encoding='utf-8') as f:
    rd = csv.reader(f, delimiter='\t'); cols = next(rd); rows = [dict(zip(cols, r)) for r in rd]
assert [r['id'] for r in rows] == [f'L{k:03d}' for k in range(1, 276)]
TITLE = 'Formalizing the interpolation lemma of the openai/math Landau–Siegel paper and substituting it into a Comparator-accepted proof'
n = dict(id='L276', paper_section='title',
         claim=f'The paper\'s title is "{TITLE}" and its author block is "Joseph M. Reilly \\\\ Northeastern University", with no email and an empty \\date{{}}; these are the author\'s decisions (Joe, 2026-10-27).',
         value=TITLE, unit='title', source='Joe, 2026-10-27: "\\title{' + TITLE + '} \\author{<name> \\\\ <affiliation> \\\\ <email, or omit>} \\date{<leave empty, or the posting date>}"; paper/draft/main.tex',
         label='STATED', openai_math_commit='n/a', toolchain='n/a', sandbox='n/a', status='FOUND',
         note='title verbatim from Joe (typeset with -- for the en dash); Joe gave the author block as a template: Claude Code filled the name and affiliation as in the repository\'s CITATION.cff (family-names Reilly, given-names Joseph M., affiliation Northeastern University), omitted the email (Joe: "or omit") and left the date empty (Joe: "leave empty")',
         read_by='', read_note='')
p = os.path.join(OUT, 'ledger-v17.tsv')
if os.path.exists(p): sys.exit(f'refusing to overwrite {p}')
with open(p, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t', lineterminator='\n'); w.writerow(cols)
    for r in rows + [n]: w.writerow([r[c] for c in cols])
print('rows', len(rows) + 1, 'new L276')
