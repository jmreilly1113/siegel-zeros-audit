#!/usr/bin/env bash
# nanoda version matrix (2026-10-26, UNOFFICIAL): run a list of <config> x <binary> checks ONE AT A TIME with
# 140_matrix_run.sh. Before each run: 69_corpus_guard.sh must be running (restarted and logged if not) and no
# GUARD_STOPPED; the export's sha256 must equal the expected value. Stops the batch on a hash mismatch, a setup error
# or an "other" outcome (possible genuine rejection: needs a human look). Run as root, detached.
# Usage: 142_matrix_batch.sh <plan tsv: config<TAB>nanoda config json<TAB>expected export sha256> <binary labels, e.g. "B1 B2 B3">
set -u
PLAN=$1; LABELS=$2
W=/mnt/c/Users/Work/dev/siegel/wsl-comparator; O=/mnt/c/Users/Work/dev/siegel/results/2026-10-26-nanoda-version-matrix
declare -A BIN=([B1]=/opt/nanoda-1gib-diag/nanoda_bin [B2]=/opt/nanoda-37cb87b/nanoda_bin [B3]=/opt/nanoda-37cb87b-patch64/nanoda_bin)
log() { echo "$(date '+%F %T') $*" >> $O/run.log; }
guard() {
  [ -f /home/checker/corpus/GUARD_STOPPED ] && { log "GUARD_STOPPED present; batch stops"; exit 1; }
  pgrep -f 69_corpus_guard.sh >/dev/null || { setsid nohup bash $W/69_corpus_guard.sh 95 1500 20 >/dev/null 2>&1 < /dev/null & sleep 2; log "guard was not running; restarted 69_corpus_guard.sh 95 1500 20"; }
}
log "142 start: plan $PLAN; binaries $LABELS"
while IFS=$'\t' read -r C NC XSHA; do
  [ -z "$C" ] || [ "${C:0:1}" = "#" ] && continue
  E=$(python3 -I -c "import json,sys; print(json.load(open(sys.argv[1]))['export_file_path'])" $NC)
  for L in $LABELS; do
    guard
    [ -f $O/runs/$C.$L.log ] && grep -q '^OUTCOME' $O/runs/$C.$L.log && { log "$C $L: already has an outcome; skipped"; continue; }
    log "$C $L: start (${BIN[$L]})"
    bash $W/140_matrix_run.sh $C-$L $NC ${BIN[$L]} $O/runs/$C.$L.log 1800 16G > /dev/null
    GOT=$(grep -oP "^export: \S+ bytes \d+ sha256 \K[0-9a-f]{64}" $O/runs/$C.$L.log)
    OUT=$(grep '^OUTCOME' $O/runs/$C.$L.log | tail -1)
    log "$C $L: $OUT"
    printf '%s\t%s\t%s\t%s\t%s\n' "$C" "$L" "${BIN[$L]}" "$GOT" "${OUT#OUTCOME: }" >> $O/outcomes-raw.tsv
    [ "$GOT" = "$XSHA" ] || { log "$C $L: EXPORT SHA256 MISMATCH (got $GOT, expected $XSHA); batch stops"; exit 1; }
    case "$OUT" in "OUTCOME: other"*|"OUTCOME: setup-error"*) log "$C $L: outcome needs a human look; batch stops"; exit 1;; esac
  done
done < $PLAN
log "142 done: plan $PLAN"
