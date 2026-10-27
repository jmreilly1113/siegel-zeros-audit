"""QuasiRiemannHypothesis: is the Comparator config, the challenge file and the solution's local import closure byte-identical
at openai/math adc7f12 and fd4aeeb? Read-only; no build. Reads blobs with `git show <commit>:<path>` from a local clone.

Usage (in WSL): python3 -I qrh_closure.py <clone> <out dir>
Closure: start from the challenge and solution modules of lean/ComparatorChallenges/QuasiRiemannHypothesis.json; follow the
`import` lines of every module whose file exists under lean/ in that commit (local modules). Imports with no local file are
external (Lake packages); they are pinned by lean/lake-manifest.json, and the files that build them are compared too.
"""
import hashlib, json, re, subprocess, sys
clone, out = sys.argv[1], sys.argv[2]
A = 'adc7f1241b42e322a6451854ab7e4b4c146bf78a'; F = 'fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb'
IMP = re.compile(r'^\s*(?:(?:public|private|meta)\s+)*import\s+(.+)$')


def show(c, p):
    r = subprocess.run(['git', '-C', clone, 'show', f'{c}:{p}'], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def closure(c):
    cfg = json.loads(show(c, 'lean/ComparatorChallenges/QuasiRiemannHypothesis.json'))
    todo = [cfg['challenge_module'], cfg['solution_module']]; local, ext = {}, set()
    while todo:
        m = todo.pop()
        if m in local or m in ext: continue
        b = show(c, 'lean/' + m.replace('.', '/') + '.lean')
        if b is None: ext.add(m); continue
        local[m] = hashlib.sha256(b).hexdigest()
        incomment = False
        for line in b.decode('utf-8', 'replace').split('\n'):
            s = line.strip()
            if incomment:
                if '-/' in s: incomment = False
                continue
            if s.startswith('/-'):
                incomment = '-/' not in s[2:]; continue
            if not s or s.startswith('--'): continue
            mm = IMP.match(line)
            if mm: todo += mm.group(1).split('--')[0].split(); continue
            if s.startswith(('module', 'prelude')): continue
            break  # end of the header
    return cfg, local, ext


ca, la, ea = closure(A); cf, lf, ef = closure(F)
BUILD = ['lean/lake-manifest.json', 'lean/lean-toolchain', 'lean/lakefile.lean', 'lean/lakefile.toml']
pa = subprocess.run(['git', '-C', clone, 'ls-tree', '-r', '--name-only', A, 'lean/patches'], capture_output=True, text=True).stdout.split()
pf = subprocess.run(['git', '-C', clone, 'ls-tree', '-r', '--name-only', F, 'lean/patches'], capture_output=True, text=True).stdout.split()
o = open(out + '/qrh-closure.tsv', 'x', encoding='utf-8', newline='\n')
o.write('kind\tname\tsha256_adc7f12\tsha256_fd4aeeb\tidentical\n')
o.write(f"config\tlean/ComparatorChallenges/QuasiRiemannHypothesis.json\t{hashlib.sha256(show(A, 'lean/ComparatorChallenges/QuasiRiemannHypothesis.json')).hexdigest()}\t{hashlib.sha256(show(F, 'lean/ComparatorChallenges/QuasiRiemannHypothesis.json')).hexdigest()}\t{show(A, 'lean/ComparatorChallenges/QuasiRiemannHypothesis.json') == show(F, 'lean/ComparatorChallenges/QuasiRiemannHypothesis.json')}\n")
for m in sorted(set(la) | set(lf)):
    o.write(f"local module\t{m}\t{la.get(m, 'absent')}\t{lf.get(m, 'absent')}\t{la.get(m) == lf.get(m)}\n")
for p in BUILD + sorted(set(pa) | set(pf)):
    a, f = show(A, p), show(F, p)
    o.write(f"build file\t{p}\t{hashlib.sha256(a).hexdigest() if a is not None else 'absent'}\t{hashlib.sha256(f).hexdigest() if f is not None else 'absent'}\t{a == f}\n")
o.close()
rows = [l.rstrip('\n').split('\t') for l in open(out + '/qrh-closure.tsv', encoding='utf-8')][1:]
with open(out + '/summary.txt', 'x', encoding='utf-8', newline='\n') as s:
    p = lambda *x: print(*x, file=s)
    p('# QuasiRiemannHypothesis closure, adc7f12 vs fd4aeeb (COMPUTED; read-only git show, no build)')
    p(f'# Command (WSL, as checker): python3 -I results/2026-10-27-qrh-closure/qrh_closure.py /home/checker/math results/2026-10-27-qrh-closure ; Python {sys.version.split()[0]}')
    p(f"# clone HEAD {subprocess.run(['git', '-C', clone, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()}")
    p(f'config identical: {rows[0][4]}; challenge {ca["challenge_module"]}, solution {ca["solution_module"]} (fd4aeeb: {cf["challenge_module"]}, {cf["solution_module"]})')
    p(f'local modules in closure: adc7f12 {len(la)}, fd4aeeb {len(lf)}; same module set: {set(la) == set(lf)}; identical files: {sum(r[4] == "True" for r in rows if r[0] == "local module")}; differing: {[r[1] for r in rows if r[0] == "local module" and r[4] != "True"]}')
    p(f'external imports (Lake packages): adc7f12 {len(ea)}, fd4aeeb {len(ef)}; same set: {ea == ef}; package roots: {sorted({m.split(".")[0] for m in ea | ef})}')
    p(f'build files (lake-manifest, toolchain, lakefiles, lean/patches/*): {[(r[1], r[4]) for r in rows if r[0] == "build file"]}')
    allsame = all(r[4] == 'True' or (r[0] == 'build file' and r[2] == r[3] == 'absent') for r in rows) and set(la) == set(lf) and ea == ef
    p(f'ALL IDENTICAL: {allsame}')
print(open(out + '/summary.txt', encoding='utf-8').read())
