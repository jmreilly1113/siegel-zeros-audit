#!/usr/bin/env bash
ls /root/tools
for c in /root/tools/*; do echo "== $c"; grep -rn -i 'nanoda' $c --include=*.lean --include=*.md 2>/dev/null | cut -c1-240 | head -15; done
