#!/usr/bin/env bash
# Main theorem rerouted through the paper's Lemma 3 (lean-checks/MainRerouted.lean).
# 1. build Lemma3Bridged.olean; 2. compile MainRerouted.lean (Lean kernel re-checks every copied constant)
#    and write its .olean; 3. export the two challenge theorems' closure; 4. nanoda: main, control
#    (Classical.choice not permitted), tampered (proofs of the two challenge theorems swapped).
set -u
D=/home/checker/l3k
install -d -o checker -g checker $D
for f in Lemma3Bridged MainRerouted; do
  install -o checker -g checker -m 644 /mnt/c/Users/Work/dev/siegel/lean-checks/$f.lean $D/$f.lean
done
sha256sum $D/Lemma3Bridged.lean $D/MainRerouted.lean
echo "nanoda_bin sha256: $(sha256sum /usr/local/bin/nanoda_bin | cut -c1-64)"
sudo -u checker -H bash -lc '
set -u
export PATH="$HOME/.elan/bin:$PATH"; D=/home/checker/l3k; cd $HOME/math/lean
F="has local changes|warning|^  |unused|linter|Hint|Note|^$|Omit it|deprecated"
echo "== olean Lemma3Bridged"; lake env lean --root=$D -o $D/Lemma3Bridged.olean $D/Lemma3Bridged.lean 2>&1 | grep -Eiv "$F" | head -20; echo "lean exit ${PIPESTATUS[0]}"
LP="$(lake env printenv LEAN_PATH 2>/dev/null):$D"
echo "== compile MainRerouted"; ( time LEAN_PATH="$LP" lake env lean --root=$D -o $D/MainRerouted.olean $D/MainRerouted.lean ) 2>&1 | grep -Ev "has local changes"; echo "lean exit ${PIPESTATUS[0]}"
ls -l $D/MainRerouted.olean || exit 1
A=challenge_exists_absolute_real_zero_gap; B=challenge_dirichletRealZeroBound_proof
echo "== export"; LEAN_PATH="$LP" /usr/local/bin/lean4export MainRerouted -- $A $B > $D/export-main.ndjson; echo "lean4export exit $?"; ls -l $D/export-main.ndjson | awk "{print \$5\" bytes\"}"
python3 /mnt/c/Users/Work/dev/siegel/wsl-comparator/40_nanoda_tamper_named.py $D/export-main.ndjson $D/export-main-tampered.ndjson $A $B
for mode in main control tampered; do
  EXP=$D/export-main.ndjson; [ $mode = tampered ] && EXP=$D/export-main-tampered.ndjson
  if [ $mode != control ]; then AX="[\"propext\",\"Classical.choice\",\"Quot.sound\"]"; else AX="[\"propext\",\"Quot.sound\"]"; fi
  printf "{\"use_stdin\":false,\"export_file_path\":\"%s\",\"permitted_axioms\":%s,\"unpermitted_axiom_hard_error\":true,\"num_threads\":4,\"nat_extension\":true,\"string_extension\":true,\"print_success_message\":true,\"print_axioms\":false}" $EXP "$AX" > $D/nanoda-main-$mode.json
  echo "== nanoda ($mode), config: $(cat $D/nanoda-main-$mode.json)"
  ( time /usr/local/bin/nanoda_bin $D/nanoda-main-$mode.json ) 2>&1 | tail -15; echo "nanoda exit ${PIPESTATUS[0]}"
done
'
