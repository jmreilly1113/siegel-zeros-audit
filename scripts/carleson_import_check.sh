#!/bin/bash
# Paper prep 4 follow-up, item 4: does any .lean file outside the carleson package import a Carleson module?
# Usage (in WSL, as checker): bash scripts/carleson_import_check.sh /home/checker/math   (read-only)
cd "$1/lean" || exit 1
echo "# clone HEAD $(git -c safe.directory='*' rev-parse HEAD); status lines $(git -c safe.directory='*' status --porcelain | wc -l)"
echo "# carleson in lakefile:"; grep -n 'carleson' lakefile.* | sed 's/^/#   /'
echo "# carleson in lake-manifest.json:"; grep -n -A6 '"url": "https://github.com/fpvandoorn/carleson.git"' lake-manifest.json | grep -E 'url|rev"|name' | sed 's/^/#   /'
# a module whose name starts with the Carleson root (Carleson or Carleson.X), anywhere on an import line
RE='^[[:space:]]*((public|private|meta)[[:space:]]+)*import([[:space:]]+[^[:space:]]+)*[[:space:]]+Carleson(\.[^[:space:]]+)?([[:space:]]|$)'
echo "files scanned: OAI $(find OAI -name '*.lean' | wc -l); ComparatorChallenges $(find ComparatorChallenges -name '*.lean' | wc -l); .lake/packages outside carleson $(find .lake/packages -name '*.lean' -not -path '.lake/packages/carleson/*' | wc -l); carleson $(find .lake/packages/carleson -name '*.lean' | wc -l)"
echo "import lines naming a Carleson module, outside .lake/packages/carleson (regex: $RE):"
grep -rnE --include='*.lean' "$RE" OAI ComparatorChallenges .lake/packages 2>/dev/null | grep -v '^.lake/packages/carleson/' > /tmp/carl-hits.txt
cat /tmp/carl-hits.txt
echo "count: $(wc -l < /tmp/carl-hits.txt)"
echo "import lines naming a Carleson module inside the carleson package (sanity check that the regex matches): $(grep -rnE --include='*.lean' "$RE" .lake/packages/carleson | wc -l)"
echo "for information: the gromov package vendors files under Gromov/Vendor/Carleson (a separate module namespace, Gromov.Vendor.Carleson.*):"
echo "  files: $(find .lake/packages/gromov -path '*Vendor/Carleson*' -name '*.lean' | wc -l); lines with an aesop 'unsafe' rule attribute: $(grep -rnE '@\[aesop.*unsafe' .lake/packages/gromov --include='*.lean' | grep -c Vendor/Carleson)"
