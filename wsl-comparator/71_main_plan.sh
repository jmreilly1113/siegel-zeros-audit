#!/usr/bin/env bash
# Part B planning (read-only on the clone's working tree): unpack upstream main's lean/ with git archive into
# /home/checker/mainsrc, link its .lake to the adc7f12 clone's, list modules whose source changed, and run 71_main_plan.py.
set -u
A=adc7f1241b42e322a6451854ab7e4b4c146bf78a; M=$(sudo -u checker git -C /home/checker/math rev-parse origin/main)
echo "main: $M"
rm -rf /home/checker/mainsrc; install -d -o checker -g checker /home/checker/mainsrc
sudo -u checker bash -c "cd /home/checker/math && git archive $M lean | tar -x -C /home/checker/mainsrc"
ln -s /home/checker/math/lean/.lake /home/checker/mainsrc/lean/.lake
du -sh /home/checker/mainsrc | cut -f1 | sed 's/^/unpacked size: /'
sudo -u checker git -C /home/checker/math diff --name-status $A $M -- lean/ | awk '$1=="M" && $2 ~ /^lean\/(OAI|ComparatorChallenges)\/.*\.lean$/ {sub("^lean/","",$2); sub("\.lean$","",$2); gsub("/",".",$2); print $2}' > /home/checker/mainsrc/changed-modules.txt
echo "changed existing modules: $(cat /home/checker/mainsrc/changed-modules.txt | tr '\n' ' ')"
echo "script sha256: $(sha256sum /mnt/c/Users/Work/dev/siegel/wsl-comparator/71_main_plan.py | cut -c1-64)"
TC=/home/checker/.elan/toolchains/leanprover--lean4---v4.34.1/src/lean
/usr/bin/time -f "(%e s, %M KB)" python3 -I /mnt/c/Users/Work/dev/siegel/wsl-comparator/71_main_plan.py /home/checker/mainsrc/lean /home/checker/math/lean $TC /home/checker/mainsrc/changed-modules.txt
