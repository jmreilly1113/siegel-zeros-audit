set -u
# Step 4 (2026-10-27): rebuild paper/arxiv/ alone, in a fresh /tmp folder, with pdflatex only (main.bbl ships; no bibtex).
P=/mnt/c/Users/Work/dev/siegel/results/2026-10-27-final-packaging
B=/tmp/arxiv-build; rm -rf $B; mkdir -p $B; cp /mnt/c/Users/Work/dev/siegel/paper/arxiv/* $B/; cd $B
ls
for i in 1 2 3; do pdflatex -interaction=nonstopmode -halt-on-error main.tex > run$i.log 2>&1; echo "pass $i exit $?"; done
grep -E "^! |Warning: (Reference|Citation)|undefined|Missing character" main.log | sort | uniq -c | head -20
pdfinfo main.pdf | grep Pages
echo "overfull hboxes: $(grep -c '^Overfull .hbox' main.log)"
pdftotext -enc UTF-8 main.pdf main.txt
cp main.pdf $P/arxiv-main.pdf; cp main.log $P/arxiv-main.log; cp main.txt $P/arxiv-main.utf8.txt
if cmp -s main.txt $P/draft-main.utf8.txt; then echo "PDF text identical to the draft build"; else echo "PDF text differs from the draft build:"; diff $P/draft-main.utf8.txt main.txt | head -20; fi
sha256sum main.pdf $P/draft-main.pdf
