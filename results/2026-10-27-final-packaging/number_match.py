"""Step 3 of the final packaging (2026-10-27): match every number, hash prefix and identifier in the PDF text to the ledger rows
that its source line cites. Reads files only; changes nothing. Writes number-match-2.txt (refuses to overwrite; number-match.txt is
the first run of an earlier version of this script, with coarser classes).

Usage: python -I results/2026-10-27-final-packaging/number_match.py <repo root>
The tokenizer and the row matcher are copied from paper/draft/check.py (split_comment, NAMED, LATEX, tokens, found), unchanged.
PDF text: results/2026-10-27-final-packaging/draft-main.utf8.txt (pdftotext -enc UTF-8 of draft-main.pdf). It is split at the
"References" heading and the first appendix heading; the bibliography part is matched against refs.bib and the .bbl, the rest
against the draft sources. Each body token is classed as:
  CITED       some source line with ledger cites has it among its tokens, and found() locates it in those rows (rows listed);
  QUOTE       it occurs in a %% QUOTE block (check.py step 1 compares those blocks with their source lines);
  NAMED       the number of a named part ("Theorem 1", "Section 3", ...), which check.py does not treat as a value;
  MAIN        it occurs in main.tex (title, author, date), which carries no ledger cites;
  CITE-LABEL  a bibliography label inside [...];
  LAYOUT      a page number, a section number or a table/listing counter produced by LaTeX;
  DEHYPH      equal, after removing hyphens, to a word of a cited source line all of whose tokens found() locates
              (pdftotext drops a hyphen at a line end when it joins the word);
  BROKEN      at a PDF line edge and a part of such a source word (a word split across lines, or two table cells run together);
  MISMATCH    none of the above.
"""
import csv, os, re, sys

root = sys.argv[1]
D = os.path.join(root, 'paper', 'draft'); O = os.path.join(root, 'results', '2026-10-27-final-packaging')
SUB = sys.argv[2] if len(sys.argv) > 2 else ''  # optional folder of a later build, e.g. final; output there as number-match.txt
O = os.path.join(O, SUB) if SUB else O
ledger = 'results/2026-10-26-claims-ledger/ledger-v17.tsv' if len(sys.argv) > 2 else 'results/2026-10-26-claims-ledger/ledger-v16.tsv'
FILES = ['abstract.tex', 'sec1-intro.tex', 'sec2-background.tex', 'sec3-faithfulness.tex', 'sec4-gap.tex', 'sec5-lemma3.tex', 'sec6-reroute.tex', 'sec7-corpus.tex', 'sec8-threats.tex', 'sec9-artifacts.tex', 'sec10-ai.tex', 'appendix-78-listings.tex', 'appendix-reasoning.tex']
rows = {r['id']: r for r in csv.DictReader(open(os.path.join(root, ledger), encoding='utf-8'), delimiter='\t')}
FIELDS = ['claim', 'value', 'unit', 'source', 'label', 'openai_math_commit', 'toolchain', 'sandbox', 'note', 'read_by', 'read_note']
text_of = {i: ' '.join(r.get(k, '') for k in FIELDS) for i, r in rows.items()}

# ---- copied from paper/draft/check.py ----
def split_comment(line):
    m = re.search(r'(?<!\\)%', line)
    return (line, '') if not m else (line[:m.start()], line[m.start() + 1:])
NAMED = re.compile(r'\b(Theorem|Lemma|Lemmas|Corollary|Section|Table|Listing|Remark)s?(~|\s)(\\ref\{[^}]*\}|\d+(?:\.\d+)?(\s+and\s+\d+(?:\.\d+)?)?)')
LATEX = re.compile(r'\\(texttt|emph|textbackslash|ldots|operatorname|footnote|multicolumn|scriptsize|ref|label|caption|cite)\b|\\[a-zA-Z]+\*?')
def tokens(t):
    t = re.sub(r'\\allowbreak\s*', '', t).replace('\\-', '')  # break points (main.tex layout) produce no text
    t = NAMED.sub(' ', t)
    t = re.sub(r'\\(ref|label|cite)\{[^}]*\}', ' ', t)
    t = re.sub(r'\\multicolumn\{\d+\}\{[^}]*\}', ' ', t)
    t = re.sub(r'\\begin\{[^}]*\}(\{[^}]*\})*', ' ', t)
    t = re.sub(r'>\{\\raggedright\\arraybackslash\}[pX]\{?[^}]*\}?', ' ', t)
    t = t.replace('\\_', '_').replace('\\#', '#').replace('\\%', '%').replace('\\{', '{').replace('\\}', '}').replace('{}', '')
    t = LATEX.sub(' ', t).replace('~', ' ')
    out = set()
    for m in re.finditer(r'[A-Za-z0-9_.:/#\-\[\]!⁻¹₁₂]+', t):
        w = m.group(0).strip('.:,;-()[]')
        if not w: continue
        if re.fullmatch(r'[0-9a-f]{7,}', w) and re.search(r'\d', w) and re.search(r'[a-f]', w): out.add(w); continue
        if re.fullmatch(r'\d{4}-\d{2}-\d{2}(T[\d:]+Z)?', w) or re.fullmatch(r'\d{1,2}:\d{2}(:\d{2})?', w): out.add(w); continue
        if re.search(r'[_./:]', w[1:-1] if len(w) > 2 else '') or re.fullmatch(r'[A-Z][A-Z0-9]*_[A-Z0-9_]+', w):
            out.add(w); continue
        for n in re.findall(r'\d+(?:\.\d+)?', w): out.add(n)
    return out
PROJECT = {'openai/math'}
def found(tok, ids, line='', quotes=()):
    if tok in PROJECT: return True
    for (p, a, b) in quotes:
        rng = f'{a}-{b}'
        if tok.endswith(':' + rng) and p.endswith(tok.rsplit(':', 1)[0].split('/')[-1]): return True
        if tok in (str(a), str(b)) and rng in line: return True
    for i in ids:
        tx = text_of.get(i, '')
        if re.fullmatch(r'\d+(\.\d+)?', tok):
            if re.search(r'(?<![\d.])' + re.escape(tok) + r'(?![\d])', tx): return True
        elif tok in tx: return True
    return False
# ---- end of copy ----

def detex(t):
    # tokens()'s preprocessing, without the split into tokens
    t = re.sub(r'\\allowbreak\s*', '', t).replace('\\-', '')
    t = NAMED.sub(' ', t)
    t = re.sub(r'\\(ref|label|cite)\{[^}]*\}', ' ', t)
    t = re.sub(r'\\multicolumn\{\d+\}\{[^}]*\}', ' ', t)
    t = re.sub(r'\\begin\{[^}]*\}(\{[^}]*\})*', ' ', t)
    t = re.sub(r'>\{\\raggedright\\arraybackslash\}[pX]\{?[^}]*\}?', ' ', t)
    t = t.replace('\\_', '_').replace('\\#', '#').replace('\\%', '%').replace('\\{', '{').replace('\\}', '}').replace('{}', '')
    return LATEX.sub(' ', t).replace('~', ' ')
def words(t): return [w for w in (m.group(0).strip('.:,;-()[]') for m in re.finditer(r'[A-Za-z0-9_.:/#\-\[\]!⁻¹₁₂]+', detex(t))) if w]
def norm(w): return re.sub(r'[-\u2013\u2014\s]', '', w)

cited = {}      # token -> [(file:line, cited ids)] where found() locates it in the cited rows
cited_raw = {}  # norm(word of a cited line whose tokens found() all locates) -> [(file:line, cited ids)]
quote_tok, quote_raw, named_nums = set(), set(), set()
for f in FILES:
    L = open(os.path.join(D, f), encoding='utf-8').read().split('\n')
    quotes = [(m.group(1), int(m.group(2)), int(m.group(3))) for m in (re.match(r'^%% QUOTE(?:-CONTAINED)? (\S+) (\d+)-(\d+)', x) for x in L) if m]
    inq = None
    for n, line in enumerate(L, 1):
        if inq:
            if line.startswith('\\end{' + inq + '}'): inq = None
            else: quote_tok |= tokens(line); quote_raw |= {norm(w) for w in words(line)}
            continue
        if re.match(r'^%% QUOTE', line): inq = re.match(r'\\begin\{(Verbatim|paperquote)\}', L[n]).group(1); continue
        text, com = split_comment(line)
        for m in NAMED.finditer(text): named_nums |= set(re.findall(r'\d+(?:\.\d+)?', m.group(0)))
        ids = re.findall(r'v\d+:(L\d{3})', com)
        if not ids: continue
        ref = (f'{f}:{n}', ' '.join(f'v16:{i}' for i in ids))
        for tok in tokens(text):
            if found(tok, ids, text, quotes): cited.setdefault(tok, []).append(ref)
        for w in words(text):
            if all(found(t, ids, text, quotes) for t in tokens(w)): cited_raw.setdefault(norm(w), []).append(ref)
main_tok = tokens(' '.join(split_comment(x)[0] for x in open(os.path.join(D, 'main.tex'), encoding='utf-8').read().split('\n')))
bib = open(os.path.join(D, 'refs.bib'), encoding='utf-8').read()
bib_text = ' '.join(split_comment(x)[0] for x in bib.split('\n')).replace('\\_', '_').replace('\\#', '#').replace('{', '').replace('}', '')
bbl = open(os.path.join(O, 'draft-main.bbl'), encoding='utf-8').read()
bib_norm = norm(bib_text) + ' ' + norm(bbl.replace('\\_', '_'))
NBIB = len(re.findall(r'^@\w+\{', bib, re.M))

pdf = open(os.path.join(O, 'draft-main.utf8.txt'), encoding='utf-8').read()
pages = pdf.split('\f')
body_lines, bib_lines, in_bib = [], [], False
for pg, page in enumerate(pages, 1):
    for ln in page.split('\n'):
        if re.fullmatch(r'\s*References\s*', ln): in_bib = True
        if re.fullmatch(r'\s*(A\s+)?The three 7/8 challenge statements\s*', ln): in_bib = False  # first appendix heading
        (bib_lines if in_bib else body_lines).append((pg, ln))

def edge(tok, s):
    w = s.split()
    return bool(w) and (tok in w[0] or tok in w[-1])
def layout(tok, s):
    return (tok == s and re.fullmatch(r'\d+(\.\d+)*', s) is not None) \
        or (re.match(r'^(\d+(\.\d+)*)\s+[A-Z]', s) is not None and s.split()[0] == tok) \
        or re.match(r'^(Table|Listing|Figure)\s+' + re.escape(tok) + r'[:.]', s) is not None
def cite_label(tok, s):
    if not re.fullmatch(r'\d{1,2}', tok) or not 1 <= int(tok) <= NBIB: return False
    return any(tok in [x.strip() for x in m.group(1).split(',')] for m in re.finditer(r'\[([\d,\s]+)\]', s))
def refs(lst): return '; '.join(f'{w} [{ids}]' for w, ids in lst[:2])

def classify(tok, s):
    if tok in cited: return 'CITED', refs(cited[tok])
    if tok in quote_tok: return 'QUOTE', ''
    if tok in named_nums and re.search(r'(Theorem|Lemma|Corollary|Section|Table|Listing|Remark)s?\s+(\d+(?:\.\d+)?\s+and\s+)?' + re.escape(tok) + r'\b', s): return 'NAMED', ''
    if tok in main_tok: return 'MAIN', ''
    if cite_label(tok, s): return 'CITE-LABEL', ''
    if layout(tok, s): return 'LAYOUT', ''
    k = norm(tok)
    if k in cited_raw: return 'DEHYPH', 'source word at ' + refs(cited_raw[k])
    if k in quote_raw: return 'DEHYPH', 'quoted word'
    if edge(tok, s) and len(k) >= 4:
        hit = [r for c, r in cited_raw.items() if k in c]
        if hit: return 'BROKEN', 'part of a source word at ' + refs(hit[0])
        if any(k in c for c in quote_raw): return 'BROKEN', 'part of a quoted word'
    return 'MISMATCH', ''

out_rows, counts, seen = [], {}, set()
for pg, ln in body_lines:
    s = ln.strip()
    for tok in sorted(tokens(ln)):
        cls, where = classify(tok, s)
        if (cls, tok, pg) in seen: continue
        seen.add((cls, tok, pg)); counts[cls] = counts.get(cls, 0) + 1
        out_rows.append((cls, pg, tok, where, s[:120]))
bib_rows, bc = [], {}
for pg, ln in bib_lines:
    s = ln.strip()
    for tok in sorted(tokens(ln)):
        if tok in bib_text or tok in bbl: cls = 'BIB-OK'
        elif re.fullmatch(r'\d{1,2}', tok) and s.startswith('[' + tok + ']'): cls = 'BIB-LABEL'
        elif layout(tok, s): cls = 'LAYOUT'
        elif norm(tok) in bib_norm: cls = 'BIB-DEHYPH'
        else: cls = 'BIB-MISMATCH'
        bc[cls] = bc.get(cls, 0) + 1
        bib_rows.append((cls, pg, tok, '', s[:120]))

p = os.path.join(O, 'number-match.txt' if SUB else 'number-match-2.txt')
with open(p, 'x', encoding='utf-8', newline='\n') as o:
    o.write('# Number matching (step 3), 2026-10-27. Command: python -I results/2026-10-27-final-packaging/number_match.py . ' + SUB + '\n')
    o.write(f'# ledger {ledger} ({len(rows)} rows); PDF text draft-main.utf8.txt ({len(pages)} form-feed pages); refs.bib {NBIB} entries\n')
    o.write(f'# body tokens by class (one per class, token, page): {counts}\n')
    o.write(f'# bibliography tokens: {bc}\n')
    o.write('# class\tpage\ttoken\twhere (source line [cited rows]) or note\tPDF line\n')
    for c in ['MISMATCH', 'BROKEN', 'DEHYPH', 'LAYOUT', 'CITE-LABEL', 'MAIN', 'NAMED', 'QUOTE', 'CITED']:
        for r in out_rows:
            if r[0] == c: o.write('\t'.join(str(x) for x in r) + '\n')
    for c in ['BIB-MISMATCH', 'BIB-DEHYPH', 'LAYOUT', 'BIB-LABEL', 'BIB-OK']:
        for r in bib_rows:
            if r[0] == c: o.write('\t'.join(str(x) for x in r) + '\n')
print(f'wrote {p}')
