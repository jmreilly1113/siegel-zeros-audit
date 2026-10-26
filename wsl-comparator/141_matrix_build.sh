#!/usr/bin/env bash
# nanoda version matrix (2026-10-26, UNOFFICIAL): build B2 and B3, separate from the official /usr/local/bin/nanoda_bin
# (3a24072) and the earlier /opt/nanoda-postfix and /opt/nanoda-1gib-diag builds, which are not touched.
#   B2: nanoda_lib 37cb87b (master, 2026-10-24), stock (STACK_SIZE 16 MiB)   -> /opt/nanoda-37cb87b/nanoda_bin
#   B3: 37cb87b + nealmcb's tools/patches/nanoda-let-fvar-and-succ-guard-37cb87b.patch (openai-math-lean-tooling
#       1ca7ff2), STACK_SIZE 64 MiB                                          -> /opt/nanoda-37cb87b-patch64/nanoda_bin
# Network: read-only fetch of the two sources. Run as root. Usage: 141_matrix_build.sh <log>
set -eu
LOG=$1; exec > >(tee $LOG) 2>&1
export PATH=/root/.cargo/bin:$PATH
C=37cb87b7e6cd6862ef2bd121faa9f4604f59fe96
PURL=https://raw.githubusercontent.com/nealmcb/openai-math-lean-tooling/1ca7ff2a0280760783ee2b198c0d6f2a1cfeaba4/tools/patches/nanoda-let-fvar-and-succ-guard-37cb87b.patch
PSHA=edd9824f5fd93c86d3f52acea1373a915ccfddf23db33c5e919f03f7c642bc30
T2=/root/tools/nanoda_lib-37cb87b; T3=/root/tools/nanoda_lib-37cb87b-patch64
echo "== 141 build $(date '+%F %T')"; rustc --version; cargo --version
echo "official /usr/local/bin/nanoda_bin before: $(sha256sum /usr/local/bin/nanoda_bin | cut -c1-64)"
[ -e $T2 ] || git clone -q https://github.com/ammkrn/nanoda_lib $T2
git -C $T2 fetch -q origin; git -C $T2 checkout -q $C; echo "B2 tree $T2 HEAD $(git -C $T2 rev-parse HEAD); status [$(git -C $T2 status --short | tr '\n' ' ')]"
grep -n 'STACK_SIZE: usize' $T2/src/lib.rs
rm -rf $T3; cp -a $T2 $T3
curl -fsSL $PURL -o /root/tools/nanoda-let-fvar-and-succ-guard-37cb87b.patch
echo "patch sha256 $(sha256sum /root/tools/nanoda-let-fvar-and-succ-guard-37cb87b.patch | cut -c1-64) (expected $PSHA)"
[ "$(sha256sum /root/tools/nanoda-let-fvar-and-succ-guard-37cb87b.patch | cut -c1-64)" = $PSHA ] || { echo "PATCH SHA MISMATCH"; exit 1; }
git -C $T3 apply --whitespace=nowarn /root/tools/nanoda-let-fvar-and-succ-guard-37cb87b.patch
sed -i 's/^pub(crate) const STACK_SIZE: usize = 16_777_216;$/pub(crate) const STACK_SIZE: usize = 67_108_864;/' $T3/src/lib.rs
grep -n 'STACK_SIZE: usize' $T3/src/lib.rs | grep -q 67_108_864 || { echo "STACK_SIZE edit failed"; exit 1; }
echo "== B3 diff against 37cb87b:"; git -C $T3 diff --stat; git -C $T3 diff src/lib.rs
for T in $T2 $T3; do echo "== cargo build --release --locked in $T"; (cd $T && cargo build --release --locked 2>&1 | tail -3); done
install -D -m 755 $T2/target/release/nanoda_bin /opt/nanoda-37cb87b/nanoda_bin
install -D -m 755 $T3/target/release/nanoda_bin /opt/nanoda-37cb87b-patch64/nanoda_bin
echo "== binaries"
sha256sum /opt/nanoda-1gib-diag/nanoda_bin /opt/nanoda-postfix/nanoda_bin /opt/nanoda-37cb87b/nanoda_bin /opt/nanoda-37cb87b-patch64/nanoda_bin /usr/local/bin/nanoda_bin
echo "official /usr/local/bin/nanoda_bin after: $(sha256sum /usr/local/bin/nanoda_bin | cut -c1-64)"
echo "== 141 done $(date '+%F %T')"
