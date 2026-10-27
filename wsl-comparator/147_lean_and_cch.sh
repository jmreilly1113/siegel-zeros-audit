#!/usr/bin/env bash
# nanoda version matrix (2026-10-26, UNOFFICIAL), Joe's items 1-2, one step at a time under 69_corpus_guard.sh:
#  1. Lean's kernel on KMedianThreshold and Catalan: the shipped-config comparator run (enable_nanoda false, i.e. comparator's
#     own build + export + Lean replay + statement/axiom checks), through 67d (full deny list, 16G cap), 7200 s as the extended
#     replay's shipped runs. A cap/guard/timeout is recorded, not retried.
#  2. One retry of ContinuumCoulombHardness at LEAN_NUM_THREADS=2 (143d into exp-d); size check against nealmcb; then B3, B2, B1
#     (142d) and the shipped-config comparator run (67d). If the guard stops the build: logged, no retry.
set -u
W=/mnt/c/Users/Work/dev/siegel/wsl-comparator; O=/mnt/c/Users/Work/dev/siegel/results/2026-10-26-nanoda-version-matrix
log() { echo "$(date '+%F %T') $*" >> $O/run.log; }
guard() { pgrep -f 69_corpus_guard.sh >/dev/null || { setsid nohup bash $W/69_corpus_guard.sh 95 1500 20 >/dev/null 2>&1 < /dev/null & sleep 2; log "147: guard was not running; restarted"; }; }
verdict() { local f=$1; local v
  if grep -q 'oom_kill [1-9]' $f; then v="OOM at the 16G cap (resource)"
  elif grep -q 'COMPARATOR EXIT CODE: 124' $f; then v="TIMEOUT"
  elif grep -q 'Lean default kernel accepts the solution' $f && grep -q 'Your solution is okay!' $f && grep -q 'COMPARATOR EXIT CODE: 0' $f; then v="ACCEPT_LEAN"
  else v="OTHER ($(grep -E 'COMPARATOR EXIT CODE|rejected|error' $f | tail -2 | tr '\n' ' '))"; fi
  echo "$v; wall $(grep -oP '^DURATION_SECONDS: \K\d+' $f) s; max RSS $(grep -oP 'Maximum resident set size \(kbytes\): \K\d+' $f) kB; cgroup max_usage $(grep -oP 'max_usage_in_bytes \K\d+' $f | head -1) B"; }
lean_run() { local N=$1; guard; local G0=$(wc -l < /home/checker/corpus/guard.log)
  log "147: $N: shipped-config comparator run (Lean kernel) via 67d start"
  bash $W/67d_corpus_run_capped.sh $N-shipped /home/checker/math/lean/ComparatorChallenges/$N.json 7200 $O/runs/$N.lean-shipped.log 16G
  local V=$(verdict $O/runs/$N.lean-shipped.log); local L=$(tail -n +$((G0+1)) /home/checker/corpus/guard.log | grep -m1 LIMIT)
  log "147: $N: Lean kernel (shipped config): $V${L:+; guard: $L}"
  [ -n "$L" ] && { log "147: guard stopped during $N's Lean run; chain stops"; exit 1; }; }
[ -f /home/checker/corpus/GUARD_STOPPED ] && { mv /home/checker/corpus/GUARD_STOPPED /home/checker/corpus/GUARD_STOPPED-20261026-1932; log "147: earlier GUARD_STOPPED (19:32, ContinuumCoulombHardness build) kept as GUARD_STOPPED-20261026-1932"; }
log "147 start: Lean kernel on KMedianThreshold, Catalan; then one ContinuumCoulombHardness retry at 2 threads"
for N in KMedianThreshold Catalan; do lean_run $N; done
N=ContinuumCoulombHardness; guard; G0=$(wc -l < /home/checker/corpus/guard.log)
log "147: $N: retry export (143d, LEAN_NUM_THREADS 2) start"
mv $O/exports/$N.export.log $O/exports/$N.export.stopped-20261026-1932.log 2>/dev/null
R=$(XR_THREADS=2 XR_EXPORT_DIR=/home/checker/corpus/xr/exp-d bash $W/143d_matrix_export.sh $N $O 2>&1 | tail -1); set -- $R
if ! { [ "${1:-}" = "$N" ] && [ ${#4} = 64 ]; }; then
  L=$(tail -n +$((G0+1)) /home/checker/corpus/guard.log | grep -m1 LIMIT)
  log "147: $N: retry build/export failed: $R${L:+; guard: $L}; permanently deferred (Joe: no further retry)"; exit 0; fi
E=$2; NC=$3; SHA=$4; B=$(stat -c %s $E); log "147: $N: export done: $E bytes $B sha256 $SHA; nealmcb bytes 1081490385"
[ "$B" = 1081490385 ] || { log "147: $N: EXPORT SIZE DIFFERS from nealmcb's; chain stops"; exit 1; }
printf '%s\t%s\t%s\n' $N $NC $SHA > $O/plan-$N.tsv
bash $W/142d_matrix_batch.sh $O/plan-$N.tsv "B3 B2 B1"
tail -n 2 $O/run.log | grep -q "142 done: plan $O/plan-$N.tsv" || { log "147: $N: batch stopped; chain stops"; exit 1; }
lean_run $N
log "147 done"
