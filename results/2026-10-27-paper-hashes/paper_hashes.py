"""sha256 of the family-003 papers at openai/math adc7f12 and fd4aeeb, plus their title/author/date lines (2026-10-27).
Read-only: `git show <commit>:<path>` on a local clone.
Usage (WSL): python3 -I paper_hashes.py <clone> <repo root> <out file>"""
import hashlib, re, subprocess, sys
clone, repo, out = sys.argv[1:4]
A = 'adc7f1241b42e322a6451854ab7e4b4c146bf78a'; F = 'fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb'
P = [('Uniform exclusion of Landau-Siegel zeros', 'preprints/Uniform-exclusion-of-Landau-Siegel-zeros-October-1-2026/'),
     ('The Quasi-Riemann Hypothesis (September 30)', 'preprints/The-Quasi-Riemann-Hypothesis-September-30-2026/')]
HDR = re.compile(r'^\s*\\(title|author|date)\b')
VER = re.compile(r'version|revised|\bv\d+\.\d+\b', re.I)


def show(c, p):
    r = subprocess.run(['git', '-C', clone, 'show', f'{c}:{p}'], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def h(b): return hashlib.sha256(b).hexdigest() if b is not None else 'absent'


with open(out, 'x', encoding='utf-8', newline='\n') as o:
    def p(*x): print(*x, file=o)
    p('# Paper files at openai/math adc7f12 and fd4aeeb (COMPUTED, read-only git show; 2026-10-27)')
    p('# Command (WSL, as checker): python3 -I results/2026-10-27-paper-hashes/paper_hashes.py /home/checker/math /mnt/c/Users/Work/dev/siegel '
      '/mnt/c/Users/Work/dev/siegel/results/2026-10-27-paper-hashes/paper-hashes.txt ; Python ' + sys.version.split()[0])
    for name, d in P:
        p(f'## {name}: {d}')
        for f in ('paper.pdf', 'build/paper.tex', 'README.md'):
            a, b = show(A, d + f), show(F, d + f)
            p(f'{d}{f}: adc7f12 {h(a)} ({len(a) if a else 0} bytes); fd4aeeb {h(b)} ({len(b) if b else 0} bytes); identical {a == b}')
        t = show(F, d + 'build/paper.tex').decode('utf-8', 'replace').replace('\r\n', '\n').split('\n')
        for i, l in enumerate(t, 1):
            if HDR.match(l): p(f'  build/paper.tex:{i}: {l.strip()}')
        vl = [(i, l.strip()[:160]) for i, l in enumerate(t, 1) if VER.search(l) and not l.lstrip().startswith('%')]
        p(f'  version-like text outside comments: {len(vl)} lines' + ''.join(f'\n    build/paper.tex:{i}: {l}' for i, l in vl))
    for f, d in (('refs/siegel-paper.tex', P[0][1] + 'build/paper.tex'), ('refs/siegel-paper.pdf', P[0][1] + 'paper.pdf')):
        loc = open(repo + '/' + f, 'rb').read(); g = show(F, d)
        lf = loc.replace(b'\r\n', b'\n')
        p(f'local copy {f}: sha256 {h(loc)}; LF-normalised {h(lf)}; equals fd4aeeb {d}: {loc == g or lf == g}')
print(open(out, encoding='utf-8').read())
