#!/usr/bin/env bash
# Paper prep 2, Task 3 (Joe, 2026-10-20): v1 provenance at adc7f12.
# (a) A separate clone /home/checker/math-v1 of the local fd4aeeb clone, checked out at adc7f12 (no network; the
#     fd4aeeb clone is not touched). Lake packages copied from the fd4aeeb clone (lake-manifest.json is byte-identical
#     at both commits, results/2026-10-20-paper-prep/task4-provenance-commands.txt).
# (b) lake build of the SiegelZeros closure there, then the SHIPPED SiegelZeros.json under the full network block,
#     with id, capabilities and the network self-test logged in the same unit (108_run.sh probe).
# (c) Repo files in the import closures of family 003's four configs at both commits, and
#     git diff --stat adc7f12 fd4aeeb over their union (plus lean/patches).
# Run as root, detached:  setsid nohup bash 108_paperprep2.sh > /home/checker/corpus/paperprep2.out 2>&1 &
set -u
W=/mnt/c/Users/Work/dev/siegel/wsl-comparator
OUT=/mnt/c/Users/Work/dev/siegel/results/2026-10-20-paper-prep-2/wsl
SRC=/home/checker/math; V1=/home/checker/math-v1; L=$V1/lean
ADC=adc7f1241b42e322a6451854ab7e4b4c146bf78a; FD=fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb
mkdir -p $OUT
log() { echo "$(date '+%F %T') $*" >> $OUT/run.log; }
stopped() { [ -f /home/checker/corpus/GUARD_STOPPED ]; }
rm -f /home/checker/corpus/GUARD_STOPPED
nohup bash $W/69_corpus_guard.sh 85 1500 2 >/dev/null 2>&1 &
GD=$!
UID_C=$(id -u checker)
sbx() { # sbx <lean dir> <timeout> '<command>'
  sudo -u checker -H env XDG_RUNTIME_DIR=/run/user/$UID_C DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$UID_C/bus bash -lc "
export PATH=\"\$HOME/.elan/bin:/usr/local/bin:\$PATH\"; cd $1
systemd-run --property=\"RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET\" --user --wait --pipe --collect -E PATH=\"\$PATH\" -E LEAN_NUM_THREADS=4 --working-directory \"\$(pwd)\" -- timeout --signal=TERM --kill-after=60 $2 bash -c '$3'
echo \"SANDBOX EXIT CODE: \$?\"" 2>&1 | grep -v 'has local changes' | grep -v '^✔ \['
}
log "start 108_paperprep2.sh; fd4aeeb clone HEAD $(sudo -u checker git -C $SRC rev-parse HEAD) status [$(sudo -u checker git -C $SRC status --short | tr '\n' ' ')]; disk $(df -BG --output=used / | tail -1 | tr -d ' ')"

# (a) the adc7f12 clone
if [ ! -d $V1 ]; then
  { echo "== git clone $SRC $V1 (local, no network)  $(date '+%F %T')"
    sudo -u checker git clone -q $SRC $V1 && sudo -u checker git -C $V1 checkout -q $ADC
    echo "HEAD: $(sudo -u checker git -C $V1 rev-parse HEAD); status: [$(sudo -u checker git -C $V1 status --short | tr '\n' ' ')]"
    echo "lake-manifest.json sha256: v1 $(sha256sum $L/lake-manifest.json | cut -c1-64)  fd4aeeb clone $(sha256sum $SRC/lean/lake-manifest.json | cut -c1-64)"
    echo "== copy lake packages: cp -a $SRC/lean/.lake/packages $L/.lake/"
    sudo -u checker mkdir -p $L/.lake && sudo -u checker cp -a $SRC/lean/.lake/packages $L/.lake/ && echo "copy exit $?"
    du -sh $L/.lake/packages; } > $OUT/task3-clone.log 2>&1
fi
log "v1 clone: $(grep -h 'HEAD:' $OUT/task3-clone.log)"
[ "$(sudo -u checker git -C $V1 rev-parse HEAD)" = "$ADC" ] || { log "STOP: v1 clone not at adc7f12"; echo STOP > $OUT/STOP.txt; kill $GD; exit 1; }

# (b) build and the shipped-config run with the full block
if ! stopped; then
  { echo "== prebuild SiegelZeros at adc7f12: lake build OAI.NumberTheory.SiegelZeros.Main ComparatorChallenges.SiegelZeros  $(date '+%F %T')"; t0=$(date +%s)
    sbx $L 14400 "lake build OAI.NumberTheory.SiegelZeros.Main ComparatorChallenges.SiegelZeros" </dev/null
    echo "PREBUILD_SECONDS: $(( $(date +%s) - t0 ))"; } > $OUT/task3-SiegelZeros-adc7f12.prebuild.log 2>&1
  log "prebuild: $(grep -h 'SANDBOX EXIT CODE' $OUT/task3-SiegelZeros-adc7f12.prebuild.log | tail -1) $(grep -h PREBUILD_SECONDS $OUT/task3-SiegelZeros-adc7f12.prebuild.log)"
fi
if ! stopped && grep -q 'SANDBOX EXIT CODE: 0' $OUT/task3-SiegelZeros-adc7f12.prebuild.log; then
  L_OVERRIDE=$L bash $W/108_run.sh SiegelZeros-adc7f12-shipped probe $L/ComparatorChallenges/SiegelZeros.json 7200 $OUT/task3-SiegelZeros-adc7f12-shipped.log
  log "shipped run: $(grep -h -E '^INNER id|netblock|kernel (accepts|rejected)|Your solution|COMPARATOR EXIT CODE' $OUT/task3-SiegelZeros-adc7f12-shipped.log | tr '\n' ';' | cut -c1-500)"
fi

# (c) closures and diff --stat
{ for R in $ADC $FD; do
    T=/home/checker/corpus/tree-${R:0:7}; rm -rf $T; mkdir -p $T
    sudo -u checker git -C $V1 archive $R lean | tar -x -C $T
    echo "== closure at ${R:0:7}"
    python3 -I $W/108_closure.py $T/lean $T/lean/ComparatorChallenges/DirichletSevenEighths.json $T/lean/ComparatorChallenges/HeckeSevenEighths.json $T/lean/ComparatorChallenges/QuasiRiemannHypothesis.json $T/lean/ComparatorChallenges/SiegelZeros.json > $OUT/task3-closure-${R:0:7}.txt
    grep '^CONFIG' $OUT/task3-closure-${R:0:7}.txt; echo "repo paths: $(grep -c '^PATH' $OUT/task3-closure-${R:0:7}.txt)"
    rm -rf $T
  done
  cat $OUT/task3-closure-*.txt | sed -n 's/^PATH //p' | sort -u > $OUT/task3-closure-union-paths.txt
  echo "union of repo paths: $(wc -l < $OUT/task3-closure-union-paths.txt)"
  echo "== git diff --stat $ADC $FD -- <union paths> lean/patches"
  sudo -u checker git -C $V1 diff --stat $ADC $FD -- $(cat $OUT/task3-closure-union-paths.txt) lean/patches
  echo "(diff --stat exit $?; empty output = no changes)"
  echo "== git diff --name-status, same paths"; sudo -u checker git -C $V1 diff --name-status $ADC $FD -- $(cat $OUT/task3-closure-union-paths.txt) lean/patches
} > $OUT/task3-closure-diffstat.txt 2>&1
log "closure diff: $(tail -3 $OUT/task3-closure-diffstat.txt | tr '\n' ';')"
kill $GD 2>/dev/null
log "end; v1 clone status [$(sudo -u checker git -C $V1 status --short | tr '\n' ' ')]; fd4aeeb clone status [$(sudo -u checker git -C $SRC status --short | tr '\n' ' ')]; disk $(df -BG --output=used / | tail -1 | tr -d ' ')"
if stopped; then echo "GUARD STOPPED $(date '+%F %T')" > $OUT/GUARD_STOPPED.txt; else echo "PAPERPREP2 DONE $(date '+%F %T')" > $OUT/DONE.txt; fi
sync
