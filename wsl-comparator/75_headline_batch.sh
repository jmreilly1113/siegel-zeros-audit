#!/usr/bin/env bash
# Headline batch at openai/math fd4aeeb, on C: (Joe, 2026-10-11). Run as root, detached (setsid nohup).
# Run policy: per config, prebuild with LEAN_NUM_THREADS=4 inside the network-blocking wrapper (75_sbx.sh), then one
# official comparator run with a copy of the shipped config that differs only in enable_nanoda: true (67_corpus_run.sh).
# The shipped config itself is run only (i) for configs in the seeded random sample of 10 (drawn once over all 189
# yaml-referenced configs; see sample.txt), and (ii) for every config whose nanoda run is not ACCEPT_BOTH.
# Then the Lean-level queries (lean-checks/corpus-queries/) for HarmonicGrowth and NavierStokesVelocity (query only).
# Nothing is fixed or rerouted; failures are recorded and classified (75_classify.py).
set -u
W=/mnt/c/Users/Work/dev/siegel/wsl-comparator
Q=/mnt/c/Users/Work/dev/siegel/lean-checks/corpus-queries
OUT=/mnt/c/Users/Work/dev/siegel/results/2026-10-11-corpus-headline
L=/home/checker/math/lean; C=/home/checker/corpus/configs
DISK_CAP=${DISK_CAP:-60}
mkdir -p $OUT
rm -f /home/checker/corpus/GUARD_STOPPED
nohup bash $W/69_corpus_guard.sh $DISK_CAP 1500 2 >/dev/null 2>&1 &
GD=$!
{
echo "== headline batch start $(date '+%F %T')"
echo "clone HEAD: $(sudo -u checker git -C /home/checker/math rev-parse HEAD); status: [$(sudo -u checker git -C /home/checker/math status --short | tr '\n' ' ')]"
echo "guard: 69_corpus_guard.sh $DISK_CAP 1500 2 (WSL disk use cap ${DISK_CAP} GiB, MemAvailable floor 1500 MB, drop_caches every 60 s)"
echo "disk used: $(df -BG --output=used / | tail -1 | tr -d ' ')"
} >> $OUT/run.log
# configs (nanoda copies) and the seeded sample
python3 -I - "$L" "$C" "$OUT" <<'EOF' >> $OUT/run.log
import json, os, random, sys, yaml
L, C, OUT = sys.argv[1:4]
head = ('DirichletSevenEighths HeckeSevenEighths OptimalMaxCut UniqueGamesTheorem VertexCover MatrixFields '
        'MatrixMultiplication MahlerConjecture SymmetricMahlerEquality SymmetricPolar ExactFourier UniformFourier '
        'EuclideanFiveColor PlaneColoring HarmonicGrowth').split()
y = yaml.safe_load(open(os.path.join(L, 'formalization.yaml'), encoding='utf-8'))
ref = sorted({e['comparator_config'] for e in y['status']['main_results']})
SEED = 20261011
sample = sorted(random.Random(SEED).sample(ref, 10))
with open(os.path.join(OUT, 'sample.txt'), 'w') as f:
    f.write(f'# Shipped-config sample: random.Random({SEED}).sample(sorted(yaml-referenced configs), 10), Python {sys.version.split()[0]}\n')
    f.write(f'# population: {len(ref)} configs referenced by formalization.yaml at fd4aeeb\n')
    for s in sample:
        f.write(f'{s}\t{"headline" if s.split("/")[-1][:-5] in head else ("pilot" if s.split("/")[-1][:-5] in ("SiegelZeros", "QuasiRiemannHypothesis") else "remainder")}\n')
with open(os.path.join(OUT, 'plan.tsv'), 'w') as f:
    f.write('config\tprebuild_targets\tin_sample\n')
    for n in head:
        c = json.load(open(os.path.join(L, 'ComparatorChallenges', n + '.json'), encoding='utf-8'))
        c2 = dict(c); c2['enable_nanoda'] = True
        json.dump(c2, open(os.path.join(C, n + '-nanoda.json'), 'w'), indent=2)
        tg = [c['solution_module'], c['challenge_module']] + c.get('solution_imports', [])
        f.write(f'{n}\t{" ".join(tg)}\t{"ComparatorChallenges/" + n + ".json" in sample}\n')
print(f'sample (seed {SEED}): ' + ', '.join(s.split('/')[-1][:-5] for s in sample))
EOF
chown checker:checker $C/*-nanoda.json
stopped() { [ -f /home/checker/corpus/GUARD_STOPPED ]; }
prebuild() { # prebuild <name> <targets> <timeout>
  { echo "== prebuild $1: lake build $2 with LEAN_NUM_THREADS=4  $(date '+%F %T')"; T0=$(date +%s)
    bash $W/75_sbx.sh $3 4 "lake build $2" </dev/null
    echo "PREBUILD_SECONDS: $(( $(date +%s) - T0 ))"; echo "disk used: $(df -BG --output=used / | tail -1 | tr -d ' ')"
  } 2>&1 | cat > $OUT/$1.prebuild.log
}
while IFS=$'\t' read -r N TG INS <&3; do
  stopped && break
  [ -f $OUT/$N.done ] && continue
  for f in $OUT/$N.prebuild.log $OUT/$N-nanoda.log $OUT/$N-shipped.log; do  # partial logs of a stopped run are kept, not overwritten
    [ -f $f ] && mv $f ${f%.log}.stopped-$(date +%Y%m%d%H%M%S).log
  done
  echo "$(date '+%F %T') $N: prebuild" >> $OUT/run.log
  prebuild $N "$TG" 14400
  stopped && break
  if grep -q 'SANDBOX EXIT CODE: 12[4-9]\|SANDBOX EXIT CODE: 137' $OUT/$N.prebuild.log; then
    echo "$(date '+%F %T') $N: prebuild timed out; comparator runs skipped" >> $OUT/run.log; touch $OUT/$N.done; continue
  fi
  echo "$(date '+%F %T') $N: nanoda run" >> $OUT/run.log
  bash $W/67_corpus_run.sh $N $C/$N-nanoda.json 7200 $OUT/$N-nanoda.log </dev/null
  stopped && break
  ok=no; grep -q 'nanoda kernel accepts the solution' $OUT/$N-nanoda.log && grep -q 'Lean default kernel accepts the solution' $OUT/$N-nanoda.log \
    && grep -q 'Your solution is okay!' $OUT/$N-nanoda.log && grep -q 'COMPARATOR EXIT CODE: 0' $OUT/$N-nanoda.log && ok=yes
  if [ $ok = no ] || [ "$INS" = True ]; then
    echo "$(date '+%F %T') $N: shipped-config run (nanoda ACCEPT_BOTH: $ok; in sample: $INS)" >> $OUT/run.log
    bash $W/67_corpus_run.sh $N $L/ComparatorChallenges/$N.json 7200 $OUT/$N-shipped.log </dev/null
    stopped && break
  fi
  touch $OUT/$N.done
done 3< <(tail -n +2 $OUT/plan.tsv)
# sampled configs outside the headline batch whose closure is already built (pilot): shipped run now
if ! stopped; then
  for s in $(awk -F'\t' '$2=="pilot" {print $1}' $OUT/sample.txt); do
    N=$(basename $s .json); echo "$(date '+%F %T') $N (pilot, in sample): shipped-config run" >> $OUT/run.log
    bash $W/67_corpus_run.sh $N $L/$s 7200 $OUT/$N-shipped.log </dev/null; stopped && break
  done
fi
# Lean-level queries (query only; NavierStokesVelocity is not yaml-referenced and gets no comparator run)
if ! stopped; then
  echo "$(date '+%F %T') queries: build NavierStokesVelocity solution and challenge (no replay)" >> $OUT/run.log
  grep -q "SANDBOX EXIT CODE: 0" $OUT/NavierStokesVelocity-query.prebuild.log 2>/dev/null || prebuild NavierStokesVelocity-query "OAI.MathematicalPhysics.NavierStokes.VelocityDetection.Main ComparatorChallenges.NavierStokesVelocity" 14400
  for q in HarmonicGrowthChallenge HarmonicGrowthSolution NavierStokesChallenge NavierStokesSolution; do
    stopped && break
    grep -q 'SANDBOX EXIT CODE: 0' $OUT/query-$q.log 2>/dev/null && continue
    [ -f $OUT/query-$q.log ] && mv $OUT/query-$q.log $OUT/query-$q.stopped-$(date +%Y%m%d%H%M%S).log
    { echo "== query $q  $(date '+%F %T')"; echo "file: lean-checks/corpus-queries/$q.lean sha256 $(sha256sum $Q/$q.lean | cut -c1-64)"
      bash $W/75_sbx.sh 3600 4 "lake env lean $Q/$q.lean" </dev/null; } 2>&1 | cat > $OUT/query-$q.log
  done
fi
kill $GD 2>/dev/null
echo "disk used at end: $(df -BG --output=used / | tail -1 | tr -d ' '); clone status: [$(sudo -u checker git -C /home/checker/math status --short | tr '\n' ' ')]" >> $OUT/run.log
if stopped; then echo "GUARD STOPPED $(date '+%F %T')" > $OUT/GUARD_STOPPED.txt
else python3 -I $W/75_classify.py $OUT > $OUT/outcomes.tsv 2>> $OUT/run.log; echo "HEADLINE DONE $(date '+%F %T')" > $OUT/DONE.txt; fi
sync
