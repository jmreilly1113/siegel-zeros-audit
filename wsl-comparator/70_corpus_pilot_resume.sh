#!/usr/bin/env bash
# Corpus pilot, resumed after the 2026-10-11 interruption: QuasiRiemannHypothesis, then EditApproximation.
# Memory: each solution module is first built with Lake limited to LEAN_NUM_THREADS=4, inside the same network-blocking
# systemd-run wrapper as the comparator (not inside landrun); then the official comparator runs as before
# (67_corpus_run.sh) and finds the solution already built. Started detached (setsid nohup) so it does not depend on
# the Windows-side process that launched it.
set -u
W=/mnt/c/Users/Work/dev/siegel/wsl-comparator
OUT=/mnt/c/Users/Work/dev/siegel/results/2026-10-11-corpus-pilot
L=/home/checker/math/lean; C=/home/checker/corpus/configs
rm -f /home/checker/corpus/GUARD_STOPPED
nohup bash $W/69_corpus_guard.sh 42 1500 >/dev/null 2>&1 &
GD=$!
UID_C=$(id -u checker)
prebuild() { # prebuild <name> <module> <timeout>
  {
  echo "== prebuild $1: lake build $2 with LEAN_NUM_THREADS=4  $(date '+%F %T')"
  T0=$(date +%s)
  sudo -u checker -H env XDG_RUNTIME_DIR=/run/user/$UID_C DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$UID_C/bus bash -lc "
  export PATH=\"\$HOME/.elan/bin:/usr/local/bin:\$PATH\"; cd $L
  systemd-run --property=\"RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET\" --user --wait --pipe --collect -E PATH=\"\$PATH\" -E LEAN_NUM_THREADS=4 --working-directory \"\$(pwd)\" -- timeout --signal=TERM --kill-after=60 $3 bash -c 'lake build $2'
  echo \"PREBUILD EXIT CODE: \$?\"" 2>&1 | grep -v 'has local changes' | grep -v '^✔ \['
  echo "PREBUILD_SECONDS: $(( $(date +%s) - T0 ))"; echo "disk used: $(df -BG --output=used / | tail -1 | tr -d ' ')"
  } 2>&1 | cat > $OUT/$1.prebuild.log
  grep -q "PREBUILD EXIT CODE: 0" $OUT/$1.prebuild.log
}
for spec in "QuasiRiemannHypothesis OAI.NumberTheory.DirichletL.Nonvanishing 43200" "EditApproximation OAI.Combinatorics.EditApproximation.Specification.RawBandMain 28800"; do
  set -- $spec
  [ -f /home/checker/corpus/GUARD_STOPPED ] && break
  if prebuild $1 $2 $3; then
    [ -f $OUT/$1-nanoda.log ] && mv $OUT/$1-nanoda.log $OUT/$1-nanoda.interrupted-1441.log
    bash $W/67_corpus_run.sh $1 $C/$1-nanoda.json $3 $OUT/$1-nanoda.log
  else
    echo "$1: prebuild did not finish with exit 0; comparator not run" >> $OUT/$1.prebuild.log
  fi
done
kill $GD 2>/dev/null
[ -f /home/checker/corpus/GUARD_STOPPED ] && echo "GUARD STOPPED $(date '+%F %T')" > $OUT/GUARD_STOPPED.txt || echo "PILOT DONE $(date '+%F %T')" > $OUT/DONE.txt
sync
