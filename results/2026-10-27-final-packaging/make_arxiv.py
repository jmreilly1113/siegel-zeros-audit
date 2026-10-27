"""Step 4 of the final packaging (2026-10-27): write the arXiv source package paper/arxiv/ from paper/draft/.

Usage: python -I results/2026-10-27-final-packaging/make_arxiv.py <repo root>
Copies main.tex and every file it \\input s, with comments removed:
  - outside Verbatim blocks, a line whose first non-blank character is an unescaped % is deleted;
  - outside Verbatim blocks, an unescaped % and the rest of its line are removed, with the blanks before it;
  - Verbatim blocks (fvextra) are copied unchanged, since % is literal there.
The bibliography ships as main.bbl (copied from results/2026-10-27-final-packaging/draft-main.bbl, the bibtex output of the
final draft build), so neither refs.bib nor plainurl.bst is needed. Not copied: refs-sources/, check.py, the outline,
refs-checklist.md, tex-deps.md. Refuses to write if paper/arxiv/ exists.
"""
import hashlib, os, re, shutil, sys

root = sys.argv[1]
D = os.path.join(root, 'paper', 'draft'); A = os.path.join(root, 'paper', 'arxiv'); O = os.path.join(root, 'results', '2026-10-27-final-packaging')
if len(sys.argv) > 2: O = os.path.join(O, sys.argv[2])  # optional build folder, e.g. final: main.bbl comes from its draft-main.bbl
if os.path.exists(A): sys.exit(f'refusing to overwrite {A}')
main = open(os.path.join(D, 'main.tex'), encoding='utf-8').read()
inputs = re.findall(r'^\\input\{([^}]+)\}', main, re.M)
files = ['main.tex'] + [x + '.tex' for x in inputs]

def strip(text):
    out, verb = [], False
    for line in text.split('\n'):
        if verb:
            out.append(line)
            if line.startswith('\\end{Verbatim}'): verb = False
            continue
        if re.match(r'^\s*(?<!\\)%', line): continue
        m = re.search(r'(?<!\\)%', line)
        if m: line = line[:m.start()].rstrip()
        out.append(line)
        if re.match(r'^\s*\\begin\{Verbatim\}', line): verb = True
    return '\n'.join(out)

os.makedirs(A)
log = []
for f in files:
    src = open(os.path.join(D, f), encoding='utf-8').read()
    dst = strip(src)
    open(os.path.join(A, f), 'w', encoding='utf-8', newline='\n').write(dst)
    log.append(f'{f}\t{len(src.splitlines())} -> {len(dst.splitlines())} lines\tsha256 {hashlib.sha256(dst.encode()).hexdigest()}')
shutil.copyfile(os.path.join(O, 'draft-main.bbl'), os.path.join(A, 'main.bbl'))
log.append(f'main.bbl\tcopied from draft-main.bbl\tsha256 {hashlib.sha256(open(os.path.join(A, "main.bbl"), "rb").read()).hexdigest()}')
print('\n'.join(log))
