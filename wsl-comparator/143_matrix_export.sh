#!/usr/bin/env bash
# nanoda version matrix (2026-10-26, UNOFFICIAL): regenerate ONE config's export the way comparator d03acab does, at
# openai/math fd4aeeb, as checker in the network-blocking sandbox (75_sbx.sh), under 69_corpus_guard.sh.
# (1) lake build <solution_module> (LEAN_NUM_THREADS 8, 14400 s), a no-op if its closure is still built;
# (2) LEAN_ABORT_ON_PANIC=1 lake env lean4export <solution_module> -- builtinTargets ++ theorem_names ++
#     permitted_axioms ++ primitiveTargets ++ definition_names  (the target list as in 104_discrepancy.sh);
# (3) the nanoda config comparator writes (use_stdin false, permitted_axioms, unpermitted_axiom_hard_error true,
#     num_threads 4, nat_extension true, string_extension true) pointing at the export.
# Writes <out>/exports/<config>.export.log with bytes and sha256, and prints "<config> <export> <config json> <sha256>".
# DRY=1: print the commands only. Run as root. Usage: 143_matrix_export.sh <config> <out dir>
set -u
N=$1; OUT=$2; W=/mnt/c/Users/Work/dev/siegel/wsl-comparator; CF=/home/checker/corpus/configs/$N-nanoda.json
D=/home/checker/corpus/xr/exp; E=$D/$N.export; NC=$D/$N.matrix-config.json; LG=$OUT/exports/$N.export.log
mkdir -p $OUT/exports
read -r MOD TARGETS < <(python3 -I - $CF <<'EOF'
import json, sys
c = json.load(open(sys.argv[1]))
quot = ['Quot', 'Quot.mk', 'Quot.lift', 'Quot.ind'] if 'Quot.sound' in c['permitted_axioms'] else []
prim = ['Nat.add', 'Nat.sub', 'Nat.mul', 'Nat.pow', 'Nat.gcd', 'Nat.div', 'Nat.mod', 'Nat.beq', 'Nat.ble', 'Nat.land', 'Nat.lor',
        'Nat.xor', 'Nat.shiftLeft', 'Nat.shiftRight', 'String.ofList', 'Char.ofNat', 'List', 'eagerReduce', 'Nat', 'String',
        'String.mk', 'Char', 'optParam', 'autoParam', 'semiOutParam', 'outParam']
print(c['solution_module'], c['solution_module'], '--', *(quot + c['theorem_names'] + c['permitted_axioms'] + prim + c.get('definition_names', [])))
EOF
)
[ -n "${MOD:-}" ] || { echo "no solution_module for $N ($CF)"; exit 1; }
if [ "${DRY:-0}" = 1 ]; then echo "build: lake build $MOD"; echo "export: LEAN_ABORT_ON_PANIC=1 lake env lean4export $TARGETS > $E"; exit 0; fi
[ -e $E ] && { echo "$E exists; not overwritten"; exit 1; }
{ echo "== 143 export $N  $(date '+%F %T')  (UNOFFICIAL matrix)"; echo "shipped config: $CF sha256 $(sha256sum $CF | cut -c1-64)"
  echo "clone HEAD $(git -c safe.directory='*' -C /home/checker/math rev-parse HEAD) status [$(git -c safe.directory='*' -C /home/checker/math status --short | tr '\n' ' ')]"
  echo "lean4export $(command -v lean4export) sha256 $(sha256sum $(command -v lean4export) | cut -c1-64)"
  echo "== (1) build: lake build $MOD (LEAN_NUM_THREADS 8)"; T0=$(date +%s)
  bash $W/75_sbx.sh 14400 8 "lake build $MOD" </dev/null | tail -5
  echo "BUILD_SECONDS: $(( $(date +%s) - T0 ))"; echo "disk used: $(df -BG --output=used / | tail -1 | tr -d ' ')"
} > $LG 2>&1
grep -q 'SANDBOX EXIT CODE: 0' $LG || { echo "BUILD FAILED or stopped" >> $LG; echo "$N: build failed or stopped (see $LG)"; exit 1; }
{ echo "== (2) export: LEAN_ABORT_ON_PANIC=1 lake env lean4export $TARGETS > $E"; T0=$(date +%s)
  bash $W/75_sbx.sh 3600 8 "LEAN_ABORT_ON_PANIC=1 lake env lean4export $TARGETS > $E" </dev/null | tail -4
  echo "EXPORT_SECONDS: $(( $(date +%s) - T0 ))"
} >> $LG 2>&1
grep -q 'SANDBOX EXIT CODE: 0' <(sed -n '/== (2)/,$p' $LG) || { echo "EXPORT FAILED or stopped" >> $LG; echo "$N: export failed or stopped (see $LG)"; exit 1; }
SHA=$(sha256sum $E | cut -c1-64)
python3 -I - $CF $E $NC <<'EOF'
import json, sys
c = json.load(open(sys.argv[1]))
json.dump({"export_file_path": sys.argv[2], "nat_extension": True, "num_threads": 4, "permitted_axioms": c['permitted_axioms'],
           "string_extension": True, "unpermitted_axiom_hard_error": True, "use_stdin": False}, open(sys.argv[3], 'w'), indent=1)
EOF
chown checker:checker $NC; cp $NC $OUT/exports/$N.matrix-config.json
echo "export: $E bytes $(stat -c %s $E) sha256 $SHA" >> $LG; echo "nanoda config: $NC"; cat $NC >> $LG
echo "$N $E $NC $SHA"
