#!/usr/bin/env bash
cd /root/tools/comparator
git fetch -q --tags
echo "tags:"; git tag | tail -25
echo "lean-toolchain history:"; git log --format="%h %cd %s" --date=short -- lean-toolchain | head -15
grep -n "importModules\|readModuleData\|withImportModules" -r . --include=*.lean | head
