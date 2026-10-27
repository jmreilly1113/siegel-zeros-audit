set -u
cd /mnt/c/Users/Work/dev/siegel/results/2026-10-27-final-packaging
pdfinfo draft-main.pdf | grep -E "Page size|Pages"
# words with their boxes; count words whose right edge (xMax) passes the page width 612 pt
pdftotext -bbox draft-main.pdf /tmp/bbox.html
python3 - <<'EOF'
import re
h = open('/tmp/bbox.html', encoding='utf-8').read()
pages = h.split('<page ')[1:]
tot = 0
for i, p in enumerate(pages, 1):
    W = float(re.search(r'width="([\d.]+)"', p).group(1))
    ws = [(float(a), float(b), w) for a, b, w in re.findall(r'<word xMin="([\d.]+)" yMin="[\d.]+" xMax="([\d.]+)" yMax="[\d.]+">([^<]*)</word>', p)]
    off = [w for a, b, w in ws if b > W]
    tot += len(off)
    if off: print(f'page {i}: {len(off)} words past the right page edge (width {W}): ' + ' | '.join(off[:6]))
print('total words past the page edge:', tot)
EOF
