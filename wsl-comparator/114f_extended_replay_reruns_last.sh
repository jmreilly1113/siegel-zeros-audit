#!/usr/bin/env bash
# Extended replay, 114f (2026-10-24, Joe: "move the reruns to the end"): 114e with two changes.
#  1. A config whose 7200 s nanoda run timed out is queued in <out>/rerun-end.txt and the pass goes on. Its 28800 s
#     rerun, shipped (Lean-only) run, queries and classification run after the last config of the pass, in the slow lane
#     (up to SLOW_MAX at once), after a rebuild (no-op if the build is still there; queued configs are kept by prunes).
#     A config with a finished 7200 s timeout log from an earlier attempt is queued at load time (no lookahead build).
#  2. A preempted prebuild retries once A = MemAvailable + SwapFree > RETRY_MB (8000) for 120 s, or no main-lane run
#     is active (114d/114e waited for no main-lane run only; with handoffs that can last until the run ends).
# 114e header follows.
# Extended replay, 114e (2026-10-24): 114d plus a run handoff. Over the first 51 configs the main lane averaged ~1520 s
# per config, ~300 s of it waiting on nanoda runs that outlasted the next config's build. Now a 7200 s nanoda run still
# going after HANDOFF s (900) while the next config's build has finished moves to the slow lane (if it has room): the
# config is added to active-slow.txt, active-run.txt is cleared, and a slow-lane job waits for the run and does the rest
# (28800 s rerun on a timeout, shipped run, queries, classification) as finish_one <config> slow. The main lane goes on.
# Also: a "* <threads>" line in build-threads.txt sets the default prebuild threads (read at each build; per-config
# lines still win). Everything else is 114d's, unchanged.
# 114d header follows.
# Extended replay, 114d (2026-10-23, Joe: keep work moving, finish within 60 h). 114c with job-level memory handling, so
# one heavy job no longer stops the others, and long runs no longer block the main lane. Per-config steps, sandbox,
# timeouts, logs, classification and outputs are 114c's; what changes is only WHEN and BESIDE WHAT each step runs:
#  1. Guard 69c_lane_guard.py instead of 69b: under memory pressure it freezes, then kills, ONE job by lane priority
#     (build < main run < slow), writing <out>/preempt/<config>.<lane>; with one job left it does 69b's full stop.
#  2. A preempted prebuild is retried here at half the threads (min 2) once no main-lane run is active (at most 3
#     retries; then the config is left for the next attempt). A preempted run leaves its config without a result (rc 5);
#     114d goes on and the next attempt retries it (no DONE while such configs remain; 119c restarts 114d).
#  3. A nanoda run that timed out at 7200 s gets its 28800 s rerun in the slow lane, so the main lane goes on. A finished
#     7200 s timeout log (exit 124/137 after >= 7000 s) is kept across restarts (not moved aside), so the rerun is not
#     preceded by a second 7200 s attempt.
#  4. Slow lane: up to SLOW_MAX (2) configs at once (active-slow.txt has one line per config). The lookahead build now
#     runs while the slow lane is busy (69c arbitrates memory). serial-once.txt still turns the lookahead off.
# Kept from 114c: 8-thread prebuilds (build-threads.txt overrides), lookahead of one, boundary prunes keeping
# keep-configs + current + next + slow-lane configs, at-limit marker snapshot, resumability (result.json skip,
# deferred.txt skip, partial files moved aside at the config's build start).
# Run as root, detached, via 119c_supervise_selfheal.sh. Usage: 114d_extended_replay_lanes.sh <plan tsv> <out dir>
set -u
PLAN=$1; OUT=$2; PRUNE_AT=${PRUNE_AT:-55}; THREADS=${THREADS:-8}; SLOW_MAX=${SLOW_MAX:-2}; HANDOFF=${HANDOFF:-900}; RETRY_MB=${RETRY_MB:-8000}; RQ=$OUT/rerun-end.txt
# Test hooks (defaults are the live paths): XR_W scripts dir, XR_L lean dir, XR_C corpus dir (guard.log, GUARD_STOPPED)
W=${XR_W:-/mnt/c/Users/Work/dev/siegel/wsl-comparator}; QD=${XR_QD:-/mnt/c/Users/Work/dev/siegel/lean-checks/extended-replay}
C=${XR_C:-/home/checker/corpus}; L=${XR_L:-/home/checker/math/lean}; X=$C/xr; R=$OUT/runs; PB=$X/pb-114d
NB_POST=/opt/nanoda-postfix/nanoda_bin
mkdir -p $R $X/configs $X/exp $OUT/preempt; rm -rf $PB; mkdir -p $PB; chown -R checker:checker $X
: > $OUT/active-run.txt; : > $OUT/active-build.txt; : > $OUT/active-slow.txt; rm -f $OUT/active-*.at-limit.txt $OUT/preempt/*
log() { echo "$(date '+%F %T') $*" >> $OUT/run.log; }
GL=$C/guard.log; G0=$(wc -l < $GL 2>/dev/null || echo 0)
limit_seen() { tail -n +$((G0+1)) $GL 2>/dev/null | grep -q 'LIMIT:'; }   # a LIMIT line from this attempt's guard
stopped() { [ -f $C/GUARD_STOPPED ] || [ -f $R/STOP.txt ] || limit_seen; }
cfree() { df -BG --output=avail /mnt/c | tail -1 | tr -dc 0-9; }
wused() { df -BG --output=used / | tail -1 | tr -dc 0-9; }
rm -f $C/GUARD_STOPPED
nohup python3 -I $W/69c_lane_guard.py $OUT 85 4500 2000 8000 >> $C/xr-69c.out 2>&1 &
GD=$!
# Snapshot the markers when the guard fires (before 114d moves on), so 119c blames the configs active at that moment.
( while sleep 2; do limit_seen && { for m in run build slow; do cp $OUT/active-$m.txt $OUT/active-$m.at-limit.txt; done; exit 0; }; done ) &
SW=$!
log "start 114f_extended_replay_reruns_last.sh (28800 s reruns at the end; handoff after ${HANDOFF} s; prebuild LEAN_NUM_THREADS=$THREADS, lookahead 1, slow lane up to $SLOW_MAX, prune at WSL used > ${PRUNE_AT}G) plan $(basename $PLAN); clone HEAD $(sudo -u checker git -C /home/checker/math rev-parse HEAD) status [$(sudo -u checker git -C /home/checker/math status --short | tr '\n' ' ')]; kernel $(uname -r); WSL used $(wused)G; C: free $(cfree)G; guard 69c_lane_guard.py 85 4500 2000 8000"
prebuild() { # prebuild <log> <targets> <timeout> [threads]
  local T=${4:-$THREADS}
  { echo "== prebuild: lake build $2 with LEAN_NUM_THREADS=$T (114d)  $(date '+%F %T')"; T0=$(date +%s)
    bash $W/75_sbx.sh $3 $T "lake build $2" </dev/null
    echo "PREBUILD_SECONDS: $(( $(date +%s) - T0 ))"; echo "disk used: $(df -BG --output=used / | tail -1 | tr -d ' ')"
  } 2>&1 | cat > $1
}
crun() { python3 -I $W/111_memsample.py $2 $5 ${6:-} & local SP=$!; bash $W/67_corpus_run.sh $1 $2 $3 $4 </dev/null; wait $SP; }
live() { ls $R/$1.* $R/$1-* 2>/dev/null | grep -v '\.stopped-'; }
timed_out() { # timed_out <config>: its 7200 s nanoda run finished as a timeout (exit 124/137 after >= 7000 s)
  local f=$R/$1-nanoda.log; [ -f $f ] && grep -q 'COMPARATOR EXIT CODE: 12[4-9]\|COMPARATOR EXIT CODE: 137' $f && \
    [ "$(sed -n 's/^DURATION_SECONDS: //p' $f | tail -1)" -ge 7000 ] 2>/dev/null; }
aside() { local ts f; ts=$(date +%Y%m%d%H%M%S)
  for f in $(live $1); do
    if timed_out $1 && { [ "$f" = $R/$1-nanoda.log ] || [ "$f" = $R/$1-nanoda.mem.json ]; }; then continue; fi   # finished step: kept
    mv "$f" "${f%.*}.stopped-$ts.${f##*.}"; done; }
preempted() { # preempted <config> <lane>: 69c killed this job; record the marker in runs/ and clear it
  local f=$OUT/preempt/$1.$2; [ -f $f ] || return 1; mv $f $R/$1.preempt-$2-$(date +%Y%m%d%H%M%S).txt; }
memA() { awk '/^MemAvailable:|^SwapFree:/ {s+=$2} END {print int(s/1024)}' ${XR_MI:-/proc/meminfo}; }
queue_rerun() { grep -qx "$1" $RQ 2>/dev/null || echo "$1" >> $RQ; log "$1: 7200 s nanoda run timed out; 28800 s rerun queued for the end of the pass (rerun-end.txt)"; }
bkb() { du -sk $L/.lake/build 2>/dev/null | cut -f1; }
declare -A GRP SHP ORDN
PEND=()
while IFS=$'\t' read -r -u 9 ORD N G PIL SHIP LINES NTH EXTRA FLAG; do
  [ "$ORD" = order ] && continue
  case "$ORD" in \#*) continue ;; esac
  [ -f $R/$N.result.json ] && continue
  grep -qx "$N" $OUT/deferred.txt 2>/dev/null && { log "$N: deferred (deferred.txt); skipped for now"; continue; }
  GRP[$N]=$G; SHP[$N]=$SHIP; ORDN[$N]=$ORD
  if timed_out $N; then grep -qx "$N" $RQ 2>/dev/null || echo "$N" >> $RQ; log "$N: 7200 s timeout log from an earlier attempt; 28800 s rerun at the end of the pass"; continue; fi
  PEND+=("$N")
done 9< $PLAN
log "114f: ${#PEND[@]} configs pending; reruns queued for the end: $(tr '\n' ' ' < $RQ 2>/dev/null)"

build_one() { # build_one <config>: run in the background; writes $PB/<config>.built = 1 (prebuild ok), 0, or retry
  local N=$1 CFG TG PBOK BT tries=0
  echo "$N" > $OUT/active-build.txt
  # build-threads.txt "<config> <threads>": set by 119c after a memory stop on this config's build (last line wins)
  BT=$(awk -v c="$N" '$1==c {t=$2} $1=="*" {d=$2} END {print (t != "" ? t : d)}' $OUT/build-threads.txt 2>/dev/null); BT=${BT:-$THREADS}
  [ -n "$(live $N)" ] && { log "$N: partial files from an interrupted attempt moved aside"; aside $N; }
  CFG=$X/configs/$N-nanoda.json
  python3 -I -c "import json,sys; c=json.load(open(sys.argv[1])); c['enable_nanoda']=True; json.dump(c, open(sys.argv[2],'w'), indent=2)" $L/ComparatorChallenges/$N.json $CFG
  chown checker:checker $CFG
  TG=$(python3 -I -c "import json,sys; c=json.load(open(sys.argv[1])); print(' '.join([c['solution_module'], c['challenge_module']] + c.get('solution_imports', [])))" $CFG)
  while :; do
    log "$N (${ORDN[$N]}, group ${GRP[$N]}, shipped nanoda ${SHP[$N]}): prebuild (LEAN_NUM_THREADS=$BT; concurrent run: $(cat $OUT/active-run.txt); slow lane: $(tr '\n' ' ' < $OUT/active-slow.txt))"
    printf 'build_kb_before\t%s\nconcurrent_run_at_build_start\t%s\n' "$(bkb)" "$(cat $OUT/active-run.txt)" > $R/$N.disk.tsv
    prebuild $R/$N.prebuild.log "$TG" 14400 $BT
    printf 'build_kb_after_prebuild\t%s\nwsl_disk_used_after_prebuild\t%s\nc_free_gb_after_prebuild\t%s\n' "$(bkb)" "$(wused)" "$(cfree)" >> $R/$N.disk.tsv
    if stopped; then return; fi   # marker kept: 119c reads it after a stop
    preempted $N build || break
    tries=$((tries+1)); [ $BT -gt 2 ] && BT=$((BT/2))
    mv $R/$N.prebuild.log $R/$N.prebuild.preempted-$(date +%Y%m%d%H%M%S).log
    if [ $tries -gt 3 ]; then log "$N: prebuild preempted $tries times; left for the next attempt (no result)"; echo retry > $PB/$N.built; : > $OUT/active-build.txt; return; fi
    log "$N: prebuild preempted by 69c (memory beside other jobs); retry $tries at $BT threads once A > $RETRY_MB MB for 120 s or no main-lane run is active"
    local ok=0; while [ -s $OUT/active-run.txt ] && [ $ok -lt 8 ]; do sleep ${XR_RS:-15}; stopped && return; [ "$(memA)" -gt $RETRY_MB ] && ok=$((ok+1)) || ok=0; done
  done
  if grep -q 'SANDBOX EXIT CODE: 12[4-9]\|SANDBOX EXIT CODE: 137' $R/$N.prebuild.log; then
    log "$N: prebuild TIMEOUT at 14400 s; rerun once at 57600 s"
    prebuild $R/$N.prebuild-4x.log "$TG" 57600 $BT
    printf 'build_kb_after_prebuild_4x\t%s\n' "$(bkb)" >> $R/$N.disk.tsv
    if stopped; then return; fi   # marker kept for 119c
    if preempted $N build; then log "$N: prebuild 4x preempted by 69c; left for the next attempt (no result)"; echo retry > $PB/$N.built; : > $OUT/active-build.txt; return; fi
    PBOK=$(grep -c 'SANDBOX EXIT CODE: 0' $R/$N.prebuild-4x.log)
  else
    PBOK=$(grep -c 'SANDBOX EXIT CODE: 0' $R/$N.prebuild.log)
  fi
  [ "$PBOK" -ge 1 ] && echo 1 > $PB/$N.built || echo 0 > $PB/$N.built
  : > $OUT/active-build.txt
}

SPIDS=()
slow_n() { local c=0 e; for e in "${SPIDS[@]}"; do kill -0 ${e%%:*} 2>/dev/null && c=$((c+1)); done; echo $c; }
slow_add() { ( flock 5; echo "$1" >> $OUT/active-slow.txt ) 5>$X/slow.lock; }
slow_del() { ( flock 5; grep -vx "$1" $OUT/active-slow.txt > $X/slow.tmp; cat $X/slow.tmp > $OUT/active-slow.txt ) 5>$X/slow.lock; }
to_slow() { # to_slow <config> <long|finish>: the rest of the config in the background (long: the 28800 s rerun first)
  local N=$1 M=$2
  if [ "$(slow_n)" -ge $SLOW_MAX ]; then
    log "$N: slow lane full ($(tr '\n' ' ' < $OUT/active-slow.txt)); waiting"
    while [ "$(slow_n)" -ge $SLOW_MAX ]; do sleep 20; done
  fi
  slow_add $N
  ( if [ $M = long ]; then
      log "$N: comparator rerun at 28800 s (slow lane)"
      crun $N $X/configs/$N-nanoda.json 28800 $R/$N-nanoda-4x.log $R/$N-nanoda-4x.mem.json $X/exp/$N.export
      stopped && exit 9
      if preempted $N slow; then log "$N: 28800 s rerun preempted by 69c; left for the next attempt (no result)"; slow_del $N; exit 5; fi
    fi
    finish_one $N slow; rc=$?; slow_del $N; exit $rc ) &   # slow_del again: finish_one returns early on 2/5/9
  SPIDS+=("$!:$N")
}

run_one() { # run_one <config>: comparator runs, queries, classification; returns the classifier's code (0, 2, 3), 5, 9
  local N=$1 CFG=$X/configs/$1-nanoda.json NL
  echo "$N" > $OUT/active-run.txt
  if [ "$(cat $PB/$N.built)" = 1 ]; then
    if timed_out $N; then queue_rerun $N; return 0; fi
    log "$N: nanoda run"
    rm -f $X/rdone.$N; local T0=$(date +%s)
    ( crun $N $CFG 7200 $R/$N-nanoda.log $R/$N-nanoda.mem.json $X/exp/$N.export; touch $X/rdone.$N ) &
    while [ ! -f $X/rdone.$N ]; do
      sleep 3
      # 114e handoff: the next config is built and waiting; this run moves to the slow lane and the main lane goes on
      if [ ! -f $X/rdone.$N ] && [ $(( $(date +%s) - T0 )) -ge $HANDOFF ] && [ -n "${NX:-}" ] && [ -f $PB/$NX.built ] \
         && [ "$(slow_n)" -lt $SLOW_MAX ] && ! stopped; then
        slow_add $N; : > $OUT/active-run.txt
        log "$N: nanoda run still going after $(( $(date +%s) - T0 )) s and $NX is built; handed to the slow lane (main lane goes on)"
        ( while [ ! -f $X/rdone.$N ]; do sleep 10; done; after_run $N slow; rc=$?; slow_del $N; exit $rc ) &
        SPIDS+=("$!:$N")
        return 0
      fi
    done
    after_run $N main; return
  fi
  finish_one $N main
}

after_run() { # after_run <config> <main|slow>: 114d's steps after the 7200 s nanoda run (slow: the config is in the slow lane)
  local N=$1 MODE=$2 NL; rm -f $X/rdone.$N
  stopped && return 9
  if preempted $N run || preempted $N slow; then log "$N: nanoda run preempted by 69c ($MODE lane); left for the next attempt (no result)"; return 5; fi
  if timed_out $N; then
    queue_rerun $N; return 0
  fi
  NL=$R/$N-nanoda.log
  if ! { grep -q 'nanoda kernel accepts the solution' $NL && grep -q 'Lean default kernel accepts the solution' $NL && grep -q 'Your solution is okay!' $NL && grep -q 'COMPARATOR EXIT CODE: 0' $NL; }; then
    [ $MODE = slow ] && { finish_one $N slow; return; }
    log "$N: nanoda run not ACCEPT_BOTH; shipped run, queries and classification continue in the slow lane"
    to_slow $N finish
    return 0
  fi
  finish_one $N $MODE
}

finish_one() { # finish_one <config> <main|slow>: shipped run (if needed), queries, classification, f67473b, keep/export
  local N=$1 MODE=$2 CFG=$X/configs/$1-nanoda.json NL rc NC OC EXS SP
  if [ "$(cat $PB/$N.built)" = 1 ]; then
    NL=$R/$N-nanoda.log; [ -f $R/$N-nanoda-4x.log ] && NL=$R/$N-nanoda-4x.log
    if ! { grep -q 'nanoda kernel accepts the solution' $NL && grep -q 'Lean default kernel accepts the solution' $NL && grep -q 'Your solution is okay!' $NL && grep -q 'COMPARATOR EXIT CODE: 0' $NL; }; then
      log "$N: shipped-config run (nanoda run not ACCEPT_BOTH; $MODE lane)"
      crun $N $L/ComparatorChallenges/$N.json 7200 $R/$N-shipped.log $R/$N-shipped.mem.json
      stopped && return 9
      if preempted $N slow || preempted $N run; then log "$N: shipped run preempted by 69c; left for the next attempt (no result)"; [ $MODE = slow ] && slow_del $N; return 5; fi
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
    if preempted $N slow || preempted $N run; then log "$N: f67473b direct run preempted by 69c; left for the next attempt (no result)"; [ $MODE = slow ] && slow_del $N; return 5; fi
    python3 -I $W/115_classify.py $R $N ${GRP[$N]} ${SHP[$N]}; rc=$?
  fi
  [ $rc -eq 2 ] && { log "$N: not final (a run has no exit code line)"; return 2; }
  OC=$(python3 -I -c "import json,sys; print(json.load(open(sys.argv[1]))['outcome'])" $R/$N.result.json)
  EXS=$(python3 -I -c "import json,sys; e=json.load(open(sys.argv[1])).get('export') or {}; print(e.get('export_sha256'), e.get('export_bytes'))" $R/$N.result.json)
  log "$N: outcome $OC; export sha256/bytes $EXS"
  if [ $rc -eq 3 ]; then log "STOP: $(tail -1 $R/STOP.txt)"; echo "ComparatorChallenges/$N.json" >> $OUT/keep-configs.txt; return 3; fi
  if [ "$OC" = ACCEPT_BOTH ]; then rm -f $X/exp/$N.export $X/exp/$N.export.nanoda-config.json
  else echo "ComparatorChallenges/$N.json" >> $OUT/keep-configs.txt; log "$N: build and export kept ($OC)"; fi
  if [ "$MODE" = slow ]; then slow_del $N; else : > $OUT/active-run.txt; fi
  return 0
}

WPID=; n=${#PEND[@]}
for ((j=0; j<n; j++)); do
  N=${PEND[$j]}
  stopped && break
  f=$(cfree); if [ -n "$f" ] && [ "$f" -lt 22 ]; then echo "(d) C: free ${f} GB < 22 GB before $N  $(date '+%F %T')" >> $R/STOP.txt; log "STOP (d): C: free ${f}G"; break; fi
  if [ ! -f $PB/$N.built ] && [ -z "$WPID" ]; then build_one $N & WPID=$!; fi
  [ -n "$WPID" ] && { wait $WPID; WPID=; }
  stopped && break
  [ -f $PB/$N.built ] || { log "$N: build did not finish (stopped)"; break; }
  if [ "$(cat $PB/$N.built)" = retry ]; then log "$N: build gave way to other jobs; left for the next attempt"; continue; fi
  NX=${PEND[$((j+1))]:-}
  if [ "$(wused)" -gt "$PRUNE_AT" ]; then   # boundary prune: no build running; keep current, next and slow-lane closures
    cp $OUT/keep-configs.txt $X/keep-now.txt 2>/dev/null || : > $X/keep-now.txt
    echo "ComparatorChallenges/$N.json" >> $X/keep-now.txt
    [ -n "$NX" ] && echo "ComparatorChallenges/$NX.json" >> $X/keep-now.txt
    sed 's|.*|ComparatorChallenges/&.json|' $OUT/active-slow.txt >> $X/keep-now.txt
    [ -f $RQ ] && sed 's|.*|ComparatorChallenges/&.json|' $RQ >> $X/keep-now.txt   # queued reruns keep their builds
    python3 -I $W/112_prune.py $L $X/keep-now.txt --apply > $R/$N.prune-before.log 2>&1
    log "threshold prune before running $N (WSL used > ${PRUNE_AT}G): $(head -1 $R/$N.prune-before.log); WSL used $(wused)G"
  fi
  stopped && break
  if [ -n "$NX" ] && ! grep -qx "$N" $OUT/serial-once.txt 2>/dev/null; then build_one $NX & WPID=$!
  elif [ -n "$NX" ]; then log "$N: in serial-once.txt; no concurrent build"; fi
  run_one $N; rc=$?
  [ $rc -eq 0 ] || [ $rc -eq 5 ] && : > $OUT/active-run.txt   # on a stop the marker is kept for 119c
  [ $rc -eq 3 ] || [ $rc -eq 9 ] || [ $rc -eq 2 ] && break
done
[ -n "$WPID" ] && wait $WPID
if [ $j -ge $n ] && { [ -s $RQ ] || [ "$(slow_n)" -gt 0 ]; } && ! stopped; then   # 114f: the queued 28800 s reruns, after the last config of the pass
  log "114f: pass done; queued 28800 s reruns: $(tr '\n' ' ' < $RQ)"
  SEEN=" "
  while ! stopped; do   # until no new entry and the slow lane is empty (a handed-off run can time out and queue later)
    NEW=0
    for N in $(awk '!s[$0]++' $RQ 2>/dev/null); do
    case "$SEEN" in *" $N "*) continue ;; esac
    SEEN="$SEEN$N "; NEW=1
    stopped && break
    [ -f $R/$N.result.json ] && continue
    [ -n "${GRP[$N]:-}" ] || continue                      # deferred or not in the plan
    timed_out $N || { log "$N: queued, but no finished 7200 s timeout log; left for the next attempt"; continue; }
    build_one $N
    stopped && break
    [ "$(cat $PB/$N.built 2>/dev/null)" = 1 ] || { log "$N: rebuild before the rerun did not succeed; left for the next attempt"; continue; }
    to_slow $N long
    done
    [ $NEW = 0 ] && [ "$(slow_n)" -eq 0 ] && break
    [ $NEW = 0 ] && sleep 20
  done
fi
[ "$(slow_n)" -gt 0 ] && log "114d: waiting for the slow lane ($(tr '\n' ' ' < $OUT/active-slow.txt))"
for e in "${SPIDS[@]}"; do wait ${e%%:*}; done
kill $GD $SW 2>/dev/null
log "114d end; clone status [$(sudo -u checker git -C /home/checker/math status --short | tr '\n' ' ')]; WSL used $(wused)G; C: free $(cfree)G"
if [ -f $C/GUARD_STOPPED ] || limit_seen; then echo "GUARD STOPPED $(date '+%F %T')" > $OUT/GUARD_STOPPED.txt
elif [ -f $R/STOP.txt ]; then :
elif [ $j -ge $n ] && LEFT=$(awk -F'\t' -v R=$R -v D=$OUT/deferred.txt 'BEGIN {while ((getline l < D) > 0) d[l]=1}
       $1 != "order" && $1 !~ /^#/ && !($2 in d) && system("test -f " R "/" $2 ".result.json") != 0 {c++} END {print c+0}' $PLAN) \
     && [ "$LEFT" -gt 0 ]; then log "114d: $LEFT configs without a result and not deferred; no DONE, 119c restarts"
elif [ $j -ge $n ]; then echo "EXTENDED REPLAY DONE (pending list complete; see deferred.txt) $(date '+%F %T')" > $OUT/DONE.txt; fi
sync
