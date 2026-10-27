"""Outcome-level comparison with nealmcb/openai-math-lean-tooling at 1ca7ff2 (2026-10-27). Reads files only.

Usage: python -I results/2026-10-27-neal-comparison/compare_outcomes.py <repo root> <nealmcb checkout at 1ca7ff2>
The checkout is untrusted data: it is read as JSON/text only, nothing in it is executed.
Verdict compared: does Comparator (Lean kernel) accept the config?
  ours:   189 = results/2026-10-20-corpus-summary-final.tsv (187, fd4aeeb) + the adc7f12 pilot (SiegelZeros, QuasiRiemannHypothesis);
          227 = corpus-227-v3.tsv final_outcome, with lean_kernel_here (the optional Lean-kernel runs on Catalan, KMedianThreshold)
          ACCEPT_BOTH / ACCEPT_LEAN_ONLY / LEAN_ACCEPT_NANODA_CRASH / ACCEPT_LEAN -> accept; TIMEOUT / NOT_CHECKED_HERE -> no verdict
  his:    results/cmp-all/all.jsonl 'outcome' ('accepted' -> accept; anything else is reported as is)
"""
import csv, hashlib, json, os, subprocess, sys, collections
root, nr = sys.argv[1], sys.argv[2]
out = os.path.join(root, 'results', '2026-10-27-neal-comparison')
def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()
head = subprocess.run(['git', '-C', nr, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
assert head == '1ca7ff2a0280760783ee2b198c0d6f2a1cfeaba4', head
dirty = subprocess.run(['git', '-C', nr, 'status', '--porcelain'], capture_output=True, text=True).stdout
his_p = os.path.join(nr, 'results', 'cmp-all', 'all.jsonl')
his = {}
for l in open(his_p, encoding='utf-8'):
    if l.strip():
        r = json.loads(l); assert r['config'] not in his, r['config']; his[r['config']] = r
ours = {}
for r in csv.DictReader(open(os.path.join(root, 'results/2026-10-20-corpus-summary-final.tsv'), encoding='utf-8'), delimiter='\t'):
    ours[r['config']] = ('189', 'fd4aeeb', r['config_outcome'], 'results/2026-10-20-corpus-summary-final.tsv')
for c in ('SiegelZeros', 'QuasiRiemannHypothesis'):
    assert c not in ours
    ours[c] = ('189', 'adc7f12 (pilot)', 'ACCEPT_BOTH', 'results/2026-10-11-corpus-pilot-summary.txt')
for r in csv.DictReader(open(os.path.join(root, 'results/2026-10-26-nanoda-version-matrix/extended-replay-227/corpus-227-v3.tsv'), encoding='utf-8'), delimiter='\t'):
    assert r['config'] not in ours, r['config']
    o = r['final_outcome']
    if o == 'NOT_CHECKED_HERE' and r['lean_kernel_here'].startswith('ACCEPT_LEAN'): o = 'NOT_CHECKED_HERE; optional run ACCEPT_LEAN'
    ours[r['config']] = ('227', 'fd4aeeb', o, 'corpus-227-v3.tsv')
ACC = {'ACCEPT_BOTH', 'ACCEPT_LEAN_ONLY', 'LEAN_ACCEPT_NANODA_CRASH', 'NOT_CHECKED_HERE; optional run ACCEPT_LEAN'}
NOV = {'TIMEOUT', 'NOT_CHECKED_HERE'}
def ov(o): return 'accept' if o in ACC else ('none' if o in NOV else 'other:' + o)
def hv(r): return 'none' if r is None else ('accept' if r['outcome'] == 'accepted' else 'other:' + r['outcome'])
rows, cnt = [], collections.Counter()
for c in sorted(set(ours) | set(his)):
    o = ours.get(c); h = his.get(c)
    a = ov(o[2]) if o else 'none'; b = hv(h)
    if a == 'none' or b == 'none': cls = 'no verdict here' if a == 'none' and b != 'none' else ('no verdict there' if b == 'none' and a != 'none' else 'no verdict either side')
    elif a == b: cls = 'agree'
    else: cls = 'disagree'
    cnt[(o[0] if o else 'his only', cls)] += 1
    rows.append([c, o[0] if o else '', o[1] if o else '', o[2] if o else '', h['outcome'] if h else '', str(h.get('nanoda')) if h else '', str(h.get('cmp_s')) if h else '', cls])
with open(os.path.join(out, 'outcomes.tsv'), 'x', encoding='utf-8', newline='\n') as f:
    f.write('config\tour_set\tour_commit\tour_outcome\this_outcome\this_nanoda_flag\this_cmp_s\tclass\n')
    for r in rows: f.write('\t'.join(r) + '\n')
tot = collections.Counter(r[7] for r in rows)
with open(os.path.join(out, 'summary.txt'), 'x', encoding='utf-8', newline='\n') as f:
    p = lambda *a: print(*a, file=f)
    p('# Outcome-level comparison with nealmcb/openai-math-lean-tooling (2026-10-27; COMPUTED here, his side STATED)')
    p('# Command: python -I results/2026-10-27-neal-comparison/compare_outcomes.py . <checkout>; checkout = read-only git clone of https://github.com/nealmcb/openai-math-lean-tooling at ' + head + ' (git status --porcelain: ' + (repr(dirty) if dirty else 'clean') + ')')
    p(f'# his results/cmp-all/all.jsonl sha256 {sha(his_p)} ({len(his)} configs)')
    p('# verdict compared: Comparator (Lean kernel) accepts the config. ours: 189 (187 fd4aeeb + 2 adc7f12 pilot) + 227 (final_outcome, with the optional Lean-kernel runs)')
    p(f'configs: ours {len(ours)}, his {len(his)}, union {len(rows)}, in both {len(set(ours) & set(his))}')
    p('by class: ' + str(dict(tot)))
    p('by our set and class: ' + str(dict(sorted(cnt.items()))))
    p('his outcomes: ' + str(dict(collections.Counter(r['outcome'] for r in his.values()))) + '; his configs with nanoda flag true: ' + str(sorted(c for c, r in his.items() if r.get('nanoda'))))
    for k in ('disagree', 'no verdict here', 'no verdict there', 'no verdict either side'):
        p(f'{k}: ' + str([(r[0], r[3], r[4]) for r in rows if r[7] == k]))
    p('accepted here only through the optional Lean-kernel runs: ' + str([r[0] for r in rows if 'optional run' in r[3]]))
    p('pilot pair compared across commits (ours adc7f12, his fd4aeeb): ' + str([r[0] for r in rows if r[2].startswith('adc7f12')]))
print(open(os.path.join(out, 'summary.txt'), encoding='utf-8').read())
