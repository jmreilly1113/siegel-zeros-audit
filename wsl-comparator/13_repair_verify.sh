#!/usr/bin/env bash
set -uo pipefail
sudo -u checker -H bash -lc '
export PATH="$HOME/.elan/bin:$PATH"
elan toolchain uninstall leanprover/lean4:v4.34.1 >/dev/null 2>&1
elan toolchain install leanprover/lean4:v4.34.1 2>&1 | tail -1
'
sync
echo "== toolchain: compare every file with root's copy (sha256)"
A=/root/.elan/toolchains/leanprover--lean4---v4.34.1; B=/home/checker/.elan/toolchains/leanprover--lean4---v4.34.1
(cd $A && find . -type f -print0 | sort -z | xargs -0 sha256sum) > /tmp/a.sha
(cd $B && find . -type f -print0 | sort -z | xargs -0 sha256sum) > /tmp/b.sha
echo "files: $(wc -l < /tmp/a.sha) vs $(wc -l < /tmp/b.sha); differing lines: $(diff /tmp/a.sha /tmp/b.sha | grep -c '^[<>]')"
echo "== openai/math clone: object store and every tracked file vs index blob hash"
sudo -u checker -H bash -lc '
cd $HOME/math
git fsck --full 2>&1 | tail -3; echo "fsck exit: ${PIPESTATUS[0]}"
git ls-files -s | awk "{print \$2\"\t\"\$4}" > /tmp/idx.txt
cut -f2 /tmp/idx.txt | git hash-object --stdin-paths > /tmp/wt.txt
paste <(cut -f1 /tmp/idx.txt) /tmp/wt.txt | awk "\$1!=\$2" | wc -l | xargs echo "tracked files whose content differs from the commit:"
echo "tracked files: $(wc -l < /tmp/idx.txt)"
'
