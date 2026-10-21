"""Paper prep 4, Task 9: every number the corpus paper cites, recomputed from result files, with cross-checks.

Usage: python -I scripts/paper_numbers.py <repo root> <out dir>   -> <out dir>/paper-numbers.json and numbers.tex
Each number carries its source file. The asserts encode the counts in results/2026-10-20-paper-prep-3/summary.txt;
a failing assert means a source disagrees with an earlier result (STOP and re-derive).
"""
import csv, json, os, re, sys

P3 = 'results/2026-10-20-paper-prep-3'
P4 = 'results/2026-10-21-paper-prep-4'
NINE = {'OptimalMaxCut', 'UniqueGamesTheorem', 'VertexCover', 'KaplanskyFinitelyPresented', 'GroupRingDeterminant', 'Laughlin',
        'BinPackingGap', 'IndependentSets', 'PerfectCompleteness'}


def compute(root):
    rd = lambda p: open(os.path.join(root, p), encoding='utf-8').read()
    tsv = lambda p: list(csv.DictReader((l for l in open(os.path.join(root, p), encoding='utf-8') if not l.startswith('#')), delimiter='\t'))
    N = {}

    def put(name, value, src):
        N[name] = {'value': value, 'source': src}

    t189 = tsv(f'{P3}/corpus-189.tsv')
    src = f'{P3}/corpus-189.tsv'
    put('NRefConfigs', len(t189), src)
    put('NLeanAccept', sum(r['lean_kernel'] == 'ACCEPT' for r in t189), src)
    put('NNanodaPinnedAccept', sum(r['nanoda_3a24072'] == 'ACCEPT' for r in t189), src)
    crash = {r['config'] for r in t189 if r['nanoda_3a24072'].startswith('CRASH') and r['nanoda_f67473b'] == 'ACCEPT'}
    put('NCrashNine', len(crash), src)
    put('NRunAtAdc', sum(r['commit_run_at'] == 'adc7f12' for r in t189), src)
    put('NRunAtFd', sum(r['commit_run_at'] == 'fd4aeeb' for r in t189), src)

    cx = rd(f'{P4}/nanoda55-crosscheck.txt')
    body = {m.group(1) for m in re.finditer(r'^  (\w+): IN THE ISSUE BODY', cx, re.M)}
    put('NInIssueFiftyFive', len(body & crash), f'{P4}/nanoda55-crosscheck.txt')
    put('NNanodaCommitsBetween', int(re.search(r'Commits 3a24072\.\.f67473b: (\d+)', cx).group(1)), f'{P4}/nanoda55-crosscheck.txt')

    ns = tsv(f'{P4}/nanoda-settings.tsv')
    src = f'{P4}/nanoda-settings.tsv'
    for c, tag in (('adc7f12', 'Adc'), ('fd4aeeb', 'Fd')):
        rows = [r for r in ns if r['commit'] == c]
        put(f'NConfigsOnDisk{tag}', len(rows), src)
        put(f'NNanodaFalse{tag}', sum(r['setting'] == 'false' for r in rows), src)
        put(f'NNanodaTrue{tag}', sum(r['setting'] == 'true' for r in rows), src)
        put(f'NNanodaAbsent{tag}', sum(r['setting'] in ('', 'absent') for r in rows), src)
        put(f'NRefConfigs{tag}', sum(r['referenced_by_yaml_at_commit'] == 'True' for r in rows), src)
    put('NNanodaTrueRefFd', sum(r['commit'] == 'fd4aeeb' and r['referenced_by_yaml_at_commit'] == 'True' and r['setting'] == 'true' for r in ns), src)

    cat = rd(f'{P4}/corpus-catalog-fd4aeeb-findings.txt')
    src = f'{P4}/corpus-catalog-fd4aeeb-findings.txt'
    m = re.search(r'sources (\d+); main_results (\d+); distinct configs (\d+)', cat)
    put('NSources', int(m.group(1)), src); put('NMainResults', int(m.group(2)), src); put('NDistinctConfigsYaml', int(m.group(3)), src)
    put('NMultiEntryConfigs', int(re.search(r'configs referenced by more than one entry: (\d+)', cat).group(1)), src)

    sc = rd(f'{P4}/corpus-static-scan-fd4aeeb-findings.txt')
    src = f'{P4}/corpus-static-scan-fd4aeeb-findings.txt'
    put('NScanFiles', int(re.search(r'files scanned: (\d+)', sc).group(1)), src)
    put('NUnsafeHits', int(re.search(r'^  unsafe\s+(\d+) hits', sc, re.M).group(1)), src)
    put('NConfigsReachingHit', sum(int(x) for x in re.findall(r'^  \S.*?\s+(\d+) configs$', sc, re.M)), src)
    put('NSorryEqNamed', int(re.search(r'sorry count == named theorems\+definitions: (\d+)', sc).group(1)), src)

    co = rd(f'{P4}/cost-summary.txt')
    src = f'{P4}/cost-summary.txt'
    pb = re.search(r'corpus prebuilds.*?: (\d+) builds; wall n \d+; min \d+ s; median ([\d.]+) s; p90 \d+ s \(nearest rank\); max (\d+) s; total \d+ s \(([\d.]+) h\)', co)
    put('NPrebuilds', int(pb.group(1)), src); put('PrebuildMedianS', pb.group(2), src); put('PrebuildMaxS', pb.group(3), src); put('PrebuildTotalH', pb.group(4), src)
    rp = re.search(r'fd4aeeb, 187 configs: n (\d+); min \d+ s; median ([\d.]+) s; p90 (\d+) s \(nearest rank\); max (\d+) s; total \d+ s \(([\d.]+) h\)', co)
    put('NReplaysFd', int(rp.group(1)), src); put('ReplayMedianS', rp.group(2), src); put('ReplayPNinetyS', rp.group(3), src)
    put('ReplayMaxS', rp.group(4), src); put('ReplayTotalH', rp.group(5), src)
    pf = re.search(r'9 configs: n (\d+); .*?total \d+ s \(([\d.]+) h\)', co)
    put('PostfixTotalH', pf.group(2), src)

    v = {k: d['value'] for k, d in N.items()}
    # Cross-checks against results/2026-10-20-paper-prep-3/summary.txt and the Task 1/2/6 outputs.
    assert v['NRefConfigs'] == 189 and v['NRefConfigsFd'] == 189 and v['NDistinctConfigsYaml'] == 189
    assert v['NLeanAccept'] == 189
    assert v['NNanodaPinnedAccept'] == 180 and v['NCrashNine'] == 9 and v['NNanodaPinnedAccept'] + v['NCrashNine'] == v['NRefConfigs']
    assert crash == NINE
    assert v['NInIssueFiftyFive'] == 7
    assert v['NRunAtAdc'] == 2 and v['NRunAtFd'] == 187 == v['NReplaysFd']
    assert v['NConfigsOnDiskAdc'] == 405 and v['NNanodaFalseAdc'] == 402
    assert v['NConfigsOnDiskFd'] == 416 and v['NNanodaTrueRefFd'] == 1
    assert v['NConfigsReachingHit'] == 0
    return N


def tex(N):
    out = ['% Generated by scripts/paper_numbers.py; do not edit by hand. Sources in paper-numbers.json.']
    for k, d in N.items():
        assert re.fullmatch(r'[A-Za-z]+', k), k
        out.append(f'\\newcommand{{\\{k}}}{{{d["value"]}}}  % {d["source"]}')
    return '\n'.join(out) + '\n'


if __name__ == '__main__':
    root, out = sys.argv[1:3]
    N = compute(root)
    os.makedirs(out, exist_ok=True)
    json.dump(N, open(os.path.join(out, 'paper-numbers.json'), 'w', encoding='utf-8', newline='\n'), indent=1)
    open(os.path.join(out, 'numbers.tex'), 'w', encoding='utf-8', newline='\n').write(tex(N))
    print(f'{len(N)} numbers; all asserts passed')
    for k, d in N.items():
        print(f'  {k} = {d["value"]}')
