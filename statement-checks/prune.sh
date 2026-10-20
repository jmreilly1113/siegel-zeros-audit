D=/home/checker/statement-checks
pgrep -fa "lake build|lean " | grep -v pgrep && { echo "build running; not pruned"; exit 1; }
echo "== $(date '+%F %T') statement-checks prune (Joe step 5: delete build outputs when done, after recording)"
echo "WSL disk used before: $(df -BG --output=used / | tail -1 | tr -d ' ')"
du -sh $D/.lake/packages/* $D/.lake/build 2>/dev/null
echo "-- .lake/build modules: $(find $D/.lake/build -name '*.olean' | wc -l) .olean files"
find $D/.lake/build -name '*.olean' | sed "s#$D/##" | sort
rm -rf $D/.lake && echo "removed $D/.lake (copied packages with their builds, and this project's build)"
echo "kept: $D sources, logs (*.log), lakefile.toml, lake-manifest.json, lean-toolchain"; ls $D
sync; echo 1 > /proc/sys/vm/drop_caches
echo "WSL disk used after: $(df -BG --output=used / | tail -1 | tr -d ' ')"
