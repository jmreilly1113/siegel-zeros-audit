#!/usr/bin/env bash
# Extended replay, resume after a Windows restart (2026-10-23; the 00:29 update restart cost 7.5 h idle).
# Run as root by the Windows logon task (123_boot_resume.ps1). (1) Same check as 18_olean_scan.sh on .olean files
# written in the last 48 h: an empty or bad-header .olean (an interrupted write) is moved to $Q with its .ilean/.hash/.trace,
# so lake rebuilds that module. (2) Starts keeper 122 (flock: a no-op if it already runs). Never touches results/.
set -u
OUT=/mnt/c/Users/Work/dev/siegel/results/2026-10-21-extended-replay; W=/mnt/c/Users/Work/dev/siegel/wsl-comparator
L=/home/checker/math/lean/.lake; Q=/home/checker/corpus/boot-quarantine/$(date +%Y%m%d%H%M%S)
log() { echo "$(date '+%F %T') $*" >> $OUT/run.log; }
if pgrep -u checker -f 'lake|lean|comparator' >/dev/null; then   # not a fresh boot: files may be mid-write; scan nothing
  log "123: build processes running; no scan"; exec 7>&-
  setsid nohup bash $W/122_keeper.sh $OUT/phase3-order.tsv $OUT >> /home/checker/corpus/xr-122.out 2>&1 < /dev/null &
  exit 0
fi
n=0; bad=0
while IFS= read -r -d '' f; do
  n=$((n+1))
  if [ ! -s "$f" ] || [ "$(head -c 5 "$f")" != olean ]; then
    bad=$((bad+1)); mkdir -p "$Q$(dirname "$f")"
    for g in "$f" "${f%.olean}.ilean" "${f%.olean}.hash" "${f%.olean}.trace" "$f.hash"; do [ -e "$g" ] && mv "$g" "$Q$g"; done
    echo "$f" >> $Q.list
  fi
done < <(find $L -name '*.olean' -mmin -2880 -print0)
log "123: boot resume; .olean written in the last 48 h: $n, empty or bad header: $bad$( [ $bad -gt 0 ] && echo " (moved to $Q; list $Q.list)")"
setsid nohup bash $W/122_keeper.sh $OUT/phase3-order.tsv $OUT >> /home/checker/corpus/xr-122.out 2>&1 < /dev/null &
