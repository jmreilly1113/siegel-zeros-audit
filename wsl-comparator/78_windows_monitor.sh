#!/usr/bin/env bash
# Windows-side monitor (Git Bash, run from Claude Code in the background). Every 60 s: stop checker's build if Windows
# free physical memory < 3000 MB or C: free < 15 GB; print new driver progress and verdict lines from <results dir>
# (searched recursively). Exits when <results dir>/DONE.txt or GUARD_STOPPED.txt appears.
D=$1; last=""
while true; do
  fm=$(powershell.exe -NoProfile -Command '[int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1024)' 2>/dev/null | tr -dc 0-9)
  fc=$(powershell.exe -NoProfile -Command '[int]((Get-PSDrive C).Free/1GB)' 2>/dev/null | tr -dc 0-9)
  if { [ -n "$fm" ] && [ "$fm" -lt 3000 ]; } || { [ -n "$fc" ] && [ "$fc" -lt 15 ]; }; then
    MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu-24.04 -u root -- bash -c "touch /home/checker/corpus/GUARD_STOPPED; pkill -TERM -u checker -f 'comparator|lake|lean'; sleep 20; pkill -KILL -u checker -f 'comparator|lake|lean'; sync" >/dev/null 2>&1
    echo "WINDOWS GUARD: free RAM ${fm} MB, C: free ${fc} GB; build stopped (resumable)"; break
  fi
  st=$(grep -h -E '^20' $D/run.log 2>/dev/null; grep -r -H -E 'SANDBOX EXIT CODE|kernel accepts|Your solution is okay|COMPARATOR EXIT CODE|Illegal axiom|uncaught exception|AUDIT (axioms|target|statement)' --include='*.log' $D 2>/dev/null | grep -v -E 'attempt[0-9]|stopped-' | sed "s#$D/##")
  new=$(comm -13 <(echo "$last" | sort) <(echo "$st" | sort))
  [ -n "$new" ] && echo "$new" | cut -c1-260 && echo "  [RAM ${fm} MB, C: ${fc} GB, $(date +%T)]"
  last="$st"
  [ -f $D/DONE.txt ] && { echo DONE; break; }
  [ -f $D/GUARD_STOPPED.txt ] && { echo "WSL GUARD STOPPED"; break; }
  sleep 60
done
