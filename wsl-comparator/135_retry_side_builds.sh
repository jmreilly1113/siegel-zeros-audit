#!/usr/bin/env bash
# 135 (2026-10-26 08:2x): pre-build the retry-round configs PerceptronFreeEnergy and BoltzmannNonuniqueness (left for
# 114f's next attempt after 69c preempts at 02:37/02:51; ~940 modules unbuilt) with the existing 129b side builder, so
# that the retry round after the pass is mostly runs. 129b beside 128b starved both on 2026-10-25 14:21-15:18, so this
# waits until 128b has finished its last side prebuild (BenjaminiSchramm: done / not finished / reached by 114f), then
# starts 129b on PerceptronFreeEnergy and hands over to 132_chain_side_builds.sh for BoltzmannNonuniqueness.
# Gives up if 114f/119c are gone for GRACE s or on HALT/STOP/GUARD_STOPPED. DRY=1: report and exit.
O=${XR_O:-/mnt/c/Users/Work/dev/siegel/results/2026-10-21-extended-replay}; W=${XR_W:-/mnt/c/Users/Work/dev/siegel/wsl-comparator}; C=${XR_C:-/home/checker/corpus}
A=${1:-PerceptronFreeEnergy}; B=${2:-BoltzmannNonuniqueness}; WAITFOR=${3:-BenjaminiSchramm}; DRY=${DRY:-0}
log() { echo "$(date '+%F %T') $*" >> $O/run.log; }
bad() { [ -f $C/GUARD_STOPPED ] || [ -f $O/runs/STOP.txt ] || [ -f $O/HALT.txt ] || ! pgrep -f '119c_supervise_selfheal.sh' >/dev/null; }
idle128() { grep -qE "128b: $WAITFOR (side prebuild done|side prebuild not finished|reached by 114f)" $O/run.log; }
if [ $DRY = 1 ]; then echo "128b done with $WAITFOR: $(idle128 && echo yes || echo no); bad: $(bad && echo yes || echo no); $A result: $([ -f $O/runs/$A.result.json ] && echo yes || echo no)"; exit 0; fi
log "135: started by hand (Claude): waits for 128b to finish $WAITFOR, then 129b side builds $A, then (132 chain) $B, for the retry round"
until idle128; do bad && { log "135: stop/HALT or 119c gone; nothing started"; exit 0; }; sleep ${XR_ST:-60}; done
[ -f $O/runs/$A.result.json ] && { log "135: $A already has a result; nothing started"; exit 0; }
bad && { log "135: stop/HALT or 119c gone; nothing started"; exit 0; }
log "135: 128b finished $WAITFOR; starting 129b for $A"
setsid nohup bash $W/129b_side_build_one.sh $A $O 3 >> $C/xr-129b.out 2>&1 < /dev/null &
sleep ${XR_GAP:-120}
exec bash $W/132_chain_side_builds.sh $A $B
