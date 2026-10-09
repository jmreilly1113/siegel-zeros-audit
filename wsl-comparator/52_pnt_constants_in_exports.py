"""Read-only heuristic (exploratory): which constants declared in the patched PrimeNumberTheoremAnd/SiegelZeros
files occur in existing lean4export dumps?

Names are reconstructed from source text: `namespace X` / `section` / `end` blocks plus the declared name of each
`theorem`/`lemma`/`def`/`abbrev`/`instance`/`structure`/`class`/`inductive` (private declarations skipped,
since their names are mangled). Within one Lean environment a full name is unique, so an exact match in an
export is a constant from these files, unless the reconstruction produced a wrong name that happens to equal
another constant's name. This is a text heuristic, not a Lean-level check.

Usage: python3 -I 52_pnt_constants_in_exports.py <PNT package dir> <export.ndjson> [<export.ndjson> ...]
"""
import json, os, re, sys

pnt, exports = sys.argv[1], sys.argv[2:]
d = os.path.join(pnt, 'PrimeNumberTheoremAnd', 'SiegelZeros')
files = sorted(f for f in os.listdir(d) if f.endswith('.lean'))


def strip_comments(src):
    out, i, depth, n = [], 0, 0, len(src)
    while i < n:
        if src.startswith('/-', i):
            depth += 1; i += 2; continue
        if depth and src.startswith('-/', i):
            depth -= 1; i += 2; continue
        if depth:
            i += 1; continue
        if src.startswith('--', i):
            j = src.find('\n', i); i = n if j < 0 else j; continue
        out.append(src[i]); i += 1
    return ''.join(out)


decl_re = re.compile(r"^(?:@\[[^\]]*\]\s*)?((?:private|protected|noncomputable|nonrec|unsafe|partial)\s+)*"
                     r"(theorem|lemma|def|abbrev|instance|structure|class|inductive)\s+([^\s:({\[]+)")
declared = {}
for f in files:
    stack = []  # entries: ('ns', [parts]) or ('sec', None)
    for line in strip_comments(open(os.path.join(d, f), encoding='utf-8').read()).split('\n'):
        s = line.strip()
        m = re.match(r'^namespace\s+(\S+)', s)
        if m:
            stack.append(('ns', m.group(1).split('.'))); continue
        m = re.match(r'^(noncomputable\s+)?section\b', s)
        if m:
            stack.append(('sec', None)); continue
        if re.match(r'^end\b', s) and stack:
            stack.pop(); continue
        m = decl_re.match(s)
        if m and m.group(3) not in ('where',):
            mods = m.group(1) or ''
            if 'private' in mods:
                continue
            name = m.group(3)
            if m.group(2) == 'instance' and (name.startswith(':') or name in ('(', '[')):
                continue
            prefix = [p for kind, parts in stack if kind == 'ns' for p in parts]
            full = name[len('_root_.'):] if name.startswith('_root_.') else '.'.join(prefix + [name])
            declared[full] = f
print(f'patched files: {len(files)} .lean files in {d}')
print(f'public declaration names reconstructed: {len(declared)}')
hs = sorted(n for n, f in declared.items() if f == 'HadamardSupport.lean')
print(f'  of which in HadamardSupport.lean: {len(hs)}')

for e in exports:
    names, decl_ids = {}, []
    for l in open(e, encoding='utf-8'):
        if l.startswith('{"in"') or '"str":{"pre"' in l[:40]:
            o = json.loads(l)
            if 'str' in o and isinstance(o['str'], dict):
                p = o['str']['pre']
                names[o['in']] = (names[p] + '.' if p in names else '') + o['str']['str']
            continue
        for k in ('"thm"', '"def"', '"opaque"', '"axiom"', '"inductive"'):
            if l.startswith('{' + k):
                o = json.loads(l)[k.strip('"')]
                if isinstance(o, dict) and 'name' in o:
                    decl_ids.append(o['name'])
                if k == '"inductive"':
                    for t in o.get('types', []):
                        decl_ids.append(t['name'])
                break
    decls = {names.get(i) for i in decl_ids}
    hits = sorted(n for n in declared if n in decls)
    by_file = {}
    for n in hits:
        by_file[declared[n]] = by_file.get(declared[n], 0) + 1
    print(f'\n== {e}: {len(decls)} declarations')
    print(f'  constants from patched PNT SiegelZeros files present: {len(hits)}; by file: {dict(sorted(by_file.items()))}')
    print(f'  from HadamardSupport.lean: {[n for n in hits if declared[n] == "HadamardSupport.lean"][:12]}')
