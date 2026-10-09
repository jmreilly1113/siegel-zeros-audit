#!/usr/bin/env bash
H=/home/checker; cd $H/math/lean
echo "openai/math commit: $(sudo -u checker git rev-parse HEAD)"
echo "lean-toolchain: $(cat lean-toolchain)"
echo "lean: $(sudo -u checker $H/.elan/bin/lean --version)"
echo "comparator: $(git -C /opt/comparator rev-parse HEAD 2>/dev/null || echo see 05_build_tools.log: tag v4.34.0 d03acab)"
echo "landrun: $(landrun --version 2>&1 | head -1)"
echo "lean4export: tag v4.34.0 built with v4.34.1 (05_build_tools.log)"
echo "sha256 ComparatorChallenges/SiegelZeros.lean: $(sha256sum ComparatorChallenges/SiegelZeros.lean | cut -c1-64)"
echo "sha256 ComparatorChallenges/SiegelZeros.json: $(sha256sum ComparatorChallenges/SiegelZeros.json | cut -c1-64)"
cat ComparatorChallenges/SiegelZeros.json
echo "kernel: $(uname -r)"
