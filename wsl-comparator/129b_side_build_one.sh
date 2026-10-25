#!/usr/bin/env bash
# 129b (2026-10-25): as 129, but a stop or a missing 114f ends it only if it lasts GRACE s (default 300), so it
# survives 119c's self-healing restarts and keeps its keep lines (and partial build) across them. It also runs for a
# deferred config (CycleCliqueRamsey, deferred 13:30 after an out-of-memory stop of 114f's 10-thread build).
# 129 (2026-10-25): side-builds one named config's closure beside the running 114f, retrying after memory back-offs,
# so that 114f's later prebuild of it is (nearly) a no-op. Written for CycleCliqueRamsey, whose ~220 built modules
# were pruned at 04:41 after the manual preempt and which 114f would otherwise rebuild (~3 h) at the very end.
# Usage: 129_side_build_one.sh <config> <out dir> [threads 3]. Run as root, beside 114f and 128; neither is touched.
# Same mechanics as 128_side_prebuild.sh: the config goes into keep-configs.txt (boundary prunes keep its closure,
# including partial progress after a back-off); lake build of its targets through 75_sbx.sh (14400 s timeout); its own
# systemd unit is killed if A = MemAvailable + SwapFree < LOW_MB, if 114f's active build becomes the config, or on a
# stop; a 69c preempt marker written for this unit is moved to runs/. Starts (and restarts) only at A >= MIN_MB, at
# most MAXTRY attempts. Ends when 128_closure.py reports nothing unbuilt, when 114f reaches the config (keep lines are
# then removed), on a stop, or when 114f exits. Keep lines stay while the config is unreached and partly built.
# Logs: run.log ("129: ..."), runs/<T>.side-build-<n>.log.
# Test hooks: as 128 (XR_W, XR_L, XR_C, XR_MI, XR_APP, XR_ST, XR_IDLE, XR_PG).
T=$1; OUT=$2; THR=${3:-3}
MIN_MB=${SIDE_MIN_MB:-12000}; LOW_MB=${LOW_MB:-6000}; MAXTRY=${MAXTRY:-6}; ST=${XR_ST:-5}; IDLE=${XR_IDLE:-60}
W=${XR_W:-/mnt/c/Users/Work/dev/siegel/wsl-comparator}; L=${XR_L:-/home/checker/math/lean}; C=${XR_C:-/home/checker/corpus}
APP=${XR_APP:-/sys/fs/cgroup/unified/user.slice/user-1000.slice/user@1000.service/app.slice}
PG=${XR_PG:-114f_extended_replay_reruns_last.sh}; R=$OUT/runs; KEEP=$OUT/keep-configs.txt; GL=$C/guard.log; X=$C/xr
log() { echo "$(date '+%F %T') $*" >> $OUT/run.log; }
stopped() { [ -f $C/GUARD_STOPPED ] || [ -f $R/STOP.txt ] || [ -f $OUT/HALT.txt ]; }
memA() { awk '/^MemAvailable:|^SwapFree:/ {s+=$2} END {print int(s/1024)}' ${XR_MI:-/proc/meminfo}; }
reached() { [ "$(cat $OUT/active-build.txt 2>/dev/null)" = "$1" ] || [ "$(cat $OUT/active-run.txt 2>/dev/null)" = "$1" ] || [ -f $R/$1.result.json ]; }
keep_del() { local t=$X/keep129.tmp; grep -vx "ComparatorChallenges/$1.json" $KEEP | grep -vx "# 129 side build: $1" > $t; cat $t > $KEEP; rm -f $t; }
find_unit() { local d p; for d in $APP/run-*.service; do for p in $(cat $d/cgroup.procs 2>/dev/null); do
    tr '\0' ' ' < /proc/$p/cmdline 2>/dev/null | grep -q "^[^ ]*timeout .*bash -c lake build $1 *$" && { echo $d; return 0; }
  done; done; return 1; }
ended() { local k; for ((k=0; k<${GRACE:-300}; k+=ST)); do stopped || ! pgrep -f "$PG" > /dev/null || return 1; sleep $ST; done; return 0; }
unbuilt() { python3 -I $W/128_closure.py $L $T | awk '{print $2}'; }
mkdir -p $X
TG=$(python3 -I -c "import json,sys; c=json.load(open(sys.argv[1])); print(' '.join([c['solution_module'], c['challenge_module']] + c.get('solution_imports', [])))" $L/ComparatorChallenges/$T.json) || exit 1
printf '# 129 side build: %s\nComparatorChallenges/%s.json\n' $T $T >> $KEEP
log "129b: start for $T ($THR threads, start at A >= $MIN_MB MB, back off below $LOW_MB MB, $MAXTRY attempts); $(unbuilt) modules unbuilt; kept in keep-configs.txt"
n=0
while :; do
  if stopped || ! pgrep -f "$PG" > /dev/null; then
    if ended; then keep_del $T; log "129b: stop in force or $PG not running for ${GRACE:-300} s; keep lines removed; exit"; exit 0; fi
    continue
  fi
  if reached $T; then keep_del $T; log "129b: $T reached by 114f; keep lines removed; exit"; exit 0; fi
  U=$(unbuilt); if [ "$U" = 0 ]; then log "129b: $T closure built; keep lines stay until 114f reaches it"; break; fi
  if [ $n -ge $MAXTRY ]; then log "129b: $MAXTRY attempts used ($U unbuilt); left to 114f; keep lines stay until 114f reaches it"; break; fi
  if [ "$(memA)" -lt $MIN_MB ]; then sleep $IDLE; continue; fi
  n=$((n+1)); G0=$(wc -l < $GL 2>/dev/null || echo 0); WHY=; MYU=
  log "129b: side build of $T, attempt $n ($U unbuilt; A $(memA) MB)"
  { echo "== side build (129): lake build $TG with LEAN_NUM_THREADS=$THR  $(date '+%F %T')"; T0=$(date +%s)
    bash $W/75_sbx.sh 14400 $THR "lake build $TG" </dev/null
    echo "PREBUILD_SECONDS: $(( $(date +%s) - T0 ))"; } > $R/$T.side-build-$n.log 2>&1 &
  BP=$!
  for k in $(seq 60); do sleep 1; MYU=$(find_unit "$TG") && break; kill -0 $BP 2>/dev/null || break; done
  while kill -0 $BP 2>/dev/null; do
    sleep $ST
    if stopped; then WHY="stop in force"
    elif [ "$(cat $OUT/active-build.txt 2>/dev/null)" = "$T" ]; then WHY="114f started its own build of $T"
    elif [ "$(memA)" -lt $LOW_MB ]; then WHY="A $(memA) MB < $LOW_MB MB"; fi
    if [ -n "$WHY" ]; then [ -n "$MYU" ] && echo 1 > $MYU/cgroup.kill; break; fi
  done
  wait $BP
  if [ -n "$MYU" ]; then
    b=$(tail -n +$((G0+1)) $GL 2>/dev/null | grep "PREEMPT build .*unit $(basename $MYU) killed" | tail -1 | awk '{print $5}')
    if [ -n "$b" ] && [ -f $OUT/preempt/$b.build ]; then
      mv $OUT/preempt/$b.build $R/$T.side-preempt-as-$b-$(date +%Y%m%d%H%M%S).txt
      log "129b: 69c preempted the side build of $T (unit $(basename $MYU)); marker preempt/$b.build moved to runs/"; WHY="69c preempt"
    fi
  fi
  if grep -q 'SANDBOX EXIT CODE: 0' $R/$T.side-build-$n.log && [ -z "$WHY" ]; then
    log "129b: $T side build attempt $n done ($(sed -n 's/^PREBUILD_SECONDS: //p' $R/$T.side-build-$n.log) s)"
  else
    log "129b: $T side build attempt $n not finished (${WHY:-exit $(sed -n 's/^SANDBOX EXIT CODE: //p' $R/$T.side-build-$n.log)})"
    [ "$WHY" = "114f started its own build of $T" ] && { keep_del $T; log "129b: keep lines removed; exit"; exit 0; }
    sleep $IDLE
  fi
done
# built (or attempts used): wait for 114f to reach the config, then remove the keep lines
while ! reached $T; do
  if { stopped || ! pgrep -f "$PG" > /dev/null; } && ended; then keep_del $T; log "129b: stop or $PG gone for ${GRACE:-300} s; keep lines removed; exit"; exit 0; fi
  sleep $IDLE
done
keep_del $T; log "129b: $T reached by 114f; keep lines removed; exit"
