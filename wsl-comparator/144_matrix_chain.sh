#!/usr/bin/env bash
# nanoda version matrix (2026-10-26, UNOFFICIAL), stages 2 and 3 (Joe's order): after stage 1's batch ends ("142 done"
# for plan-stage1.tsv), one step at a time:
#   2. Laughlin: regenerate the export (143), then B1, B2, B3 (142); expected sha256 = the regenerated export's (no logged value).
#   3. KaplanskyFinitelyPresented, then GroupRingDeterminant: regenerate (143); the sha256 must equal the value logged on
#      2026-10-20 (results/2026-10-20-nanoda-discrepancy/SUMMARY.txt), else STOP; then B1, B2, B3 (142).
# Stops on: stage 1 not ending with "142 done", any 143 failure, a hash mismatch, or a 142 batch not ending with "142 done".
# Run as root, detached. Usage: 144_matrix_chain.sh
set -u
W=/mnt/c/Users/Work/dev/siegel/wsl-comparator; O=/mnt/c/Users/Work/dev/siegel/results/2026-10-26-nanoda-version-matrix
log() { echo "$(date '+%F %T') $*" >> $O/run.log; }
log "144 start: waits for stage 1"
while pgrep -f "142_matrix_batch.sh $O/plan-stage1.tsv" >/dev/null; do sleep 30; done
tail -n 3 $O/run.log | grep -q "142 done: plan $O/plan-stage1.tsv" || { log "144: stage 1 did not end with '142 done'; chain stops"; exit 1; }
declare -A LOGGED=([KaplanskyFinitelyPresented]=7b9235575213e672a217d9cfdf783ac7590d6f346002309e0b0c276b707f398c
                   [GroupRingDeterminant]=bda46ad6b35cc220ba4fbb8c7c93329d920682e3040257134f923bd0a53877e5)
for N in Laughlin KaplanskyFinitelyPresented GroupRingDeterminant; do
  [ -f /home/checker/corpus/GUARD_STOPPED ] && { log "144: GUARD_STOPPED present; chain stops"; exit 1; }
  pgrep -f 69_corpus_guard.sh >/dev/null || { setsid nohup bash $W/69_corpus_guard.sh 95 1500 20 >/dev/null 2>&1 < /dev/null & sleep 2; log "144: guard was not running; restarted 69_corpus_guard.sh 95 1500 20"; }
  log "144: $N: export (143) start"
  R=$(bash $W/143_matrix_export.sh $N $O 2>&1 | tail -1)
  set -- $R
  [ "${1:-}" = "$N" ] && [ ${#4} = 64 ] || { log "144: $N: export failed: $R; chain stops"; exit 1; }
  E=$2; NC=$3; SHA=$4; log "144: $N: export done: $E sha256 $SHA bytes $(stat -c %s $E)"
  if [ -n "${LOGGED[$N]:-}" ]; then
    [ "$SHA" = "${LOGGED[$N]}" ] || { log "144: $N: EXPORT SHA256 MISMATCH with the 2026-10-20 value ${LOGGED[$N]}; chain stops (Joe: stop and report)"; exit 1; }
    log "144: $N: sha256 equals the 2026-10-20 logged value"
  fi
  printf '%s\t%s\t%s\n' $N $NC $SHA > $O/plan-$N.tsv
  bash $W/142_matrix_batch.sh $O/plan-$N.tsv "B1 B2 B3"
  tail -n 2 $O/run.log | grep -q "142 done: plan $O/plan-$N.tsv" || { log "144: $N: batch stopped; chain stops"; exit 1; }
done
log "144 done: stages 2 and 3"
