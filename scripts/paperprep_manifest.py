"""Paper prep Task 4: provenance manifest and its diff against the v1 Siegel packet's methods text.

Usage: python -I scripts/paperprep_manifest.py <repo root>
Writes results/2026-10-20-paper-prep/manifest.json and prints the mismatch list (redirect it to a file).
Every value is either read here from a results/ file or the v1 tag (path given in "source"), or was printed by
the WSL commands recorded in results/2026-10-20-paper-prep/task4-provenance-commands.txt.
"""
import json, os, re, subprocess, sys

root = sys.argv[1]
pp = os.path.join(root, 'results', '2026-10-20-paper-prep')
posthoc = open(os.path.join(pp, 'wsl', 'task4-SiegelZeros-posthoc.log'), encoding='utf-8').read()


def inner(key):
    m = re.search(r'^INNER ' + re.escape(key) + r':?\s*(.*)$', posthoc, re.M)
    return m.group(1).strip() if m else None


m = {
    'openai_math': {
        'corpus_replay_commit': 'fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb',
        'siegel_packet_v1_and_pilot_commit': 'adc7f1241b42e322a6451854ab7e4b4c146bf78a',
        'main_at_check': '1581d4cbdd69a0faf34b2089614fe2a814316a6a (2026-10-12; anonymous clone 2026-10-20)',
        'flagged_paths_changed_since_adc7f12': False,
        'source': 'results/2026-10-20-paper-prep/task2e-gitlog.txt; wsl/run.log line 1',
    },
    'lean_toolchain': {
        'file': 'leanprover/lean4:v4.34.1 (identical at adc7f12, fd4aeeb, main)',
        'lean': 'Lean 4.34.1, commit 5045d0056413266e57c625dcd7c365b10e377c52, x86_64-unknown-linux-gnu, Release',
        'elan': '4.2.4 (227caca13 2026-08-25)',
        'source': 'task4-provenance-commands.txt; results/2026-10-11-corpus-provenance.txt',
    },
    'lake_manifest': {
        'sha256': 'cf6105a25d9dca2f166b241d9191bd12c7e13305890dc9c4d0952351cccc0794',
        'identical_at': ['adc7f12', 'fd4aeeb', 'main 1581d4c'],
        'lakefile_lean_sha256': '4cca977ebece444b6c999d99755c1ad3c93119bafc127ea761f7f703c7279e74',
        'packages': 42,
        'mathlib_rev': 'd13f23b723b8a846827a245b89c10fc7d3f11612',
        'per_package_revs': 'results/2026-10-11-corpus-provenance.txt (42 rows)',
        'note': 'lake update applies lean/patches/*-lean4341.patch to several packages (counts in the provenance file)',
    },
    'tools': {
        'comparator': {'commit': 'd03acab154d269c06e60e4de7e4cc85deebff94b', 'tag': 'v4.34.0',
                       'binary_sha256': 'afa65e57a1770f5961efe7681626a9a1cd99705262421658abd30b705f66e4a2'},
        'lean4export': {'commit': '076e8e57707e813375e8f9da8bf989799ace9680', 'tag': 'v4.34.0',
                        'binary_sha256': '8c5d64ba68f4d3a68b3bcb7e1c5f188e35ae573b29470b8d4530a62324c9ddd1'},
        'landrun': {'commit': '811cfff51ceaf3d9843708aa6d22e9b84ccac8b4', 'git_describe': 'v0.1.17-4-g811cfff',
                    'self_reported_version': '0.1.18',
                    'binary_sha256': '5f6fd588dbdf5116969c3dee3fee52ba7f46aa80df2bb58277326a9186e736de'},
        'nanoda_lib': {'commit': '3a2407216ee84a75f9e1aead6803d0578be06ae7', 'cargo_version': '0.4.19',
                       'checker_thread_stack': '16 MiB, explicit (src/lib.rs STACK_SIZE; src/tc.rs:160 .stack_size)',
                       'binary_sha256': '897971d7e99f1ac2ce3d43131d291a63858badf41cab409f70b99dbd04e0b714'},
        'nanoda_postfix_unofficial': {'commit': 'f67473ba5f9397266f89c7852082c9c914b5d219',
                                      'binary_sha256': 'be15131c173f1b803e3e51239604dbf44489d8be25fe675419ba9a0c9b47ada5',
                                      'used_for': 'results/2026-10-20-nanoda-postfix-f67473b only (not the table)'},
        'rustc_for_nanoda': 'rustc 1.99.0 (b940084d7 2026-09-28) (results/2026-10-08-lean-comparator-nanoda-netblock.txt)',
    },
    'platform': {
        'windows': '10.0.26200.9457 (Windows 11 Home)',
        'wsl': '2.4.11.0', 'wsl_kernel': inner('kernel'),
        'wsl_kernel_recorded_2026_10_08': '5.15.167.4-microsoft-standard-WSL2 (results/2026-10-08-lean-comparator-wsl.txt)',
        'distro': 'Ubuntu 24.04.5 LTS', 'systemd': '255 (255.4-1ubuntu8.18)',
        'landlock': 'kernel < 6.7: Landlock cannot restrict network (v1 reproduce.md); network blocked by seccomp instead',
    },
    'sandbox': {
        'wrapper': 'sudo -u checker; systemd-run --user --wait --pipe --collect '
                   '--property="RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET"; timeout',
        'scripts': 'wsl-comparator/67_corpus_run.sh (replay), 107_run.sh + 107_inner.sh (post-hoc)',
    },
    'replay_identity': {
        'recorded_in_replay_logs': False,
        'note': 'No corpus replay log prints id. A separate probe with the same wrapper recorded uid=1000(checker) on '
                '2026-10-11 (results/2026-10-11-corpus-runas-2.txt).',
        'post_hoc': True,
        'post_hoc_run': 'SiegelZeros at fd4aeeb, 2026-10-20, results/2026-10-20-paper-prep/wsl/task4-SiegelZeros-posthoc.log',
        'id': inner('id'), 'Uid': inner('Uid'), 'CapEff': inner('CapEff'), 'NoNewPrivs': inner('NoNewPrivs'),
        'cgroup': inner('cgroup'),
        'netblock_self_test': {k: inner('netblock ' + k) for k in
                               ('tcp 1.1.1.1:443', 'python AF_INET udp socket', 'python AF_INET6 socket',
                                'python AF_UNIX socket')},
        'post_hoc_verdict': ('ACCEPT_BOTH' if 'nanoda kernel accepts the solution' in posthoc
                             and 'Lean default kernel accepts the solution' in posthoc
                             and 'COMPARATOR EXIT CODE: 0' in posthoc else 'NOT ACCEPT_BOTH'),
    },
}
os.makedirs(pp, exist_ok=True)
with open(os.path.join(pp, 'manifest.json'), 'w', encoding='utf-8', newline='\n') as f:
    json.dump(m, f, indent=2, ensure_ascii=False)
    f.write('\n')

# Methods text of the v1 packet (tag reviewer-packet-v1), quoted lines
v1 = subprocess.run(['git', '-C', root, 'show', 'reviewer-packet-v1:docs/reproduce.md'], capture_output=True,
                    text=True, encoding='utf-8').stdout.splitlines()
v1w = subprocess.run(['git', '-C', root, 'show', 'reviewer-packet-v1:docs/writeup.md'], capture_output=True,
                     text=True, encoding='utf-8').stdout.splitlines()
q = lambda lines, n: lines[n - 1].strip()
print('Manifest vs methods text of the v1 Siegel packet (tag reviewer-packet-v1: docs/reproduce.md, docs/writeup.md)')
print('Quoted v1 lines are verbatim from the tag.\n')
rows = [
    ('openai/math commit', q(v1, 7)[:130], 'v1 runs: adc7f12. Corpus replay: fd4aeeb. Post-hoc SiegelZeros: fd4aeeb.',
     'MISMATCH (scope): the replay is at a later commit. Pinned paths and lake-manifest are identical across the two.'),
    ('comparator / lean4export', q(v1, 43)[:160], 'd03acab (v4.34.0) / 076e8e5 (v4.34.0), built with 4.34.1', 'MATCH'),
    ('landrun', 'landrun 0.1.18 (reproduce.md:43)', 'commit 811cfff = git describe v0.1.17-4-g811cfff; binary reports 0.1.18',
     'MISMATCH (labelling): v1 gives a version number that has no tag at this commit; the commit is not stated in v1.'),
    ('nanoda', q(v1, 46)[:120], '3a24072, Cargo 0.4.19, binary sha256 897971d7...', 'MATCH'),
    ('Lean toolchain', 'toolchain v4.34.1 (reproduce.md:43)', 'v4.34.1, Lean commit 5045d005', 'MATCH'),
    ('Mathlib / lake-manifest', 'Mathlib at d13f23b (reproduce.md:121, Windows lean-build); no lake-manifest hash in v1',
     'd13f23b; lake-manifest sha256 cf6105a2...; 42 packages',
     'MISMATCH (omission): v1 states no lake-manifest hash and no package list for the WSL runs.'),
    ('platform', q(v1, 42)[:100], 'WSL 2.4.11.0, Ubuntu 24.04.5, kernel 5.15.167.4', 'MATCH (v1 gives no WSL version or kernel build; it says "5.15")'),
    ('WSL kernel', q(v1, 45)[-120:], '5.15.167.4-microsoft-standard-WSL2 (2026-10-08 and now)', 'MATCH'),
    ('network block', 'RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET (reproduce.md:45)',
     'same property; post-hoc self-test: AF_INET, AF_INET6, AF_UNIX all EAFNOSUPPORT', 'MATCH'),
    ('network block, first v1 run', 'reproduce.md:45 lists the full block under "What we actually ran" (lines 42-47)',
     'results/2026-10-08-lean-comparator-wsl.txt header: the first comparator run (08_comparator.sh) used '
     'RestrictAddressFamilies=~AF_UNIX only; the full block applies from the nanoda run (29_comparator_nanoda.sh)',
     'MISMATCH (wording): reproduce.md:45 reads as if every run had the full block. writeup.md 2.8 (4)/(5) and '
     'README item 1 tie the block to the nanoda run, which is correct. The accepted-by-both-kernels claim rests on '
     'the nanoda run, which had the full block.'),
    ('user / uid', q(v1, 44)[:120], 'post-hoc: uid=1000(checker), CapEff 0, NoNewPrivs 1',
     'MISMATCH (evidence): v1 states the user name; no v1 run log records id. Evidence is the 2026-10-11 probe and '
     'the 2026-10-20 post-hoc run (POST-HOC).'),
    ('run times', q(v1, 47)[-110:], 'post-hoc SiegelZeros (fd4aeeb, prebuilt): 797 s comparator after a 649 s prebuild',
     'NOT COMPARABLE (different build state); no claim depends on it.'),
]
for k, a, b, c in rows:
    print(f'- {k}\n    v1: {a}\n    manifest: {b}\n    -> {c}')
