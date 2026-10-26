man systemd.exec 2>/dev/null | col -b | sed -n '/^ *RestrictAddressFamilies=/,/^ *RestrictFileSystems=/p' | head -40
echo "== journal"; journalctl -n 20 --no-pager 2>/dev/null | grep -i -E "RestrictAddress|Invalid|address famil" | tail -5
echo "== try forms (system unit, command true)"
for v in none "~" "" "AF_UNIX" "~AF_VSOCK"; do printf '%-12s ' "[$v]"; systemd-run --wait --collect -q -p "RestrictAddressFamilies=$v" true 2>&1 | head -1; echo " rc=$?"; done
