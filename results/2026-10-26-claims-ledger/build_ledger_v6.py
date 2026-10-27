"""Claims ledger v6 (2026-10-27). Read-only on the repo; writes ledger-v6.tsv next to this file (refuses to overwrite).

Usage: python -I results/2026-10-26-claims-ledger/build_ledger_v6.py <repo root>
Append-only (id-stability.md): every ledger-v5.tsv row is copied unchanged; new rows take explicit ids from L143 on.
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


A_ = 'adc7f1241b42e322a6451854ab7e4b4c146bf78a'; F_ = 'fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb'
NR = 'n/a'; PH = 'results/2026-10-27-paper-hashes/paper-hashes.txt'
SZ = 'preprints/Uniform-exclusion-of-Landau-Siegel-zeros-October-1-2026/'; QR = 'preprints/The-Quasi-Riemann-Hypothesis-September-30-2026/'

with open(os.path.join(OUT, 'ledger-v5.tsv'), encoding='utf-8') as f:
    rd = csv.reader(f, delimiter='\t'); cols = next(rd); rows = [dict(zip(cols, r)) for r in rd]
assert [r['id'] for r in rows] == [f'L{k:03d}' for k in range(1, 143)], 'ledger-v5.tsv ids are not L001-L142'
new = []


def row(i, sec, claim, value, unit, src, label, commit, tc, sb, status='FOUND', note=''):
    new.append(dict(id=i, paper_section=sec, claim=claim, value=value, unit=unit, source='; '.join(src), label=label,
                    openai_math_commit=commit, toolchain=tc, sandbox=sb, status=status, note=note, read_by='', read_note=''))


NOTE = 'no version label: the scan for version-like text outside comments finds only words such as "inversion" and bibliography entries (listed in the results file)'
row('L143', '9', 'Citation identity of the paper (family 003): "Uniform exclusion of Landau--Siegel zeros", author OpenAI, \\date{October 1, 2026}, openai/math ' + SZ + 'paper.pdf; the PDF, build/paper.tex and README.md are byte-identical at adc7f12 and fd4aeeb, and refs/siegel-paper.tex and refs/siegel-paper.pdf equal them.',
    'paper.pdf sha256 fab9f6e84ece2a37d834b2c031d8eb14e81413d9f6270791e7b5468b295214ef (404812 bytes); build/paper.tex sha256 b011ba9c1f55ee2164292492c55e0c6d75c458eb30d4808808f9953823b8ded4; identical at both commits', 'sha256',
    [R(PH, SZ + 'paper.pdf: adc7f12 fab9f6e8'), R(PH, SZ + 'build/paper.tex: adc7f12 b011ba9c'), R(PH, SZ + 'README.md: adc7f12'), R(PH, 'build/paper.tex:34: \\title{Uniform exclusion of Landau--Siegel zeros}'),
     R(PH, 'build/paper.tex:35: \\author{OpenAI}'), R(PH, 'build/paper.tex:36: \\date{October 1, 2026}'), R(PH, 'local copy refs/siegel-paper.tex'), R(PH, 'local copy refs/siegel-paper.pdf')],
    'COMPUTED', A_ + ' and ' + F_, 'git show on /home/checker/math; Python 3.12.3 (WSL)', 'read-only', note=NOTE + '; closes the UNCONFIRMED version-label entry in citations-needed.md')
row('L144', '9', 'Citation identity of the 7/8 paper: "The Quasi-Riemann Hypothesis" (subtitle "A Zero-Free Half-Plane Re s > 7/8"), author OpenAI, \\date{30 September 2026}, openai/math ' + QR + 'paper.pdf; the PDF, build/paper.tex and README.md are byte-identical at adc7f12 and fd4aeeb.',
    'paper.pdf sha256 8fe93046f8cf5ef1ba5969c89addc02d76311adc4ee907509ff9cd96f7ec99e7 (1588969 bytes); build/paper.tex sha256 42a5ee0febca59fd1def55cfd6c6808c322ef4237d7726303ea52f711deac6a3; identical at both commits', 'sha256',
    [R(PH, QR + 'paper.pdf: adc7f12 8fe93046'), R(PH, QR + 'build/paper.tex: adc7f12 42a5ee0f'), R(PH, QR + 'README.md: adc7f12'), R(PH, 'build/paper.tex:29: \\title{The Quasi-Riemann Hypothesis'),
     R(PH, 'build/paper.tex:31: \\author{OpenAI}'), R(PH, 'build/paper.tex:32: \\date{30 September 2026}')],
    'COMPUTED', A_ + ' and ' + F_, 'git show on /home/checker/math; Python 3.12.3 (WSL)', 'read-only', note=NOTE + '; the October 5 companion (paper2) is a different paper (docs/log.md 2026-10-20) and is not covered here')

if problems:
    print('PROBLEMS (ledger not written):'); print('\n'.join(problems)); sys.exit(1)
p = os.path.join(OUT, 'ledger-v6.tsv')
if os.path.exists(p): sys.exit(f'refusing to overwrite {p}')
with open(p, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t', lineterminator='\n'); w.writerow(cols)
    for r in rows + new: w.writerow([r[c] for c in cols])
print('rows', len(rows) + len(new), 'new', len(new), dict(collections.Counter(r['label'] for r in new)))
