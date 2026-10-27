"""Claims ledger v5 (2026-10-27). Read-only on the repo; writes ledger-v5.tsv next to this file (refuses to overwrite).

Usage: python -I results/2026-10-26-claims-ledger/build_ledger_v5.py <repo root>
Append-only (id-stability.md): every ledger-v4.tsv row is copied unchanged, except the status of a superseded row
("SUPERSEDED by v5:Lxxx"); new rows take explicit ids from L140 on.
"""
import csv, hashlib, os, sys, collections

root = sys.argv[1]
OUT = os.path.join(root, 'results', '2026-10-26-claims-ledger')
problems = []


def _read(p):
    b = open(os.path.join(root, p), 'rb').read().replace(b'\r\n', b'\n')
    return b, b.decode('utf-8', 'replace').split('\n')


def R(path, sub, nth=1):
    _, L = _read(path)
    hits = [i + 1 for i, l in enumerate(L) if sub in l]
    if len(hits) < nth:
        problems.append(f'R not found: {path} :: {sub!r}'); return f'{path}:?'
    return f'{path}:{hits[nth - 1]}'


def L(path, a, b, sub):
    raw, lines = _read(path)
    if sub not in '\n'.join(lines[a - 1:b]): problems.append(f'L mismatch: {path}:{a}-{b} :: {sub!r}')
    return f'{path}:{a}-{b} (LF sha256 {hashlib.sha256(raw).hexdigest()})'


A_ = 'adc7f1241b42e322a6451854ab7e4b4c146bf78a'; F_ = 'fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb'
TC = 'Lean 4.34.1 / Mathlib d13f23b / Comparator d03acab / lean4export 076e8e5'
NR = 'n/a'
NEAL = 'https://github.com/nealmcb/openai-math-lean-tooling/blob/1ca7ff2a0280760783ee2b198c0d6f2a1cfeaba4/'
LG = 'results/2026-10-26-claims-ledger/'; EV3 = LG + 'v3-evidence/'; EV5 = LG + 'v5-evidence/'
NCmp = 'results/2026-10-27-neal-comparison/'; QC = 'results/2026-10-27-qrh-closure/'

with open(os.path.join(OUT, 'ledger-v4.tsv'), encoding='utf-8') as f:
    rd = csv.reader(f, delimiter='\t'); cols = next(rd); rows = [dict(zip(cols, r)) for r in rd]
assert [r['id'] for r in rows] == [f'L{k:03d}' for k in range(1, 140)], 'ledger-v4.tsv ids are not L001-L139'
byid = {r['id']: r for r in rows}
new = []


def row(i, sec, claim, value, unit, src, label, commit, tc, sb, status='FOUND', note='', read_by='', read_note=''):
    new.append(dict(id=i, paper_section=sec, claim=claim, value=value, unit=unit,
                    source='; '.join(src) if isinstance(src, (list, tuple)) else src, label=label, openai_math_commit=commit,
                    toolchain=tc, sandbox=sb, status=status, note=note, read_by=read_by, read_note=read_note))


def supersede(old, by):
    r = byid[old]; assert r['status'] == 'FOUND', (old, r['status']); r['status'] = f'SUPERSEDED by v5:{by}'


# ---- item 1a: QuasiRiemannHypothesis closure, adc7f12 vs fd4aeeb ----
QS = QC + 'summary.txt'; Q2 = QC + 'second-check.txt'
row('L140', '7', 'QuasiRiemannHypothesis: the Comparator config, the challenge file, every local module in the solution import closure (followed from OAI.NumberTheory.DirichletL.Nonvanishing and ComparatorChallenges.QuasiRiemannHypothesis), and the build files (lake-manifest.json, lean-toolchain, lakefile.lean, lakefile.toml, lean/patches/*) are byte-identical at adc7f12 and fd4aeeb. A second method finds no changed module imported anywhere in the closure.',
    '2925 of 2925 local modules identical; config, toolchain, manifest, lakefiles, 24 patches identical; 252 external imports, same set; 0 of 738 changed modules in the closure',
    'files', [R(QS, 'config identical: True'), R(QS, 'local modules in closure: adc7f12 2925, fd4aeeb 2925; same module set: True; identical files: 2925; differing: []'),
              R(QS, 'external imports (Lake packages): adc7f12 252, fd4aeeb 252; same set: True'), R(QS, 'ALL IDENTICAL: True'),
              R(Q2, 'of them .lean modules: 738'), R(Q2, 'changed modules that are in the closure: []'), R(Q2, 'import lines anywhere in closure files that name a changed module: 0'), QC + 'qrh-closure.tsv (sha256 per file, both commits)'],
    'COMPUTED', A_ + ' and ' + F_, 'git show on the local clone /home/checker/math; Python 3.12.3 (WSL)', 'read-only, no build',
    note='closure found by parsing import lines in the module headers, not by Lake; the second method scans every line of each closure file. External packages are pinned by the identical lake-manifest.json and patches, so their files are the same at both commits (INFERRED from the pins; package files were not hashed)')

# ---- item 1b: the comparison re-run with SiegelZeros at fd4aeeb ----
S2 = NCmp + 'summary-v2.txt'
row('L141', '0; 7', "Outcome-level comparison with nealmcb's Comparator results at 1ca7ff2, re-run with SiegelZeros taken from the fd4aeeb control run (v4:L093) instead of the adc7f12 pilot. QuasiRiemannHypothesis stays at the adc7f12 pilot, whose closure is byte-identical at fd4aeeb (v5:L140). Verdict compared: Comparator with the Lean kernel accepts the config.",
    '416 compared; 402 agree; 0 disagree; 14 no verdict here (ContinuumCoulombHardness, CycleCliqueRamsey, DefocusingNLS, FalconerAllDimensions, InvariantIsing, JointDickman, MUBSix, OrdinaryTwoPointCorrelations, OstmannComplete, PattersonFirstMoment, PolycyclicRecognition, SurfaceImmersion, UniversalTensorSquares: NOT_CHECKED_HERE; PlanarPacking: TIMEOUT); 0 no verdict there; 0 no verdict on either side; ours not at fd4aeeb: QuasiRiemannHypothesis only',
    'configs', [R(S2, 'configs: ours 416, his 416, union 416, in both 416'), R(S2, "by class: {'agree': 402, 'no verdict here': 14}"), R(S2, 'disagree: []'), R(S2, 'no verdict there: []'),
                R(S2, "ours not at fd4aeeb: [('QuasiRiemannHypothesis'"), NCmp + 'outcomes-v2.tsv', R('results/2026-10-27-reroute-fd4aeeb/control-comparator.log', 'COMPARATOR EXIT CODE: 0'), NEAL + 'results/cmp-all/all.jsonl'],
    'COMPUTED', F_ + ' (QuasiRiemannHypothesis at ' + A_ + ', closure identical)', TC, NR,
    note='his side is STATED (all.jsonl at 1ca7ff2, sha256 6753e7de...). Same counts as v4:L131; the only change is the commit of our SiegelZeros record')
supersede('L131', 'L141')

# ---- item 2: what both kernels depend on (STATED, tool READMEs at the pinned commits) ----
CR = EV3 + 'comparator-README-d03acab.md'; ER = EV5 + 'lean4export-README-076e8e5.md'; NRD = EV3 + 'nanoda_lib-README-3a24072.md'
cc = '/root/tools/comparator/README.md (clone d03acab154d269c06e60e4de7e4cc85deebff94b; README unmodified, ' + R(EV3 + 'tool-readmes.txt', 'clone /root/tools/comparator HEAD d03acab') + ')'
ce = '/root/tools/lean4export/README.md (clone 076e8e57707e813375e8f9da8bf989799ace9680; README unmodified, ' + R(EV5 + 'tool-readmes-v5.txt', 'clone /root/tools/lean4export HEAD 076e8e5') + ')'
cn = '/root/tools/nanoda_lib/README.md (clone 3a2407216ee84a75f9e1aead6803d0578be06ae7; README unmodified)'
row('L142', '8', "What the two kernel checks depend on, as Comparator's and lean4export's READMEs state it (plus nanoda's README for its input). SHARED by both: the Lake build of Solution in a landrun sandbox (Comparator steps 1 and 3), the lean4export export of Solution (steps 2 and 3), and Comparator's own statement and axiom checks (steps 4 and 5); the export is the module and its transitive dependencies, without unsafe declarations or Expr.mdata by default. LEAN KERNEL ONLY: the replay of the Solution environment into the Lean kernel inside the Comparator process (step 6). EXTERNAL KERNEL (nanoda) ONLY: a separate process given a file containing the solution export, with a nanoda-style config.json.",
    'Comparator README: 178-179 "1. Build `Challenge` using `lake` in a `landrun` sandbox"; 182 "2. Run `lean4export` on the produced `Challenge.olean`"; 184 "3. Repeat the same build sandboxed and export sandboxed steps with `Solution`"; 185-186 "4. Verify that all declarations used in the statement of all relevant theorems in `Challenge` are the same as in the `Solution` environment."; 189-190 "5. Verify that the body of all relevant theorems in the `Solution` environment only uses axioms listed in `permitted_axioms`"; 191-194 "6. Replay the `Solution` environment into the Lean kernel. Doing this within the same process as the comparator should be safe ..."; 175-176 "We generally adopt a policy of not loading olean files"; 77-78 "pass a file, containing the solution export to the kernel"; 80-83 "`enable_nanoda: true` ... passing a `nanoda`-style `config.json`". lean4export README: 1 "A simple declaration exporter for Lean 4 using the [Lean 4 NDJSON export format]"; 23 "exports the contents of the given Lean module ... and its transitive dependencies"; 27 "The option `--export-unsafe` can be used to include unsafe declarations"; 29 "`Expr.mdata` items ... are removed by default as they should not have an effect on type checking". nanoda README: 13 "Export files can be created with [lean4export]".',
    'tool documentation',
    [cc + ' lines 77-83, 175-194', ce + ' lines 1, 23, 27, 29', cn + ' line 13',
     L(CR, 178, 179, '1. Build `Challenge` using `lake` in a `landrun` sandbox'), L(CR, 182, 182, '2. Run `lean4export` on the produced `Challenge.olean`'), L(CR, 184, 184, '3. Repeat the same build sandboxed and export sandboxed steps with `Solution`'),
     L(CR, 185, 186, '4. Verify that all declarations used in the statement of all relevant theorems in `Challenge`'), L(CR, 189, 190, '5. Verify that the body of all relevant theorems in the `Solution` environment only uses axioms'),
     L(CR, 191, 194, '6. Replay the `Solution` environment into the Lean kernel. Doing this within the same process as the'), L(CR, 175, 176, 'We generally adopt a policy of not loading olean files'),
     L(CR, 77, 78, 'file, containing the solution export to the kernel'), L(CR, 80, 83, 'For backwards compatibility reasons users may instead set `enable_nanoda: true`'),
     L(ER, 1, 1, 'A simple declaration exporter for Lean 4 using the [Lean 4 NDJSON export format]'), L(ER, 23, 23, 'and its transitive dependencies'), L(ER, 27, 27, 'The option `--export-unsafe` can be used to include unsafe declarations'),
     L(ER, 29, 29, 'which are removed by default as they should not have an effect on type checking'), L(NRD, 13, 13, 'Export files can be created with [lean4export]')],
    'STATED', NR, 'Comparator d03acab (v4.34.0); lean4export 076e8e5 (v4.34.0); nanoda_lib 3a24072', NR,
    note='INFERRED, not stated in the READMEs: that the environment the Lean kernel replays in step 6 is the one read from the Solution export (from the policy at 175-176 of not loading .olean files); the READMEs do not say whether both kernels read the same export file. Comparator README 178-179 names Challenge; step 3 (184) repeats the build and export for Solution')

# ---- write ----
if problems:
    print('PROBLEMS (ledger not written):'); print('\n'.join(problems)); sys.exit(1)
assert [r['id'] for r in new] == [f'L{k:03d}' for k in range(140, 140 + len(new))]
p = os.path.join(OUT, 'ledger-v5.tsv')
if os.path.exists(p): sys.exit(f'refusing to overwrite {p}')
with open(p, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t', lineterminator='\n'); w.writerow(cols)
    for r in rows + new: w.writerow([r[c] for c in cols])
print('rows', len(rows) + len(new), 'new', len(new), 'new by label', dict(collections.Counter(r['label'] for r in new)), 'status', dict(collections.Counter(r['status'] for r in rows + new)))
