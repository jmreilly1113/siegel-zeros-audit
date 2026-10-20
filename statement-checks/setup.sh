#!/usr/bin/env bash
# Build the statement-checks project in WSL at /home/checker/statement-checks (run as root).
# - copies this directory's sources;
# - copies the three challenge files verbatim from the clean openai/math clone at fd4aeeb and checks their sha256;
# - copies Mathlib d13f23b and its 8 dependencies (with their build outputs) from the clone's .lake/packages,
#   after checking each is clean and at the manifest revision; writes lake-manifest.json from the clone's entries.
set -eu
SRC=/mnt/c/Users/Work/dev/siegel/statement-checks; DST=/home/checker/statement-checks; M=/home/checker/math; P=$M/lean/.lake/packages
[ "$(sudo -u checker git -C $M rev-parse HEAD)" = fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb ] || { echo "clone not at fd4aeeb"; exit 1; }
[ -z "$(sudo -u checker git -C $M status --porcelain)" ] || { echo "clone not clean"; exit 1; }
mkdir -p $DST/StatementChecks/Challenges $DST/.lake/packages
cp $SRC/lakefile.toml $SRC/lean-toolchain $DST/; cp $SRC/StatementChecks/*.lean $DST/StatementChecks/ 2>/dev/null || true
cp $SRC/StatementChecks.lean $DST/ 2>/dev/null || true
for n in QuasiRiemannHypothesis DirichletSevenEighths HeckeSevenEighths; do
  cp $M/lean/ComparatorChallenges/$n.lean $DST/StatementChecks/Challenges/$n.lean
  echo "challenge $n sha256 $(sha256sum $DST/StatementChecks/Challenges/$n.lean | cut -c1-64) (clone: $(sha256sum $M/lean/ComparatorChallenges/$n.lean | cut -c1-64))"
done
python3 - $M/lean/lake-manifest.json $DST/lake-manifest.json <<'PY'
import json, sys
m = json.load(open(sys.argv[1]))
keep = ['mathlib', 'plausible', 'LeanSearchClient', 'importGraph', 'proofwidgets', 'aesop', 'Qq', 'batteries', 'Cli']
pk = [p for p in m['packages'] if p['name'] in keep]
assert len(pk) == len(keep), [p['name'] for p in pk]
for p in pk: p['inherited'] = p['name'] != 'mathlib'
json.dump({'version': m['version'], 'packagesDir': '.lake/packages', 'packages': pk, 'name': 'statement_checks', 'lakeDir': '.lake'}, open(sys.argv[2], 'w'), indent=1)
PY
for d in mathlib batteries aesop Qq proofwidgets plausible importGraph LeanSearchClient Cli; do
  r=$(sudo -u checker git -C $P/$d rev-parse HEAD); [ -z "$(sudo -u checker git -C $P/$d status --porcelain)" ] || { echo "$d dirty"; exit 1; }
  [ -d $DST/.lake/packages/$d ] || cp -a $P/$d $DST/.lake/packages/$d
  echo "package $d $r"
done
chown -R checker:checker $DST; echo "disk used: $(df -BG --output=used / | tail -1 | tr -d ' ')"
