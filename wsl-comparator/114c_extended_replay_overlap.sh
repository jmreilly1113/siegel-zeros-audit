#!/usr/bin/env bash
# Extended replay, 114c (Joe, 2026-10-21 ~16:40: "builds at 8 threads" + "overlap next build with current run").
# Same per-config steps, logs, sandbox, timeouts, checks and outputs as 114b_extended_replay_shared.sh, with two changes:
#  1. prebuilds use LEAN_NUM_THREADS=$THREADS (8; the 189 used 4). Comparator runs and queries are unchanged.
#  2. lookahead of ONE: while config j's comparator runs and queries run, config j+1's prebuild runs. Builds stay serial
#     (j+1's build starts only after j's build finished, so j's closure is complete before its comparator run, and
#     j+1's build writes only modules outside it). Threshold prunes (WSL used > PRUNE_AT) happen only at a config
#     boundary while no build runs, keeping keep-configs.txt plus the next config's closure.
# A config listed in serial-once.txt runs with no concurrent build (set by 119b after a memory stop with both active).
# 2026-10-22 fix: on a stop, active-run.txt / active-build.txt are no longer cleared, so 119b can attribute the stop
# (before, 119b always saw both empty after a stop and did not restart: 03:27 on 2026-10-22).
# 2026-10-22 slow lane (Joe: finishing quickly is essential): when a nanoda run is not ACCEPT_BOTH, the rest of that
# config (shipped run, queries, classification, f67473b direct run) runs in the background as the SLOW LANE (at most
# one config; active-slow.txt), and the main loop goes on. While the slow lane runs, no lookahead build is started
# (so at most two comparator runs and no build share memory), and boundary prunes keep the slow-lane config's build.
# 2026-10-23 fixes (the 2026-10-22 22:52 memory stop): (1) boundary prunes also keep the next config's closure, as
# stated above (before, a fully built next config could be pruned); (2) a LIMIT line in guard.log from this attempt's
# guard counts as stopped at once (before, 114c went on until the guard's GUARD_STOPPED touch 20 s later, and started
# a new build); (3) when the guard fires, the markers are copied to active-{run,build,slow}.at-limit.txt for 119c.
# Markers for 119b: active-run.txt (config whose comparator/queries run), active-build.txt (config being built).
# Resumable as 114b (result.json skip, deferred.txt skip, partial files moved aside at the config's build start).
# Run as root, detached, via 119b_supervise_overlap.sh. Usage: 114c_extended_replay_overlap.sh <plan tsv> <out dir>
set -u
PLAN=$1; OUT=$2; PRUNE_AT=${PRUNE_AT:-55}; THREADS=${THREADS:-8}
W=/mnt/c/Users/Work/dev/siegel/wsl-comparator; QD=/mnt/c/Users/Work/dev/siegel/lean-checks/extended-replay
L=/home/checker/math/lean; X=/home/checker/corpus/xr; R=$OUT/runs; PB=$X/pb-114c
NB_POST=/opt/nanoda-postfix/nanoda_bin
mkdir -p $R $X/configs $X/exp; rm -rf $PB; mkdir -p $PB; chown -R checker:checker $X
: > $OUT/active-run.txt; : > $OUT/active-build.txt; rm -f $OUT/active-*.at-limit.txt
log() { echo "$(date '+%F %T') $*" >> $OUT/run.log; }
GL=/home/checker/corpus/guard.log; G0=$(wc -l < $GL 2>/dev/null || echo 0)
limit_seen() { tail -n +$((G0+1)) $GL 2>/dev/null | grep -q 'LIMIT:'; }   # a LIMIT line from this attempt's guard
stopped() { [ -f /home/checker/corpus/GUARD_STOPPED ] || [ -f $R/STOP.txt ] || limit_seen; }
cfree() { df -BG --output=avail /mnt/c | tail -1 | tr -dc 0-9; }
wused() { df -BG --output=used / | tail -1 | tr -dc 0-9; }
rm -f /home/checker/corpus/GUARD_STOPPED
nohup bash $W/69_corpus_guard.sh 85 1500 2 >/dev/null 2>&1 &
GD=$!
# Snapshot the markers when the guard fires (before 114c moves on), so 119c blames the configs active at that moment.
( while sleep 2; do limit_seen && { for m in run build slow; do cp $OUT/active-$m.txt $OUT/active-$m.at-limit.txt; done; exit 0; }; done ) &
SW=$!
log "start 114c_extended_replay_overlap.sh (prebuild LEAN_NUM_THREADS=$THREADS, lookahead 1, prune at WSL used > ${PRUNE_AT}G) plan $(basename $PLAN); clone HEAD $(sudo -u checker git -C /home/checker/math rev-parse HEAD) status [$(sudo -u checker git -C /home/checker/math status --short | tr '\n' ' ')]; kernel $(uname -r); WSL used $(wused)G; C: free $(cfree)G; guard 69_corpus_guard.sh 85 1500 2"
prebuild() { # prebuild <log> <targets> <timeout>
  { echo "== prebuild: lake build $2 with LEAN_NUM_THREADS=$THREADS (114c)  $(date '+%F %T')"; T0=$(date +%s)
    bash $W/75_sbx.sh $3 $THREADS "lake build $2" </dev/null
    echo "PREBUILD_SECONDS: $(( $(date +%s) - T0 ))"; echo "disk used: $(df -BG --output=used / | tail -1 | tr -d ' ')"
  } 2>&1 | cat > $1
}
crun() { python3 -I $W/111_memsample.py $2 $5 ${6:-} & local SP=$!; bash $W/67_corpus_run.sh $1 $2 $3 $4 </dev/null; wait $SP; }
live() { ls $R/$1.* $R/$1-* 2>/dev/null | grep -v '\.stopped-'; }
aside() { local ts; ts=$(date +%Y%m%d%H%M%S); for f in $(live $1); do mv "$f" "${f%.*}.stopped-$ts.${f##*.}"; done; }
bkb() { du -sk $L/.lake/build 2>/dev/null | cut -f1; }
declare -A GRP SHP ORDN
PEND=()
while IFS=$'\t' read -r -u 9 ORD N G PIL SHIP LINES NTH EXTRA FLAG; do
  [ "$ORD" = order ] && continue
  case "$ORD" in \#*) continue ;; esac
  [ -f $R/$N.result.json ] && continue
  grep -qx "$N" $OUT/deferred.txt 2>/dev/null && { log "$N: deferred (deferred.txt); skipped for now"; continue; }
  PEND+=("$N"); GRP[$N]=$G; SHP[$N]=$SHIP; ORDN[$N]=$ORD
done 9< $PLAN
log "114c: ${#PEND[@]} configs pending"

build_one() { # build_one <config>: run in the background; writes $PB/<config>.built = 1 (prebuild ok) or 0
  local N=$1 CFG TG PBOK
  echo "$N" > $OUT/active-build.txt
  [ -n "$(live $N)" ] && { log "$N: partial files from an interrupted attempt moved aside"; aside $N; }
  CFG=$X/configs/$N-nanoda.json
  python3 -I -c "import json,sys; c=json.load(open(sys.argv[1])); c['enable_nanoda']=True; json.dump(c, open(sys.argv[2],'w'), indent=2)" $L/ComparatorChallenges/$N.json $CFG
  chown checker:checker $CFG
  TG=$(python3 -I -c "import json,sys; c=json.load(open(sys.argv[1])); print(' '.join([c['solution_module'], c['challenge_module']] + c.get('solution_imports', [])))" $CFG)
  log "$N (${ORDN[$N]}, group ${GRP[$N]}, shipped nanoda ${SHP[$N]}): prebuild (LEAN_NUM_THREADS=$THREADS; concurrent run: $(cat $OUT/active-run.txt))"
  printf 'build_kb_before\t%s\nconcurrent_run_at_build_start\t%s\n' "$(bkb)" "$(cat $OUT/active-run.txt)" > $R/$N.disk.tsv
  prebuild $R/$N.prebuild.log "$TG" 14400
  printf 'build_kb_after_prebuild\t%s\nwsl_disk_used_after_prebuild\t%s\nc_free_gb_after_prebuild\t%s\n' "$(bkb)" "$(wused)" "$(cfree)" >> $R/$N.disk.tsv
  if stopped; then return; fi   # marker kept: 119b reads it after a stop
  if grep -q 'SANDBOX EXIT CODE: 12[4-9]\|SANDBOX EXIT CODE: 137' $R/$N.prebuild.log; then
    log "$N: prebuild TIMEOUT at 14400 s; rerun once at 57600 s"
    prebuild $R/$N.prebuild-4x.log "$TG" 57600
    printf 'build_kb_after_prebuild_4x\t%s\n' "$(bkb)" >> $R/$N.disk.tsv
    if stopped; then return; fi   # marker kept for 119b
    PBOK=$(grep -c 'SANDBOX EXIT CODE: 0' $R/$N.prebuild-4x.log)
  else
    PBOK=$(grep -c 'SANDBOX EXIT CODE: 0' $R/$N.prebuild.log)
  fi
  [ "$PBOK" -ge 1 ] && echo 1 > $PB/$N.built || echo 0 > $PB/$N.built
  : > $OUT/active-build.txt
}

run_one() { # run_one <config>: comparator runs, queries, classification; returns the classifier's code (0, 2, 3)
  local N=$1 CFG=$X/configs/$1-nanoda.json NL rc NC OC EXS SP
  echo "$N" > $OUT/active-run.txt
  if [ "$(cat $PB/$N.built)" = 1 ]; then
    log "$N: nanoda run"
    crun $N $CFG 7200 $R/$N-nanoda.log $R/$N-nanoda.mem.json $X/exp/$N.export
    stopped && return 9
    if grep -q 'COMPARATOR EXIT CODE: 12[4-9]\|COMPARATOR EXIT CODE: 137' $R/$N-nanoda.log; then
      log "$N: comparator TIMEOUT at 7200 s; rerun once at 28800 s"
      crun $N $CFG 28800 $R/$N-nanoda-4x.log $R/$N-nanoda-4x.mem.json $X/exp/$N.export
      stopped && return 9
    fi
    NL=$R/$N-nanoda.log; [ -f $R/$N-nanoda-4x.log ] && NL=$R/$N-nanoda-4x.log
    if ! { grep -q 'nanoda kernel accepts the solution' $NL && grep -q 'Lean default kernel accepts the solution' $NL && grep -q 'Your solution is okay!' $NL && grep -q 'COMPARATOR EXIT CODE: 0' $NL; }; then
      if [ -n "$SPID" ] && kill -0 $SPID 2>/dev/null; then log "$N: waiting for the slow lane ($(cat $OUT/active-slow.txt)) to finish"; wait $SPID; fi
      echo "$N" > $OUT/active-slow.txt; SLOWN=$N
      log "$N: nanoda run not ACCEPT_BOTH; shipped run, queries and classification continue in the slow lane"
      finish_one $N slow &
      SPID=$!
      return 0
    fi
  fi
  finish_one $N main
}

finish_one() { # finish_one <config> <main|slow>: shipped run (if needed), queries, classification, f67473b, keep/export
  local N=$1 MODE=$2 CFG=$X/configs/$1-nanoda.json NL rc NC OC EXS SP
  if [ "$(cat $PB/$N.built)" = 1 ]; then
    NL=$R/$N-nanoda.log; [ -f $R/$N-nanoda-4x.log ] && NL=$R/$N-nanoda-4x.log
    if ! { grep -q 'nanoda kernel accepts the solution' $NL && grep -q 'Lean default kernel accepts the solution' $NL && grep -q 'Your solution is okay!' $NL && grep -q 'COMPARATOR EXIT CODE: 0' $NL; }; then
      log "$N: shipped-config run (nanoda run not ACCEPT_BOTH; $MODE lane)"
      crun $N $L/ComparatorChallenges/$N.json 7200 $R/$N-shipped.log $R/$N-shipped.mem.json
      stopped && return 9
    fi
    log "$N: #print axioms"
    { echo "== #print axioms $N: lake env lean $QD/$N-axioms.lean  $(date '+%F %T')"; echo "file sha256 $(sha256sum $QD/$N-axioms.lean | cut -c1-64)"
      bash $W/75_sbx.sh 3600 4 "lake env lean $QD/$N-axioms.lean" </dev/null; } > $R/$N-axioms.log 2>&1
    for S in challenge solution; do
      [ -f $QD/$N-audit-$S.lean ] || continue
      log "$N: audit query ($S)"
      { echo "== audit query $N $S: lake env lean $QD/$N-audit-$S.lean  $(date '+%F %T')"; echo "file sha256 $(sha256sum $QD/$N-audit-$S.lean | cut -c1-64)"
        bash $W/75_sbx.sh 3600 4 "lake env lean $QD/$N-audit-$S.lean" </dev/null; } > $R/$N-audit-$S.log 2>&1
    done
    stopped && return 9
  fi
  python3 -I $W/115_classify.py $R $N ${GRP[$N]} ${SHP[$N]}; rc=$?
  if [ $rc -eq 4 ]; then
    NC=$X/exp/$N.f67473b-config.json
    python3 -I -c "import json,sys; c=json.load(open(sys.argv[1])); c['export_file_path']=sys.argv[3]; json.dump(c, open(sys.argv[2],'w'), indent=1)" $X/exp/$N.export.nanoda-config.json $NC $X/exp/$N.export
    chown checker:checker $NC $X/exp/$N.export
    log "$N: nanoda crash; nanoda f67473b directly on the retained export (default stack)"
    python3 -I $W/111_memsample.py $NC $R/$N-f67473b-direct.mem.json & SP=$!
    bash $W/113_nanoda_direct.sh $N $NC $NB_POST 7200 $R/$N-f67473b-direct.log </dev/null
    wait $SP
    stopped && return 9
    python3 -I $W/115_classify.py $R $N ${GRP[$N]} ${SHP[$N]}; rc=$?
  fi
  [ $rc -eq 2 ] && { log "$N: not final (a run has no exit code line)"; return 2; }
  OC=$(python3 -I -c "import json,sys; print(json.load(open(sys.argv[1]))['outcome'])" $R/$N.result.json)
  EXS=$(python3 -I -c "import json,sys; e=json.load(open(sys.argv[1])).get('export') or {}; print(e.get('export_sha256'), e.get('export_bytes'))" $R/$N.result.json)
  log "$N: outcome $OC; export sha256/bytes $EXS"
  if [ $rc -eq 3 ]; then log "STOP: $(tail -1 $R/STOP.txt)"; echo "ComparatorChallenges/$N.json" >> $OUT/keep-configs.txt; return 3; fi
  if [ "$OC" = ACCEPT_BOTH ]; then rm -f $X/exp/$N.export $X/exp/$N.export.nanoda-config.json
  else echo "ComparatorChallenges/$N.json" >> $OUT/keep-configs.txt; log "$N: build and export kept ($OC)"; fi
  if [ "$MODE" = slow ]; then : > $OUT/active-slow.txt; else : > $OUT/active-run.txt; fi
  return 0
}

WPID=; SPID=; SLOWN=; : > $OUT/active-slow.txt; n=${#PEND[@]}
slow_on() { [ -n "$SPID" ] && kill -0 $SPID 2>/dev/null; }
for ((j=0; j<n; j++)); do
  N=${PEND[$j]}
  stopped && break
  f=$(cfree); if [ -n "$f" ] && [ "$f" -lt 22 ]; then echo "(d) C: free ${f} GB < 22 GB before $N  $(date '+%F %T')" >> $R/STOP.txt; log "STOP (d): C: free ${f}G"; break; fi
  if [ ! -f $PB/$N.built ] && [ -z "$WPID" ]; then build_one $N & WPID=$!; fi
  [ -n "$WPID" ] && { wait $WPID; WPID=; }
  stopped && break
  [ -f $PB/$N.built ] || { log "$N: build did not finish (stopped)"; break; }
  NX=${PEND[$((j+1))]:-}
  if [ "$(wused)" -gt "$PRUNE_AT" ]; then   # boundary prune: no build running; keep the current and next configs' closures too
    cp $OUT/keep-configs.txt $X/keep-now.txt 2>/dev/null || : > $X/keep-now.txt
    echo "ComparatorChallenges/$N.json" >> $X/keep-now.txt
    [ -n "$NX" ] && echo "ComparatorChallenges/$NX.json" >> $X/keep-now.txt   # 2026-10-23: was missing (MUBSix's full build pruned 22-10 23:10)
    slow_on && echo "ComparatorChallenges/$SLOWN.json" >> $X/keep-now.txt
    python3 -I $W/112_prune.py $L $X/keep-now.txt --apply > $R/$N.prune-before.log 2>&1
    log "threshold prune before running $N (WSL used > ${PRUNE_AT}G): $(head -1 $R/$N.prune-before.log); WSL used $(wused)G"
  fi
  stopped && break
  if [ -n "$NX" ] && slow_on; then log "$N: slow lane busy ($SLOWN); no concurrent build"
  elif [ -n "$NX" ] && ! grep -qx "$N" $OUT/serial-once.txt 2>/dev/null; then build_one $NX & WPID=$!
  elif [ -n "$NX" ]; then log "$N: in serial-once.txt; no concurrent build"; fi
  run_one $N; rc=$?
  [ $rc -eq 0 ] && : > $OUT/active-run.txt   # on a stop the marker is kept for 119b
  [ $rc -eq 3 ] || [ $rc -eq 9 ] || [ $rc -eq 2 ] && break
done
[ -n "$WPID" ] && wait $WPID
slow_on && { log "114c: waiting for the slow lane ($SLOWN)"; wait $SPID; }
kill $GD $SW 2>/dev/null
log "114c end; clone status [$(sudo -u checker git -C /home/checker/math status --short | tr '\n' ' ')]; WSL used $(wused)G; C: free $(cfree)G"
if [ -f /home/checker/corpus/GUARD_STOPPED ] || limit_seen; then echo "GUARD STOPPED $(date '+%F %T')" > $OUT/GUARD_STOPPED.txt
elif [ -f $R/STOP.txt ]; then :
elif [ $j -ge $n ]; then echo "EXTENDED REPLAY DONE (pending list complete; see deferred.txt) $(date '+%F %T')" > $OUT/DONE.txt; fi
sync
