#!/usr/bin/env bash
# UNOFFICIAL post-fix batch (Joe 2026-10-19, option b). After the main remainder run ends (DONE.txt), rerun the
# nanoda-enabled config of every config whose official outcome is ACCEPT_LEAN_ONLY, with nanoda_lib f67473b (98).
# Serial, one run at a time, same WSL guard as the corpus run. Builds are kept (keep-configs.txt), so nothing is
# compiled except what the comparator itself builds. Outcomes go to <out>/outcomes.tsv only, never into the main table.
# A run without a COMPARATOR EXIT CODE line, or ended by a guard, is STOPPED (not a result).
# Run as root, detached. Usage: 99_postfix_batch.sh <config list (names)> <out dir>
set -u
LIST=$1; OUT=$2; W=/mnt/c/Users/Work/dev/siegel/wsl-comparator; C=/home/checker/corpus/configs
mkdir -p $OUT
log() { echo "$(date '+%F %T') $*" >> $OUT/run.log; }
stopped() { [ -f /home/checker/corpus/GUARD_STOPPED ]; }
rm -f /home/checker/corpus/GUARD_STOPPED
nohup bash $W/69_corpus_guard.sh 85 1500 2 >/dev/null 2>&1 &
GD=$!
log "start 99_postfix_batch.sh (UNOFFICIAL, nanoda f67473b); configs: $(grep -v '^#' $LIST | tr '\n' ' ')"
[ -f $OUT/outcomes.tsv ] || printf 'config\tpostfix_outcome\tevidence\n' > $OUT/outcomes.tsv
for N in $(grep -v '^#' $LIST); do
  stopped && break
  grep -q "^$N	" $OUT/outcomes.tsv && continue
  [ -f $C/$N-nanoda.json ] || { log "$N: no $C/$N-nanoda.json; skipped"; continue; }
  [ -f $OUT/$N-postfix.log ] && mv $OUT/$N-postfix.log $OUT/$N-postfix.stopped-$(date +%Y%m%d%H%M%S).log
  log "$N: post-fix nanoda run"
  bash $W/98_postfix_run.sh $N $C/$N-nanoda.json 7200 $OUT/$N-postfix.log </dev/null
  F=$OUT/$N-postfix.log
  if stopped || ! grep -q 'COMPARATOR EXIT CODE' $F; then
    log "$N: STOPPED (guard or no exit code line); not a result"; continue
  fi
  ev=$(grep -h -E 'nanoda kernel (accepts|rejected)|Lean default kernel accepts|Your solution is okay|overflowed its stack|panicked|Illegal axiom|COMPARATOR EXIT CODE' $F | tr '\n' ';' | cut -c1-400)
  if grep -q 'nanoda kernel accepts the solution' $F && grep -q 'Lean default kernel accepts the solution' $F && grep -q 'Your solution is okay!' $F && grep -q 'COMPARATOR EXIT CODE: 0' $F; then o=POSTFIX_ACCEPT_BOTH
  elif grep -q 'overflowed its stack' $F; then o=POSTFIX_NANODA_STACK_OVERFLOW
  elif grep -q 'SANDBOX EXIT CODE: 12[4-9]\|COMPARATOR EXIT CODE: 12[4-9]' $F; then o=POSTFIX_TIMEOUT
  else o=POSTFIX_OTHER; fi
  printf '%s\t%s\t%s\n' "$N" "$o" "$ev" >> $OUT/outcomes.tsv; log "$N: $o"
done
kill $GD 2>/dev/null
if stopped; then echo "GUARD STOPPED $(date '+%F %T')" > $OUT/GUARD_STOPPED.txt; log "guard stopped"; else echo "POSTFIX DONE $(date '+%F %T')" > $OUT/DONE.txt; log "end"; fi
sync
