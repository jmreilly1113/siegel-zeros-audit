set -u
# Final build (2026-10-27), after the title block and the layout edits. Outputs to results/2026-10-27-final-packaging/final/.
P=/mnt/c/Users/Work/dev/siegel/results/2026-10-27-final-packaging/final; mkdir -p $P
B=/tmp/final-build; rm -rf $B; mkdir -p $B; cp /mnt/c/Users/Work/dev/siegel/paper/draft/*.tex /mnt/c/Users/Work/dev/siegel/paper/draft/refs.bib /mnt/c/Users/Work/dev/siegel/paper/draft/*.bst $B/; cd $B
pdflatex -interaction=nonstopmode -halt-on-error main.tex > run1.log 2>&1; echo "pass1 exit $?"
bibtex main > bibtex.log 2>&1; echo "bibtex exit $?"; grep -i "warning\|error" bibtex.log | head
pdflatex -interaction=nonstopmode -halt-on-error main.tex > run2.log 2>&1; pdflatex -interaction=nonstopmode -halt-on-error main.tex > run3.log 2>&1; echo "main exit $?"
grep -E "^! |Warning: (Reference|Citation)|undefined|Missing character" main.log | sort | uniq -c | head -20
pdfinfo main.pdf | grep Pages
echo "overfull hboxes: $(grep -c '^Overfull .hbox' main.log)"
grep -A1 "^Overfull .hbox" main.log | grep -v "^--" | paste - - | cut -c1-160
pdftotext -enc UTF-8 main.pdf main.utf8.txt
pdftotext -bbox main.pdf bbox.html
python3 - <<'EOF'
import re
h = open('bbox.html', encoding='utf-8').read()
tot = 0
for i, p in enumerate(h.split('<page ')[1:], 1):
    W = float(re.search(r'width="([\d.]+)"', p).group(1))
    off = [w for a, b, w in re.findall(r'<word xMin="([\d.]+)" yMin="[\d.]+" xMax="([\d.]+)" yMax="[\d.]+">([^<]*)</word>', p) if float(b) > W]
    tot += len(off)
    if off: print(f'page {i}: ' + ' | '.join(off))
print('words past the right page edge:', tot)
EOF
cp main.pdf $P/draft-main.pdf; cp main.log $P/draft-main.log; cp main.bbl $P/draft-main.bbl; cp main.utf8.txt $P/draft-main.utf8.txt
sha256sum main.pdf
