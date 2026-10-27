set -u
# Build the paper PDF from the git archive of tag paper-v1 alone (2026-10-27); compare with final/draft-main.pdf.
Z=/mnt/d/siegel-audit-offload/zenodo-paper-v1
B=/tmp/tag-build; rm -rf $B; mkdir -p $B; cd $B
python3 -c "import zipfile; zipfile.ZipFile('$Z/siegel-zeros-audit-paper-v1.zip').extractall('.')"
cd siegel-zeros-audit-paper-v1/paper/draft
pdflatex -interaction=nonstopmode -halt-on-error main.tex > r1.log 2>&1; echo "pass1 $?"; bibtex main > b.log 2>&1; echo "bibtex $?"
pdflatex -interaction=nonstopmode -halt-on-error main.tex > r2.log 2>&1; pdflatex -interaction=nonstopmode -halt-on-error main.tex > r3.log 2>&1; echo "pass3 $?"
pdfinfo main.pdf | grep Pages; echo "overfull hboxes: $(grep -c '^Overfull .hbox' main.log)"
pdftotext -enc UTF-8 main.pdf main.utf8.txt
F=/mnt/c/Users/Work/dev/siegel/results/2026-10-27-final-packaging/final
if cmp -s main.utf8.txt $F/draft-main.utf8.txt; then echo "PDF text identical to final/draft-main.pdf"; else echo "PDF text DIFFERS"; diff $F/draft-main.utf8.txt main.utf8.txt | head; fi
cp main.pdf $Z/siegel-zeros-audit-paper-v1.pdf
cd $Z; sha256sum siegel-zeros-audit-paper-v1.pdf siegel-zeros-audit-paper-v1.zip; ls -l
