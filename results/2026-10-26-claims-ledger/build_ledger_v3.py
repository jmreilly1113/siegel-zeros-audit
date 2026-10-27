"""Claims ledger v3 (2026-10-27). Read-only on the repo; writes ledger-v3.tsv next to this file (refuses to overwrite).

Usage: python -I results/2026-10-26-claims-ledger/build_ledger_v3.py <repo root>

Ids are append-only from v3 on (v2 renumbered v1's L050-L090; see id-stability.md):
  - every ledger-v2.tsv row is copied with its id, claim, value and source unchanged;
  - new rows carry explicit ids from L099 on; an id is never reused or renumbered;
  - a row that is no longer wanted keeps its id and gets a status change, it is not deleted.
New columns: read_by (who read a statement match, as recorded in docs/log.md) and read_note.
Sources are resolved as in build_ledger.py: R(path, substring) -> path:LINE; L(path, a, b, substring) -> path:a-b (LF sha256).
"""
import csv, hashlib, os, sys, collections

root = sys.argv[1]
OUT = os.path.join(root, 'results', '2026-10-26-claims-ledger')
problems = []


def _read(p):
    full = os.path.join(root, p) if not p.startswith('\\\\') else p
    b = open(full, 'rb').read().replace(b'\r\n', b'\n')
    return b, b.decode('utf-8', 'replace').split('\n')


def R(path, sub, nth=1):
    _, L = _read(path)
    hits = [i + 1 for i, l in enumerate(L) if sub in l]
    if len(hits) < nth:
        problems.append(f'R not found: {path} :: {sub!r}'); return f'{path}:?'
    return f'{path}:{hits[nth - 1]}'


def L(path, a, b, sub):
    raw, lines = _read(path)
    seg = '\n'.join(lines[a - 1:b])
    if sub not in seg: problems.append(f'L mismatch: {path}:{a}-{b} :: {sub!r}')
    return f'{path}:{a}-{b} (LF sha256 {hashlib.sha256(raw).hexdigest()})'


A_ = 'adc7f1241b42e322a6451854ab7e4b4c146bf78a'; F_ = 'fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb'
TC = 'Lean 4.34.1 / Mathlib d13f23b / Comparator d03acab / lean4export 076e8e5'
TCN = TC + ' / nanoda 3a24072 (STACK_SIZE 16 MiB)'
SB45 = '45-family RestrictAddressFamilies (every family of kernel 5.15.167.4; 75d/140d/67d), checker, NoNewPrivs'
NR = 'n/a'; NONE = 'none (no run; source text)'
NEAL = 'https://github.com/nealmcb/openai-math-lean-tooling/blob/1ca7ff2a0280760783ee2b198c0d6f2a1cfeaba4/'
WSLM = '\\\\wsl.localhost\\Ubuntu-24.04\\home\\checker\\math\\lean\\'
IJW = WSLM + 'OAI\\NumberTheory\\SiegelZeros\\Structure\\InvariantJetLinearMap.lean'
BR = 'lean-checks/comparator-copy/PaperLemma3/Bridge.lean'
PL = 'lean-checks/comparator-copy/PaperLemma3/Lemma3.lean'
TEX = 'refs/siegel-paper.tex'
LG = 'results/2026-10-26-claims-ledger/'; EV = LG + 'v3-evidence/'
RR = 'results/2026-10-27-reroute-fd4aeeb/'
MX = 'results/2026-10-26-nanoda-version-matrix/'
CMP = 'results/2026-10-25-extended-replay-vs-mcburnett/comparison.txt'
T227 = MX + 'extended-replay-227/corpus-227-v3.tsv'
LOG = 'docs/log.md'
PJ = 'PENDING JOE READING'

# ---------------- v2 rows, unchanged ----------------
cols2 = None; rows = []
with open(os.path.join(OUT, 'ledger-v2.tsv'), encoding='utf-8') as f:
    rd = csv.reader(f, delimiter='\t')
    cols2 = next(rd)
    for r in rd: rows.append(dict(zip(cols2, r)))
assert cols2 == ['id', 'paper_section', 'claim', 'value', 'unit', 'source', 'label', 'openai_math_commit', 'toolchain', 'sandbox', 'status', 'note'], cols2
ids = [r['id'] for r in rows]
assert ids == [f'L{k:03d}' for k in range(1, 99)], 'ledger-v2.tsv ids are not L001-L098'
for r in rows: r['read_by'] = ''; r['read_note'] = ''

# read_by for the four challenge faithfulness rows (docs/log.md is first-person, written in the Claude Code sessions)
RB = {
    'L002': ('Claude Code', R(LOG, '2026-10-20, new task: statement-faithfulness check of the other three family-003 challenges'),
             'Joe approved the QRH and Dirichlet findings at step 4 (' + R(LOG, 'Joe approved steps 1-3') + '); no reading by Joe is recorded'),
    'L004': ('Claude Code', R(LOG, '2026-10-20, new task: statement-faithfulness check of the other three family-003 challenges'),
             'Joe approved the QRH and Dirichlet findings at step 4 (' + R(LOG, 'Joe approved steps 1-3') + '); no reading by Joe is recorded'),
    'L006': ('Claude Code', R(LOG, '2026-10-20, new task: statement-faithfulness check of the other three family-003 challenges'),
             "Joe's ruling MATCHES on the Hecke LFunction row only (" + R(LOG, "Joe's ruling on the Hecke LFunction row") + '); no reading by Joe of the other rows is recorded'),
    'L008': ('Claude Code', R(LOG, '### Step 2 (statement fidelity), reading Mathlib @ d13f23b'),
             'log entry: "Inference: statement is faithful; no hidden weakening found" (' + R(LOG, 'Inference: statement is faithful; no hidden weakening found') + '); no reading by Joe is recorded'),
}
for i, (who, where, note) in RB.items():
    r = rows[int(i[1:]) - 1]; assert r['id'] == i and r['label'] == 'INFERRED'
    r['read_by'] = f'{who} ({where})'; r['read_note'] = note

# ---------------- new rows, explicit append-only ids ----------------
new = []


def row(i, sec, claim, value, unit, src, label, commit, tc, sb, status='FOUND', note='', read_by='', read_note=''):
    new.append(dict(id=i, paper_section=sec, claim=claim, value=value, unit=unit,
                    source='; '.join(src) if isinstance(src, (list, tuple)) else src, label=label, openai_math_commit=commit,
                    toolchain=tc, sandbox=sb, status=status, note=note, read_by=read_by, read_note=read_note))


# item 2: OAI's Corollary 4 proof invokes the multiplicity estimate
row('L099', '4', "Inside OAI's proof of actual_biquadratic_rectangle_span (InvariantJetLinearMap.lean, statement 471-484, proof 485-511, at fd4aeeb), exactly two places name the multiplicity lemmas: line 493 applies Geometry.source_rectangle_span_of_polynomial_zero_test and line 496 applies Geometry.uniform_rectangular_multiplicity.",
    '493-494: "apply Geometry.source_rectangle_span_of_polynomial_zero_test φ.toRingHom / ![1, a, b, a * b] σ.toRingHom τ.toRingHom H N n hninj hn"; 496-497: "apply Geometry.uniform_rectangular_multiplicity (Nat.succ_le_iff.mpr hH) hHN / (biquadraticCoefficients (φ a) (φ b)) hc D\' F hF"',
    'source lines', [L(IJW, 493, 494, 'apply Geometry.source_rectangle_span_of_polynomial_zero_test φ.toRingHom'), L(IJW, 494, 494, '![1, a, b, a * b] σ.toRingHom τ.toRingHom H N n hninj hn'),
                     L(IJW, 496, 497, 'apply Geometry.uniform_rectangular_multiplicity (Nat.succ_le_iff.mpr hH) hHN'), L(IJW, 497, 497, "(biquadraticCoefficients (φ a) (φ b)) hc D' F hF"),
                     L(IJW, 471, 471, 'theorem actual_biquadratic_rectangle_span'), L(IJW, 512, 512, 'end WeightedTorusJets')],
    'COMPUTED', F_, NR, 'read-only source reading of the clean fd4aeeb clone', note='same file LF sha256 as L016 (09b8bd7f...), so the lines are the same at adc7f12; a text search of lines 485-511 finds no other line naming either lemma')

# item 3: statement-match rows for Lemma 3 and Corollary 4
row('L100', '5', 'Lemma3.interpolation (comparator copy) matches the paper\'s Lemma 3, tex 252-267, clause by clause.', PJ, 'finding',
    [L(PL, 816, 825, 'theorem interpolation'), R(TEX, '\\begin{lemma}\\label{lem:interpolation}'), R(TEX, '\\end{lemma}', 2), R(LOG, 'the Lean statement matches tex lines 252-267 clause by clause'), R('docs/lemma3-lean-statement-review.md', 'Clause-by-clause comparison with the paper (inference: my reading)')],
    'INFERRED', NR, TC, NONE, note='blocked in the outline until read_by includes Joe',
    read_by='Claude Code (' + R(LOG, 'the Lean statement matches tex lines 252-267 clause by clause') + '; docs/lemma3-lean-statement-review.md, "inference: my reading")', read_note='no reading by Joe is recorded')
row('L101', '5', "Lemma3.rectangle (comparator copy) matches the paper's Corollary 4, tex 410-420.", PJ, 'finding',
    [L(BR, 96, 109, 'theorem rectangle'), R(TEX, '\\begin{corollary}\\label{cor:rectangle}'), R(TEX, '\\end{corollary}')],
    'INFERRED', NR, TC, NONE, note='blocked in the outline until read_by includes Joe; L029 records that bridge_main equals OAI 471-484 apart from the name, which is a different comparison',
    read_by='none recorded', read_note='docs/log.md records no reading of Lemma3.rectangle against tex 410-420')

# item 4: tool documentation (STATED), from the pinned local clones; copies in v3-evidence/ for resolution
CR = EV + 'comparator-README-d03acab.md'; NRD = EV + 'nanoda_lib-README-3a24072.md'
cl_c = '/root/tools/comparator/README.md (clone d03acab154d269c06e60e4de7e4cc85deebff94b; README unmodified, ' + R(EV + 'tool-readmes.txt', 'clone /root/tools/comparator HEAD d03acab') + ')'
cl_n = '/root/tools/nanoda_lib/README.md (clone 3a2407216ee84a75f9e1aead6803d0578be06ae7; README unmodified, ' + R(EV + 'tool-readmes.txt', 'clone /root/tools/nanoda_lib HEAD 3a24072') + ')'
TCC = 'Comparator d03acab (v4.34.0)'
row('L102', '2', 'Comparator check 1: every listed theorem in Solution proves the same statement as in Challenge; internally, all declarations used in the statements of the relevant Challenge theorems must be the same in the Solution environment.',
    '"Prove the same statement as provided in `Challenge`"', 'tool documentation',
    [cl_c + ' lines 46-47 and 185-188', R(CR, '1. Prove the same statement as provided in `Challenge`'), R(CR, '4. Verify that all declarations used in the statement of all relevant theorems in `Challenge`')], 'STATED', NR, TCC, NR)
row('L103', '2', 'Comparator check 2: the listed theorems use no more axioms than permitted_axioms; internally, the bodies of the relevant theorems in the Solution environment are checked to use only those axioms.',
    '"Use no more axioms than listed in `permitted_axioms`"', 'tool documentation',
    [cl_c + ' lines 48 and 189-190', R(CR, '2. Use no more axioms than listed in `permitted_axioms`'), R(CR, '5. Verify that the body of all relevant theorems in the `Solution` environment only uses axioms')], 'STATED', NR, TCC, NR)
row('L104', '2', 'Comparator check 3: the listed theorems are accepted by the Lean kernel; internally, the Solution environment is replayed into the Lean kernel. External kernels registered in external_kernels are given a file containing the solution export.',
    '"Be accepted by the Lean kernel"', 'tool documentation',
    [cl_c + ' lines 49, 77-78 and 191-194', R(CR, '3. Be accepted by the Lean kernel'), R(CR, '6. Replay the `Solution` environment into the Lean kernel'), R(CR, 'file, containing the solution export to the kernel')], 'STATED', NR, TCC, NR)
row('L105', '2', 'nanoda input format: nanoda_bin takes one argument, a JSON configuration file; the export file (created by lean4export) is given by export_file_path or streamed on stdin (use_stdin), and the permitted axioms are listed in the configuration. With enable_nanoda: true, Comparator passes nanoda a nanoda-style config.json.',
    'JSON config + lean4export export file', 'tool documentation',
    [cl_n + ' lines 11, 13 and 27-29', R(NRD, 'The binary takes a single argument, which is a path to a json configuration file'), R(NRD, 'Export files can be created with [lean4export]'),
     R(NRD, 'Users can either specify a path to the export file to be checked'), R(NRD, 'The `"permitted_axioms"` list is where users specify'),
     cl_c + ' lines 80-84', R(CR, 'For backwards compatibility reasons users may instead set `enable_nanoda: true`'), R(CR, '`config.json` to them')], 'STATED', NR, 'nanoda_lib 3a24072; ' + TCC, NR)

# item 4: the paper's proof structure (STATED, paper.tex lines)
for i, nm, lab, a, b, what in (
        ('L106', 'Theorem 1', 'thm:main', 66, 73, 'there is an absolute c > 0 such that every real zero beta in (0,1) of every primitive nonprincipal real Dirichlet L-function of conductor q >= 3 satisfies (1 - beta) log q >= c, equation (1.1)'),
        ('L107', 'Lemma 2', 'lem:primebias', 181, 194, 'for X >= 3, the prime-sum bound (2.1) over p <= X with chi(p) = 1, and its consequence (2.2), a lower bound for the mass of primes H < p <= X, p not dividing 2q, with chi(p) = -1'),
        ('L108', 'Lemma 3', 'lem:interpolation', 252, 267, 'for a surjective linear A: C^4 -> C^3 with ker A = C c, c with Q-linearly independent coordinates, and t satisfying the budget (3.1), evaluation at A n, n in E_N = {0,...,N-1}^4, is surjective from P_t'),
        ('L109', 'Corollary 4', 'cor:rectangle', 410, 420, 'under the hypotheses of Lemma 3, for 1 <= H <= N, U = N^(4/3), T_1 = 32 H^(2/3) U, T_2 = T_3 = 32 H^(-1/3) U, the monomial rows with alpha_j <= T_j span C^(E_N)'),
        ('L110', 'Lemma 6', 'lem:exponents', 517, 524, 'absolute c_0, C_0 > 0 with S_1 >= c_0 M H^(2/3) U and S_2 <= C_0 M H^(-1/3) U for N large in terms of H, equation (4.4); so S_2/S_1 <= (C_0/c_0)/H'),
        ('L111', 'Lemma 7', 'lem:divisibility', 598, 604, 'for every admissible prime p, Delta lies in p^(E_p) R with E_p the sum over alpha in P of floor(alpha_1/p), equation (5.3)')):
    env = {'thm:main': 'theorem', 'cor:rectangle': 'corollary'}.get(lab, 'lemma')
    row(i, '2', f"The paper states {nm} ({lab}) at refs/siegel-paper.tex:{a}-{b}: {what}.", f'{nm}, tex {a}-{b}', 'paper statement',
        [L(TEX, a, a, '\\begin{' + env + '}\\label{' + lab + '}'), L(TEX, b, b, '\\end{' + env + '}')], 'STATED', A_, NR, NR,
        note='numbering: amsart, one shared counter (tex 16-21), so Remark 5 sits between Corollary 4 and Lemma 6')

# item 5: outcome-level agreement with nealmcb (comparison.txt)
row('L112', '7', "Outcome-level comparison with nealmcb's Comparator run (cmp-all), from comparison.txt: 160 extended-replay configs with a result here at 2026-10-25 ~20:50 were compared; all 160 are accepted there. Here: ACCEPT_BOTH 153, LEAN_ACCEPT_NANODA_CRASH 6, TIMEOUT 1. So the Lean-kernel verdict agrees for 159; 1 has no verdict here; no config accepted there is rejected here.",
    '160 compared; 159 agree; 0 disagree; 1 no verdict here (PlanarPacking, TIMEOUT); nanoda 3a24072 crashed here on 6 (DirectedFeedback, KaplanskyDirectFiniteness, LaughlinFock, LaughlinPlanar, MinUncut, SquareDifference)', 'configs',
    [R(CMP, "our results 160 {'ACCEPT_BOTH': 153"), R(CMP, 'in Neal cmp-all: 160 accepted there: 160'), R(CMP, "our non-ACCEPT_BOTH: [('DirectedFeedback'"),
     R(T227, 'DirectedFeedback\tU\tfalse\tRESULT\tLEAN_ACCEPT_NANODA_CRASH'), R(T227, 'PlanarPacking\tU\tfalse\tRESULT\tTIMEOUT'), R(T227, 'SquareDifference\tU\tfalse\tRESULT\tLEAN_ACCEPT_NANODA_CRASH')],
    'COMPUTED', F_, TCN, NR, note='covers 160 of the final 212 extended-replay results; the other 52 and the 189 are not in comparison.txt. nealmcb\'s side is STATED (his cmp-all, fetched 2026-10-25 ~20:50; the commit of that fetch is not recorded in comparison.txt). The 6 LEAN_ACCEPT_NANODA_CRASH and the TIMEOUT are also the final outcomes in corpus-227-v3.tsv')

# item 5: fd4aeeb control and reroute, times, memory, guard, clone
row('L113', '6', 'fd4aeeb control prebuild (lake build of the solution and challenge modules, 4 threads, in the new clone): service runtime and job count.', '11min 19.935s; 9243 jobs', 'wall time',
    [R(RR + 'control-prebuild.log', 'Service runtime: 11min 19.935s'), R(RR + 'run.log', 'control: prebuild done: Build completed successfully (9243 jobs)')], 'COMPUTED', F_, TC, SB45)
row('L114', '6', 'fd4aeeb reroute prebuild (same clone, after the control, with the two PaperLemma3 modules and the +2/-1 patch): service runtime and job count.', '1min 39.395s; 9245 jobs', 'wall time',
    [R(RR + 'reroute-prebuild.log', 'Service runtime: 1min 39.395s'), R(RR + 'run.log', 'reroute: prebuild done: Build completed successfully (9245 jobs)'), R(RR + 'reroute-prebuild.log', 'Built OAI.NumberTheory.SiegelZeros.PaperLemma3.Lemma3')], 'COMPUTED', F_, TC, SB45)
row('L115', '6', 'Why the reroute prebuild is shorter: it ran in the same clone after the control, so lake reused the control\'s build outputs and rebuilt only the two new modules, the patched module and the modules that depend on it.', 'incremental rebuild', 'reason',
    [R(RR + 'run.log', 'reroute: prebuild start'), R(RR + 'run.log', 'control: prebuild done')], 'INFERRED', F_, TC, SB45,
    note='rests on: the order of the runs (run.log) and lake\'s incremental build; reroute-prebuild.log lists only modules that printed warnings, so the set of rebuilt modules is not recorded')
for i, lab, sec, rss, cg in (('L116', 'control', 842, 7707508, 7412195328), ('L117', 'reroute', 659, 7662352, 6280855552)):
    row(i, '6', f'fd4aeeb {lab} comparator run (nanoda 3a24072 enabled, 16G v1 cgroup cap): wall time, largest process RSS, cgroup peak, OOM kills.', f'{sec} s; max RSS {rss} kB; cgroup max_usage {cg} B; oom_kill 0', 'resources',
        [R(RR + f'{lab}-comparator.log', f'DURATION_SECONDS: {sec}'), R(RR + f'{lab}-comparator.log', f'Maximum resident set size (kbytes): {rss}'), R(RR + f'{lab}-comparator.log', f'cgroup: max_usage_in_bytes {cg}'), R(RR + f'{lab}-comparator.log', 'oom_kill 0')],
        'COMPUTED', F_, TCN, SB45 + ' + 16G v1 cgroup cap (67r)')
row('L118', '6', 'The guard (69_corpus_guard.sh 95 1500 20) made no stops during the fd4aeeb control and reroute (run.log 22:17:36-23:00:18): guard.log has no LIMIT or stopped line in that window, and its periodic drop_caches lines show it running.', '0 LIMIT lines; 0 stops', 'guard events',
    [R(EV + 'guard-window-20261026.txt', "LIMIT lines in window: 0; 'stopped' lines in window: 0"), R(EV + 'guard-window-20261026.txt', '2026-10-26 22:51:03 drop_caches'), R(RR + 'run.log', '150 done')], 'COMPUTED', F_, NR, NR,
    note='guard.log is /home/checker/corpus/guard.log (outside the repo); the extract records its sha256 at extraction')
row('L119', '6', 'Clone setup of the fd4aeeb reroute runs: /home/checker/math-r2 is a local git clone of /home/checker/math (no network), at fd4aeeb with 0 tracked changes; lake-manifest.json, lean-toolchain and lakefile.lean equal the original\'s; lean/.lake/packages is bind-mounted read-only from the original clone and a write as checker was refused; the mount was removed at the end.',
    'local clone; packages read-only bind mount; write refused', 'setup',
    [R(RR + 'run.log', '1. clone /home/checker/math-r2 HEAD fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb, tracked changes 0, origin /home/checker/math'), R(RR + 'run.log', 'lean/lake-manifest.json: original cf6105a25d9dca2f clone cf6105a25d9dca2f'),
     R(RR + 'run.log', 'packages: /dev/sdc[/home/checker/math/lean/.lake/packages] /home/checker/math-r2/lean/.lake/packages ro,'), R(RR + 'run.log', 'packages mount is read-only (write as checker refused)'),
     R(RR + 'run.log', 'bind mount removed', 2), R(EV + 'clone-r2-provenance.txt', 'clone: from /home/checker/math')], 'COMPUTED', F_, NR, NR)
row('L120', '6', 'The OAI closure was built from scratch in that clone: the clone was created at 2026-10-26 22:17:36 (precheck), its lean/.lake/build directory was created at 22:19:37, after the control prebuild started (22:19:09), and the oldest OAI .olean dates from 22:19:53.',
    'build dir born 22:19:37 (control prebuild start 22:19:09)', 'provenance',
    [R(EV + 'clone-r2-provenance.txt', '1793067456 = 2026-10-26 22:17:36'), R(EV + 'clone-r2-provenance.txt', '| /home/checker/math-r2/lean/.lake/build'), R(EV + 'clone-r2-provenance.txt', 'OAI/NumberTheory/SiegelZeros/Differentials/LogDerivative.olean'), R(RR + 'run.log', 'control: prebuild start')],
    'COMPUTED', F_, NR, NR, note='birth times from stat %w (ext4) and the clone reflog, read 2026-10-27; packages were not rebuilt (L119)')

# item 5: Lean-kernel comparator runs on Catalan and KMedianThreshold
for i, c, s, el in (('L121', 'KMedianThreshold', 369, '6:09.14'), ('L122', 'Catalan', 2234, '37:14.35')):
    row(i, '7', f'{c}: the shipped-config Comparator run (enable_nanoda false, Lean kernel only) accepts; wall time of the whole run (build, export, checks).', f'{s} s; exit 0', 'wall time',
        [R(MX + f'runs/{c}.lean-shipped.log', 'Lean default kernel accepts the solution'), R(MX + f'runs/{c}.lean-shipped.log', 'COMPARATOR EXIT CODE: 0'), R(MX + f'runs/{c}.lean-shipped.log', f'DURATION_SECONDS: {s}'),
         R(MX + f'runs/{c}.lean-shipped.log', '"enable_nanoda": false'), R(RR + 'optional/README.md', f'| {c} |')], 'COMPUTED', F_, TC, SB45 + ' + 16G v1 cgroup cap (67d)',
        note=f'/usr/bin/time elapsed {el}; this is the whole comparator run, not the kernel replay alone')

# item 5: sandbox of the 2026-10-20 statement checks and of the 2026-10-08 standalone nanoda run
row('L123', '8', 'Sandbox of the 2026-10-20 statement-check build (the v2 log): statement-checks/build.sh runs lake build as checker via sudo -u checker, with the WSL guard; no systemd-run unit and no RestrictAddressFamilies filter.',
    'sudo -u checker; no systemd-run; no address-family filter', 'sandbox',
    [R('statement-checks/build.sh', 'sudo -u checker -H bash -lc "export PATH=\\$HOME/.elan/bin:\\$PATH LEAN_NUM_THREADS=4; cd $DST && lake build'), R('statement-checks/build.sh', '69_corpus_guard.sh 85 1500 2'),
     R(LG + 'statement-checks-final-v2.log', '== build 2026-10-20 12:49:57 lake build')], 'COMPUTED', F_, TC, NR,
    note='the log header matches build.sh line 7; build.sh was committed in 1a11952 (2026-10-20 12:52), 3 minutes after the build, and is unchanged since')
row('L124', '8', 'Sandbox of the 2026-10-08 standalone nanoda run on Lemma3Bridged (L033-L035): wsl-comparator/36_nanoda_lemma3.sh runs lean, lean4export and nanoda_bin as checker via sudo -u checker; no systemd-run unit and no RestrictAddressFamilies filter.',
    'sudo -u checker; no systemd-run; no address-family filter', 'sandbox',
    [R('wsl-comparator/36_nanoda_lemma3.sh', "sudo -u checker -H bash -lc '"), R('results/2026-10-08-lean-lemma3-nanoda.txt', 'wsl-comparator/36_nanoda_lemma3.sh')], 'COMPUTED', A_, TCN, NR,
    note='the script is first committed in 447ad02 (2026-10-09 08:50), after the run, and is unchanged since; that the committed text is the text that ran is INFERRED')

# item 6: nealmcb's ContinuumCoulombHardness figures (STATED)
NOTE6 = 'local transcriptions only (no network); comparison.txt was fetched 2026-10-25 ~20:50 at a commit it does not record, so agreement with 1ca7ff2 is UNCONFIRMED'
row('L125', '7', "nealmcb: Comparator as shipped (Lean kernel) accepts ContinuumCoulombHardness, check time 923.63 s.", 'accepted; 923.63 s', 'verdict',
    [NEAL + 'results/cmp-all/STATUS.md', R(CMP, 'ContinuumCoulombHardness | cmp: accepted nanoda_cfg False build None cmp 923.63')], 'STATED', F_, 'nealmcb pins (MANIFEST.txt at 1ca7ff2)', 'nealmcb sandbox (landrun)', note=NOTE6)
row('L126', '7', "nealmcb: on his ContinuumCoulombHardness export, the kernel-pair sweep records exit 1 for both the Lean kernel replay and nanoda 3a24072 (99.3 s).", 'lean 1; nanoda 1 (99.3 s)', 'exit codes',
    [NEAL + 'results/kernel-pair-sweep.jsonl', R(CMP, 'pair: lean 1  nanoda 1 99.3 None')], 'STATED', F_, 'nealmcb pins', 'nealmcb', note=NOTE6 + '; the cause of exit 1 is not recorded locally')
row('L127', '7', "nealmcb: nanoda f67473b retests of ContinuumCoulombHardness: exit 0 at 130.1 s and 114.3 s, exit 134 at 28.6 s and 28.8 s; 998e0a8 exit 134 at 32.8 s. The ~24 GiB figure for f67473b is from nanoda_lib #61.", "('f67473b', 0, 130.1), ('f67473b', 0, 114.3), ('f67473b', 134, 28.6), ('f67473b', 134, 28.8), ('998e0a8', 134, 32.8); ~24 GiB",
    'exit code, seconds', [NEAL + 'results/', 'https://github.com/ammkrn/nanoda_lib/issues/61', R(CMP, "retest: [('f67473b', 0, 130.1), ('f67473b', 0, 114.3), ('f67473b', 134, 28.6)"), R(MX + 'matrix-v3.tsv', 'STATED: accepted, 130 s, ~24 GiB')],
    'STATED', F_, 'nanoda f67473b / 998e0a8', 'nealmcb', note=NOTE6 + '; the #61 text with ~24 GiB is not saved locally (matrix-v3.tsv transcribes it)')
row('L128', '7', "nealmcb: with the let fix and the Nat.succ guard (his patch) at STACK_SIZE 64 MiB, nanoda 37cb87b passes ContinuumCoulombHardness at 50.0 s and 1.8 GB; with the let fix alone it overflows at 64 MiB (34 s, 4 GB) and 256 MiB (48 s, 13 GB).", 'pass 50.0 s 1.8GB; let fix alone: overflow 34 s 4GB (64 MiB), overflow 48 s 13GB (256 MiB)', 'result',
    [NEAL + 'results/nanoda-stack-size-2026-10-25.txt', R(CMP, 'ContinuumCoulombHardness     pass 50.0 s 1.8GB'), R(CMP, 'ContinuumCoulombHardness     -                 overflow 34 s 4GB  -                 overflow 48 s 13GB')],
    'STATED', F_, 'nanoda 37cb87b (+ patch)', 'nealmcb', note='comparison.txt copies the file verbatim; ' + NOTE6)

# item 7: section 10 facts (git trailers, docs/log.md)
TF = EV + 'claude-trailer-files.txt'
row('L129', '10', "Files under lean-checks/, wsl-comparator/ and src/ that have at least one commit whose message carries a 'Co-Authored-By: Claude' trailer: all tracked files in each directory.", 'lean-checks 260 of 260; wsl-comparator 214 of 214; src 22 of 22', 'files',
    [R(TF, '# lean-checks: tracked 260; touched by a trailer commit 260'), R(TF, '# wsl-comparator: tracked 214; touched by a trailer commit 214'), R(TF, '# src: tracked 22; touched by a trailer commit 22'), R(TF, 'with the trailer: 174')], 'COMPUTED', NR, NR, NR,
    note='file list in claude-trailer-files.txt; 174 of 175 commits carry the trailer (the other is 505334b, README only). A trailer marks a commit, not who wrote each line')
POSTS = [('grwtsk/openai-math #40, comment 6291050955 (2026-10-20)', 'drafts saved, not posted: docs/drafts/2026-10-20-issue40-corpus-comment.md', 'Posted the #40 comment (Joe approved, with my wording change kept)'),
         ('nanoda_lib #55, comment 6291244827 (2026-10-20)', 'docs/drafts/2026-10-20-nanoda55-comment.md (facts, commands and the neutral question', 'Posted the #55 comment (approved)'),
         ('grwtsk/openai-math #29, comment 6296359378 (2026-10-20)', 'saved as docs/drafts/2026-10-20-issue29-statement-check.md', 'posted the #29 comment (Joe approved, with his three added lines)'),
         ('nanoda_lib #61, comment 6431284502 (2026-10-26)', 'reply-61-draft.md (not posted)', 'The body is results/2026-10-26-nanoda-version-matrix/reply-61-draft.md')]
row('L130', '10', 'Public posts whose drafts docs/log.md records as written in the session (first-person log entries of the Claude Code sessions) before posting: ' + '; '.join(p[0] for p in POSTS) + '.',
    '4 posts: ' + '; '.join(p[0] for p in POSTS), 'posts', [R(LOG, s) for p in POSTS for s in p[1:]], 'COMPUTED', NR, NR, NR,
    note='not listed, because docs/log.md records the post but no draft or drafter: the 2026-10-09 #40 packet comment and a Lean Zulip post (' + R(LOG, 'Comment on grwtsk/openai-math issue #40: [comment URL to be added]') + '), and the 2026-10-26 #40 vsock follow-up 6431288875 (' + R(LOG, 'the one-line vsock follow-up in results/2026-10-26-network-check/zenodo-descriptions.md') + '). The #40 2026-10-20 draft is recorded as "Joe\'s text plus his cause sentence"')

# item 8: L086 is cut from the outline but keeps its id (status unchanged here; see claim-map.tsv)

# ---------------- write ----------------
if problems:
    print('PROBLEMS (ledger not written):'); print('\n'.join(problems)); sys.exit(1)
cols = cols2 + ['read_by', 'read_note']
allrows = rows + new
seen = [r['id'] for r in allrows]
assert len(seen) == len(set(seen)), 'duplicate id'
assert [r['id'] for r in new] == [f'L{k:03d}' for k in range(99, 99 + len(new))], 'new ids must be consecutive from L099'
p = os.path.join(OUT, 'ledger-v3.tsv')
if os.path.exists(p): sys.exit(f'refusing to overwrite {p}')
with open(p, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t', lineterminator='\n'); w.writerow(cols)
    for r in allrows: w.writerow([r[c] for c in cols])
print('rows', len(allrows), '(v2', len(rows), '+ new', len(new), ')', 'new by label', dict(collections.Counter(r['label'] for r in new)),
      'all by label', dict(collections.Counter(r['label'] for r in allrows)), 'status', dict(collections.Counter(r['status'] for r in allrows)))
