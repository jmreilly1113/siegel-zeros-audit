"""Tabulate corpus replay outcomes from the results files (no WSL access; reads logs and outcomes.tsv only).

Usage: python -I wsl-comparator/87_corpus_summary.py <repo root>
Prints tab-separated rows: stage, batch, config, in_sample, nanoda_run, shipped_run, config_outcome, evidence.
Finished batches use their outcomes.tsv. A batch without outcomes.tsv (still running) is classified with
75_classify.py's rules for configs that have a <name>.done marker only; other configs are listed as PENDING.
Batches of the merged schedule (results/2026-10-13-corpus-remainder-schedule-merged.json) not yet started: NOT_STARTED.
"""
import importlib.util, io, json, os, sys, contextlib

root = sys.argv[1]
res = os.path.join(root, 'results')
spec = importlib.util.spec_from_file_location('cls', os.path.join(root, 'wsl-comparator', '75_classify.py'))


def classify(d):
    """Run 75_classify.py on directory d and return its rows (as lists)."""
    m = importlib.util.module_from_spec(spec)
    buf = io.StringIO()
    old = sys.argv
    sys.argv = ['75_classify.py', d]
    try:
        with contextlib.redirect_stdout(buf):
            spec.loader.exec_module(m)
    finally:
        sys.argv = old
    return [l.split('\t') for l in buf.getvalue().splitlines()[1:]]


def rows_of(tsv):
    return [l.rstrip('\n').split('\t') for l in open(tsv, encoding='utf-8')][1:]


out = []
for r in rows_of(os.path.join(res, '2026-10-11-corpus-headline', 'outcomes.tsv')):
    out.append(['headline', '-'] + r[:2] + r[3:7])
rem = os.path.join(res, '2026-10-12-corpus-remainder')
for b in sorted(d for d in os.listdir(rem) if d.startswith('batch-')):
    bd = os.path.join(rem, b)
    plan = [l.split('\t')[0] for l in open(os.path.join(bd, 'plan.tsv'), encoding='utf-8')][1:]
    if os.path.isfile(os.path.join(bd, 'outcomes.tsv')):
        for r in rows_of(os.path.join(bd, 'outcomes.tsv')):
            out.append(['remainder', b] + r[:2] + r[3:7])
    else:
        got = {r[0]: r for r in classify(bd)}
        for n in plan:
            if os.path.isfile(os.path.join(bd, n + '.done')) and n in got:
                r = got[n]; out.append(['remainder', b + ' (running)'] + r[:2] + r[3:7])
            else:
                out.append(['remainder', b + ' (running)', n, '', '', '', 'PENDING', ''])
sched = json.load(open(os.path.join(res, '2026-10-13-corpus-remainder-schedule-merged.json')))
for k, b in enumerate(sched['batches'], 1):
    if not os.path.isfile(os.path.join(rem, 'batch-%02d' % k, 'plan.tsv')):
        for r in b:
            out.append(['remainder', 'batch-%02d (not started)' % k, r.split('/')[-1][:-5], '', '', '', 'NOT_STARTED', ''])
print('stage\tbatch\tconfig\tin_sample\tnanoda_run\tshipped_run\tconfig_outcome\tevidence')
for r in out:
    print('\t'.join(r))
