# Tamper control for nanoda: copy the export and replace the proof (value) of theorem A by that of theorem B.
# Usage: python3 40_nanoda_tamper_named.py src.ndjson dst.ndjson A B. A real type checker must reject dst.
import json, sys
src, dst, a, b = sys.argv[1:5]
names = {}
lines = open(src).read().splitlines()
for l in lines:
    if '"str":{"pre"' in l[:40]:
        o = json.loads(l)
        if 'str' in o and isinstance(o['str'], dict):
            pre = o['str']['pre']; s = o['str']['str']
            names[o['in']] = (names.get(pre, '') + '.' if pre else '') + s
ids = {v: k for k, v in names.items()}
aid, bid = ids[a], ids[b]
thm = {}
for i, l in enumerate(lines):
    if l.startswith('{"thm"'):
        o = json.loads(l)['thm']
        if o['name'] in (aid, bid): thm[o['name']] = (i, o)
(ai, ao), (_, bo) = thm[aid], thm[bid]
print(f'{a} thm line {ai} value {ao["value"]} -> replaced by value of {b}: {bo["value"]}')
ao['value'] = bo['value']
lines[ai] = json.dumps({'thm': ao}, separators=(',', ':'))
open(dst, 'w').write('\n'.join(lines) + '\n')
