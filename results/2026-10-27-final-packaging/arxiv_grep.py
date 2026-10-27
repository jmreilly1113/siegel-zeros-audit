"""Step 4 grep (2026-10-27) of paper/arxiv/*: the ledger-id pattern v[0-9]+:L[0-9]{3}, "Claude", "ledger", and unescaped %.
Unescaped % inside Verbatim blocks is marked (literal there). Writes <folder>/arxiv-grep.txt (refuses to overwrite).

Usage: python -I results/2026-10-27-final-packaging/arxiv_grep.py <repo root> <folder under results/2026-10-27-final-packaging>
"""
import glob, os, re, sys
root, sub = sys.argv[1], sys.argv[2]
PATS = [('ledger id', r'v[0-9]+:L[0-9]{3}'), ('Claude', r'Claude'), ('ledger', r'ledger'), ('unescaped %', r'(?<!\\)%')]
out = []
for p in sorted(glob.glob(os.path.join(root, 'paper', 'arxiv', '*'))):
    verb = False
    for n, line in enumerate(open(p, encoding='utf-8').read().split('\n'), 1):
        for k, pat in PATS:
            if re.search(pat, line):
                out.append(f'{k}\t{os.path.basename(p)}:{n}\t{"in Verbatim; " if verb and k == "unescaped %" else ""}{line[:170]}')
        if re.match(r'^\s*\\begin\{Verbatim\}', line): verb = True
        elif line.startswith('\\end{Verbatim}'): verb = False
f = os.path.join(root, 'results', '2026-10-27-final-packaging', sub, 'arxiv-grep.txt')
with open(f, 'x', encoding='utf-8', newline='\n') as o:
    o.write(f'# Step 4 grep of paper/arxiv/ (2026-10-27). Command: python -I results/2026-10-27-final-packaging/arxiv_grep.py . {sub}\n')
    o.write('# hits by pattern: ' + str({k: sum(1 for x in out if x.startswith(k + '\t')) for k, _ in PATS}) + '\n')
    o.write(''.join(x + '\n' for x in out))
print(open(f, encoding='utf-8').read())
