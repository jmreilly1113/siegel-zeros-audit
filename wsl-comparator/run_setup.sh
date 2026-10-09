#!/usr/bin/env bash
# Windows-side driver: run setup scripts 01, 02, 05, 06, 07 in order inside WSL (as root; 06/07 drop to 'checker').
for s in 01_base 02_clone_tools 05_build_tools 06_user_clone 07_lake_update; do
  echo "######## $s $(date +%T)"
  MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu-24.04 -u root -- bash /mnt/c/Users/Work/dev/siegel/wsl-comparator/$s.sh > $s.log 2>&1
  rc=$?; echo "$s exit $rc"; tail -4 $s.log | tr '\r' '\n' | tail -4
  [ $rc -ne 0 ] && [ $s != 07_lake_update ] && { echo "stopping: $s failed"; exit 1; }
done
echo "######## done $(date +%T)"
