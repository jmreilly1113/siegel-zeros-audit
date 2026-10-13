#!/usr/bin/env bash
# Move WSL crash dumps (nanoda aborts) from C: Temp to D:\siegel-audit-offload (Joe 2026-10-12), hashing each first.
# Git Bash. Appends "<sha256>  <name>" to sha256-before-move.txt in the dated D: folder.
S=/c/Users/Work/AppData/Local/Temp/wsl-crashes; D=/d/siegel-audit-offload/wsl-crashes-$(date +%F); mkdir -p $D
for f in $S/*.dmp; do [ -f "$f" ] || continue
  sleep 10  # let the dump finish writing
  (cd $S && sha256sum "$(basename $f)") >> $D/sha256-before-move.txt
  cp "$f" $D/ && cmp -s "$f" "$D/$(basename $f)" && rm "$f" && echo "moved $(basename $f) $(stat -c %s $D/$(basename $f)) bytes to $D"
done
