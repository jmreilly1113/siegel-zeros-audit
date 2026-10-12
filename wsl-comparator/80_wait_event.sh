#!/usr/bin/env bash
# Waits (Git Bash) until the remainder run produces something to act on, prints it and exits:
# a new batch outcome/prune line, a non-zero comparator or prebuild exit, an illegal axiom, an uncaught exception,
# a guard stop, the Windows monitor ending, or DONE. Usage: 80_wait_event.sh <results dir> <windows monitor output file>
D=$1; M=$2
pat='COMPARATOR EXIT CODE: [1-9]|SANDBOX EXIT CODE: [1-9]|Illegal axiom|uncaught exception'
base=$(grep -r -l -E "$pat" --include='*.log' $D 2>/dev/null | sort); bl=$(grep -c -E 'outcomes|pruned|end;' $D/run.log)
while true; do
  now=$(grep -r -l -E "$pat" --include='*.log' $D 2>/dev/null | sort)
  new=$(comm -13 <(echo "$base") <(echo "$now"))
  [ -n "$new" ] && { echo "NEW NON-ZERO/EXCEPTION:"; for f in $new; do echo "$f"; grep -E "$pat|overflow" $f | head -3; done; exit 0; }
  [ $(grep -c -E 'outcomes|pruned|end;' $D/run.log) -gt $bl ] && { echo "DRIVER:"; grep -E 'outcomes|pruned|end;' $D/run.log | tail -2; exit 0; }
  [ -f $D/GUARD_STOPPED.txt ] || [ -f $D/DONE.txt ] && { ls $D/*.txt; exit 0; }
  tail -3 $M | grep -q -E 'GUARD|DONE|exited' && { tail -3 $M; exit 0; }
  sleep 60
done
