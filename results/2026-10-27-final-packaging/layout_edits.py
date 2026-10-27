"""Layout edits to paper/draft (2026-10-27, Joe: "fix the offpage text", "don't include the ledger ids"). Prints every change.

Usage: python -I results/2026-10-27-final-packaging/layout_edits.py <repo root>
Text outside comments, Verbatim blocks and %% QUOTE blocks only; the words and values are unchanged:
  1. every hex string of 40-64 characters becomes \\hash{...} (main.tex: a break point after each character);
  2. in \\caption lines, a path with three or more / gets \\allowbreak after each /;
  3. sec7-corpus.tex table cell ContinuumCoulombHardness gets discretionary hyphens (Continuum\\-Coulomb\\-Hardness);
  4. the four reasoning-point captions lose " (v7:L00x)";
  5. refs.bib: \\texttt{preprints/...} becomes \\nolinkurl{preprints/...} (breaks at /).
"""
import os, re, sys
root = sys.argv[1]; D = os.path.join(root, 'paper', 'draft')
FILES = ['abstract.tex', 'sec1-intro.tex', 'sec2-background.tex', 'sec3-faithfulness.tex', 'sec4-gap.tex', 'sec5-lemma3.tex', 'sec6-reroute.tex', 'sec7-corpus.tex', 'sec8-threats.tex', 'sec9-artifacts.tex', 'sec10-ai.tex', 'appendix-78-listings.tex', 'appendix-reasoning.tex']

def split_comment(line):
    m = re.search(r'(?<!\\)%', line)
    return (line, '') if not m else (line[:m.start()], line[m.start():])

n_changes = 0
for f in FILES:
    p = os.path.join(D, f)
    L = open(p, encoding='utf-8', newline='').read().split('\n')
    inq = None
    for i, line in enumerate(L):
        if inq:
            if line.startswith('\\end{' + inq + '}'): inq = None
            continue
        if re.match(r'^%% QUOTE', line):
            inq = re.match(r'\\begin\{(Verbatim|paperquote)\}', L[i + 1]).group(1); continue
        m = re.match(r'^\s*\\begin\{(Verbatim)\}', line)
        if m: inq = 'Verbatim'; continue
        if line.lstrip().startswith('%'): continue
        text, com = split_comment(line)
        new = re.sub(r'(?<![0-9a-fA-F{])([0-9a-f]{40,64})(?![0-9a-fA-F])', r'\\hash{\1}', text)
        if text.lstrip().startswith('\\caption'):
            new = re.sub(r'(?<![\w/])((?:[\w.\-]+/){3,}[\w.\-:]+)', lambda m: m.group(1).replace('/', '/\\allowbreak '), new)
        if f == 'sec7-corpus.tex' and new.startswith('ContinuumCoulombHardness &'):
            new = new.replace('ContinuumCoulombHardness', 'Continuum\\-Coulomb\\-Hardness', 1)
        new = re.sub(r' \(v7:L00[2468]\)', '', new) if 'Reasoning points behind' in new else new
        if new != text:
            n_changes += 1
            print(f'{f}:{i + 1}\n  - {text[:200]}\n  + {new[:200]}')
            L[i] = new + com
    open(p, 'w', encoding='utf-8', newline='').write('\n'.join(L))
b = os.path.join(D, 'refs.bib')
s = open(b, encoding='utf-8', newline='').read()
s2, k = re.subn(r'\\texttt\{(preprints/[^}]*)\}', r'\\nolinkurl{\1}', s)
open(b, 'w', encoding='utf-8', newline='').write(s2)
print(f'refs.bib: {k} \\texttt -> \\nolinkurl')
print('changed lines:', n_changes)
