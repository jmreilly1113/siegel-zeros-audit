#!/usr/bin/env bash
sudo -u checker -H bash -lc '
cd $HOME/math
git status --short | head; echo "--- manifest diff vs commit:"; git diff --stat -- lean/lake-manifest.json; git diff -- lean/lake-manifest.json | head -40
cd lean
python3 - <<PY
import json,subprocess
m=json.load(open("lake-manifest.json"))
for p in m["packages"]:
    if p["name"] in ("aesop","mathlib","batteries","Qq"):
        d=".lake/packages/"+p["name"]
        url=subprocess.run(["git","-C",d,"remote","get-url","origin"],capture_output=True,text=True).stdout.strip()
        head=subprocess.run(["git","-C",d,"rev-parse","HEAD"],capture_output=True,text=True).stdout.strip()
        print(p["name"], "manifest url:", p.get("url"), "| origin:", url, "| rev match:", head==p["rev"])
PY
'
