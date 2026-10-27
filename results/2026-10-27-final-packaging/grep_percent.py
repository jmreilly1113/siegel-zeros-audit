"""Step 4 (2026-10-27): unescaped % in paper/arxiv/* (the shell grep in arxiv-grep.txt failed on quoting). Writes arxiv-grep-percent.txt.

Usage: python -I results/2026-10-27-final-packaging/grep_percent.py <repo root>
An unescaped % is a % not preceded by a backslash. Verbatim blocks are reported separately (% is literal there).
"""
import glob, os, re, sys
root = sys.argv[1]
out = []
for p in sorted(glob.glob(os.path.join(root, 'paper', 'arxiv', '*'))):
    verb = False
    for n, line in enumerate(open(p, encoding='utf-8').read().split('\n'), 1):
        if re.search(r'(?<!\\)%', line): out.append(f'{"in Verbatim" if verb else "outside Verbatim"}\t{os.path.basename(p)}:{n}\t{line[:150]}')
        if re.match(r'^\s*\\begin\{Verbatim\}', line): verb = True
        elif line.startswith('\\end{Verbatim}'): verb = False
f = os.path.join(root, 'results', '2026-10-27-final-packaging', 'arxiv-grep-percent.txt')
with open(f, 'x', encoding='utf-8', newline='\n') as o:
    o.write('# Unescaped % in paper/arxiv/ (2026-10-27). Command: python -I results/2026-10-27-final-packaging/grep_percent.py .\n')
    o.write(f'# hits: {len(out)}\n' + ''.join(x + '\n' for x in out))
print(open(f, encoding='utf-8').read())
