"""Extended replay, Phase 0.4 + Phase 4 inputs (read-only on the clone; new files only).

Usage: python -I scripts/extended_plan.py <clone at fd4aeeb> <repo root> <out dir> <query dir>
Writes <out dir>/phase0-configs-227.tsv (run order: the 5 pilot configs first), phase0-configs-227-summary.txt,
phase4-challenge-placeholders.tsv, and <query dir>/<config>-axioms.lean, <config>-audit-{challenge,solution}.lean.
Refuses to overwrite any existing output.
"""
import csv, json, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
clone, root, out, qdir = sys.argv[1:5]
L = os.path.join(clone, 'lean')
P4 = os.path.join(root, 'results', '2026-10-21-paper-prep-4')
STD = {'propext', 'Classical.choice', 'Quot.sound'}
outs = [os.path.join(out, f) for f in ('phase0-configs-227.tsv', 'phase0-configs-227-summary.txt', 'phase4-challenge-placeholders.tsv')]
for p in outs:
    if os.path.exists(p): sys.exit(f'refusing to overwrite {p}')
if os.path.isdir(qdir) and os.listdir(qdir): sys.exit(f'refusing: {qdir} is not empty')
os.makedirs(out, exist_ok=True); os.makedirs(qdir, exist_ok=True)

grp = {r['config']: r['group'] for r in csv.DictReader(open(os.path.join(P4, 'unreferenced-configs.tsv'), encoding='utf-8'), delimiter='\t')}
ns = {r['config']: r['setting'] for r in csv.DictReader(open(os.path.join(P4, 'nanoda-settings.tsv'), encoding='utf-8'), delimiter='\t') if r['commit'] == 'fd4aeeb'}
assert len(grp) == 227
C = {n: json.load(open(os.path.join(L, 'ComparatorChallenges', n + '.json'), encoding='utf-8')) for n in grp}
lines = {n: sum(1 for _ in open(os.path.join(L, 'ComparatorChallenges', n + '.lean'), encoding='utf-8')) for n in grp}
on = sorted(n for n in grp if ns[n] == 'true')
assert len(on) == 1, on
pilot = {g: min((n for n in grp if grp[n] == g), key=lambda n: (lines[n], n)) for g in 'PCUSN'}
order = [pilot[g] for g in 'PCUSN'] + sorted(n for n in grp if n not in pilot.values())

# ---- challenge-file placeholders: axiom / opaque declarations anywhere; sorry / admit outside theorem/lemma stubs
def strip(src):  # comments -> spaces, newlines kept (line numbers preserved)
    out, i, depth, n = [], 0, 0, len(src)
    while i < n:
        if src.startswith('/-', i): depth += 1; out.append('  '); i += 2; continue
        if depth and src.startswith('-/', i): depth -= 1; out.append('  '); i += 2; continue
        if depth or src.startswith('--', i) and not depth:
            if depth:
                out.append('\n' if src[i] == '\n' else ' '); i += 1; continue
            j = src.find('\n', i); j = n if j < 0 else j; out.append(' ' * (j - i)); i = j; continue
        out.append(src[i]); i += 1
    return ''.join(out)

MODS = r'(?:@\[[^\]]*\]\s*)?(?:(?:private|protected|noncomputable|partial|unsafe)\s+)*'
DECL = re.compile(r'^\s*' + MODS + r'(theorem|lemma|def|abbrev|instance|structure|inductive|opaque|axiom|example|class)\b\s*(\S*)', re.M)
rows = []
for n in order:
    src = strip(open(os.path.join(L, 'ComparatorChallenges', n + '.lean'), encoding='utf-8').read())
    nsstack = []
    lns = src.split('\n')
    decls = []  # (line, kind, name, qualified)
    for i, l in enumerate(lns, 1):
        m = re.match(r'^\s*namespace\s+(\S+)', l)
        if m: nsstack.append(m.group(1)); continue
        m = re.match(r'^\s*(?:noncomputable\s+)?section\b\s*(\S*)', l)
        if m: nsstack.append(None); continue
        m = re.match(r'^\s*end\b\s*(\S*)', l)
        if m and nsstack: nsstack.pop(); continue
        m = DECL.match(l)
        if m:
            nm = m.group(2)
            q = nm[len('_root_.'):] if nm.startswith('_root_.') else '.'.join([x for x in nsstack if x] + [nm])
            decls.append((i, m.group(1), nm, q))
    for (i, k, nm, q) in decls:
        if k in ('axiom', 'opaque'):
            rows.append((n, grp[n], k + ' declaration', i, k, q, q in C[n].get('definition_names', []), lns[i - 1].strip()[:150]))
    for pat, what in ((r'\bsorry\b', 'sorry'), (r'\badmit\b', 'admit')):
        for i, l in enumerate(lns, 1):
            if not re.search(pat, l): continue
            d = [x for x in decls if x[0] <= i]
            if d and d[-1][1] in ('theorem', 'lemma'): continue
            k, q = (d[-1][1], d[-1][3]) if d else ('(none)', '')
            in_def = q in C[n].get('definition_names', []) or q.split('.')[-1] in {x.split('.')[-1] for x in C[n].get('definition_names', [])}
            rows.append((n, grp[n], f'{what} outside theorem/lemma', i, k, q, in_def, l.strip()[:150]))

with open(outs[2], 'w', encoding='utf-8', newline='\n') as f:
    f.write('config\tgroup\tfinding\tline\tenclosing_kind\tenclosing_name_qualified_guess\tin_definition_names\ttext\n')
    for r in rows: f.write('\t'.join(map(str, r)) + '\n')
flagged = sorted({r[0] for r in rows})

with open(outs[0], 'w', encoding='utf-8', newline='\n') as f:
    f.write('order\tconfig\tgroup\tpilot\tshipped_nanoda\tchallenge_lines\tn_theorems\textra_permitted_axioms\tplaceholder_flagged\n')
    for i, n in enumerate(order, 1):
        extra = sorted(set(C[n]['permitted_axioms']) - STD)
        f.write(f'{i}\t{n}\t{grp[n]}\t{n in pilot.values()}\t{ns[n] or "absent"}\t{lines[n]}\t{len(C[n]["theorem_names"])}\t{",".join(extra)}\t{n in flagged}\n')

# ---- Lean query files
tmpl = open(os.path.join(root, 'lean-checks', 'corpus-queries', '_template.lean.in'), encoding='utf-8').read()
head, last = tmpl.rsplit('#audit_query @THM@ @TARGET@', 1)
for n in order:
    with open(os.path.join(qdir, f'{n}-axioms.lean'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(f'-- Extended replay, Phase 4.1 (generated by scripts/extended_plan.py): #print axioms on every theorem_names entry of\n'
                f'-- ComparatorChallenges/{n}.json and every definition_names entry, in the solution environment.\n'
                f'-- Run with `lake env lean <file>` in the checker sandbox.\n'
                f'import {C[n]["solution_module"]}\n' +
                ''.join(f'#print axioms {t}\n' for t in C[n]['theorem_names'] + C[n].get('definition_names', [])))
for n in flagged:
    targets = sorted({r[5] for r in rows if r[0] == n and r[5]})
    for side, mod in (('challenge', C[n]['challenge_module']), ('solution', C[n]['solution_module'])):
        body = head.replace('@MODULE@', mod).replace('gen.sh', 'scripts/extended_plan.py')
        body += ''.join(f'#audit_query {t} {g}\n' for t in (C[n]['theorem_names'] or C[n].get('definition_names', [])) for g in targets)
        open(os.path.join(qdir, f'{n}-audit-{side}.lean'), 'w', encoding='utf-8', newline='\n').write(body + last.lstrip('\n'))

extra_all = [(n, sorted(set(C[n]['permitted_axioms']) - STD)) for n in order if set(C[n]['permitted_axioms']) - STD]
S = ['Extended replay, Phase 0.4 (COMPUTED; scripts/extended_plan.py; clone at fd4aeeb)',
     f'configs: {len(order)}; by group: ' + ', '.join(f'{g} {sum(1 for n in grp if grp[n] == g)}' for g in 'PCUSN'),
     f'shipped nanoda setting among the 227: true {sum(ns[n] == "true" for n in grp)}, false {sum(ns[n] == "false" for n in grp)}, absent {sum(ns[n] in ("", "absent") for n in grp)}',
     f'the one config shipping with nanoda on: {on[0]}',
     f'configs with no nanoda key (Comparator default: off): {sorted(n for n in grp if ns[n] in ("", "absent"))}',
     'pilot (smallest challenge file per group): ' + '; '.join(f'{g} {pilot[g]} ({lines[pilot[g]]} lines)' for g in 'PCUSN'),
     f'Phase 4.2 inputs: {len(rows)} placeholder findings in {len(flagged)} challenge files: {flagged}',
     f'Phase 4.3: configs whose permitted_axioms go beyond propext, Classical.choice, Quot.sound: {len(extra_all)} {extra_all}',
     f'query files written to {os.path.relpath(qdir, root)}: {len(os.listdir(qdir))}']
open(outs[1], 'w', encoding='utf-8', newline='\n').write('\n'.join(S) + '\n')
print('\n'.join(S))
