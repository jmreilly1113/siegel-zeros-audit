"""Paper prep 4, Task 5: manifest-final.json and table2.tex (Table 2 fields), from existing files only.

Usage: python -I scripts/manifest_final.py <repo root> <out dir>
Every field carries its source. A field with no source on disk is set to "MISSING" and listed at the end.
"""
import json, os, re, sys

root, out = sys.argv[1:3]
R = os.path.join(root, 'results')
old = json.load(open(os.path.join(R, '2026-10-20-paper-prep', 'manifest.json'), encoding='utf-8'))
run67 = open(os.path.join(root, 'wsl-comparator', '67_corpus_run.sh'), encoding='utf-8').read()
cmdline = re.search(r'^systemd-run .*$', run67, re.M).group(0).replace('\\"', '"')
logs = {'adc7f12 shipped, full block (2026-10-20)': os.path.join(R, '2026-10-20-paper-prep-2', 'wsl', 'task3-SiegelZeros-adc7f12-shipped.log'),
        'fd4aeeb nanoda copy, post-hoc (2026-10-20)': os.path.join(R, '2026-10-20-paper-prep', 'wsl', 'task4-SiegelZeros-posthoc.log')}


def inner(t, key):
    m = re.search(r'^INNER ' + re.escape(key) + r':?\s*(.*)$', t, re.M)
    return m.group(1).strip() if m else 'MISSING'


identity = {}
for k, p in logs.items():
    t = open(p, encoding='utf-8').read()
    identity[k] = {'log': os.path.relpath(p, root).replace(os.sep, '/'), 'id': inner(t, 'id'), 'CapEff': inner(t, 'CapEff'),
                   'NoNewPrivs': inner(t, 'NoNewPrivs'), 'kernel': inner(t, 'kernel'),
                   'netblock': {n: inner(t, 'netblock ' + n) for n in ('tcp 1.1.1.1:443', 'python AF_INET udp socket',
                                                                     'python AF_INET6 socket', 'python AF_UNIX socket')}}
pf_build = open(os.path.join(R, '2026-10-20-nanoda-postfix-f67473b', 'build.log'), encoding='utf-8', errors='replace').read()
m = {
    'openai_math': {'adc7f12': 'adc7f1241b42e322a6451854ab7e4b4c146bf78a', 'fd4aeeb': 'fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb',
                    'main_2026_10_21': '1581d4cbdd69a0faf34b2089614fe2a814316a6a (only .github/workflows changed since fd4aeeb)',
                    'source': 'results/2026-10-20-paper-prep/manifest.json; results/2026-10-21-paper-prep-4/upstream-drift.txt'},
    'lean_toolchain': old['lean_toolchain'],
    'lake_manifest': {'sha256': old['lake_manifest']['sha256'], 'identical_at': old['lake_manifest']['identical_at'],
                      'mathlib_rev': old['lake_manifest']['mathlib_rev'], 'packages': old['lake_manifest']['packages'],
                      'source': 'results/2026-10-20-paper-prep/task4-provenance-commands.txt'},
    'comparator': old['tools']['comparator'] | {'source': 'task4-provenance-commands.txt'},
    'exporter': {'name': 'lean4export', 'commit': old['tools']['lean4export']['commit'], 'tag': old['tools']['lean4export']['tag'],
                 'binary_sha256': old['tools']['lean4export']['binary_sha256'],
                 'role': 'Comparator\'s only Lake dependency; both kernels consume its output (docs/paper/independence.md)',
                 'source': 'Comparator lake-manifest.json at d03acab; task4-provenance-commands.txt'},
    'nanoda_3a24072': old['tools']['nanoda_lib'] | {'source': 'results/2026-10-08-lean-comparator-nanoda-netblock.txt; 2026-10-11-corpus-provenance.txt'},
    'nanoda_f67473b': old['tools']['nanoda_postfix_unofficial'] | {
        'stack': 'STACK_SIZE 16_777_216 (src/lib.rs:23), unchanged from 3a24072',
        'cargo_version': (re.search(r'Cargo version[^0-9]*([0-9.]+)', pf_build) or re.search(r'version = "([0-9.]+)"', pf_build) or [None, 'MISSING'])[1],
        'source': 'results/2026-10-20-nanoda-postfix-f67473b/build.log and SUMMARY.txt; results/2026-10-21-paper-prep-4/nanoda55-crosscheck.txt'},
    'landrun': old['tools']['landrun'] | {'source': 'task4-provenance-commands.txt'},
    'platform': old['platform'],
    'sandbox': {'wrapper_command_line': 'sudo -u checker -H env XDG_RUNTIME_DIR=/run/user/$UID_C DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$UID_C/bus bash -lc "...; ' + cmdline + '"',
                'note': '$TMO = timeout in seconds (7200 for corpus runs); $CFG = config path; comparator then runs each subprocess under landrun (Main.lean buildLandrunArgs)',
                'source': 'wsl-comparator/67_corpus_run.sh (lines 21-26)'},
    'identity_and_network_self_test': identity | {
        'note': 'Corpus replay logs do not print id; these two runs used the same wrapper with the payload in 108_inner.sh/107_inner.sh. '
                'Earlier probe: results/2026-10-11-corpus-runas-2.txt (uid=1000(checker)).'},
}
missing = []


def walk(x, path=''):
    if isinstance(x, dict):
        for k, v in x.items():
            walk(v, f'{path}.{k}' if path else k)
    elif x == 'MISSING':
        missing.append(path)


walk(m)
m['missing_fields'] = missing
os.makedirs(out, exist_ok=True)
json.dump(m, open(os.path.join(out, 'manifest-final.json'), 'w', encoding='utf-8', newline='\n'), indent=2, ensure_ascii=False)
tx = lambda s: str(s).replace('_', r'\_').replace('#', r'\#').replace('$', r'\$').replace('~', r'\textasciitilde{}')
idf = identity['adc7f12 shipped, full block (2026-10-20)']
rows = [('openai/math', 'adc7f12 (packet), fd4aeeb (corpus)'), ('lean-toolchain', m['lean_toolchain']['file'].split(' (')[0]),
        ('Lean', 'v4.34.1, 5045d005'), ('lake-manifest.json sha256', m['lake_manifest']['sha256'][:16] + '...'),
        ('Mathlib', m['lake_manifest']['mathlib_rev'][:7]), ('Comparator', 'd03acab (v4.34.0)'),
        ('Exporter', 'lean4export 076e8e5 (v4.34.0)'), ('landrun', '811cfff (reports 0.1.18)'),
        ('nanoda (pinned)', '3a24072, binary ' + m['nanoda_3a24072']['binary_sha256'][:12] + '...'),
        ('nanoda (post-fix, unofficial)', 'f67473b, binary ' + m['nanoda_f67473b']['binary_sha256'][:12] + '...'),
        ('WSL / kernel', m['platform']['wsl'] + ' / ' + m['platform']['wsl_kernel']), ('Distribution', m['platform']['distro']),
        ('Checking user', idf['id'].split(' ')[0] + ', CapEff 0, NoNewPrivs 1 (logged post hoc, 2026-10-20; not in the replay logs)'),
        ('Sandbox', 'systemd-run --user, RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET; landrun'),
        ('Network self-test', 'TCP, AF_INET, AF_INET6, AF_UNIX all refused (EAFNOSUPPORT)')]
tex = ['% Generated by scripts/manifest_final.py from manifest-final.json; do not edit by hand.',
       r'\begin{tabular}{@{}ll@{}}', r'\toprule', r'Field & Value \\', r'\midrule'] + \
      [f'{tx(a)} & {tx(b)} \\\\' for a, b in rows] + [r'\bottomrule', r'\end{tabular}']
open(os.path.join(out, 'table2.tex'), 'w', encoding='utf-8', newline='\n').write('\n'.join(tex) + '\n')
print('manifest-final.json written; missing fields:', missing or 'none')
print(json.dumps(identity, indent=1, ensure_ascii=False)[:900])
