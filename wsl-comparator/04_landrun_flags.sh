#!/usr/bin/env bash
cd /root/tools/comparator
ls Comparator
grep -rln "landrun\|whichLandrun" . --include=*.lean
grep -rn "best-effort\|\"--ro\"\|\"--rw\"\|\"--rox\"\|unrestricted\|whichLandrun" . --include=*.lean | head -40
