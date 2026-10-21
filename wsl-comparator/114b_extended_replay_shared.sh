#!/usr/bin/env bash
# Extended replay (Joe, 2026-10-21): the 227 configs at fd4aeeb that formalization.yaml does not reference, under the
# pipeline used for the 189 (93_remainder_serial_v4.sh): prebuild with 75_sbx.sh (LEAN_NUM_THREADS=4, 14400 s), then
# 67_corpus_run.sh on the enable_nanoda copy (7200 s), then 67_corpus_run.sh on the shipped config if the nanoda run is
# not ACCEPT_BOTH. Guard 69_corpus_guard.sh 85 1500 2 as before. 67_corpus_run.sh and 75_sbx.sh are used unchanged.
# Added (outside the sandbox; no unit property changed): 111_memsample.py per comparator run (peak memory, export capture),
# du of lean/.lake/build before and after the prebuild, #print axioms and challenge-placeholder audit queries (75_sbx.sh,
# 3600 s), a 4x rerun of any TIMEOUT, 113_nanoda_direct.sh (nanoda f67473b, default stack) on the retained export of a
# nanoda crash, and a per-config prune (112_prune.py) of every ACCEPT_BOTH build. Resumable: a config with
# <runs>/<config>.result.json is skipped; partial logs of an interrupted config are moved aside, never overwritten.
# Stops on <runs>/STOP.txt (conditions a, b, d), the guard marker, or C: free < 22 GB.
# Run as root, detached:  setsid nohup bash 114_extended_replay.sh <plan tsv> <out dir> [max configs] > ... 2>&1 &
#
# 114b (Joe, 2026-10-21, to cut the run from ~5 days to 2-3): identical to 114 except the prune policy. Builds are NOT
# pruned after each config; after a config, if WSL disk used > PRUNE_AT (55 G), 112_prune.py deletes every OAI build
# output outside the keep list (as the 189's batch-end prunes did). Later configs therefore reuse shared modules, and
# build_disk_kb (du after - du before) is the config's INCREMENTAL footprint; the total build size after the prebuild is
# also recorded (build_kb_after_prebuild). Use with a plan ordered by solution module (phase3-order.tsv) so configs of
# one project run consecutively. Sandbox, timeouts, threads, checks and outputs are unchanged.
set -u
PLAN=$1; OUT=$2; MAX=${3:-100000}; PRUNE_AT=${PRUNE_AT:-55}
W=/mnt/c/Users/Work/dev/siegel/wsl-comparator; QD=/mnt/c/Users/Work/dev/siegel/lean-checks/extended-replay
L=/home/checker/math/lean; X=/home/checker/corpus/xr; R=$OUT/runs
NB_POST=/opt/nanoda-postfix/nanoda_bin
mkdir -p $R $X/configs $X/exp; chown -R checker:checker $X
log() { echo "$(date '+%F %T') $*" >> $OUT/run.log; }
stopped() { [ -f /home/checker/corpus/GUARD_STOPPED ] || [ -f $R/STOP.txt ]; }
cfree() { df -BG --output=avail /mnt/c | tail -1 | tr -dc 0-9; }
rm -f /home/checker/corpus/GUARD_STOPPED
nohup bash $W/69_corpus_guard.sh 85 1500 2 >/dev/null 2>&1 &
GD=$!
log "start 114b_extended_replay_shared.sh (prune at WSL used > ${PRUNE_AT}G) plan $(basename $PLAN) max $MAX; clone HEAD $(sudo -u checker git -C /home/checker/math rev-parse HEAD) status [$(sudo -u checker git -C /home/checker/math status --short | tr '\n' ' ')]; kernel $(uname -r); WSL disk used $(df -BG --output=used / | tail -1 | tr -d ' '); C: free $(cfree)G; guard 69_corpus_guard.sh 85 1500 2"
prebuild() { # prebuild <log> <targets> <timeout>  (as 93_remainder_serial_v4.sh)
  { echo "== prebuild: lake build $2 with LEAN_NUM_THREADS=4 (114, as 93)  $(date '+%F %T')"; T0=$(date +%s)
    bash $W/75_sbx.sh $3 4 "lake build $2" </dev/null
    echo "PREBUILD_SECONDS: $(( $(date +%s) - T0 ))"; echo "disk used: $(df -BG --output=used / | tail -1 | tr -d ' ')"
  } 2>&1 | cat > $1
}
crun() { # crun <name> <config> <timeout> <log> <mem json> [export copy]: sampler + 67_corpus_run.sh
  python3 -I $W/111_memsample.py $2 $5 ${6:-} & local SP=$!
  bash $W/67_corpus_run.sh $1 $2 $3 $4 </dev/null
  wait $SP
}
live() { ls $R/$1.* $R/$1-* 2>/dev/null | grep -v '\.stopped-'; }
aside() { local ts; ts=$(date +%Y%m%d%H%M%S); for f in $(live $1); do mv "$f" "${f%.*}.stopped-$ts.${f##*.}"; done; }
bkb() { du -sk $L/.lake/build 2>/dev/null | cut -f1; }
i=0
while IFS=$'\t' read -r -u 9 ORD N G PIL SHIP LINES NTH EXTRA FLAG; do
  [ "$ORD" = order ] && continue
  case "$ORD" in \#*) continue ;; esac
  [ $i -ge $MAX ] && break
  stopped && break
  [ -f $R/$N.result.json ] && { i=$((i+1)); continue; }
  f=$(cfree); if [ -n "$f" ] && [ "$f" -lt 22 ]; then echo "(d) C: free ${f} GB < 22 GB before $N  $(date '+%F %T')" >> $R/STOP.txt; log "STOP (d): C: free ${f}G"; break; fi
  [ -n "$(live $N)" ] && { log "$N: partial files from an interrupted attempt moved aside"; aside $N; }
  i=$((i+1))
  CFG=$X/configs/$N-nanoda.json
  python3 -I -c "import json,sys; c=json.load(open(sys.argv[1])); c['enable_nanoda']=True; json.dump(c, open(sys.argv[2],'w'), indent=2)" $L/ComparatorChallenges/$N.json $CFG
  chown checker:checker $CFG
  TG=$(python3 -I -c "import json,sys; c=json.load(open(sys.argv[1])); print(' '.join([c['solution_module'], c['challenge_module']] + c.get('solution_imports', [])))" $CFG)
  log "$N ($ORD, group $G, shipped nanoda $SHIP): prebuild"
  printf 'build_kb_before\t%s\n' "$(bkb)" > $R/$N.disk.tsv
  prebuild $R/$N.prebuild.log "$TG" 14400
  printf 'build_kb_after_prebuild\t%s\nwsl_disk_used_after_prebuild\t%s\nc_free_gb_after_prebuild\t%s\n' "$(bkb)" "$(df -BG --output=used / | tail -1 | tr -d ' ')" "$(cfree)" >> $R/$N.disk.tsv
  stopped && break
  if grep -q 'SANDBOX EXIT CODE: 12[4-9]\|SANDBOX EXIT CODE: 137' $R/$N.prebuild.log; then
    log "$N: prebuild TIMEOUT at 14400 s; rerun once at 57600 s"
    prebuild $R/$N.prebuild-4x.log "$TG" 57600
    printf 'build_kb_after_prebuild_4x\t%s\n' "$(bkb)" >> $R/$N.disk.tsv
    stopped && break
    PBOK=$(grep -c 'SANDBOX EXIT CODE: 0' $R/$N.prebuild-4x.log)
  else
    PBOK=$(grep -c 'SANDBOX EXIT CODE: 0' $R/$N.prebuild.log)
  fi
  if [ "$PBOK" -ge 1 ]; then
    log "$N: nanoda run"
    crun $N $CFG 7200 $R/$N-nanoda.log $R/$N-nanoda.mem.json $X/exp/$N.export
    stopped && break
    if grep -q 'COMPARATOR EXIT CODE: 12[4-9]\|COMPARATOR EXIT CODE: 137' $R/$N-nanoda.log; then
      log "$N: comparator TIMEOUT at 7200 s; rerun once at 28800 s"
      crun $N $CFG 28800 $R/$N-nanoda-4x.log $R/$N-nanoda-4x.mem.json $X/exp/$N.export
      stopped && break
    fi
    NL=$R/$N-nanoda.log; [ -f $R/$N-nanoda-4x.log ] && NL=$R/$N-nanoda-4x.log
    if ! { grep -q 'nanoda kernel accepts the solution' $NL && grep -q 'Lean default kernel accepts the solution' $NL && grep -q 'Your solution is okay!' $NL && grep -q 'COMPARATOR EXIT CODE: 0' $NL; }; then
      log "$N: shipped-config run (nanoda run not ACCEPT_BOTH)"
      crun $N $L/ComparatorChallenges/$N.json 7200 $R/$N-shipped.log $R/$N-shipped.mem.json
      stopped && break
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
    stopped && break
  fi
  python3 -I $W/115_classify.py $R $N $G $SHIP; rc=$?
  if [ $rc -eq 4 ]; then
    NC=$X/exp/$N.f67473b-config.json
    python3 -I -c "import json,sys; c=json.load(open(sys.argv[1])); c['export_file_path']=sys.argv[3]; json.dump(c, open(sys.argv[2],'w'), indent=1)" $X/exp/$N.export.nanoda-config.json $NC $X/exp/$N.export
    chown checker:checker $NC $X/exp/$N.export
    log "$N: nanoda crash; nanoda f67473b directly on the retained export (default stack)"
    python3 -I $W/111_memsample.py $NC $R/$N-f67473b-direct.mem.json & SP=$!
    bash $W/113_nanoda_direct.sh $N $NC $NB_POST 7200 $R/$N-f67473b-direct.log </dev/null
    wait $SP
    stopped && break
    python3 -I $W/115_classify.py $R $N $G $SHIP; rc=$?
  fi
  if [ $rc -eq 2 ]; then log "$N: not final (a run has no exit code line); stopping"; break; fi
  OC=$(python3 -I -c "import json,sys; print(json.load(open(sys.argv[1]))['outcome'])" $R/$N.result.json)
  EXS=$(python3 -I -c "import json,sys; e=json.load(open(sys.argv[1])).get('export') or {}; print(e.get('export_sha256'), e.get('export_bytes'))" $R/$N.result.json)
  log "$N: outcome $OC; export sha256/bytes $EXS"
  if [ $rc -eq 3 ]; then log "STOP: $(tail -1 $R/STOP.txt)"; echo "ComparatorChallenges/$N.json" >> $OUT/keep-configs.txt; break; fi
  if [ "$OC" = ACCEPT_BOTH ]; then
    rm -f $X/exp/$N.export $X/exp/$N.export.nanoda-config.json
  else
    echo "ComparatorChallenges/$N.json" >> $OUT/keep-configs.txt
    log "$N: build and export kept ($OC)"
  fi
  U=$(df -BG --output=used / | tail -1 | tr -dc 0-9)
  if [ "$U" -gt "$PRUNE_AT" ]; then
    python3 -I $W/112_prune.py $L $OUT/keep-configs.txt --apply > $R/$N.prune.log 2>&1
    log "threshold prune after $N (WSL used ${U}G > ${PRUNE_AT}G): $(head -1 $R/$N.prune.log); build now $(bkb) KB; WSL disk used $(df -BG --output=used / | tail -1 | tr -d ' ')"
  fi
done 9< $PLAN
kill $GD 2>/dev/null
log "end (processed $i of max $MAX); clone status [$(sudo -u checker git -C /home/checker/math status --short | tr '\n' ' ')]; WSL disk used $(df -BG --output=used / | tail -1 | tr -d ' '); C: free $(cfree)G"
if [ -f /home/checker/corpus/GUARD_STOPPED ]; then echo "GUARD STOPPED $(date '+%F %T')" > $OUT/GUARD_STOPPED.txt
elif [ -f $R/STOP.txt ]; then :
elif [ $i -ge $MAX ]; then echo "PART DONE ($i) $(date '+%F %T')" > $OUT/PART_DONE-$i.txt
else echo "EXTENDED REPLAY DONE $(date '+%F %T')" > $OUT/DONE.txt; fi
sync
