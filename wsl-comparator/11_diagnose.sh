#!/usr/bin/env bash
T=/home/checker/.elan/toolchains/leanprover--lean4---v4.34.1
F=$T/lib/lean/Std/Data/Internal/List/Associative.olean.server
ls -la $F; head -c 64 $F | od -A d -c | head -4
echo "== zero-filled .olean* files in checker toolchain (first 16 bytes all NUL):"
find $T/lib -name "*.olean*" -size +0 | while read f; do h=$(head -c 16 "$f" | od -An -tx1 | tr -d ' \n'); [ "$h" = "00000000000000000000000000000000" ] && echo "$f"; done | wc -l
echo "== same check, root toolchain:"
find /root/.elan/toolchains -name "*.olean*" -size +0 | while read f; do h=$(head -c 16 "$f" | od -An -tx1 | tr -d ' \n'); [ "$h" = "00000000000000000000000000000000" ] && echo "$f"; done | wc -l
echo "== mathlib build oleans zero-headed:"
find /home/checker/math/lean/.lake/packages/mathlib/.lake/build/lib -name "*.olean" | head -3000 | while read f; do h=$(head -c 16 "$f" | od -An -tx1 | tr -d ' \n'); [ "$h" = "00000000000000000000000000000000" ] && echo "$f"; done | wc -l
echo "== git fsck openai/math (connectivity only)"
sudo -u checker git -C /home/checker/math fsck --connectivity-only 2>&1 | tail -3
