#!/usr/bin/env bash
# Extended replay, Phase 0.1: live provenance for manifest-extended.json (read-only). Same commands as
# results/2026-10-20-paper-prep/task4-provenance-commands.txt. Prints KEY<TAB>VALUE lines. Run as root.
# Usage: 110_provenance.sh
set -u
L=/home/checker/math/lean
kv() { printf '%s\t%s\n' "$1" "$2"; }
kv clone_head "$(sudo -u checker git -C /home/checker/math rev-parse HEAD)"
kv clone_status_lines "$(sudo -u checker git -C /home/checker/math status --porcelain | wc -l)"
kv lean_toolchain_file "$(cat $L/lean-toolchain)"
kv lean_version "$(sudo -u checker -H bash -lc "export PATH=\$HOME/.elan/bin:\$PATH; cd $L; lean --version")"
kv elan_version "$(sudo -u checker -H bash -lc 'export PATH=$HOME/.elan/bin:$PATH; elan --version')"
kv lake_manifest_sha256 "$(sha256sum $L/lake-manifest.json | cut -c1-64)"
kv lake_manifest_packages "$(python3 -I -c "import json,sys; print(len(json.load(open(sys.argv[1]))['packages']))" $L/lake-manifest.json)"
kv mathlib_rev "$(python3 -I -c "import json,sys; print([p['rev'] for p in json.load(open(sys.argv[1]))['packages'] if p['name']=='mathlib'][0])" $L/lake-manifest.json)"
kv comparator_commit "$(git -C /root/tools/comparator rev-parse HEAD)"
kv comparator_tag "$(git -C /root/tools/comparator describe --tags)"
kv comparator_binary_sha256 "$(sha256sum /usr/local/bin/comparator | cut -c1-64)"
kv exporter_commit "$(git -C /root/tools/lean4export rev-parse HEAD)"
kv exporter_tag "$(git -C /root/tools/lean4export describe --tags)"
kv exporter_binary_sha256 "$(sha256sum /usr/local/bin/lean4export | cut -c1-64)"
kv nanoda_pinned_binary_sha256 "$(sha256sum /usr/local/bin/nanoda_bin | cut -c1-64)"
kv nanoda_postfix_binary_sha256 "$(sha256sum /opt/nanoda-postfix/nanoda_bin | cut -c1-64)"
kv landrun_commit "$(git -C /root/tools/landrun rev-parse HEAD)"
kv landrun_describe "$(git -C /root/tools/landrun describe --tags)"
kv landrun_version "$(landrun --version 2>&1 | head -1)"
kv landrun_binary_sha256 "$(sha256sum /usr/local/bin/landrun | cut -c1-64)"
kv systemd "$(systemctl --version | head -1)"
kv distro "$(. /etc/os-release; echo $PRETTY_NAME)"
kv wsl_kernel "$(uname -r)"
kv wrapper_systemd_run_line "$(grep -E '^systemd-run ' /mnt/c/Users/Work/dev/siegel/wsl-comparator/67_corpus_run.sh)"
kv wrapper_67_sha256 "$(sha256sum /mnt/c/Users/Work/dev/siegel/wsl-comparator/67_corpus_run.sh | cut -c1-64)"
kv wrapper_75sbx_sha256 "$(sha256sum /mnt/c/Users/Work/dev/siegel/wsl-comparator/75_sbx.sh | cut -c1-64)"
kv checker_uid "$(id checker)"
kv date "$(date '+%F %T %Z')"
