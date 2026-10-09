#!/usr/bin/env bash
echo "config diff, repo ComparatorChallenges/SiegelZeros.json vs our /home/checker/SiegelZeros-nanoda.json:"
diff <(python3 -m json.tool /home/checker/math/lean/ComparatorChallenges/SiegelZeros.json) <(python3 -m json.tool /home/checker/SiegelZeros-nanoda.json)
echo "nanoda_bin: $(sha256sum /usr/local/bin/nanoda_bin | cut -c1-64), nanoda_lib commit $(git -C /root/tools/nanoda_lib rev-parse HEAD) ($(grep -m1 '^version' /root/tools/nanoda_lib/Cargo.toml))"
echo "rustc: $(/root/.cargo/bin/rustc --version)"
