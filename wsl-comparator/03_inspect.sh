#!/usr/bin/env bash
cd /root/tools
sed -n 300,420p comparator/Main.lean
echo "===== lean4export tags/branches ====="
git -C lean4export tag | tail -30; git -C lean4export branch -r | head; cat lean4export/lean-toolchain
echo "===== landrun README excerpt ====="; grep -n -i -E "abi|best.effort|kernel|5\.13|6\.7|network|--" landrun/README.md | head -40
echo "===== systemd in WSL? ====="; ps -p 1 -o comm=; cat /etc/wsl.conf 2>/dev/null
