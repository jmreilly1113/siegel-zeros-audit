"""Corpus checks, phase 3 supplement (read-only, HEURISTIC): the phase-3A patterns of 63_corpus_static_scan.py,
applied to the challenge files (lean/ComparatorChallenges/*.lean), comments stripped. Also locates `sorry`
occurrences that are not the body of a theorem/lemma (e.g. inside a def), as review pointers.
Usage: python3 -I 64_challenge_pattern_scan.py <openai/math lean dir>
"""
import glob, os, re, sys
lean = sys.argv[1]
def strip_comments(src):
    out, i, depth, n = [], 0, 0, len(src)
    while i < n:
        if src.startswith('/-', i): depth += 1; i += 2; continue
        if depth and src.startswith('-/', i): depth -= 1; i += 2; out.append(' '); continue
        if depth:
            if src[i] == '\n': out.append('\n')
            i += 1; continue
        if src.startswith('--', i):
            j = src.find('\n', i); i = n if j < 0 else j; continue
        out.append(src[i]); i += 1
    return ''.join(out)
PATTERNS = [('native_decide', r'\bnative_decide\b'), ('decide_native_or_kernel_option', r'\bdecide\s*\+\s*native\b|\bnative\s*:=\s*true'),
    ('Lean.ofReduceBool', r'\bofReduceBool\b'), ('Lean.ofReduceNat', r'\bofReduceNat\b'), ('implemented_by', r'\bimplemented_by\b'),
    ('extern', r'@\[\s*extern\b'), ('unsafe (keyword)', r'^\s*(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+)*unsafe\s+(?:def|theorem|opaque|instance)\b'),
    ('set_option debug.*', r'\bset_option\s+debug\.'), ('skipKernelTC', r'\bskipKernelTC\b'),
    ('axiom declaration', r'^\s*(?:@\[[^\]]*\]\s*)?(?:(?:private|protected|noncomputable)\s+)*axiom\s+\S'),
    ('admit', r'\badmit\b'), ('addDecl / addAndCompile', r'\baddDecl\b|\baddAndCompile\b')]
files = sorted(glob.glob(os.path.join(lean, 'ComparatorChallenges', '*.lean')))
print(f'challenge files: {len(files)}')
tot = {}
for p in files:
    src = strip_comments(open(p, encoding='utf-8', errors='replace').read())
    lines = src.split('\n')
    for k, rx in PATTERNS:
        for m in re.finditer(rx, src, re.M):
            ln = src.count('\n', 0, m.start()) + 1
            tot[k] = tot.get(k, 0) + 1
            print(f'  {k}: {os.path.basename(p)}:{ln}: {lines[ln-1].strip()[:150]}')
    # sorry not belonging to a theorem/lemma: find the nearest preceding declaration keyword
    for m in re.finditer(r'\bsorry\b', src):
        before = src[:m.start()]
        d = list(re.finditer(r'^\s*(?:@\[[^\]]*\]\s*)?(?:(?:private|protected|noncomputable)\s+)*(theorem|lemma|def|abbrev|instance|structure|inductive|opaque|example)\b\s*(\S*)', before, re.M))
        if d and d[-1].group(1) not in ('theorem', 'lemma'):
            ln = src.count('\n', 0, m.start()) + 1
            tot['sorry outside theorem/lemma'] = tot.get('sorry outside theorem/lemma', 0) + 1
            print(f'  sorry outside theorem/lemma: {os.path.basename(p)}:{ln} (in {d[-1].group(1)} {d[-1].group(2)}): {lines[ln-1].strip()[:150]}')
print('totals:', tot)
