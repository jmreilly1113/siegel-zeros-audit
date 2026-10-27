"""Step 2 of the final packaging (2026-10-27): residue scan. Reports hits; fixes nothing.

Usage: python -I results/2026-10-27-final-packaging/residue_scan.py <repo root>
Scans every paper/draft/*.tex and refs.bib (whole lines, comments included), the compiled PDF's text (draft-main.utf8.txt, pdftotext -enc UTF-8),
and the LaTeX log (draft-main.log). Patterns:
  placeholders: TODO, XXX, TAG-PENDING, MISSING-ROW, UNCONFIRMED, JOE WRITES, and <...> template tokens;
  chatbot residue: "As an AI", "Certainly", "Here is", "I hope", "Let me", "I'll", and second person (you, your, yours, yourself);
  the log: undefined references or citations.
"""
import glob, os, re, sys
root = sys.argv[1]; D = os.path.join(root, 'paper', 'draft'); O = os.path.join(root, 'results', '2026-10-27-final-packaging')
SUB = sys.argv[2] if len(sys.argv) > 2 else ''  # optional output folder, e.g. final (the final build); its files have no -2 suffix
O = os.path.join(O, SUB) if SUB else O
PLACE = [('TODO', r'TODO'), ('XXX', r'XXX'), ('TAG-PENDING', r'TAG-PENDING'), ('MISSING-ROW', r'MISSING-ROW'), ('UNCONFIRMED', r'UNCONFIRMED'), ('JOE WRITES', r'JOE WRITES'),
         ('<...> token', r'<[A-Za-z][A-Za-z0-9 _.-]{0,40}>')]
CHAT = [('As an AI', r'(?i)\bas an ai\b'), ('Certainly', r'\bCertainly\b'), ('Here is', r'\bHere is\b'), ('I hope', r'\bI hope\b'), ('Let me', r'\bLet me\b'), ("I'll", r"\bI'll\b"),
        ('second person', r'(?i)\b(you|your|yours|yourself)\b')]
hits = []
def scan(label, text):
    for n, line in enumerate(text.split('\n'), 1):
        for kind, pat in PLACE + CHAT:
            if re.search(pat, line):
                hits.append((kind, f'{label}:{n}', line.strip()[:140]))
for f in sorted(glob.glob(os.path.join(D, '*.tex'))) + [os.path.join(D, 'refs.bib')]:
    scan('paper/draft/' + os.path.basename(f), open(f, encoding='utf-8').read())
scan('PDF text', open(os.path.join(O, 'draft-main.utf8.txt'), encoding='utf-8').read().replace('’', "'"))  # pdftotext -enc UTF-8; curly apostrophe normalised
log = open(os.path.join(O, 'draft-main.log'), encoding='latin-1').read()
for n, line in enumerate(log.split('\n'), 1):
    if re.search(r'(?i)undefined|There were undefined|Citation .* undefined|Reference .* undefined', line):
        hits.append(('LaTeX log: undefined', f'draft-main.log:{n}', line.strip()[:140]))
out = os.path.join(O, 'residue-scan.txt' if SUB else 'residue-scan-2.txt')  # second run: UTF-8 PDF text, one hit per (pattern, line); residue-scan.txt is the first run
with open(out, 'x', encoding='utf-8', newline='\n') as o:
    o.write('# Residue scan (step 2), 2026-10-27. Command: python -I results/2026-10-27-final-packaging/residue_scan.py . ' + SUB + '\n')
    o.write(f'# hits: {len(hits)}\n')
    for k, w, l in hits: o.write(f'{k}\t{w}\t{l}\n')
print(open(out, encoding='utf-8').read())
