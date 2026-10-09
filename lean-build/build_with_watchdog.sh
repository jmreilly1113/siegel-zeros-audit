#!/usr/bin/env bash
# Run lake build; stop it if free space on C: drops below 2.5 GB.
export PATH="$HOME/.elan/bin:$PATH"
export LEAN_NUM_THREADS=${LEAN_NUM_THREADS:-3}
LOG=build.log
date > $LOG; echo "LEAN_NUM_THREADS=$LEAN_NUM_THREADS" >> $LOG
lake build OAISiegelZeros >> $LOG 2>&1 &
PID=$!
while kill -0 $PID 2>/dev/null; do
  FREE=$(df --output=avail -B1M /c | tail -1 | tr -d ' ')
  echo "$(date +%T) $FREE" >> freespace.log
  if [ "$FREE" -lt 2560 ]; then
    echo "WATCHDOG: free space ${FREE} MB < 2560 MB, stopping build" >> $LOG
    taskkill //F //T //PID $(cat /proc/$PID/winpid) >/dev/null 2>&1; kill $PID 2>/dev/null
    exit 2
  fi
  sleep 1
done
wait $PID; RC=$?
echo "lake exit code: $RC" >> $LOG; date >> $LOG
df -h /c | tail -1 >> $LOG
exit $RC
