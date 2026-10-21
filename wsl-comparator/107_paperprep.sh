#!/usr/bin/env bash
# Paper prep (Joe, 2026-10-20). Read-only on openai/math: the clone at /home/checker/math (fd4aeeb) is not edited;
# the one control file is a NEW untracked file, removed afterwards (same method as the pilot's control (b)).
# Builds were pruned 2026-10-20, so each closure is rebuilt first (lake build, as checker, in the sandbox).
#   Task 2  b,c : HarmonicGrowth and NavierStokesVelocity: #print axioms (new files lean-checks/paper-prep/) and the
#                 closure queries of 2026-10-12 (lean-checks/corpus-queries/), rerun unchanged.
#   Task 2  d   : HarmonicGrowth negative control: solution = copy of the challenge whose proof is `by exact mainStatement`.
#   Task 4      : SiegelZeros rerun (POST-HOC) logging id, capabilities and the network-block self-test in the same unit.
#   Task 3      : the 9 non-ACCEPT_BOTH configs: comparator with ulimit -s unlimited + RUST_MIN_STACK=1 GiB, timeout
#                 4 x 7200 s; and nanoda 3a24072 directly on the comparator-identical export with the same settings,
#                 timeout 4 x 3600 s. STOP if a nanoda run ends in a rejection that is not a crash.
# Run as root, detached:  setsid nohup bash 107_paperprep.sh > /home/checker/corpus/paperprep.out 2>&1 &
set -u
W=/mnt/c/Users/Work/dev/siegel/wsl-comparator
P=/mnt/c/Users/Work/dev/siegel/lean-checks/paper-prep
Q=/mnt/c/Users/Work/dev/siegel/lean-checks/corpus-queries
OUT=/mnt/c/Users/Work/dev/siegel/results/2026-10-20-paper-prep/wsl
L=/home/checker/math/lean; C=/home/checker/corpus/configs; X=/home/checker/corpus/pp; NB=/usr/local/bin/nanoda_bin
mkdir -p $OUT $X; chown checker:checker $X
log() { echo "$(date '+%F %T') $*" >> $OUT/run.log; }
stopped() { [ -f /home/checker/corpus/GUARD_STOPPED ] || [ -f $OUT/STOP.txt ]; }
rm -f /home/checker/corpus/GUARD_STOPPED
nohup bash $W/69_corpus_guard.sh 85 1500 2 >/dev/null 2>&1 &
GD=$!
UID_C=$(id -u checker)
sbx() { # sbx <timeout> '<command>' [extra env]: as checker, in the corpus sandbox, in $L (as 75_sbx.sh / 104)
  sudo -u checker -H env XDG_RUNTIME_DIR=/run/user/$UID_C DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$UID_C/bus bash -lc "
export PATH=\"\$HOME/.elan/bin:/usr/local/bin:\$PATH\"; cd $L
systemd-run --property=\"RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET\" --user --wait --pipe --collect -E PATH=\"\$PATH\" -E LEAN_NUM_THREADS=4 -E LEAN_ABORT_ON_PANIC=1 --working-directory \"\$(pwd)\" -- timeout --signal=TERM --kill-after=60 $1 bash -c '$2'
echo \"SANDBOX EXIT CODE: \$?\"" 2>&1 | grep -v 'has local changes' | grep -v '^✔ \['
}
prebuild() { # prebuild <name> <config json>
  local TG; TG=$(python3 -I -c "import json,sys; c=json.load(open(sys.argv[1])); print(' '.join([c['solution_module'], c['challenge_module']] + c.get('solution_imports', [])))" $2)
  { echo "== prebuild $1: lake build $TG  $(date '+%F %T')"; local t0=$(date +%s)
    sbx 14400 "lake build $TG" </dev/null
    echo "PREBUILD_SECONDS: $(( $(date +%s) - t0 ))"; echo "disk used: $(df -BG --output=used / | tail -1 | tr -d ' ')"; } > $OUT/$1.prebuild.log 2>&1
  log "$1: prebuild $(grep -h 'SANDBOX EXIT CODE' $OUT/$1.prebuild.log | tail -1) $(grep -h PREBUILD_SECONDS $OUT/$1.prebuild.log)"
}
clean_clone() { echo "$(sudo -u checker git -C /home/checker/math status --short | tr '\n' ' ')"; }
log "start 107_paperprep.sh; clone HEAD $(sudo -u checker git -C /home/checker/math rev-parse HEAD) status [$(clean_clone)]; kernel $(uname -r); nanoda_bin sha256 $(sha256sum $NB | cut -c1-64); comparator $(git -C /root/tools/comparator rev-parse HEAD); disk $(df -BG --output=used / | tail -1 | tr -d ' ')"

# ---------- Task 2 b,c
for N in HarmonicGrowth NavierStokesVelocity; do stopped || prebuild $N $L/ComparatorChallenges/$N.json; done
for q in $P/HGChallengePrintAxioms $P/HGSolutionPrintAxioms $P/NSChallengePrintAxioms $P/NSSolutionPrintAxioms \
         $Q/HarmonicGrowthChallenge $Q/HarmonicGrowthSolution $Q/NavierStokesChallenge $Q/NavierStokesSolution; do
  stopped && break
  b=$(basename $q)
  { echo "== query $b  $(date '+%F %T')"; echo "file: $q.lean sha256 $(sha256sum $q.lean | cut -c1-64)"
    sbx 3600 "lake env lean $q.lean" </dev/null; } > $OUT/task2-query-$b.log 2>&1
  log "task2 query $b: $(grep -h 'SANDBOX EXIT CODE' $OUT/task2-query-$b.log)"
done

# ---------- Task 2 d: negative control
if ! stopped; then
  A=$L/ComparatorChallenges/HarmonicGrowthNegControl.lean
  python3 -I - $L/ComparatorChallenges/HarmonicGrowth.lean $A <<'EOF'
import sys
src = open(sys.argv[1], encoding='utf-8').read()
old = 'theorem main : MainClaim := mainStatement'
assert src.count(old) == 1
open(sys.argv[2], 'w', encoding='utf-8').write(src.replace(old, 'theorem main : MainClaim := by\n  exact mainStatement'))
EOF
  chown checker:checker $A
  { echo "== negative-control solution: diff ComparatorChallenges/HarmonicGrowth.lean $A"; diff $L/ComparatorChallenges/HarmonicGrowth.lean $A
    echo "sha256 $(sha256sum $A | cut -c1-64)"; } > $OUT/task2d-control-diff.txt
  for V in shipped nanoda; do
    CF=$X/HarmonicGrowth-negcontrol-$V.json
    python3 -I -c "import json,sys; c=json.load(open(sys.argv[1])); c['solution_module']='ComparatorChallenges.HarmonicGrowthNegControl'; c['enable_nanoda']=(sys.argv[3]=='nanoda'); json.dump(c, open(sys.argv[2],'w'), indent=2)" $L/ComparatorChallenges/HarmonicGrowth.json $CF $V
    chown checker:checker $CF
    stopped && break
    bash $W/107_run.sh HarmonicGrowth-negcontrol-$V plain $CF 7200 $OUT/task2d-negcontrol-$V.log
    log "task2d negcontrol $V: $(grep -h -E 'Illegal axiom|Your solution is okay|kernel (accepts|rejected)|COMPARATOR EXIT CODE' $OUT/task2d-negcontrol-$V.log | tr '\n' ';' | cut -c1-300)"
  done
  rm -f $A; rm -f $L/.lake/build/lib/lean/ComparatorChallenges/HarmonicGrowthNegControl.* $L/.lake/build/ir/ComparatorChallenges/HarmonicGrowthNegControl.* 2>/dev/null
  echo "clone status after removing the control file: '$(clean_clone)'" >> $OUT/task2d-control-diff.txt
  log "task2d: control file removed; clone status [$(clean_clone)]"
fi

# ---------- Task 4: SiegelZeros post-hoc rerun with id + network self-test
if ! stopped; then
  prebuild SiegelZeros $L/ComparatorChallenges/SiegelZeros.json
  CF=$X/SiegelZeros-nanoda.json
  python3 -I -c "import json,sys; c=json.load(open(sys.argv[1])); c['enable_nanoda']=True; json.dump(c, open(sys.argv[2],'w'), indent=2)" $L/ComparatorChallenges/SiegelZeros.json $CF
  chown checker:checker $CF
  stopped || bash $W/107_run.sh SiegelZeros-posthoc probe $CF 7200 $OUT/task4-SiegelZeros-posthoc.log
  log "task4 SiegelZeros: $(grep -h -E '^INNER id|netblock|Your solution is okay|kernel (accepts|rejected)|COMPARATOR EXIT CODE' $OUT/task4-SiegelZeros-posthoc.log | tr '\n' ';' | cut -c1-400)"
fi

# ---------- Task 3: the 9 non-ACCEPT_BOTH configs
for N in OptimalMaxCut UniqueGamesTheorem VertexCover KaplanskyFinitelyPresented GroupRingDeterminant Laughlin BinPackingGap IndependentSets PerfectCompleteness; do
  stopped && break
  prebuild $N $L/ComparatorChallenges/$N.json
  grep -q 'SANDBOX EXIT CODE: 0' $OUT/$N.prebuild.log || { log "$N: prebuild failed; runs skipped"; continue; }
  stopped && break
  bash $W/107_run.sh $N-bigenv bigenv $C/$N-nanoda.json 28800 $OUT/task3-$N-comparator-bigenv.log
  log "task3 $N comparator bigenv: $(grep -h -E 'overflowed|kernel (accepts|rejected)|exited with|Your solution|COMPARATOR EXIT CODE|DURATION' $OUT/task3-$N-comparator-bigenv.log | tr '\n' ';' | cut -c1-300)"
  stopped && break
  # export exactly as comparator d03acab does (104_discrepancy.sh), then nanoda directly with the same settings
  T=$(python3 -I - $C/$N-nanoda.json <<'EOF'
import json, sys
c = json.load(open(sys.argv[1]))
quot = ['Quot', 'Quot.mk', 'Quot.lift', 'Quot.ind'] if 'Quot.sound' in c['permitted_axioms'] else []
prim = ['Nat.add', 'Nat.sub', 'Nat.mul', 'Nat.pow', 'Nat.gcd', 'Nat.div', 'Nat.mod', 'Nat.beq', 'Nat.ble', 'Nat.land', 'Nat.lor',
        'Nat.xor', 'Nat.shiftLeft', 'Nat.shiftRight', 'String.ofList', 'Char.ofNat', 'List', 'eagerReduce', 'Nat', 'String',
        'String.mk', 'Char', 'optParam', 'autoParam', 'semiOutParam', 'outParam']
print(c['solution_module'], '--', *(quot + c['theorem_names'] + c['permitted_axioms'] + prim + c.get('definition_names', [])))
EOF
)
  E=$X/$N.export
  { echo "== export $N  $(date '+%F %T')"; echo "command: lake env lean4export $T > $E"
    sbx 1800 "lake env lean4export $T > $E" </dev/null; ls -l $E; sha256sum $E; } > $OUT/task3-$N.export.log 2>&1
  if grep -q 'SANDBOX EXIT CODE: 0' $OUT/task3-$N.export.log; then
    PA=$(python3 -I -c "import json,sys; print(json.dumps(json.load(open(sys.argv[1]))['permitted_axioms']))" $C/$N-nanoda.json)
    NC=$X/$N.nanoda.json
    printf '{"use_stdin":false,"export_file_path":"%s","permitted_axioms":%s,"unpermitted_axiom_hard_error":true,"num_threads":4,"nat_extension":true,"string_extension":true}\n' $E "$PA" > $NC
    chown checker:checker $NC; cp $NC $OUT/task3-$N.nanoda-config.json
    bash $W/107_run.sh $N-nanoda-direct nanoda $NC 14400 $OUT/task3-$N-nanoda-direct.log $NB
    log "task3 $N nanoda direct: $(grep -h -E 'overflowed|panicked|Checked|error|COMPARATOR EXIT CODE|DURATION' $OUT/task3-$N-nanoda-direct.log | tr '\n' ';' | cut -c1-300)"
  else
    log "task3 $N: export failed; direct nanoda run skipped"
  fi
  rm -f $E
  # STOP rule: a nanoda run that ended non-zero without a crash signature is a possible genuine rejection
  for f in $OUT/task3-$N-comparator-bigenv.log $OUT/task3-$N-nanoda-direct.log; do
    [ -f $f ] || continue
    if grep -q -E 'nanoda kernel rejected|COMPARATOR EXIT CODE: [1-9]' $f && ! grep -q -E 'nanoda kernel accepts|overflowed its stack|fatal runtime error|exited with 13[4-9]|COMPARATOR EXIT CODE: 13[4-9]|COMPARATOR EXIT CODE: 12[4-9]' $f; then
      echo "STOP: possible genuine nanoda rejection in $f  $(date '+%F %T')" > $OUT/STOP.txt; log "STOP: $f"
    fi
  done
done

kill $GD 2>/dev/null
log "end; clone status [$(clean_clone)]; disk $(df -BG --output=used / | tail -1 | tr -d ' ')"
if [ -f /home/checker/corpus/GUARD_STOPPED ]; then echo "GUARD STOPPED $(date '+%F %T')" > $OUT/GUARD_STOPPED.txt
elif [ -f $OUT/STOP.txt ]; then :
else echo "PAPERPREP DONE $(date '+%F %T')" > $OUT/DONE.txt; fi
sync
