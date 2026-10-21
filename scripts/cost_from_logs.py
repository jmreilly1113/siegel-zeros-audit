"""Paper prep 4, Task 3: build and replay cost from existing logs only (read-only; nothing estimated).

Usage: python -I scripts/cost_from_logs.py <repo root> <out dir>
Reads results/*/...prebuild.log, <C>-nanoda.log, <C>-shipped.log, <C>-postfix.log (final runs only), the copied WSL guard
log and retained-disk.txt in <out dir>. Fields not present in the logs are reported as MISSING.
"""
import os, re, statistics, sys

root, out = sys.argv[1:3]
R = os.path.join(root, 'results')
rel = lambda p: os.path.relpath(p, root).replace(os.sep, '/')


def num(t, pat, last=True, cast=int):
    m = re.findall(pat, t)
    return cast(m[-1] if last else m[0]) if m else None


def disk_g(t):
    return [int(x) for x in re.findall(r'disk used(?: before| after|)?:\s*(\d+)G', t)]


stage_dirs = [('pilot adc7f12', '2026-10-11-corpus-pilot'), ('headline fd4aeeb', '2026-10-11-corpus-headline')]
stage_dirs += [(f'remainder {b}', f'2026-10-12-corpus-remainder/{b}') for b in sorted(os.listdir(os.path.join(R, '2026-10-12-corpus-remainder'))) if b.startswith('batch-')]
stage_dirs += [('postfix f67473b', '2026-10-20-nanoda-postfix-f67473b'), ('paper-prep rebuild 2026-10-20', '2026-10-20-paper-prep/wsl'),
               ('paper-prep-2 adc7f12 2026-10-20', '2026-10-20-paper-prep-2/wsl')]
rows = []
for stage, d in stage_dirs:
    D = os.path.join(R, d)
    for f in sorted(os.listdir(D)):
        p = os.path.join(D, f)
        if '.stopped' in f or '.interrupted' in f or not f.endswith('.log'):
            continue
        t = open(p, encoding='utf-8', errors='replace').read()
        if f.endswith('.prebuild.log'):
            kind, cfg = 'build', f[:-len('.prebuild.log')]
            secs = num(t, r'PREBUILD_SECONDS:\s*(\d+)')
        else:
            m = re.match(r'^(?:task3-|task4-)?([A-Za-z0-9]+?)(?:-(nanoda|shipped|postfix|comparator-bigenv|nanoda-direct|posthoc|adc7f12-shipped))?\.log$', f)
            if not m or not m.group(2):
                continue
            cfg, k = m.group(1), m.group(2)
            kind = {'nanoda': 'replay nanoda-3a24072+Lean', 'shipped': 'replay Lean-only (shipped config)',
                    'postfix': 'replay nanoda-f67473b+Lean', 'comparator-bigenv': 'diagnostic 3a24072 bigenv',
                    'nanoda-direct': 'diagnostic 3a24072 direct', 'posthoc': 'replay nanoda-3a24072+Lean (post-hoc)',
                    'adc7f12-shipped': 'replay Lean-only (shipped config)'}[k]
            secs = num(t, r'DURATION_SECONDS:\s*(\d+)')
        jobs = max([int(x) for x in re.findall(r'Build completed successfully \((\d+) jobs\)', t)] or [0]) or None
        dg = disk_g(t)
        rows.append(dict(stage=stage, kind=kind, config=cfg, seconds=secs, jobs=jobs, disk_max_G=max(dg) if dg else None, log=rel(p)))

os.makedirs(out, exist_ok=True)
with open(os.path.join(out, 'cost.tsv'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('stage\tkind\tconfig\twall_seconds\tmax_build_jobs\tWSL_disk_used_max_G\tlog\n')
    for r in rows:
        f.write('\t'.join('MISSING' if r[k] is None else str(r[k]) for k in ('stage', 'kind', 'config', 'seconds', 'jobs', 'disk_max_G', 'log')) + '\n')


def stats(xs):
    xs = sorted(xs)
    if not xs:
        return 'MISSING'
    p90 = xs[min(len(xs) - 1, int(round(0.9 * (len(xs) - 1))))]
    return (f'n {len(xs)}; min {xs[0]} s; median {statistics.median(xs):g} s; p90 {p90} s (nearest rank); max {xs[-1]} s; '
            f'total {sum(xs)} s ({sum(xs) / 3600:.2f} h)')


S = ['Paper prep 4, Task 3: cost from existing logs (COMPUTED; scripts/cost_from_logs.py; per-row data in cost.tsv)',
     'Scope: final runs only (stopped/interrupted logs excluded). Wall times are DURATION_SECONDS / PREBUILD_SECONDS as',
     'printed by the drivers. Nothing is estimated; anything not in a log is MISSING.', '']
corpus_build = [r for r in rows if r['kind'] == 'build' and r['stage'].split()[0] in ('pilot', 'headline', 'remainder')]
S.append('(a) Builds (prebuild = `lake build` of solution + challenge modules, LEAN_NUM_THREADS=4, in the sandbox):')
for label, sel in [('corpus prebuilds (pilot, headline, remainder)', corpus_build),
                   ('2026-10-20 paper-prep rebuilds (12 closures)', [r for r in rows if r['kind'] == 'build' and r['stage'].startswith('paper-prep rebuild')]),
                   ('2026-10-20 adc7f12 SiegelZeros rebuild', [r for r in rows if r['kind'] == 'build' and r['stage'].startswith('paper-prep-2')])]:
    secs = [r['seconds'] for r in sel if r['seconds'] is not None]
    jobs = [r['jobs'] for r in sel if r['jobs'] is not None]
    S.append(f'  {label}: {len(sel)} builds; wall {stats(secs)}')
    S.append(f'    job counts (largest "Build completed successfully (N jobs)" per log): {"MISSING" if not jobs else f"min {min(jobs)}, max {max(jobs)}, logs with a count {len(jobs)}/{len(sel)}"}')
    dmax = [r['disk_max_G'] for r in sel if r['disk_max_G'] is not None]
    S.append(f'    WSL filesystem "disk used" printed in these logs: {"MISSING" if not dmax else f"max {max(dmax)} G"} '
             '(whole WSL filesystem, not per-build footprint; a per-build footprint is MISSING)')
S.append('  The 2026-10-08 SiegelZeros build (first comparator run, includes build): see results/2026-10-08-lean-comparator-wsl.txt '
         '(26 min end to end); no PREBUILD_SECONDS line exists for it.')
S.append('')
S.append('(b) Replay wall time per config (comparator run on a prebuilt closure: export of challenge and solution, statement and')
S.append('    axiom checks, then the kernels). Per-kernel time inside one comparator run is NOT logged: MISSING.')
for label, sel in [('nanoda 3a24072 + Lean kernel (enable_nanoda copy), fd4aeeb, 187 configs',
                    [r for r in rows if r['kind'] == 'replay nanoda-3a24072+Lean' and r['stage'].split()[0] in ('headline', 'remainder')]),
                   ('nanoda 3a24072 + Lean kernel, pilot adc7f12', [r for r in rows if r['kind'] == 'replay nanoda-3a24072+Lean' and r['stage'].startswith('pilot')]),
                   ('Lean kernel only (shipped config), corpus', [r for r in rows if r['kind'] == 'replay Lean-only (shipped config)' and r['stage'].split()[0] in ('headline', 'remainder', 'pilot')]),
                   ('nanoda f67473b + Lean kernel (unofficial batch), 9 configs', [r for r in rows if r['kind'] == 'replay nanoda-f67473b+Lean'])]:
    secs = [r['seconds'] for r in sel if r['seconds'] is not None]
    S.append(f'  {label}: {stats(secs)}')
    top = sorted((r for r in sel if r['seconds'] is not None), key=lambda r: -r['seconds'])[:5]
    S.append('    five slowest: ' + '; '.join(f'{r["config"]} {r["seconds"]} s' for r in top))
S.append('  Note: for the 9 crash configs the 3a24072 figure is time to the nanoda abort plus the Lean kernel, not a completed nanoda check.')
S.append('')
S.append('(c) Peak memory: per-run peak RSS is not logged for any replay or build: MISSING.')
g = open(os.path.join(out, 'wsl-guard-log-copy.txt'), encoding='utf-8').read()
mem = [int(x) for x in re.findall(r'MemAvailable (\d+)MB', g)]
lim = re.findall(r'LIMIT: .*', g)
S.append(f'  System-level only (WSL guard log, copied as wsl-guard-log-copy.txt; samples every 30-600 s): MemAvailable min {min(mem)} MB, '
         f'max {max(mem)} MB over {len(mem)} samples; guard limit events: {len(lim)}.' if mem else '  guard log: MISSING')
S.append('  The static scan 63 prints /usr/bin/time "(s, KB)" for itself only (corpus-static-scan findings).')
S.append('')
S.append('(d) Disk used by retained builds now: see retained-disk.txt (du -sh, 2026-10-21): ' +
         ' | '.join(l.strip() for l in open(os.path.join(out, 'retained-disk.txt'), encoding='utf-8') if not l.startswith('#')))
open(os.path.join(out, 'cost-summary.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(S) + '\n')

def texrow(label, sel):
    xs = sorted(r['seconds'] for r in sel if r['seconds'] is not None)
    if not xs:
        return f'{label} & \\multicolumn{{6}}{{c}}{{MISSING}} \\\\'
    p90 = xs[min(len(xs) - 1, int(round(0.9 * (len(xs) - 1))))]
    return f'{label} & {len(xs)} & {xs[0]} & {statistics.median(xs):g} & {p90} & {xs[-1]} & {sum(xs) / 3600:.1f} \\\\'

tex = ['% Generated by scripts/cost_from_logs.py from existing logs; do not edit by hand. Seconds; total in hours.',
       r'\begin{tabular}{@{}lrrrrrr@{}}', r'\toprule', r'Run & $n$ & min & median & p90 & max & total (h) \\', r'\midrule',
       texrow('Prebuild (corpus)', corpus_build),
       texrow('Comparator, nanoda 3a24072 + Lean (fd4aeeb)', [r for r in rows if r['kind'] == 'replay nanoda-3a24072+Lean' and r['stage'].split()[0] in ('headline', 'remainder')]),
       texrow('Comparator, Lean only (shipped config)', [r for r in rows if r['kind'] == 'replay Lean-only (shipped config)' and r['stage'].split()[0] in ('headline', 'remainder', 'pilot')]),
       texrow('Comparator, nanoda f67473b + Lean (9)', [r for r in rows if r['kind'] == 'replay nanoda-f67473b+Lean']),
       r'\bottomrule', r'\end{tabular}']
open(os.path.join(out, 'tables-5-6.tex'), 'w', encoding='utf-8', newline='\n').write('\n'.join(tex) + '\n')
print('\n'.join(S))
