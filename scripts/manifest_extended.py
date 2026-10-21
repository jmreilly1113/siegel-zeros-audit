"""Extended replay, Phase 0.1: manifest-extended.json (same fields as manifest-final.json, values taken live) and its diff.

Usage: python -I scripts/manifest_extended.py <repo root> <out dir>
Inputs: <out dir>/phase0-provenance.tsv (wsl-comparator/110_provenance.sh), <out dir>/phase1/phase0-probe-*.log
(107_run.sh probe), `wsl --version` output in <out dir>/phase0-wsl-version.txt. Writes manifest-extended.json and
manifest-diff.txt; refuses to overwrite. STOP (c) fields: openai/math commit (must be fd4aeeb), lean-toolchain, Comparator
commit, nanoda commit (pinned binary hash = 3a24072's), exporter commit, landrun commit, lake-manifest hash, sandbox
wrapper command, uid. A WSL kernel change is reported without stopping; timestamps and source/note fields are ignored.
"""
import copy, glob, json, os, re, sys

root, out = sys.argv[1:3]
for f in ('manifest-extended.json', 'manifest-diff.txt'):
    if os.path.exists(os.path.join(out, f)): sys.exit(f'refusing to overwrite {f}')
old = json.load(open(os.path.join(root, 'results', '2026-10-21-paper-prep-4', 'manifest-final.json'), encoding='utf-8'))
pv = dict(l.rstrip('\n').split('\t', 1) for l in open(os.path.join(out, 'phase0-provenance.tsv'), encoding='utf-8') if '\t' in l)
probe = sorted(glob.glob(os.path.join(out, 'phase1', 'phase0-probe-*.log')))[0]
pt = open(probe, encoding='utf-8').read()
inner = lambda k: (re.search(r'^INNER ' + re.escape(k) + r':?\s*(.*)$', pt, re.M) or [None, 'MISSING'])[1].strip()
wv = open(os.path.join(out, 'phase0-wsl-version.txt'), encoding='utf-8', errors='replace').read().replace('\0', '')
rel = lambda p: os.path.relpath(p, root).replace(os.sep, '/')
SRC = rel(os.path.join(out, 'phase0-provenance.tsv'))

m = copy.deepcopy(old)
m['openai_math'] = {'fd4aeeb': pv['clone_head'], 'clone_status_lines': pv['clone_status_lines'], 'source': SRC}
m['lean_toolchain'] = {'file': pv['lean_toolchain_file'], 'lean': pv['lean_version'], 'elan': pv['elan_version'], 'source': SRC}
m['lake_manifest'] = {'sha256': pv['lake_manifest_sha256'], 'mathlib_rev': pv['mathlib_rev'], 'packages': int(pv['lake_manifest_packages']), 'source': SRC}
m['comparator'] = {'commit': pv['comparator_commit'], 'tag': pv['comparator_tag'], 'binary_sha256': pv['comparator_binary_sha256'], 'source': SRC}
m['exporter'] = {'name': 'lean4export', 'commit': pv['exporter_commit'], 'tag': pv['exporter_tag'], 'binary_sha256': pv['exporter_binary_sha256'], 'source': SRC}
m['nanoda_3a24072'] = {'binary_sha256': pv['nanoda_pinned_binary_sha256'], 'source': SRC}
m['nanoda_f67473b'] = {'binary_sha256': pv['nanoda_postfix_binary_sha256'], 'source': SRC}
m['landrun'] = {'commit': pv['landrun_commit'], 'git_describe': pv['landrun_describe'], 'self_reported_version': pv['landrun_version'].split()[-1],
                'binary_sha256': pv['landrun_binary_sha256'], 'source': SRC}
m['platform'] = {'wsl': (re.search(r'WSL version: (\S+)', wv) or [None, 'MISSING'])[1], 'wsl_kernel': pv['wsl_kernel'], 'distro': pv['distro'],
                 'systemd': pv['systemd'].replace('systemd ', ''), 'windows': (re.search(r'Windows version: (\S+)', wv) or [None, 'MISSING'])[1]}
m['sandbox'] = {'wrapper_systemd_run_line': pv['wrapper_systemd_run_line'], 'wrapper_67_sha256': pv['wrapper_67_sha256'],
                'sbx_75_sha256': pv['wrapper_75sbx_sha256'], 'source': 'wsl-comparator/67_corpus_run.sh and 75_sbx.sh, used unchanged by 114_extended_replay.sh'}
m['identity_and_network_self_test'] = {'probe 2026-10-21': {'log': rel(probe), 'id': inner('id'), 'CapEff': inner('CapEff'), 'NoNewPrivs': inner('NoNewPrivs'),
                                       'kernel': inner('kernel'), 'netblock': {n: inner('netblock ' + n) for n in ('tcp 1.1.1.1:443', 'python AF_INET udp socket', 'python AF_INET6 socket', 'python AF_UNIX socket')}}}
m.pop('missing_fields', None)

oldid = old['identity_and_network_self_test']['fd4aeeb nanoda copy, post-hoc (2026-10-20)']
newid = m['identity_and_network_self_test']['probe 2026-10-21']
# Both sides normalized the same way. Attempt 1 unescaped \$ on the new side only (manifest_final.py had unescaped \" only),
# so the same source line looked different: results/2026-10-21-extended-replay/manifest-diff-attempt1-escaping-artifact.txt.
norm = lambda x: x.replace('\\"', '"').replace('\\$', '$').rstrip('"').strip()
old_line = norm(re.search(r'systemd-run .*', old['sandbox']['wrapper_command_line']).group(0))
new_line = norm(pv['wrapper_systemd_run_line'])
checks = [  # (field, old, new, stop?)
    ('openai/math commit', old['openai_math']['fd4aeeb'], m['openai_math']['fd4aeeb'], True),
    ('clone clean (status lines)', '0', pv['clone_status_lines'], True),
    ('lean-toolchain', old['lean_toolchain']['file'].split(' (')[0], m['lean_toolchain']['file'], True),
    ('Lean version', old['lean_toolchain']['lean'].split(',')[1].strip().split()[-1], re.search(r'commit (\w+)', m['lean_toolchain']['lean']).group(1), True),
    ('Comparator commit', old['comparator']['commit'], m['comparator']['commit'], True),
    ('Comparator binary', old['comparator']['binary_sha256'], m['comparator']['binary_sha256'], True),
    ('nanoda 3a24072 binary', old['nanoda_3a24072']['binary_sha256'], m['nanoda_3a24072']['binary_sha256'], True),
    ('nanoda f67473b binary', old['nanoda_f67473b']['binary_sha256'], m['nanoda_f67473b']['binary_sha256'], True),
    ('exporter commit', old['exporter']['commit'], m['exporter']['commit'], True),
    ('exporter binary', old['exporter']['binary_sha256'], m['exporter']['binary_sha256'], True),
    ('landrun commit', old['landrun']['commit'], m['landrun']['commit'], True),
    ('landrun binary', old['landrun']['binary_sha256'], m['landrun']['binary_sha256'], True),
    ('lake-manifest sha256', old['lake_manifest']['sha256'], m['lake_manifest']['sha256'], True),
    ('mathlib rev', old['lake_manifest']['mathlib_rev'], m['lake_manifest']['mathlib_rev'], True),
    ('sandbox systemd-run line', old_line, new_line, True),
    ('67_corpus_run.sh sha256 (last changed in 30dbb30, 2026-10-11)', '5626871e435b055474e290f81f8bec7502ddf4fc944af4e77178f550a2abaf89', pv['wrapper_67_sha256'], True),
    ('uid', oldid['id'], newid['id'], True),
    ('CapEff', oldid['CapEff'], newid['CapEff'], True),
    ('NoNewPrivs', oldid['NoNewPrivs'], newid['NoNewPrivs'], True),
] + [(f'netblock {k}', oldid['netblock'][k], newid['netblock'][k], True) for k in oldid['netblock']] + [
    ('WSL kernel', old['platform']['wsl_kernel'], m['platform']['wsl_kernel'], False),
    ('WSL version', old['platform']['wsl'], m['platform']['wsl'], False),
    ('distro', old['platform']['distro'], m['platform']['distro'], False),
    ('systemd', old['platform']['systemd'], m['platform']['systemd'], False),
    ('Windows', old['platform']['windows'].split()[0], m['platform']['windows'], False),
]
L = ['Extended replay, Phase 0.1: manifest-extended.json vs results/2026-10-21-paper-prep-4/manifest-final.json (COMPUTED; scripts/manifest_extended.py)', '']
stop = []
for f, a, b, s in checks:
    same = str(a).strip() == str(b).strip()
    L.append(f'{"same" if same else ("DIFFERENT" if s else "different (report only)")}\t{f}\t{a}' + ('' if same else f'\t-> {b}'))
    if not same and s: stop.append(f)
L.append('')
L.append('STOP (c): ' + (f'YES, fields {stop}' if stop else 'no; every STOP field is identical'))
m['diff_vs_manifest_final'] = {'stop_c': bool(stop), 'stop_fields': stop, 'detail': rel(os.path.join(out, 'manifest-diff.txt'))}
json.dump(m, open(os.path.join(out, 'manifest-extended.json'), 'w', encoding='utf-8', newline='\n'), indent=2, ensure_ascii=False)
open(os.path.join(out, 'manifest-diff.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
print('\n'.join(L))
sys.exit(3 if stop else 0)
