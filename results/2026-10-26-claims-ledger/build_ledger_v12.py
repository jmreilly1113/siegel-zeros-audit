"""Claims ledger v12 (2026-10-27): rows for the abstract, introduction and sections 8 and 10. Writes ledger-v12.tsv.

Usage: python -I results/2026-10-26-claims-ledger/build_ledger_v12.py <repo root>
Append-only: every ledger-v11.tsv row is copied byte-for-byte; new rows L258-L269.
Rows L263-L266 record the author's own reasoning, and L267 his statement about his process, as he gave them (docs/log.md, 2026-10-27).
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
NR = 'n/a'; NONE = 'none (no run; source text)'
EV = 'results/2026-10-26-claims-ledger/v12-evidence/'; LOG = 'docs/log.md'; RD = 'results/2026-10-27-readings/readings-claude-code.md'
AU = 'J. Reilly, 2026-10-27 (author\'s reasoning as stated in his prompt, recorded verbatim in docs/log.md)'

with open(os.path.join(OUT, 'ledger-v11.tsv'), encoding='utf-8') as f:
    rd = csv.reader(f, delimiter='\t'); cols = next(rd); rows = [dict(zip(cols, r)) for r in rd]
assert [r['id'] for r in rows] == [f'L{k:03d}' for k in range(1, 258)], 'ledger-v11.tsv ids are not L001-L257'
new = []


def row(i, sec, claim, value, unit, src, label, commit, tc, sb, note='', read_by='', read_note=''):
    assert i == f'L{258 + len(new):03d}', i
    new.append(dict(id=i, paper_section=sec, claim=claim, value=value, unit=unit, source='; '.join(src),
                    label=label, openai_math_commit=commit, toolchain=tc, sandbox=sb, status='FOUND', note=note, read_by=read_by, read_note=read_note))


AB = EV + 'arxiv-2610.08144-abstract.txt'
row('L258', '1', 'arXiv:2610.08144v1 (6 Oct 2026), "Navier-Stokes lost in translation: Why Lean verification of AI autoformalisation does not guarantee correct natural language proofs", argues that a Lean check of an AI autoformalisation may offer no confidence in the natural-language argument, and states "we show that the formalised Lean proof does not correspond to the NL proof of blow-up of solutions to the Navier-Stokes equations". Its Section 1 states: "We do not make claims about the correctness of OpenAI\'s NL proof, we only make statements about mistranslations into Lean."',
    'Bastounis, Circelli and Hansen [arXiv:2610.08144] argue that a Lean check of an AI autoformalisation need not certify the natural-language proof, and show for OpenAI\'s Navier–Stokes formalisation that the Lean proof does not correspond to the natural-language proof.', 'framing sentence',
    [R(AB, 'Title:Navier-Stokes lost in translation'), R(AB, 'may offer no confidence in the original NL argument'), R(AB, 'we show that the formalised Lean proof does not correspond to the NL proof of blow-up'), R(AB, 'Section 1, disclaimer:'),
     R(RD, '**Suggested sentence:**')],
    'STATED', NR, NR, NR, note='the framing sentence is the one suggested in readings-claude-code.md (reading 7); the abstract and disclaimer are quoted from the read-only copy (sha256 in the evidence file)',
    read_by='', read_note='Joe: "i did that reading" (' + R(LOG, 'Author\'s reading of arXiv:2610.08144: "i did that reading"') + '); no sign-off line with a finding')
row('L259', '1', 'The explicit-constant note docs/effectivity/note-v2.pdf is contained in the tag reviewer-packet-v3, archived as Zenodo 10.5281/zenodo.23523697 (checked on GitHub\'s zipball of the tag, not on the Zenodo-archived file).',
    'docs/effectivity/note-v2.pdf in reviewer-packet-v3 (10.5281/zenodo.23523697)', 'archive content',
    [R('results/2026-10-21-v3-deposit/archive-comparison-github-zipball.txt', 'contains docs/effectivity/note-v2.pdf: True'), R('results/2026-10-21-v3-deposit/archive-comparison-github-zipball.txt', 'v3 deposit: archive comparison (COMPUTED on GitHub\'s zipball of tag reviewer-packet-v3, NOT on the Zenodo-archived file)')],
    'COMPUTED', NR, NR, NR, note='the Zenodo file itself (md5 048a6d06...) was not compared byte for byte; the zipball md5 differs, as recorded in the same file')
PS = 'results/2026-10-11-corpus-pilot-summary.txt'
row('L260', '8', 'Comparator negative controls on SiegelZeros (pilot, adc7f12): with Classical.choice not permitted, Comparator reports "Illegal axiom detected: \'Classical.choice\'" and exits 1; with the challenge statement altered, it reports "Challenge and solution theorem statement do not match" for exists_absolute_real_zero_gap and exits 1.',
    'control-noChoice: Illegal axiom detected, exit 1; control-altered: statement mismatch, exit 1', 'verdict',
    [R(PS, "SiegelZeros-control-noChoice: uncaught exception: Illegal axiom detected: 'Classical.choice' | COMPARATOR EXIT CODE: 1"), R(PS, "SiegelZeros-control-altered: uncaught exception: Challenge and solution theorem statement do not match"), R(PS, 'No negative control was accepted.')],
    'COMPUTED', A_, 'Lean 4.34.1 / Mathlib d13f23b / Comparator d03acab / lean4export 076e8e5 / nanoda 3a24072 (STACK_SIZE 16 MiB)', 'systemd-run --user, checker, NoNewPrivs; 5-family filter (pilot, 2026-10-11)')
TF = EV + 'claude-trailer-files-paper.txt'
row('L261', '10', "Files under paper/ (the outline, the claim map, the draft sections 2-7, main.tex, check.py) and the ledger builders build_ledger*.py that have at least one commit carrying a 'Co-Authored-By: Claude' trailer: all tracked ones.",
    '22 of 22', 'files', [R(TF, '# tracked: 22; touched by a trailer commit: 22'), R(TF, 'trailer\tpaper/draft/check.py'), R(TF, 'trailer\tpaper/draft/sec2-background.tex'), R(TF, 'trailer\tresults/2026-10-26-claims-ledger/build_ledger.py')],
    'COMPUTED', NR, NR, NR, note='a trailer marks a commit, not who wrote each line; complements v3:L129 (lean-checks/, wsl-comparator/, src/)')
row('L262', '10', 'The reading notes results/2026-10-27-readings/readings-claude-code.md are Claude Code\'s readings, made on 2026-10-27 at Joe\'s request, as the file\'s own header states.',
    "Claude Code's readings", 'authorship', [L(RD, 1, 3, "These are Claude Code's readings, made on 2026-10-27 at Joe's request.")], 'COMPUTED', NR, NR, NR)
for i, sec, claim, sub, basis in (
        ('L263', '8', 'Two kernels reduce the risk of a kernel bug but not of an exporter or build bug.', '"two kernels reduce the risk of a kernel bug but not of an exporter or build bug."', 'both kernel checks share the Lake build and the lean4export export (v5:L142)'),
        ('L264', '8', 'Every outcome on both sides of the 402-of-402 comparison was acceptance, so the comparison does not test rejection.', '"every outcome on both sides was acceptance, so the comparison doesn\'t test rejection."', 'his 416 outcomes are all accepted and ours with a verdict are all Lean-kernel acceptances (v5:L141)'),
        ('L265', '3; 8', 'The non-vacuity lemmas rule out a vacuous challenge but do not establish faithfulness.', '"The non-vacuity lemmas rule out a vacuous challenge but don\'t establish faithfulness."', 'the non-vacuity lemmas show the hypotheses can be met (v2:L011-L014); faithfulness rests on the readings (v7:L002-L008)'),
        ('L266', '8', 'None of the three runs with no network filter (NonVacuity, standalone nanoda, statement checks) is a run where a filter affects the result.', '"None of those three is a run where a filter affects the result."', 'v4:L138, v3:L124, v3:L123')):
    row(i, sec, claim, claim.rstrip('.'), "author's reasoning", [R(LOG, sub)], 'INFERRED', NR, NR, NR, note=f'rests on the author\'s reasoning; basis: {basis}', read_by=AU)
row('L267', '10', 'The author states that Claude in chat did the planning and the prompts, gave the Lemma 3 and Corollary 4 statement comparison that preceded his reading, and helped draft public posts.',
    "author's statement", 'statement', [R(LOG, '"Claude in chat did the planning and the prompts, gave the Lemma 3 and Corollary 4 statement comparison that preceded your reading, and helped draft public posts."')],
    'STATED', NR, NR, NR, note='source: the author (docs/log.md). The repository record differs in part: the 2026-10-08 statement review of Lemma 3 is a first-person Claude Code log entry (docs/log.md:277, docs/lemma3-lean-statement-review.md; v3:L100 read_by), and v3:L130 records four post drafts written in the Claude Code sessions. Both can be true; the paper should state what the author can confirm',
    read_by='J. Reilly (author statement)')

row('L268', '1', 'Citation identity of arXiv:2610.15483: v1, dated October 11, 2026, DOI 10.48550/arXiv.2610.15483 (local citation note in refs/; the PDF is not redistributed). Cited in the paper only as arXiv:2610.15483.',
    'arXiv:2610.15483 v1 (October 11, 2026); doi:10.48550/arXiv.2610.15483', 'citation',
    [R('refs/banks-2610.15483.md', 'arXiv:2610.15483 [v1, dated October 11, 2026'), R('refs/banks-2610.15483.md', '- Abstract page: https://arxiv.org/abs/2610.15483')], 'STATED', NR, NR, NR,
    note='cite by arXiv number only (project rule)')

row('L269', '1; 10', 'The author states that no specialist in analytic number theory or transcendence has reviewed the mathematics.',
    "author's statement", 'statement', [R(LOG, 'No specialist in analytic number theory or transcendence has reviewed the')], 'STATED', NR, NR, NR,
    note='source: the author (docs/log.md, 2026-10-27); his sentence was cut off after "the" and is completed as "the mathematics"', read_by='J. Reilly (author statement)')

if problems:
    print('PROBLEMS (ledger not written):'); print('\n'.join(ascii(x) for x in problems)); sys.exit(1)
p = os.path.join(OUT, 'ledger-v12.tsv')
if os.path.exists(p): sys.exit(f'refusing to overwrite {p}')
with open(p, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t', lineterminator='\n'); w.writerow(cols)
    for r in rows + new: w.writerow([r[c] for c in cols])
print('rows', len(rows) + len(new), 'new', [r['id'] for r in new], dict(collections.Counter(r['label'] for r in new)))
