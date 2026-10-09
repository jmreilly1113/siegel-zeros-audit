#!/usr/bin/env bash
echo "kernel: $(uname -r)"
mountpoint -q /sys/kernel/security || mount -t securityfs securityfs /sys/kernel/security 2>/dev/null
echo "LSM list: $(cat /sys/kernel/security/lsm 2>&1)"
python3 - <<'PY'
import ctypes, os
libc = ctypes.CDLL(None, use_errno=True)
SYS_landlock_create_ruleset = 444
LANDLOCK_CREATE_RULESET_VERSION = 1
abi = libc.syscall(SYS_landlock_create_ruleset, None, 0, LANDLOCK_CREATE_RULESET_VERSION)
print("Landlock ABI version:", abi, "(errno %d)" % ctypes.get_errno() if abi < 0 else "")
PY
