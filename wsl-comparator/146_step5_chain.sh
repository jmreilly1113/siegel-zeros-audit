#!/usr/bin/env bash
# nanoda version matrix (2026-10-26, UNOFFICIAL), step 5 (Joe): KMedianThreshold, Catalan, ContinuumCoulombHardness, one at a
# time, under 69_corpus_guard.sh and the full address-family deny list (75d/140d/142d/143d). For each config:
#   export with 143d (LEAN_NUM_THREADS 4, into /home/checker/corpus/xr/exp-d so the extended replay's exports are untouched);
#   compare sha256 with our logged value where one exists (extended replay runs/<C>-nanoda.mem.json) and the byte size with nealmcb's
#   results/nanoda-ab-let.jsonl; any mismatch: STOP. Then B3, B2, B1 (142d); a B1 cap or overflow is an expected outcome.
# Stops at the first build or export failure (a guard stop during a build counts as a build OOM). Run as root, detached.
set -u
W=/mnt/c/Users/Work/dev/siegel/wsl-comparator; O=/mnt/c/Users/Work/dev/siegel/results/2026-10-26-nanoda-version-matrix
log() { echo "$(date '+%F %T') $*" >> $O/run.log; }
declare -A LOGGED=([KMedianThreshold]=4bec532ccf5b8bd53718ec9bba1936401ca7ad94c006b5b70527765ac1627bc9
                   [Catalan]=6cfe74f401c34124c2bf8f47c76739e8fbbdde25226d6c3193a3af47e913f1ba)
declare -A NEAL=([KMedianThreshold]=620096646 [Catalan]=832532249 [ContinuumCoulombHardness]=1081490385)
mkdir -p /home/checker/corpus/xr/exp-d; chown checker:checker /home/checker/corpus/xr/exp-d
log "146 start: step 5 (KMedianThreshold, Catalan, ContinuumCoulombHardness; B3 B2 B1; full deny list)"
for N in KMedianThreshold Catalan ContinuumCoulombHardness; do
  [ -f /home/checker/corpus/GUARD_STOPPED ] && { log "146: GUARD_STOPPED present; chain stops"; exit 1; }
  pgrep -f 69_corpus_guard.sh >/dev/null || { setsid nohup bash $W/69_corpus_guard.sh 95 1500 20 >/dev/null 2>&1 < /dev/null & sleep 2; log "146: guard was not running; restarted 69_corpus_guard.sh 95 1500 20"; }
  G0=$(wc -l < /home/checker/corpus/guard.log)
  log "146: $N: export (143d, 4 threads) start"
  R=$(XR_THREADS=4 XR_EXPORT_DIR=/home/checker/corpus/xr/exp-d bash $W/143d_matrix_export.sh $N $O 2>&1 | tail -1)
  set -- $R
  if ! { [ "${1:-}" = "$N" ] && [ ${#4} = 64 ]; }; then
    L=$(tail -n +$((G0+1)) /home/checker/corpus/guard.log | grep -m1 LIMIT)
    log "146: $N: build/export failed: $R${L:+; guard: $L}; chain stops (Joe: stop at the first build OOM and report)"; exit 1
  fi
  E=$2; NC=$3; SHA=$4; B=$(stat -c %s $E)
  log "146: $N: export done: $E bytes $B sha256 $SHA; nealmcb bytes ${NEAL[$N]}"
  [ "$B" = "${NEAL[$N]}" ] || { log "146: $N: EXPORT SIZE DIFFERS from nealmcb's; chain stops"; exit 1; }
  if [ -n "${LOGGED[$N]:-}" ]; then
    [ "$SHA" = "${LOGGED[$N]}" ] || { log "146: $N: EXPORT SHA256 MISMATCH with the extended replay's logged ${LOGGED[$N]}; chain stops"; exit 1; }
    log "146: $N: sha256 equals the extended replay's logged value"
  fi
  printf '%s\t%s\t%s\n' $N $NC $SHA > $O/plan-$N.tsv
  bash $W/142d_matrix_batch.sh $O/plan-$N.tsv "B3 B2 B1"
  tail -n 2 $O/run.log | grep -q "142 done: plan $O/plan-$N.tsv" || { log "146: $N: batch stopped; chain stops"; exit 1; }
done
log "146 done: step 5"
