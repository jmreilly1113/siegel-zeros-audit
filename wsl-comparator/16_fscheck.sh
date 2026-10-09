#!/usr/bin/env bash
echo "ext4 errors in kernel log: $(dmesg 2>/dev/null | grep -ci 'ext4.*error\|EXT4-fs error')"
cd /home/checker/math/lean/.lake/packages
n=$(find . -type f 2>/tmp/find.err | wc -l); echo "files under .lake/packages: $n; find errors: $(wc -l < /tmp/find.err)"
for p in aesop Qq batteries mathlib; do echo "$p: $(sudo -u checker git -C $p remote get-url origin) rev $(sudo -u checker git -C $p rev-parse --short HEAD)"; done
