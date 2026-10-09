#!/usr/bin/env bash
for T in /root/.elan/toolchains/leanprover--lean4---v4.34.1 /home/checker/.elan/toolchains/leanprover--lean4---v4.34.1; do
  find $T/lib -name "*.olean*" -size +0 | while read f; do h=$(head -c 16 "$f" | od -An -tx1 | tr -d ' \n'); [ "$h" = "00000000000000000000000000000000" ] && echo "ZERO: $f"; done
done
find /root/.elan/toolchains -maxdepth 1; ls -la --time-style=full-iso /root/.elan/toolchains/ /home/checker/.elan/toolchains/
sha256sum /root/.elan/toolchains/leanprover--lean4---v4.34.1/lib/lean/Std/Data/Internal/List/Associative.olean.server
