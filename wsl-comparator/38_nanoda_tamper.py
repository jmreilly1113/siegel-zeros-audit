# Tamper control for nanoda: copy the export, replace the proof (value) of Lemma3.rectangle by the
# proof of Lemma3.interpolation. A real type checker must reject the result.
import json, sys
src, dst = sys.argv[1], sys.argv[2]
names = {}   # id -> full name
lines = open(src).read().splitlines()
for l in lines:
    if l.startswith('{"in"') or '"str":{"pre"' in l[:40]:
        o = json.loads(l)
        if 'str' in o and isinstance(o['str'], dict):
            pre = o['str']['pre']; s = o['str']['str']
            names[o['in']] = (names.get(pre, '') + '.' if pre else '') + s
ids = {v: k for k, v in names.items()}
rid, iid = ids['Lemma3.rectangle'], ids['Lemma3.interpolation']
thm = {}
for i, l in enumerate(lines):
    if l.startswith('{"thm"'):
        o = json.loads(l)['thm']
        if o['name'] in (rid, iid): thm[o['name']] = (i, o)
(ri, ro), (_, io) = thm[rid], thm[iid]
print('rectangle thm line', ri, 'value', ro['value'], '-> replaced by interpolation value', io['value'])
ro['value'] = io['value']
lines[ri] = json.dumps({'thm': ro}, separators=(',', ':'))
open(dst, 'w').write('\n'.join(lines) + '\n')
