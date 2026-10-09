#!/usr/bin/env bash
echo "root fs device: $(findmnt -no SOURCE /)"; echo "uptime: $(cat /proc/uptime | cut -d' ' -f1)s"
dmesg -T 2>/dev/null | grep -i 'ext4.*error\|EXT4-fs error' | awk '{$1=$1};1' | cut -c1-160 | sort | uniq -c | sort -rn | head -8
echo "last ext4 error line:"; dmesg -T | grep -i 'EXT4-fs error' | tail -1 | cut -c1-200
echo "mount events:"; dmesg -T | grep -i "EXT4-fs (sd" | tail -6 | cut -c1-160
