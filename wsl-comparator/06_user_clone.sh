#!/usr/bin/env bash
set -euo pipefail
id checker >/dev/null 2>&1 || useradd -m -s /bin/bash checker
cp /root/tools/lean4export/.lake/build/bin/lean4export /usr/local/bin/
cp /root/tools/comparator/.lake/build/bin/comparator /usr/local/bin/
loginctl enable-linger checker
sudo -u checker -H bash -lc '
set -euo pipefail
if [ ! -x "$HOME/.elan/bin/elan" ]; then
  curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -o /tmp/elan-init-$USER.sh
  sh /tmp/elan-init-$USER.sh -y --default-toolchain none >/dev/null
fi
cd $HOME
[ -d math ] || git clone -q https://github.com/openai/math
cd math && git checkout -q adc7f1241b42e322a6451854ab7e4b4c146bf78a
echo "openai/math HEAD: $(git rev-parse HEAD); autocrlf=$(git config core.autocrlf || echo unset); dirty files: $(git status --short | wc -l)"
echo "challenge blob: $(git rev-parse HEAD:lean/ComparatorChallenges/SiegelZeros.lean) json: $(cat lean/ComparatorChallenges/SiegelZeros.json | tr -d " \n")"
'
id checker; ls -l /usr/local/bin/ | grep -E "landrun|lean4export|comparator"; systemctl is-active user@$(id -u checker).service
sync
