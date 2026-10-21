#!/usr/bin/env bash
# Extended replay, Phase 0.2 + Phase 1 test (Joe, 2026-10-21), on TalagrandDiscreteConvexity (referenced; fd4aeeb corpus run
# 2026-10-12 batch-01: ACCEPT_BOTH, 27 s), with the corpus config copy /home/checker/corpus/configs/<name>-nanoda.json:
#   0. prebuild (75_sbx.sh, as 93)
#   1. Phase 0.2: 107_run.sh probe (id, /proc/self/status, network-block self-test, then comparator) -- as the v1 rerun
#   2. 67_corpus_run.sh WITHOUT instrumentation
#   3. 67_corpus_run.sh WITH 111_memsample.py (peak memory + export capture)
#   4. reference export with lean4export exactly as 107_paperprep.sh task 3, to compare with the captured export
#   5. prune the build (112_prune.py, empty keep list)
# Run as root, detached. Usage: 116_phase1_test.sh <out dir>
set -u
OUT=$1; W=/mnt/c/Users/Work/dev/siegel/wsl-comparator; L=/home/checker/math/lean; X=/home/checker/corpus/xr
N=TalagrandDiscreteConvexity; CFG=/home/checker/corpus/configs/$N-nanoda.json
mkdir -p $OUT $X/exp; chown -R checker:checker $X
log() { echo "$(date '+%F %T') $*" >> $OUT/run.log; }
rm -f /home/checker/corpus/GUARD_STOPPED
nohup bash $W/69_corpus_guard.sh 85 1500 2 >/dev/null 2>&1 &
GD=$!
log "start 116_phase1_test.sh; config $CFG sha256 $(sha256sum $CFG | cut -c1-64); clone HEAD $(sudo -u checker git -C /home/checker/math rev-parse HEAD) status [$(sudo -u checker git -C /home/checker/math status --short | tr '\n' ' ')]; kernel $(uname -r)"
TG=$(python3 -I -c "import json,sys; c=json.load(open(sys.argv[1])); print(' '.join([c['solution_module'], c['challenge_module']] + c.get('solution_imports', [])))" $CFG)
printf 'build_kb_before\t%s\n' "$(du -sk $L/.lake/build 2>/dev/null | cut -f1)" > $OUT/$N.disk.tsv
{ echo "== prebuild: lake build $TG with LEAN_NUM_THREADS=4  $(date '+%F %T')"; T0=$(date +%s)
  bash $W/75_sbx.sh 14400 4 "lake build $TG" </dev/null
  echo "PREBUILD_SECONDS: $(( $(date +%s) - T0 ))"; echo "disk used: $(df -BG --output=used / | tail -1 | tr -d ' ')"; } 2>&1 | cat > $OUT/$N.prebuild.log
printf 'build_kb_after_prebuild\t%s\n' "$(du -sk $L/.lake/build | cut -f1)" >> $OUT/$N.disk.tsv
log "prebuild: $(grep -h 'SANDBOX EXIT CODE\|PREBUILD_SECONDS' $OUT/$N.prebuild.log | tr '\n' ' ')"
bash $W/107_run.sh $N-probe probe $CFG 7200 $OUT/phase0-probe-$N.log
log "probe: $(grep -h -E '^INNER (id|kernel|netblock)|Your solution|COMPARATOR EXIT CODE|DURATION' $OUT/phase0-probe-$N.log | tr '\n' ';' | cut -c1-500)"
bash $W/67_corpus_run.sh $N $CFG 7200 $OUT/$N-plain.log </dev/null
log "plain: $(grep -h -E 'kernel accepts|Your solution|COMPARATOR EXIT CODE|DURATION' $OUT/$N-plain.log | tr '\n' ';')"
python3 -I $W/111_memsample.py $CFG $OUT/$N-instr.mem.json $X/exp/$N.export & SP=$!
bash $W/67_corpus_run.sh $N $CFG 7200 $OUT/$N-instr.log </dev/null
wait $SP
log "instrumented: $(grep -h -E 'kernel accepts|Your solution|COMPARATOR EXIT CODE|DURATION' $OUT/$N-instr.log | tr '\n' ';'); mem $(python3 -I -c "import json,sys; j=json.load(open(sys.argv[1])); print({k: j.get(k) for k in ('samples','peak_rss_sum_kb','peak_hwm_kb','peak_hwm_proc')}, (j.get('export') or {}).get('export_sha256'))" $OUT/$N-instr.mem.json)"
T=$(python3 -I - $CFG <<'EOF'
import json, sys
c = json.load(open(sys.argv[1]))
quot = ['Quot', 'Quot.mk', 'Quot.lift', 'Quot.ind'] if 'Quot.sound' in c['permitted_axioms'] else []
prim = ['Nat.add', 'Nat.sub', 'Nat.mul', 'Nat.pow', 'Nat.gcd', 'Nat.div', 'Nat.mod', 'Nat.beq', 'Nat.ble', 'Nat.land', 'Nat.lor',
        'Nat.xor', 'Nat.shiftLeft', 'Nat.shiftRight', 'String.ofList', 'Char.ofNat', 'List', 'eagerReduce', 'Nat', 'String',
        'String.mk', 'Char', 'optParam', 'autoParam', 'semiOutParam', 'outParam']
print(c['solution_module'], '--', *(quot + c['theorem_names'] + c['permitted_axioms'] + prim + c.get('definition_names', [])))
EOF
)
E=$X/exp/$N.ref-export
{ echo "== reference export (107_paperprep.sh task 3 method): lake env lean4export $T > $E  $(date '+%F %T')"
  bash $W/75_sbx.sh 1800 4 "lake env lean4export $T > $E" </dev/null; ls -l $E; sha256sum $E; } > $OUT/$N.ref-export.log 2>&1
log "reference export: $(grep -h -E 'SANDBOX EXIT CODE' $OUT/$N.ref-export.log) sha256 $(sha256sum $E | cut -c1-64) bytes $(stat -c %s $E)"
rm -f $E $X/exp/$N.export $X/exp/$N.export.nanoda-config.json
: > $OUT/empty-keep.txt
python3 -I $W/112_prune.py $L $OUT/empty-keep.txt --apply > $OUT/$N.prune.log 2>&1
log "pruned: $(cat $OUT/$N.prune.log); build now $(du -sk $L/.lake/build | cut -f1) KB"
kill $GD 2>/dev/null
echo "PHASE1 TEST DONE $(date '+%F %T')" > $OUT/DONE.txt
sync
