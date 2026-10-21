"""Recount corpus-replay outcomes from the raw per-config run logs (read-only on results/).

Usage: python -I scripts/recount.py <repo root>

Raw files read: every <Config>-nanoda*.log and <Config>-shipped*.log under
  results/2026-10-11-corpus-pilot, results/2026-10-11-corpus-headline (and its attempt*-guard-stopped dirs),
  results/2026-10-12-corpus-remainder/batch-*.
Each log is classified with the run rules of wsl-comparator/75_classify.py (copied verbatim by exec of its
function definitions; the file is not modified). The outcomes.tsv files are NOT used for the counts; they are
only compared against at the end.

Prints:
  (a) per-config outcome counts, after deduping by config name (the final, non-stopped run of each kind wins);
  (b) per-run counts (every log file, every batch, including stopped/interrupted and duplicate runs);
  (c) assertions that the category sums equal the config total;
  configs that appear in more than one batch directory.
"""
import collections, os, re, sys

root = sys.argv[1]
res = os.path.join(root, 'results')

# Load run_class / code / line from 75_classify.py without running its main part.
src = open(os.path.join(root, 'wsl-comparator', '75_classify.py'), encoding='utf-8').read()
ns = {'__name__': 'cls'}
exec(compile(src[:src.index('\nplan = ')], '75_classify.py', 'exec'), ns)
run_class = ns['run_class']

dirs = [('pilot', os.path.join(res, '2026-10-11-corpus-pilot'))]
hl = os.path.join(res, '2026-10-11-corpus-headline')
dirs += [('headline/' + d, os.path.join(hl, d)) for d in sorted(os.listdir(hl)) if d.startswith('attempt')]
dirs.append(('headline', hl))
rem = os.path.join(res, '2026-10-12-corpus-remainder')
dirs += [('remainder/' + d, os.path.join(rem, d)) for d in sorted(os.listdir(rem)) if d.startswith('batch-')]

pat = re.compile(r'^([A-Za-z0-9]+)-(nanoda|shipped)(\..*)?\.log$')
runs = []  # (batch, config, kind, variant, class, evidence)
for batch, d in dirs:
    for f in sorted(os.listdir(d)):
        m = pat.match(f)
        if not m:
            continue
        cfg, kind, var = m.group(1), m.group(2), (m.group(3) or '')[1:]
        ns['out'] = d  # run_class looks for GUARD_STOPPED.txt in the run's own directory
        c, ev = run_class(os.path.join(d, f), kind == 'nanoda')
        runs.append((batch, cfg, kind, var, c, ev))

# (b) per-run counts
print('== (b) per-run counts (every raw log file)')
by_batch = collections.defaultdict(collections.Counter)
for b, cfg, kind, var, c, ev in runs:
    by_batch[b][(kind, 'final' if not var else 'stopped/interrupted', c)] += 1
tot = collections.Counter()
for b in by_batch:
    for k, n in sorted(by_batch[b].items()):
        print(f'{b}\t{k[0]}\t{k[1]}\t{k[2]}\t{n}')
        tot[k] += n
print('-- all batches')
for k, n in sorted(tot.items()):
    print(f'ALL\t{k[0]}\t{k[1]}\t{k[2]}\t{n}')
print(f'total raw log files: {len(runs)}')

# configs in more than one batch directory
where = collections.defaultdict(set)
for b, cfg, *_ in runs:
    where[cfg].add(b)
multi = {c: sorted(v) for c, v in where.items() if len(v) > 1}
print('\n== configs with raw logs in more than one batch directory:', len(multi))
for c in sorted(multi):
    print(f'{c}\t' + ', '.join(multi[c]))

# (a) per-config outcome, deduped by config name. Official stages only (headline + remainder at fd4aeeb);
# pilot (adc7f12) reported separately. Final (non-stopped) runs only; a later directory in `dirs` order wins.
def outcome(stage_filter):
    final = {}
    for b, cfg, kind, var, c, ev in runs:
        if var or not stage_filter(b):
            continue
        final.setdefault(cfg, {})[kind] = (c, b)
    oc = {}
    for cfg, k in final.items():
        nr = k.get('nanoda', ('NOT_RUN', ''))[0]
        sr = k.get('shipped', ('NOT_RUN', ''))[0]
        if nr != 'ACCEPT_BOTH' and sr == 'ACCEPT_LEAN':
            oc[cfg] = 'ACCEPT_LEAN_ONLY'
        elif nr == 'NOT_RUN':
            oc[cfg] = 'SHIPPED_ONLY:' + sr
        else:
            oc[cfg] = nr
    return final, oc

print('\n== (a) per-config outcomes, deduped by config name')
fd_final, fd = outcome(lambda b: b.startswith('headline') or b.startswith('remainder'))
pi_final, pi = outcome(lambda b: b == 'pilot')
for name, oc in [('fd4aeeb (headline + remainder)', fd), ('pilot (adc7f12)', pi)]:
    cnt = collections.Counter(oc.values())
    print(f'-- {name}: {len(oc)} configs')
    for k, n in sorted(cnt.items()):
        print(f'   {k}\t{n}')
    assert sum(cnt.values()) == len(oc), 'category sum != config total'
    print(f'   (c) assertion OK: sum of categories {sum(cnt.values())} == config total {len(oc)}')
both = sorted(set(fd) & set(pi))
print(f'-- configs in both the pilot and fd4aeeb stages: {both}')
for stage in ('headline', 'remainder'):
    sub = {c: o for c, o in fd.items() if any(fd_final[c][k][1].startswith(stage) for k in fd_final[c])}
    cnt = collections.Counter(sub.values())
    print(f'-- by stage {stage}: {len(sub)} configs: ' + ', '.join(f'{k} {n}' for k, n in sorted(cnt.items())))
non_both = sorted(c for c, o in fd.items() if o != 'ACCEPT_BOTH')
print('-- fd4aeeb configs not ACCEPT_BOTH:', non_both)

# compare against the batch outcomes.tsv files (consistency check only)
print('\n== cross-check against outcomes.tsv (config_outcome column)')
tsv = {}
for b, d in dirs:
    p = os.path.join(d, 'outcomes.tsv')
    if b.startswith('headline/') or b == 'pilot' or not os.path.isfile(p):
        continue
    for l in open(p, encoding='utf-8').read().splitlines()[1:]:
        r = l.split('\t')
        tsv[r[0]] = r[5]
diff = sorted((c, fd.get(c), tsv.get(c)) for c in set(fd) | set(tsv) if fd.get(c) != tsv.get(c))
print(f'outcomes.tsv rows: {len(tsv)}; recount configs: {len(fd)}; differences: {len(diff)}')
for x in diff:
    print('   DIFF', x)
