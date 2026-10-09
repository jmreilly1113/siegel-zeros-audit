#!/usr/bin/env bash
# Second kernel (nanoda) on lean-checks/Lemma3Bridged.lean: build .olean, export the three theorems'
# dependency closure with lean4export, check with nanoda_bin (same settings comparator uses).
# Control run: same export with Classical.choice not permitted must be rejected.
set -u
D=/home/checker/l3k
install -d -o checker -g checker $D
install -o checker -g checker -m 644 /mnt/c/Users/Work/dev/siegel/lean-checks/Lemma3Bridged.lean $D/Lemma3Bridged.lean
sha256sum $D/Lemma3Bridged.lean
echo "nanoda_bin sha256: $(sha256sum /usr/local/bin/nanoda_bin | cut -c1-64); lean4export: /usr/local/bin/lean4export (v4.34.0 built with 4.34.1)"
sudo -u checker -H bash -lc '
set -u
export PATH="$HOME/.elan/bin:$PATH"; D=/home/checker/l3k; cd $HOME/math/lean
echo "== olean"; lake env lean --root=$D -o $D/Lemma3Bridged.olean $D/Lemma3Bridged.lean 2>&1 | grep -v "has local changes" | grep -Eiv "warning|^  |unused|linter|Hint|Note|^$|Omit it" | head -20; echo "lean exit ${PIPESTATUS[0]}"; ls -l $D/*.olean
LP="$(lake env printenv LEAN_PATH 2>/dev/null):$D"
echo "== export"; LEAN_PATH="$LP" /usr/local/bin/lean4export Lemma3Bridged -- Lemma3.interpolation Lemma3.rectangle Lemma3.actual_biquadratic_rectangle_span_via_lemma3 > $D/export.ndjson; echo "lean4export exit $?"; ls -l $D/export.ndjson | awk "{print \$5\" bytes\"}"
python3 /mnt/c/Users/Work/dev/siegel/wsl-comparator/38_nanoda_tamper.py $D/export.ndjson $D/export-tampered.ndjson
for mode in main control tampered; do
  EXP=$D/export.ndjson; [ $mode = tampered ] && EXP=$D/export-tampered.ndjson
  if [ $mode != control ]; then AX="[\"propext\",\"Classical.choice\",\"Quot.sound\"]"; else AX="[\"propext\",\"Quot.sound\"]"; fi
  printf "{\"use_stdin\":false,\"export_file_path\":\"%s\",\"permitted_axioms\":%s,\"unpermitted_axiom_hard_error\":true,\"num_threads\":4,\"nat_extension\":true,\"string_extension\":true,\"print_success_message\":true,\"print_axioms\":true}" $EXP "$AX" > $D/nanoda-$mode.json
  echo "== nanoda ($mode), config: $(cat $D/nanoda-$mode.json)"
  ( time /usr/local/bin/nanoda_bin $D/nanoda-$mode.json ) 2>&1 | tail -25; echo "nanoda exit ${PIPESTATUS[0]}"
done
'
