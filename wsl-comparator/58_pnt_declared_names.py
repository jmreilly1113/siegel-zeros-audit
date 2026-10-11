"""Read-only: write the public declaration names reconstructed from the patched
PrimeNumberTheoremAnd/SiegelZeros/*.lean files (same text heuristic as 52_pnt_constants_in_exports.py),
one per line, gzipped. Used by src/route_overlap.py to label PrimeNumberTheoremAnd-patch names.
Usage: python3 -I 58_pnt_declared_names.py <PNT package dir> <out.txt.gz>
"""
import gzip, os, re, sys

pnt, out = sys.argv[1], sys.argv[2]
d = os.path.join(pnt, 'PrimeNumberTheoremAnd', 'SiegelZeros')


def strip_comments(src):
    o, i, depth, n = [], 0, 0, len(src)
    while i < n:
        if src.startswith('/-', i):
            depth += 1; i += 2; continue
        if depth and src.startswith('-/', i):
            depth -= 1; i += 2; continue
        if depth:
            i += 1; continue
        if src.startswith('--', i):
            j = src.find('\n', i); i = n if j < 0 else j; continue
        o.append(src[i]); i += 1
    return ''.join(o)


decl_re = re.compile(r"^(?:@\[[^\]]*\]\s*)?((?:private|protected|noncomputable|nonrec|unsafe|partial)\s+)*"
                     r"(theorem|lemma|def|abbrev|instance|structure|class|inductive)\s+([^\s:({\[]+)")
names = set()
for f in sorted(x for x in os.listdir(d) if x.endswith('.lean')):
    stack = []
    for line in strip_comments(open(os.path.join(d, f), encoding='utf-8').read()).split('\n'):
        s = line.strip()
        m = re.match(r'^namespace\s+(\S+)', s)
        if m:
            stack.append(('ns', m.group(1).split('.'))); continue
        if re.match(r'^(noncomputable\s+)?section\b', s):
            stack.append(('sec', None)); continue
        if re.match(r'^end\b', s) and stack:
            stack.pop(); continue
        m = decl_re.match(s)
        if m and 'private' not in (m.group(1) or ''):
            name = m.group(3)
            if m.group(2) == 'instance' and (name.startswith(':') or name in ('(', '[')):
                continue
            prefix = [p for k, parts in stack if k == 'ns' for p in parts]
            names.add(name[7:] if name.startswith('_root_.') else '.'.join(prefix + [name]))
with gzip.open(out, 'wt', encoding='utf-8') as fh:
    fh.write('\n'.join(sorted(names)) + '\n')
print(f'{len(names)} names written to {out}')
