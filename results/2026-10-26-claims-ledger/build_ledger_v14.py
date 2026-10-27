"""Claims ledger v14 (2026-10-27): the paper's citation of Fischler. Writes ledger-v14.tsv (refuses to overwrite).

Usage: python -I results/2026-10-26-claims-ledger/build_ledger_v14.py <repo root>
Append-only: every ledger-v13.tsv row is copied byte-for-byte; new row L273.
"""
import csv, hashlib, os, sys

root = sys.argv[1]
OUT = os.path.join(root, 'results', '2026-10-26-claims-ledger')
TEX = 'refs/siegel-paper.tex'
raw = open(os.path.join(root, TEX), 'rb').read().replace(b'\r\n', b'\n'); L = raw.decode('utf-8').split('\n')
assert '\\cite[Theorem~1.1 and Lemma~1.3]{Fischler}' in L[154], L[154]
assert '\\bibitem{Fischler}' in L[735] and 'Interpolation on algebraic groups' in L[736] and 'Compos. Math. \\textbf{141} (2005), no.~4, 907--925.' in L[737] and 'S0010437X05001351' in L[738]
sha = hashlib.sha256(raw).hexdigest()
with open(os.path.join(OUT, 'ledger-v13.tsv'), encoding='utf-8') as f:
    rd = csv.reader(f, delimiter='\t'); cols = next(rd); rows = [dict(zip(cols, r)) for r in rd]
assert [r['id'] for r in rows] == [f'L{k:03d}' for k in range(1, 273)], 'ledger-v13.tsv ids are not L001-L272'
n = dict(id='L273', paper_section='2', claim='The paper cites S. Fischler, Interpolation on algebraic groups, Compos. Math. 141 (2005), no. 4, 907-925, as [Fischler, Theorem 1.1 and Lemma 1.3] at refs/siegel-paper.tex:155; its bibliography entry is at lines 736-739.',
         value='cited by the paper as [Fischler, Theorem 1.1 and Lemma 1.3]', unit='citation',
         source=f'{TEX}:155-155 (LF sha256 {sha}); {TEX}:736-739 (LF sha256 {sha})', label='STATED', openai_math_commit='adc7f1241b42e322a6451854ab7e4b4c146bf78a', toolchain='n/a', sandbox='n/a', status='FOUND',
         note='the theorem and lemma numbers inside Fischler\'s paper were not checked against a copy of it (citations-needed.md); the paper is cited only as the paper cites it', read_by='', read_note='')
p = os.path.join(OUT, 'ledger-v14.tsv')
if os.path.exists(p): sys.exit(f'refusing to overwrite {p}')
with open(p, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t', lineterminator='\n'); w.writerow(cols)
    for r in rows + [n]: w.writerow([r[c] for c in cols])
print('rows', len(rows) + 1, 'new L273')
