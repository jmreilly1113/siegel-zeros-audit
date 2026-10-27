"""Check (2026-10-27) that the Zenodo metadata draft carries no personal contact details. Writes final/contact-check.txt (refuses to overwrite).

Usage: python -I results/2026-10-27-final-packaging/contact_check.py <repo root>
Checks the description, and separately every metadata field, for: an email address or '@', 'mailto', a phone-number pattern,
'ORCID' or an ORCID iD pattern, a street-address word, the affiliation 'Northeastern', and 'Joe'/'Joseph'/'Reilly' (the creator
field is the one place the name is expected).
"""
import json, os, re, sys
root = sys.argv[1]
d = json.load(open(os.path.join(root, 'docs', 'zenodo-paper-v1-metadata.json'), encoding='utf-8'))['metadata']
PATS = [('email or @', r'@|[\w.+-]+\s*\[?at\]?\s*[\w-]+\.(edu|com|org)'), ('mailto', r'(?i)mailto'), ('phone', r'\+?\d[\d\s().-]{8,}\d'),
        ('ORCID', r'(?i)orcid|\b\d{4}-\d{4}-\d{4}-\d{3}[\dX]\b'), ('address', r'(?i)\b(street|avenue|boston|suite|zip code)\b'),
        ('affiliation', r'(?i)northeastern'), ('name', r'(?i)\b(joe|joseph|reilly)\b')]
def scan(label, text):
    return [f'{label}\t{k}\t{m.group(0)!r}' for k, p in PATS for m in re.finditer(p, text)]
hits = scan('description', d['description'])
other = {k: v for k, v in d.items() if k not in ('description',)}
hits += scan('other fields', json.dumps(other, ensure_ascii=False))
f = os.path.join(root, 'results', '2026-10-27-final-packaging', 'final', 'contact-check.txt')
with open(f, 'x', encoding='utf-8', newline='\n') as o:
    o.write('# Contact-detail check of docs/zenodo-paper-v1-metadata.json (2026-10-27). Command: python -I results/2026-10-27-final-packaging/contact_check.py .\n')
    o.write(f'# description hits: {sum(1 for h in hits if h.startswith("description"))}; other-field hits: {sum(1 for h in hits if h.startswith("other"))}\n')
    o.write(''.join(h + '\n' for h in hits))
print(open(f, encoding='utf-8').read())
