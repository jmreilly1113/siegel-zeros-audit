#!/usr/bin/env bash
# Windows-side: stop all of checker's processes in WSL if C: drops below 4 GB.
while true; do
  FREE=$(df --output=avail -B1M /c | tail -1 | tr -d ' ')
  echo "$(date +%T) $FREE" >> freespace-wsl.log
  if [ "$FREE" -lt 4096 ]; then
    echo "$(date +%T) WATCHDOG: ${FREE} MB free, stopping checker processes" >> freespace-wsl.log
    MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu-24.04 -u root -- pkill -u checker
  fi
  sleep 5
done
