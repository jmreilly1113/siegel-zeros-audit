#!/usr/bin/env bash
# DIAGNOSTIC (Joe 2026-10-20, step 2; does not change the official table). KaplanskyFinitelyPresented and
# GroupRingDeterminant: nanoda 3a24072 overflowed through comparator here, but nealmcb's export runs accepted them.
# (a) Export each solution exactly as comparator d03acab does (Main.lean compareIt/safeExport: lean4export <solution
#     module> -- builtinTargets ++ theorem_names ++ permitted_axioms ++ primitiveTargets ++ definition_names, with
#     LEAN_ABORT_ON_PANIC=1), as checker in the network-blocking sandbox, from the kept builds (no rebuild expected).
# (b) Run the OFFICIAL /usr/local/bin/nanoda_bin (3a24072) directly on each export, one variable at a time:
#     R1 comparator's config = nealmcb's stated config (num_threads 4, nat/string extensions true, hard error true);
#     R2 = R1 with num_threads 1. nat_extension is true in both his and comparator's config, so no nat_extension run.
# Same WSL guard as the corpus runs. A run without an exit line, or with a guard marker, is STOPPED.
# Run as root, detached. Usage: 104_discrepancy.sh <out dir>
set -u
OUT=$1; W=/mnt/c/Users/Work/dev/siegel/wsl-comparator; D=/home/checker/corpus/disc; L=/home/checker/math/lean
NB=/usr/local/bin/nanoda_bin; C=/home/checker/corpus/configs
mkdir -p $OUT $D; chown checker:checker $D
log() { echo "$(date '+%F %T') $*" >> $OUT/run.log; }
stopped() { [ -f /home/checker/corpus/GUARD_STOPPED ]; }
rm -f /home/checker/corpus/GUARD_STOPPED
nohup bash $W/69_corpus_guard.sh 85 1500 2 >/dev/null 2>&1 &
GD=$!
UID_C=$(id -u checker)
sbx() { # sbx <timeout> '<command>' : as checker, in the corpus sandbox, in $L
  sudo -u checker -H env XDG_RUNTIME_DIR=/run/user/$UID_C DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$UID_C/bus bash -lc "
export PATH=\"\$HOME/.elan/bin:/usr/local/bin:\$PATH\"; cd $L
systemd-run --property=\"RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET\" --user --wait --pipe --collect -E PATH=\"\$PATH\" -E LEAN_ABORT_ON_PANIC=1 --working-directory \"\$(pwd)\" -- timeout --signal=TERM --kill-after=60 $1 bash -c '$2'
echo \"EXIT CODE: \$?\""
}
log "start 104_discrepancy.sh (DIAGNOSTIC); clone HEAD $(sudo -u checker git -C /home/checker/math rev-parse HEAD) status [$(sudo -u checker git -C /home/checker/math status --short | tr '\n' ' ')]; nanoda_bin sha256 $(sha256sum $NB | cut -c1-64); lean4export $(command -v lean4export) sha256 $(sha256sum $(command -v lean4export) | cut -c1-64); disk $(df -BG --output=used / | tail -1 | tr -d ' ')"
for N in KaplanskyFinitelyPresented GroupRingDeterminant; do
  stopped && break
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
  E=$D/$N.export
  { echo "== export $N  $(date '+%F %T')"; echo "command: lake env lean4export $T > $E"; t0=$(date +%s)
    sbx 1800 "lake env lean4export $T > $E"
    echo "SECONDS: $(( $(date +%s) - t0 ))"; ls -l $E; sha256sum $E; } > $OUT/$N.export.log 2>&1
  log "$N: export $(grep 'EXIT CODE' $OUT/$N.export.log) bytes $(stat -c %s $E 2>/dev/null) sha256 $(sha256sum $E | cut -c1-64)"
  grep -q 'EXIT CODE: 0' $OUT/$N.export.log || { log "$N: export failed or stopped; nanoda runs skipped"; continue; }
  for R in R1:4 R2:1; do
    stopped && break
    RN=${R%%:*}; TH=${R##*:}; CF=$D/$N.$RN.json
    printf '{"use_stdin":false,"export_file_path":"%s","permitted_axioms":["propext","Quot.sound","Classical.choice"],"unpermitted_axiom_hard_error":true,"num_threads":%s,"nat_extension":true,"string_extension":true}\n' $E $TH > $CF
    chown checker:checker $CF; cp $CF $OUT/$N.$RN.json
    { echo "== $RN $N: official nanoda 3a24072, num_threads $TH  $(date '+%F %T')"; echo "binary: $NB sha256 $(sha256sum $NB | cut -c1-64)"
      echo "config: $(cat $CF)"; echo "command: $NB $CF"; t0=$(date +%s)
      sbx 3600 "$NB $CF"
      echo "WALL_SECONDS: $(( $(date +%s) - t0 ))"; } > $OUT/$N.$RN.log 2>&1
    log "$N $RN (threads $TH): $(grep -h -E 'EXIT CODE|overflowed|Checked|panicked' $OUT/$N.$RN.log | tr '\n' ';' | cut -c1-200) $(grep WALL $OUT/$N.$RN.log)"
  done
done
kill $GD 2>/dev/null
if stopped; then echo "GUARD STOPPED $(date '+%F %T')" > $OUT/GUARD_STOPPED.txt; log "guard stopped"; else echo "DISC DONE $(date '+%F %T')" > $OUT/DONE.txt; log "end; disk $(df -BG --output=used / | tail -1 | tr -d ' ')"; fi
sync
