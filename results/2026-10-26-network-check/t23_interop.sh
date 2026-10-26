#!/usr/bin/env bash
# Does WSL interop (Windows .exe via vsock) work inside the sandbox unit? Read-only GET to github.com.
UID_C=$(id -u checker)
echo "== binfmt WSLInterop: $(cat /proc/sys/fs/binfmt_misc/WSLInterop 2>&1 | head -1)"; grep -A3 '^\[interop\]' /etc/wsl.conf 2>/dev/null || echo "/etc/wsl.conf: no [interop] section"
echo "== inside the unit, as checker (same properties as 67_corpus_run.sh)"
sudo -u checker -H env XDG_RUNTIME_DIR=/run/user/$UID_C DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$UID_C/bus bash -lc '
systemd-run --property="RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET" --user --wait --pipe --collect -- bash -c "
ls -l /mnt/c/Windows/System32/curl.exe 2>&1 | head -1
timeout 20 /mnt/c/Windows/System32/cmd.exe /c ver 2>&1 | tr -d \"\r\" | head -3; echo \"cmd.exe exit \$?\"
timeout 20 /mnt/c/Windows/System32/curl.exe -s -o NUL -w \"windows curl https://github.com http %{http_code}\" https://github.com 2>&1 | tr -d \"\r\"; echo \" (exit \$?)\"
"'
