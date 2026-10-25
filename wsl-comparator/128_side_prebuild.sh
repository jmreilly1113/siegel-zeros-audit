#!/usr/bin/env bash
# 128 (2026-10-25): side prebuilds a few configs ahead of the running 114f, so its later prebuild of them is a no-op.
# Why: the pass is build-bound (one 114f build at a time, lookahead 1) while the build's dependency chains leave about
# half of the 12 CPUs idle (DirectedFeedback: 225 modules in 2,525 s at load ~7).
# Usage: 128_side_prebuild.sh <plan> <out dir> [threads 3]. Run as root, beside 114f; 114f is not touched.
# Each round: C = 114f's active build (else its active run). Candidates are the AHEAD configs after C in plan order
# with no result, not deferred, not in the slow lane. The target T is the first candidate after C's successor whose
# unbuilt closure (128_closure.py) is non-empty and disjoint from the unbuilt closures of C and every config between
# C and T, so 114f's builds and this one never compile the same module. T is added to keep-configs.txt (boundary prunes
# keep its closure) and built through 75_sbx.sh like 114f's prebuild (14400 s timeout). This build's systemd unit is
# killed and T left to 114f if A = MemAvailable + SwapFree drops below LOW_MB (so 69c, soft 4500 MB, rarely needs to
# act), if 114f's active build becomes T, or on a stop. If 69c preempts this unit (its guard.log PREEMPT line names
# the unit), the preempt/<name>.build marker it wrote under 114f's build name is moved to runs/, so 114f does not
# take it as its own. T's keep lines are removed once 114f has reached T (active build/run, or result), or at once
# if the side build did not finish. Each config is tried once.
# Logs: run.log ("128: ..."), runs/<T>.side-prebuild.log.
# Test hooks: XR_W, XR_L, XR_C, XR_MI, XR_APP (unit dir), XR_ST (poll s, default 5), XR_IDLE (idle wait s, default 60),
# XR_PG (114f name).
PLAN=$1; OUT=$2; THR=${3:-3}
AHEAD=${AHEAD:-6}; MIN_MB=${SIDE_MIN_MB:-12000}; LOW_MB=${LOW_MB:-6000}; ST=${XR_ST:-5}; IDLE=${XR_IDLE:-60}
W=${XR_W:-/mnt/c/Users/Work/dev/siegel/wsl-comparator}; L=${XR_L:-/home/checker/math/lean}; C=${XR_C:-/home/checker/corpus}
APP=${XR_APP:-/sys/fs/cgroup/unified/user.slice/user-1000.slice/user@1000.service/app.slice}
PG=${XR_PG:-114f_extended_replay_reruns_last.sh}; R=$OUT/runs; KEEP=$OUT/keep-configs.txt; GL=$C/guard.log; X=$C/xr
log() { echo "$(date '+%F %T') $*" >> $OUT/run.log; }
stopped() { [ -f $C/GUARD_STOPPED ] || [ -f $R/STOP.txt ] || [ -f $OUT/HALT.txt ]; }
memA() { awk '/^MemAvailable:|^SwapFree:/ {s+=$2} END {print int(s/1024)}' ${XR_MI:-/proc/meminfo}; }
cur() { local b; b=$(cat $OUT/active-build.txt 2>/dev/null); [ -n "$b" ] && echo "$b" || cat $OUT/active-run.txt 2>/dev/null; }
reached() { [ "$(cat $OUT/active-build.txt 2>/dev/null)" = "$1" ] || [ "$(cat $OUT/active-run.txt 2>/dev/null)" = "$1" ] || [ -f $R/$1.result.json ]; }
keep_del() { local t=$X/keep128.tmp; grep -vx "ComparatorChallenges/$1.json" $KEEP | grep -vx "# 128 side prebuild: $1" > $t; cat $t > $KEEP; rm -f $t; }
find_unit() { # find_unit <lake targets>: the unit dir whose `timeout` root runs exactly this lake build
  local d p; for d in $APP/run-*.service; do for p in $(cat $d/cgroup.procs 2>/dev/null); do
    tr '\0' ' ' < /proc/$p/cmdline 2>/dev/null | grep -q "^[^ ]*timeout .*bash -c lake build $1 *$" && { echo $d; return 0; }
  done; done; return 1; }
reap_keeps() { local t k=(); for t in "${KEPT[@]}"; do if reached $t; then keep_del $t; log "128: $t reached by 114f; keep lines removed"; else k+=("$t"); fi; done; KEPT=("${k[@]}"); }
mkdir -p $X
mapfile -t ORD < <(awk -F'\t' '$1 !~ /^#/ && $1 != "order" {print $2}' $PLAN)
declare -A TRIED; KEPT=()
log "128: start (threads $THR, ahead $AHEAD, start at A >= $MIN_MB MB, give up below $LOW_MB MB)"
while :; do
  reap_keeps
  stopped && { for t in "${KEPT[@]}"; do keep_del $t; done; log "128: stop in force; keep lines removed; exit"; exit 0; }
  pgrep -f "$PG" > /dev/null || { for t in "${KEPT[@]}"; do keep_del $t; done; log "128: $PG not running; keep lines removed; exit"; exit 0; }
  CU=$(cur); [ -n "$CU" ] || { sleep $IDLE; continue; }
  i=-1; for k in "${!ORD[@]}"; do [ "${ORD[$k]}" = "$CU" ] && { i=$k; break; }; done
  [ $i -ge 0 ] || { sleep $IDLE; continue; }
  CAND=("$CU")
  for ((k=i+1; k<${#ORD[@]} && ${#CAND[@]}<=AHEAD; k++)); do
    n=${ORD[$k]}
    [ -f $R/$n.result.json ] && continue
    grep -qx "$n" $OUT/deferred.txt 2>/dev/null && continue
    grep -qx "$n" $OUT/active-slow.txt 2>/dev/null && continue
    CAND+=("$n")
  done
  T=$(python3 -I $W/128_closure.py $L "${CAND[@]}" | awk -v tried=" ${!TRIED[*]} " '
    { n[NR]=$1; c[NR]=$2; for (j=3; j<=NF; j++) m[NR, $j]=1; line[NR]=$0 }
    END { for (t=3; t<=NR; t++) { if (c[t]==0 || index(tried, " " n[t] " ")) continue; k=split(line[t], a, " "); ok=1
            for (s=1; s<t && ok; s++) for (j=3; j<=k; j++) if ((s, a[j]) in m) { ok=0; break }
            if (ok) { print n[t]; exit } } }')
  if [ -z "$T" ] || [ "$(memA)" -lt $MIN_MB ]; then sleep $IDLE; continue; fi
  TRIED[$T]=1
  TG=$(python3 -I -c "import json,sys; c=json.load(open(sys.argv[1])); print(' '.join([c['solution_module'], c['challenge_module']] + c.get('solution_imports', [])))" $L/ComparatorChallenges/$T.json)
  printf '# 128 side prebuild: %s\nComparatorChallenges/%s.json\n' $T $T >> $KEEP; KEPT+=("$T")
  G0=$(wc -l < $GL 2>/dev/null || echo 0)
  log "128: side prebuild of $T ($THR threads; 114f at $CU; A $(memA) MB); kept in keep-configs.txt until 114f reaches it"
  { echo "== side prebuild (128): lake build $TG with LEAN_NUM_THREADS=$THR  $(date '+%F %T')"; T0=$(date +%s)
    bash $W/75_sbx.sh 14400 $THR "lake build $TG" </dev/null
    echo "PREBUILD_SECONDS: $(( $(date +%s) - T0 ))"; } > $R/$T.side-prebuild.log 2>&1 &
  BP=$!; WHY=; MYU=
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
      log "128: 69c preempted the side build of $T (unit $(basename $MYU)); marker preempt/$b.build moved to runs/"; WHY="69c preempt"
    fi
  fi
  if grep -q 'SANDBOX EXIT CODE: 0' $R/$T.side-prebuild.log && [ -z "$WHY" ]; then
    log "128: $T side prebuild done ($(sed -n 's/^PREBUILD_SECONDS: //p' $R/$T.side-prebuild.log) s)"
  else
    log "128: $T side prebuild not finished (${WHY:-exit $(sed -n 's/^SANDBOX EXIT CODE: //p' $R/$T.side-prebuild.log)}); left to 114f"
    keep_del $T; k=(); for t in "${KEPT[@]}"; do [ "$t" = "$T" ] || k+=("$t"); done; KEPT=("${k[@]}")
  fi
done
