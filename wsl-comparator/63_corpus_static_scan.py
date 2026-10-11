"""Corpus checks, phase 3 (read-only, HEURISTIC text scans): solution sources and challenge files.

Usage: python3 -I 63_corpus_static_scan.py <openai/math lean dir> <toolchain src/lean dir> <out prefix>
A. Every .lean file under lean/OAI, plus the files created or changed by lake update's patches in
   lean/.lake/packages (per `git status --porcelain` of each package), with comments stripped (nested block
   comments handled; string literals are not stripped). Patterns below. Hits are mapped to configs whose
   solution module's import closure contains the hit's module (same header-only import parsing as
   43_bridge_import_closure.py / 50_module_closure.py).
B. Every challenge module named by a config: line count, custom def/structure/inductive/class/abbrev
   declarations, theorem/lemma declarations, `sorry` count, and junk-value hazard pointers.
Writes <out prefix>.tsv (per hit), <out prefix>-challenges.tsv, and prints summaries.
"""
import glob, json, os, re, subprocess, sys
from collections import Counter, defaultdict

lean, core, outp = sys.argv[1], sys.argv[2], sys.argv[3]
pkgs = os.path.join(lean, '.lake', 'packages')


def strip_comments(src):
    out, i, depth, n = [], 0, 0, len(src)
    while i < n:
        if src.startswith('/-', i):
            depth += 1; i += 2; continue
        if depth and src.startswith('-/', i):
            depth -= 1; i += 2; out.append(' '); continue
        if depth:
            if src[i] == '\n':
                out.append('\n')
            i += 1; continue
        if src.startswith('--', i):
            j = src.find('\n', i); i = n if j < 0 else j; continue
        out.append(src[i]); i += 1
    return ''.join(out)


PATTERNS = [
    ('native_decide', r'\bnative_decide\b'),
    ('decide_native_or_kernel_option', r'\bdecide\s*\+\s*native\b|\bdecide\s*\(\s*config\s*:=[^)]*kernel|\bnative\s*:=\s*true'),
    ('Lean.ofReduceBool', r'\bofReduceBool\b'),
    ('Lean.ofReduceNat', r'\bofReduceNat\b'),
    ('implemented_by', r'\bimplemented_by\b'),
    ('extern', r'@\[\s*extern\b|\bextern\s+"'),
    ('unsafe', r'\bunsafe\b'),
    ('set_option debug.*', r'\bset_option\s+debug\.'),
    ('skipKernelTC', r'\bskipKernelTC\b'),
    ('axiom declaration', r'^\s*(?:@\[[^\]]*\]\s*)?(?:(?:private|protected|noncomputable)\s+)*axiom\s+\S'),
    ('sorry', r'\bsorry\b'),
    ('admit', r'\badmit\b'),
    ('addDecl / addAndCompile', r'\baddDecl\b|\baddAndCompile\b'),
]
CRE = [(k, re.compile(p, re.M)) for k, p in PATTERNS]

# module -> file over OAI, toolchain, packages
modfile = {}
for base, tops in [(lean, ['OAI', 'ComparatorChallenges']), (core, ['Init', 'Lean', 'Std']), (os.path.join(core, 'lake'), ['Lake'])] + \
        [(os.path.join(pkgs, p), None) for p in sorted(os.listdir(pkgs))]:
    tops = tops or [d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d)) and not d.startswith('.')]
    for t in tops:
        for dp, dns, fs in os.walk(os.path.join(base, t)):
            dns[:] = [d for d in dns if not d.startswith('.')]
            for f in fs:
                if f.endswith('.lean'):
                    p = os.path.join(dp, f)
                    modfile.setdefault(os.path.relpath(p, base)[:-5].replace(os.sep, '.'), p)
    for f in os.listdir(base):
        if f.endswith('.lean'):
            modfile.setdefault(f[:-5], os.path.join(base, f))
fmod = {p: m for m, p in modfile.items()}

icache = {}
def imports(m):
    if m in icache:
        return icache[m]
    p = modfile.get(m)
    if p is None:
        icache[m] = None; return None
    toks = strip_comments(open(p, encoding='utf-8', errors='replace').read()).split()
    out, i = [], 0
    while i < len(toks) and toks[i] in ('module', 'prelude'):
        i += 1
    while i < len(toks):
        j = i
        while j < len(toks) and toks[j] in ('public', 'meta', 'private'):
            j += 1
        if j < len(toks) and toks[j] == 'import':
            j += 1
            if j < len(toks) and toks[j] == 'all':
                j += 1
            out.append(toks[j]); i = j + 1
        else:
            break
    icache[m] = out
    return out


def closure(roots):
    seen, missing, st = set(), set(), list(roots)
    while st:
        x = st.pop()
        if x in seen:
            continue
        seen.add(x)
        im = imports(x)
        if im is None:
            missing.add(x); continue
        st += im
    return seen, missing


# files to scan
scan = sorted(p for p in glob.glob(os.path.join(lean, 'OAI', '**', '*.lean'), recursive=True))
patched = []
for pk in sorted(os.listdir(pkgs)):
    d = os.path.join(pkgs, pk)
    r = subprocess.run(['git', '-c', 'safe.directory=*', '-C', d, 'status', '--porcelain', '--untracked-files=all'],
                       capture_output=True, text=True)
    for line in r.stdout.splitlines():
        f = line[3:].strip()
        if f.endswith('.lean') and os.path.isfile(os.path.join(d, f)):
            patched.append(os.path.join(d, f))
print(f'A. files scanned: {len(scan)} under lean/OAI + {len(patched)} .lean files created or changed by dependency patches')

hits = []  # (pattern, module, file, line no, line text)
for p in scan + patched:
    try:
        src = strip_comments(open(p, encoding='utf-8', errors='replace').read())
    except Exception as e:
        print('  read error', p, e); continue
    for k, rx in CRE:
        for m in rx.finditer(src):
            ln = src.count('\n', 0, m.start()) + 1
            text = src.split('\n')[ln - 1].strip()[:160]
            hits.append((k, fmod.get(p, '?'), os.path.relpath(p, lean), ln, text))
per = Counter(h[0] for h in hits)
print('pattern hit counts (comments stripped; HEURISTIC):')
for k, _ in PATTERNS:
    files = len({h[2] for h in hits if h[0] == k})
    print(f'  {k:<32} {per.get(k, 0):>7} hits in {files} files')

# map hit modules to configs
cfgs = {}
for p in sorted(glob.glob(os.path.join(lean, 'ComparatorChallenges', '*.json'))):
    cfgs[os.path.relpath(p, lean).replace(os.sep, '/')] = json.load(open(p, encoding='utf-8'))
cl, miss = {}, {}
for r, c in cfgs.items():
    roots = [c['solution_module']] + c.get('solution_imports', [])
    cl[r], miss[r] = closure(roots)
unres = {r: m for r, m in miss.items() if m}
print(f'solution-module import closures computed for {len(cl)} configs; configs with unresolved imports: {len(unres)}')
for r, m in list(unres.items())[:10]:
    print(f'  {r}: {sorted(m)[:5]}')
mod_cfgs = defaultdict(list)
hit_mods = {h[1] for h in hits}
for r, s in cl.items():
    for m in hit_mods & s:
        mod_cfgs[m].append(r)
with open(outp + '.tsv', 'w', encoding='utf-8') as fh:
    fh.write('# Phase 3A static scan hits (HEURISTIC text match, comments stripped). configs = configs whose solution import closure contains the module.\n')
    fh.write('pattern\tmodule\tfile\tline\tn_configs\tconfigs\ttext\n')
    for h in sorted(hits):
        cs = sorted(mod_cfgs.get(h[1], []))
        fh.write(f'{h[0]}\t{h[1]}\t{h[2]}\t{h[3]}\t{len(cs)}\t{",".join(c.split("/")[-1][:-5] for c in cs)}\t{h[4]}\n')
print('patterns by number of configs whose solution closure reaches a hit (HEURISTIC):')
for k, _ in PATTERNS:
    reach = {c for h in hits if h[0] == k for c in mod_cfgs.get(h[1], [])}
    print(f'  {k:<32} {len(reach)} configs')

# B. challenge files
HAZ = [('sInf', r'\bsInf\b|⨅'), ('sSup', r'\bsSup\b|⨆'), ('inverse ⁻¹', r'⁻¹'), ('division /', r'(?<![/-])/(?![/-])'),
       ('Nat subtraction (heuristic: "- " near ℕ)', r'ℕ[^\n]*\s-\s|\s-\s[^\n]*ℕ'), ('riemannZeta', r'\briemannZeta\b'),
       ('Classical.choose / epsilon', r'\bClassical\.choose\b|\bClassical\.epsilon\b|\bChoose\b|\bepsilon\b')]
rows = []
for r, c in sorted(cfgs.items()):
    p = os.path.join(lean, *c['challenge_module'].split('.')) + '.lean'
    raw = open(p, encoding='utf-8', errors='replace').read()
    src = strip_comments(raw)
    custom = len(re.findall(r'^\s*(?:@\[[^\]]*\]\s*)?(?:(?:private|protected|noncomputable)\s+)*(?:def|abbrev|structure|inductive|class|instance|opaque)\b', src, re.M))
    thms = len(re.findall(r'^\s*(?:@\[[^\]]*\]\s*)?(?:(?:private|protected)\s+)*(?:theorem|lemma)\b', src, re.M))
    nsorry = len(re.findall(r'\bsorry\b', src))
    hz = [len(re.findall(x, src)) for _, x in HAZ]
    stated = len(c.get('theorem_names', [])) + len(c.get('definition_names', []))
    rows.append((r, raw.count('\n') + 1, custom, thms, nsorry, len(c.get('theorem_names', [])), len(c.get('definition_names', [])), nsorry == stated, *hz))
with open(outp + '-challenges.tsv', 'w', encoding='utf-8') as fh:
    fh.write('# Phase 3B challenge-file scan (HEURISTIC; hazard columns are review pointers, not findings). sorry_eq_named = sorry count equals theorem_names + definition_names.\n')
    fh.write('\t'.join(['config', 'lines', 'custom_decls', 'theorem_decls', 'sorry', 'n_theorem_names', 'n_definition_names', 'sorry_eq_named'] + [h for h, _ in HAZ]) + '\n')
    for row in rows:
        fh.write('\t'.join(map(str, row)) + '\n')
print(f'B. challenge files: {len(rows)}; total lines {sum(r[1] for r in rows)}; largest: {max(rows, key=lambda r: r[1])[:2]}; '
      f'smallest: {min(rows, key=lambda r: r[1])[:2]}')
print(f'   sorry count == named theorems+definitions: {sum(1 for r in rows if r[7])}; differs: {[(r[0].split("/")[-1], r[4], r[5], r[6]) for r in rows if not r[7]][:40]}')
print('   hazard pointers (number of challenge files with >=1 occurrence): ' + ', '.join(f'{h} {sum(1 for r in rows if r[8 + i])}' for i, (h, _) in enumerate(HAZ)))
top = sorted(rows, key=lambda r: -r[1])[:5]
print('   five largest challenge files: ' + ', '.join(f'{r[0].split("/")[-1]} ({r[1]} lines)' for r in top))
