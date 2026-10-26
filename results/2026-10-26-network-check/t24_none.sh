#!/usr/bin/env bash
# 2026-10-26: test RestrictAddressFamilies=none (75n_sbx.sh / 140n_matrix_run.sh) before use. Everything else as 75_sbx.sh / 140_matrix_run.sh.
W=/mnt/c/Users/Work/dev/siegel/wsl-comparator; T=/tmp/t24; rm -rf $T; mkdir -p $T; chmod 777 $T
UID_C=$(id -u checker)
SCR=/mnt/c/Users/Work/AppData/Local/Temp/claude/C--Users-Work-dev-siegel/594ab20c-2cc0-4c87-89de-90414bba6150/scratchpad
eval "$(cat $SCR/t24_probe_block.txt | sed 's#/tmp/t22_probe.py#/tmp/t24/probe.py#')"; chmod 644 $T/probe.py
echo "== kernel $(uname -r); $(systemctl --version | head -1); date $(date '+%F %T')"
echo "== (A1) probes in a user unit as checker, property RestrictAddressFamilies=none (75n_sbx.sh style)"
bash $W/75n_sbx.sh 120 1 "id -u; grep -E \"^(Seccomp|NoNewPrivs)\" /proc/self/status; python3 -I /tmp/t24/probe.py; timeout 10 curl -sS -m 8 -o /dev/null -w \"curl https://github.com http %{http_code}\n\" https://github.com 2>&1 | head -2; getent hosts github.com || echo \"getent hosts github.com: no result\"; (exec 3<>/dev/tcp/1.1.1.1/443) 2>&1 | head -1"
echo "== (A2) probes in a system unit with setpriv to checker, property RestrictAddressFamilies=none (140n_matrix_run.sh style)"
systemd-run --wait --pipe --collect --property="RestrictAddressFamilies=none" -E PATH=/usr/local/bin:/usr/bin:/bin --working-directory /home/checker -- /bin/bash -c "setpriv --reuid=$UID_C --regid=$(id -g checker) --init-groups --no-new-privs env HOME=/home/checker bash -c 'id -u; grep -E \"^(Seccomp|NoNewPrivs)\" /proc/self/status; python3 -I /tmp/t24/probe.py'"
echo "== (A3) interop (t23) in a user unit with RestrictAddressFamilies=none"
bash $W/75n_sbx.sh 60 1 "timeout 20 /mnt/c/Windows/System32/cmd.exe /c ver 2>&1 | tr -d \"\r\" | head -3; echo \"cmd.exe pipeline done\"; timeout 20 /mnt/c/Windows/System32/curl.exe -s -o NUL -w \"windows curl https://github.com http %{http_code}\" https://github.com 2>&1 | tr -d \"\r\"; echo"
echo "== (B1) small lake build: fresh project /tmp/t24/proj (toolchain from the clone), via 75n_sbx.sh"
mkdir -p $T/proj; cp /home/checker/math/lean/lean-toolchain $T/proj/; printf 'name = "t24"\ndefaultTargets = ["T24"]\n\n[[lean_lib]]\nname = "T24"\n' > $T/proj/lakefile.toml
printf 'def t24x : Nat := 2 + 3\ntheorem t24t : t24x = 5 := rfl\n#print axioms t24t\n' > $T/proj/T24.lean; chown -R checker:checker $T/proj
bash $W/75n_sbx.sh 600 4 "cd /tmp/t24/proj && lake build 2>&1 | tail -4; ls -l .lake/build/lib/lean/T24.olean 2>&1 | cut -c1-80"
echo "== (B2) lake build in the clone (no-op expected): OAI.Analysis.Laughlin.Main, via 75n_sbx.sh"
bash $W/75n_sbx.sh 1800 4 "lake build OAI.Analysis.Laughlin.Main 2>&1 | tail -2"
echo "== (B3) lean4export: Laughlin export again under 75n_sbx.sh; must equal 842b632a... (2026-10-26 14:37, under 75_sbx.sh)"
TG=$(DRY=1 bash $W/143n_matrix_export.sh Laughlin /tmp/t24/dry | grep '^export:' | sed 's/^export: //; s# > .*##')
bash $W/75n_sbx.sh 3600 8 "$TG > /tmp/t24/Laughlin.export" | tail -2
echo "t24 export bytes $(stat -c %s $T/Laughlin.export) sha256 $(sha256sum $T/Laughlin.export | cut -c1-64)"
rm -f $T/Laughlin.export
echo "== (B4) nanoda B3 on the KaplanskyDirectFiniteness export via 140n_matrix_run.sh"
bash $W/140n_matrix_run.sh t24-KDF-B3 /home/checker/corpus/xr/exp/KaplanskyDirectFiniteness.f67473b-config.json /opt/nanoda-37cb87b-patch64/nanoda_bin $T/KDF-B3.log 600 16G
grep -E "^export:|RestrictAddress|^limits|memcg" $T/KDF-B3.log | cut -c1-200
echo "== t24 done $(date '+%F %T')"
