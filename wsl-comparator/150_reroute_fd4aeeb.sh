#!/usr/bin/env bash
# 2026-10-26/27 (Joe's step 2): the SiegelZeros control and the reroute at openai/math fd4aeeb, under the 45-family deny list,
# the guard, and the official nanoda 3a24072 (/usr/local/bin/nanoda_bin, used by comparator from PATH). One job at a time.
#   0. MemoryMax non-enforcement test (2d)
#   1. local clone /home/checker/math-r2 of the clean fd4aeeb clone (no network); lean/.lake/packages bind-mounted READ-ONLY from
#      /home/checker/math/lean/.lake/packages (same pinned, prebuilt packages; no extra disk; writes fail instead of touching the original)
#   2. control: prebuild (75r, 4 threads), official comparator with enable_nanoda true (67r, 16G cap), dependency scan (ReroutedDeps.lean)
#   3. reroute: comparator-copy files (sha256 must be 1ce196f5.../af401514...), the +2/-1 patch (numstat must be 1 2 1),
#      prebuild, comparator, dependency scan
# STOP (exit 1, logged) on: existing clone, hash mismatch, diff check, build failure, or a scan block that differs from 10-09.
# The bind mount is always undone (trap). PRECHECK=1: steps 1 + read-only check + unmount, then exit.
# Usage (root): 150_reroute_fd4aeeb.sh <out dir>
set -u
O=$1; W=/mnt/c/Users/Work/dev/siegel/wsl-comparator; REPO=/mnt/c/Users/Work/dev/siegel
F=fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb; R=/home/checker/math-r2; RL=$R/lean; SRCPK=/home/checker/math/lean/.lake/packages
T=/tmp/r2; mkdir -p $O $T; chmod 755 $T
log() { echo "$(date '+%F %T') $*" | tee -a $O/run.log; }
stop() { log "STOP: $*"; exit 1; }
cleanup() { mountpoint -q $RL/.lake/packages && { umount $RL/.lake/packages && log "bind mount removed"; }; }
trap cleanup EXIT
pgrep -f 69_corpus_guard.sh >/dev/null || { setsid nohup bash $W/69_corpus_guard.sh 95 1500 20 >/dev/null 2>&1 < /dev/null & sleep 2; log "guard started: 69_corpus_guard.sh 95 1500 20"; }
log "150 start (PRECHECK=${PRECHECK:-0}); disk $(df -BG --output=used / | tail -1 | tr -d ' '); guard $(pgrep -f 69_corpus_guard.sh | head -1)"

if [ "${PRECHECK:-0}" != 1 ] && [ ! -f $O/memorymax-test.out ]; then
  log "0. MemoryMax test"; bash $O/memorymax-test.sh > $O/memorymax-test.out 2>&1; log "0. done (memorymax-test.out)"
fi

# 1. clone
if [ ! -d $R ]; then
  sudo -u checker git clone -q /home/checker/math $R || stop "git clone failed"
  sudo -u checker git -C $R checkout -q $F || stop "checkout failed"
fi
H=$(sudo -u checker git -C $R rev-parse HEAD); S=$(sudo -u checker git -C $R status --short | wc -l)
[ "$H" = $F ] || stop "clone HEAD $H"
log "1. clone $R HEAD $H, tracked changes $S, origin $(sudo -u checker git -C $R remote get-url origin)"
for f in lean/lake-manifest.json lean/lean-toolchain lean/lakefile.toml lean/lakefile.lean; do [ -f /home/checker/math/$f ] && log "   $f: original $(sha256sum /home/checker/math/$f | cut -c1-16) clone $(sha256sum $R/$f | cut -c1-16)"; done
[ "$(sha256sum < /home/checker/math/lean/lake-manifest.json)" = "$(sha256sum < $RL/lake-manifest.json)" ] || stop "lake-manifest differs"
sudo -u checker mkdir -p $RL/.lake/packages
mountpoint -q $RL/.lake/packages || { mount --bind $SRCPK $RL/.lake/packages && mount -o remount,bind,ro $RL/.lake/packages || stop "bind mount failed"; }
log "   packages: $(findmnt -no SOURCE,TARGET,OPTIONS $RL/.lake/packages | tr -s ' ')"
sudo -u checker touch $RL/.lake/packages/.writetest 2>/dev/null && { rm -f $RL/.lake/packages/.writetest; stop "packages mount is writable"; }
log "   packages mount is read-only (write as checker refused)"
[ "${PRECHECK:-0}" = 1 ] && { log "PRECHECK done"; exit 0; }

prebuild() { # prebuild <label> : the solution and challenge modules at 4 threads, in the clone
  log "$1: prebuild start"; XR_L=$RL bash $W/75r_sbx.sh 14400 4 "lake build OAI.NumberTheory.SiegelZeros.Main ComparatorChallenges.SiegelZeros" > $O/$1-prebuild.log 2>&1
  grep -q 'SANDBOX EXIT CODE: 0' $O/$1-prebuild.log || stop "$1 prebuild failed (see $1-prebuild.log)"
  log "$1: prebuild done: $(grep -E 'Build completed|error' $O/$1-prebuild.log | tail -1); disk $(df -BG --output=used / | tail -1 | tr -d ' ')"; }
comparator() { # comparator <label>
  install -o checker -g checker -m 644 $W/SiegelZeros-nanoda.json $T/SiegelZeros-nanoda.json
  log "$1: comparator start (config $T/SiegelZeros-nanoda.json, sha256 $(sha256sum $T/SiegelZeros-nanoda.json | cut -c1-16); nanoda_bin $(sha256sum /usr/local/bin/nanoda_bin | cut -c1-16))"
  XR_L=$RL bash $W/67r_corpus_run_capped.sh $1-SiegelZeros $T/SiegelZeros-nanoda.json 7200 $O/$1-comparator.log 16G
  log "$1: comparator: $(grep -E 'nanoda kernel (accepts|rejected)|Lean default kernel (accepts|rejected)|Your solution is okay|COMPARATOR EXIT CODE|oom_kill [1-9]' $O/$1-comparator.log | tr '\n' ';')"; }
deps() { # deps <label> <10-09 section header substring>
  cp $REPO/lean-checks/ReroutedDeps.lean $T/ReroutedDeps.lean; chmod 644 $T/ReroutedDeps.lean
  log "$1: dependency scan (ReroutedDeps.lean sha256 $(sha256sum $T/ReroutedDeps.lean | cut -c1-16))"
  XR_L=$RL bash $W/75r_sbx.sh 3600 4 "lake env lean /tmp/r2/ReroutedDeps.lean" > $O/$1-deps.log 2>&1
  sed -n '/^OAI.SiegelZeros.WeightedTorusJets.dirichletRealZeroBound_proof:/,/^LEAN EXIT CODE\|^SANDBOX EXIT CODE/p' $O/$1-deps.log | grep -v -E '^(LEAN|SANDBOX) EXIT CODE|^Service runtime|^Finished|^Main proc' > $T/$1-new.txt
  awk -v h="$2" 'index($0,h){f=1;next} f&&/^== clone/{exit} f' $REPO/results/2026-10-09-lean-rerouted-comparator-deps.txt | grep -v '^LEAN EXIT CODE' > $T/$1-old.txt
  if diff $T/$1-old.txt $T/$1-new.txt > $T/$1-diff.txt; then log "$1: scan block identical to 10-09 ($(grep -c . $T/$1-new.txt) lines): $(grep -o '[0-9]* constants in closure' $T/$1-new.txt | tr '\n' ' ')"
  else cp $T/$1-diff.txt $O/$1-deps-diff-vs-20261009.txt; stop "$1 scan differs from 10-09 (diff in $1-deps-diff-vs-20261009.txt)"; fi; }

# 2. control
prebuild control; comparator control; deps control "== clone /home/checker/math (HEAD"

# 3. reroute: install + patch
SRC=$REPO/lean-checks/comparator-copy/PaperLemma3; D=$RL/OAI/NumberTheory/SiegelZeros/PaperLemma3
[ "$(sha256sum $SRC/Lemma3.lean | cut -c1-64)" = 1ce196f54fa98689bbea6bd74f2abdb110f5cbcca2eecddcca9316b8af465283 ] || stop "Lemma3.lean source sha256 mismatch"
[ "$(sha256sum $SRC/Bridge.lean | cut -c1-64)" = af401514808dde5bb913ce8e87cc5280b704a234ea324897d1a1ced1f218f250 ] || stop "Bridge.lean source sha256 mismatch"
[ -e $D ] && stop "$D already exists"
install -d -o checker -g checker $D; for f in Lemma3 Bridge; do install -o checker -g checker -m 644 $SRC/$f.lean $D/$f.lean; done
log "reroute: installed $(sha256sum $D/Lemma3.lean $D/Bridge.lean | sed "s#$R/##" | tr '\n' ';')"
[ "$(sha256sum $D/Lemma3.lean | cut -c1-64)" = 1ce196f54fa98689bbea6bd74f2abdb110f5cbcca2eecddcca9316b8af465283 ] && [ "$(sha256sum $D/Bridge.lean | cut -c1-64)" = af401514808dde5bb913ce8e87cc5280b704a234ea324897d1a1ced1f218f250 ] || stop "installed sha256 mismatch"
sed -n '/^diff --git/,$p' $REPO/results/2026-10-09-rerouted-comparator-diff.txt | sed '/^== /,$d' > $T/reroute.patch; chmod 644 $T/reroute.patch
sudo -u checker git -C $R apply $T/reroute.patch || stop "git apply failed"
N=$(sudo -u checker git -C $R diff --numstat | awk '{a+=$1; d+=$2; n++} END {print n" "a" "d}')
{ echo "== git status --short"; sudo -u checker git -C $R status --short; echo "== git diff --numstat"; sudo -u checker git -C $R diff --numstat; echo "== git diff"; sudo -u checker git -C $R diff; echo "== new files sha256"; sha256sum $D/*.lean | sed "s#$R/##"; echo "== patched file sha256"; sha256sum $RL/OAI/NumberTheory/SiegelZeros/Characters/CharacterGlobalGreedyDeterminantMasterBounds.lean | sed "s#$R/##"; } > $O/reroute-diff.txt
[ "$N" = "1 2 1" ] || stop "diff check: $N (expected 1 2 1)"
log "reroute: patch applied; numstat 1 file +2/-1 (reroute-diff.txt); challenge file sha256 $(sha256sum $RL/ComparatorChallenges/SiegelZeros.lean | cut -c1-16)"
prebuild reroute; comparator reroute; deps reroute "== clone /home/checker/math-rerouted (HEAD"
log "150 done; disk $(df -BG --output=used / | tail -1 | tr -d ' ')"
