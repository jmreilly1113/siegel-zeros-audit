"""Check the draft sections against the claims ledger (2026-10-27). Reads files only; changes nothing.

Usage: python -I paper/draft/check.py <repo root> [ledger file]   (default: results/2026-10-26-claims-ledger/ledger-v14.tsv; ids agree across v2-v14)

For each of sec2-sec7 and the appendix files:
 1. Quotes. A line "%% QUOTE <path> <a>-<b> [sha=<vN:Lxxx>]" must precede a Verbatim or paperquote block. The block must
    equal lines a..b of <path> (CRLF normalised to LF). "%% QUOTE-CONTAINED" requires each block line to occur inside lines a..b.
    With sha=..., the file's LF (or raw) sha256 must occur in that ledger row, or the path must occur in the row's source.
    A paperquote line that starts with \\expandafter\\def\\csname paperref@ is a local \\ref mapping, not quoted text; it is
    listed in the report.
 2. Citations. Every other line with text outside comments must carry a comment naming ledger rows (vN:Lxxx). The rows
    must exist and have status FOUND. A comment containing MISSING-ROW is reported as a missing row.
 3. Values. From the text of each cited line (outside comments), every number, hex string of 7+ characters and identifier
    (a token with '_', '.', '/' or ':' inside, or an upper-case token with '_') must occur in the cited rows' fields.
    Phrases naming paper results or draft parts ("Theorem 1", "Lemma 3", "Section~\\ref", ...) are not values.
    Quote locators are not ledger values: "path:a-b", and a or b next to "a-b", pass only if the same file has a
    "%% QUOTE" with exactly that range (whose text step 1 checks). "openai/math" (the repository name) passes.
    A line with no fact (a table header, a list lead-in, the organization paragraph) carries "% no-fact: <reason>" and may contain
    no digits outside named references; such lines are counted in the report.
Prints every finding; exit 1 if there is any.
"""
import csv, hashlib, os, re, sys

root = sys.argv[1]
ledger = sys.argv[2] if len(sys.argv) > 2 else 'results/2026-10-26-claims-ledger/ledger-v14.tsv'
D = os.path.join(root, 'paper', 'draft')
FILES = ['abstract.tex', 'sec1-intro.tex', 'sec2-background.tex', 'sec3-faithfulness.tex', 'sec4-gap.tex', 'sec5-lemma3.tex', 'sec6-reroute.tex', 'sec7-corpus.tex', 'sec8-threats.tex', 'sec9-artifacts.tex', 'sec10-ai.tex', 'appendix-78-listings.tex', 'appendix-reasoning.tex']
rows = {r['id']: r for r in csv.DictReader(open(os.path.join(root, ledger), encoding='utf-8'), delimiter='\t')}
FIELDS = ['claim', 'value', 'unit', 'source', 'label', 'openai_math_commit', 'toolchain', 'sandbox', 'note', 'read_by', 'read_note']
text_of = {i: ' '.join(r.get(k, '') for k in FIELDS) for i, r in rows.items()}
find = []
nofact = []


def rep(kind, f, n, msg): find.append(f'{kind}\t{f}:{n}\t{msg}')


def src_lines(p):
    b = open(os.path.join(root, p), 'rb').read()
    lf = b.replace(b'\r\n', b'\n')
    return lf.decode('utf-8').split('\n'), {hashlib.sha256(b).hexdigest(), hashlib.sha256(lf).hexdigest()}


def split_comment(line):
    m = re.search(r'(?<!\\)%', line)
    return (line, '') if not m else (line[:m.start()], line[m.start() + 1:])


STRUCT = re.compile(r'^\s*\\(section|subsection|begin|end|label|paragraph\{[^}]*\}$|small|footnotesize|scriptsize|toprule|midrule|bottomrule|centering|footnote\{?\s*$)')
NAMED = re.compile(r'\b(Theorem|Lemma|Lemmas|Corollary|Section|Table|Listing|Remark)s?(~|\s)(\\ref\{[^}]*\}|\d+(?:\.\d+)?(\s+and\s+\d+(?:\.\d+)?)?)')
LATEX = re.compile(r'\\(texttt|emph|textbackslash|ldots|operatorname|footnote|multicolumn|scriptsize|ref|label|caption|cite)\b|\\[a-zA-Z]+\*?')


def tokens(t):
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


PROJECT = {'openai/math'}  # the repository's name, used as a proper noun; not a ledger value


def found(tok, ids, line='', quotes=()):
    if tok in PROJECT: return True
    # quote locators: "path:a-b", or a or b of "a-b", where a "%% QUOTE" in the same file has exactly that range (checked in step 1)
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


for f in FILES:
    L = open(os.path.join(D, f), encoding='utf-8').read().split('\n')
    quotes = [(m.group(1), int(m.group(2)), int(m.group(3))) for m in (re.match(r'^%% QUOTE(?:-CONTAINED)? (\S+) (\d+)-(\d+)', x) for x in L) if m]
    i = 0
    while i < len(L):
        line = L[i]; n = i + 1
        m = re.match(r'^%% (QUOTE|QUOTE-CONTAINED) (\S+) (\d+)-(\d+)(?: sha=(v\d+:L\d{3}))?\s*$', line)
        if m:
            mode, p, a, b, sha = m.group(1), m.group(2), int(m.group(3)), int(m.group(4)), m.group(5)
            j = i + 1
            assert re.match(r'\\begin\{(Verbatim|paperquote)\}', L[j]), (f, n)
            env = re.match(r'\\begin\{(Verbatim|paperquote)\}', L[j]).group(1)
            k = j + 1; body = []
            while not L[k].startswith('\\end{' + env + '}'): body.append(L[k]); k += 1
            local = [x for x in body if x.startswith('\\expandafter\\def\\csname paperref@')]
            for x in local: rep('NOTE', f, n, f'local \\ref mapping line inside the quote, not quoted text: {x[:70]}')
            body = [x for x in body if x not in local]
            try:
                lines, shas = src_lines(p)
            except OSError as e:
                rep('QUOTE-ERROR', f, n, f'cannot read {p}: {e}'); i = k + 1; continue
            src = lines[a - 1:b]
            if mode == 'QUOTE':
                if body != src:
                    diff = [(x, y) for x, y in zip(body, src) if x != y][:2]
                    rep('QUOTE-MISMATCH', f, n, f'{p}:{a}-{b}: block has {len(body)} lines, source {len(src)}; first differences {diff}')
            else:
                for x in body:
                    if not any(x.strip() in y for y in src): rep('QUOTE-MISMATCH', f, n, f'{p}:{a}-{b}: line not contained: {x[:60]}')
            if sha:
                rid = sha.split(':')[1]; tx = text_of.get(rid)
                if tx is None: rep('CITE-UNKNOWN', f, n, f'{sha} not in ledger')
                elif not (any(h in tx for h in shas) or p.split('/', 1)[-1] in rows[rid]['source'] or p in rows[rid]['source']):
                    rep('QUOTE-SHA', f, n, f'{p}: none of its sha256 {sorted(h[:16] for h in shas)} and not its path occurs in {sha}')
            i = k + 1; continue
        text, com = split_comment(line)
        if line.lstrip().startswith('%'): i += 1; continue
        t = text.strip()
        if not t or t in ('}', '\\\\') or STRUCT.match(t) or t.startswith('\\begin{tabularx}') or t.startswith('\\input'):
            i += 1; continue
        ids = re.findall(r'v\d+:(L\d{3})', com)
        if 'MISSING-ROW' in com: rep('MISSING-ROW', f, n, com.split('MISSING-ROW', 1)[1].strip(' :'))
        if com.strip().startswith('no-fact:'):
            if re.search(r'\d', NAMED.sub(' ', text)): rep('NO-FACT-WITH-DIGITS', f, n, t[:100])
            nofact.append(com.strip()); i += 1; continue
        if 'TAG-PENDING' in com:
            rep('TAG-PENDING', f, n, 'repository tag not yet set: ' + t[:80]); i += 1; continue
        if not ids:
            rep('UNCITED', f, n, t[:100]); i += 1; continue
        for r in ids:
            if r not in rows: rep('CITE-UNKNOWN', f, n, r)
            elif rows[r]['status'] != 'FOUND': rep('CITE-SUPERSEDED', f, n, f"{r}: {rows[r]['status']}")
        for tok in sorted(tokens(text)):
            if not found(tok, ids, text, quotes): rep('VALUE-NOT-IN-CITED-ROWS', f, n, f'{tok!r} (cited: {" ".join(ids)})')
        i += 1

# 4. Bibliography: every \cite key is in refs.bib, every refs.bib entry is cited, and each "UNCONFIRMED: <fields>" note is a finding.
bib = open(os.path.join(D, 'refs.bib'), encoding='utf-8').read()
entries = {}
for m in re.finditer(r'^@\w+\{([^,\s]+),(.*?)^\}', bib, re.S | re.M):
    entries[m.group(1)] = m.group(2)
cited = {}
for f in FILES:
    for n, line in enumerate(open(os.path.join(D, f), encoding='utf-8').read().split('\n'), 1):
        text, _ = split_comment(line)
        for m in re.finditer(r'\\cite(?:\[[^\]]*\])?\{([^}]*)\}', text):
            for k in m.group(1).split(','):
                cited.setdefault(k.strip(), []).append(f'{f}:{n}')
for k, where in sorted(cited.items()):
    if k not in entries: rep('CITE-NOT-IN-BIB', where[0].split(':')[0], where[0].split(':')[1], k)
for k in entries:
    if k not in cited: rep('BIB-UNCITED', 'refs.bib', 0, k)
    m = re.search(r'UNCONFIRMED:\s*([^}]*)', entries[k])
    if m: rep('BIB-UNCONFIRMED', 'refs.bib', 0, f'{k}: {m.group(1).strip()}')

print(f'# check.py: {len(FILES)} files against {ledger} ({len(rows)} rows); refs.bib {len(entries)} entries, {len(cited)} keys cited')
kinds = {}
for x in find: kinds[x.split('\t')[0]] = kinds.get(x.split('\t')[0], 0) + 1
print('# findings by kind:', kinds if kinds else 'none')
import collections as _c
print('# no-fact lines:', dict(_c.Counter(nofact)))
for x in find: print(x)
sys.exit(1 if any(not x.startswith('NOTE') for x in find) else 0)
