"""Edit ONE sentence in the description of published Zenodo records (metadata only; files untouched), 2026-10-26.

Usage: python -I scripts/zenodo_edit_description.py <out dir> [--apply]
  Without --apply: read-only. For each record, GET the deposition, find the old sentence in the HTML description
  (exactly one occurrence required) and write <out dir>/<id>-before.json and <id>-after-planned.json.
  With --apply (Joe's approval, 2026-10-26): POST actions/edit, PUT the metadata with only that sentence replaced,
  POST actions/publish, then GET the public record and check that the new sentence is there and the old one is gone.
Token: read from C:\\Users\\Work\\zenodo-token.txt into this process only; never printed, logged or written (redact()).
The sentences are those in results/2026-10-26-network-check/zenodo-descriptions.md. Stops at the first failure.
"""
import html
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://zenodo.org/api"
TOKEN_FILE = r"C:\Users\Work\zenodo-token.txt"
NOTE = "https://github.com/jmreilly1113/siegel-zeros-audit/blob/bb6f197b69d77cf505decba848b21e7f5a12c48d/results/2026-10-26-network-check/README.md"
EDITS = {
    23499651: ("It contains: the official Lean FRO comparator rerun with nanoda as a second kernel and the network blocked;",
               "It contains: the official Lean FRO comparator rerun with nanoda as a second kernel, with IP and Unix-domain sockets "
               f"blocked by a seccomp filter (see the 2026-10-26 network note, {NOTE});"),
    23523697: ("Contents: (1) the official Lean FRO comparator with nanoda as a second kernel accepts the family's Lean statements "
               "with standard axioms only, under a full network block;",
               "Contents: (1) the official Lean FRO comparator with nanoda as a second kernel accepts the family's Lean statements "
               f"with standard axioms only (IP and Unix-domain sockets blocked by a seccomp filter; see the 2026-10-26 network note, {NOTE});"),
    23505836: ("Toolchain: Lean 4.34.1, Mathlib d13f23b, lean4export 076e8e5, landrun 811cfff, nanoda_lib 3a24072, on x86_64 WSL2 "
               "in a network-blocked systemd-run sandbox.",
               "Toolchain: Lean 4.34.1, Mathlib d13f23b, lean4export 076e8e5, landrun 811cfff, nanoda_lib 3a24072, on x86_64 WSL2 "
               f"in a systemd-run sandbox with IP and Unix-domain sockets blocked by a seccomp filter (see the 2026-10-26 network note, {NOTE})."),
}


def load_token():
    with open(TOKEN_FILE, encoding="utf-8") as f:
        os.environ["ZENODO_TOKEN"] = f.read().strip()


def redact(text):
    t = os.environ.get("ZENODO_TOKEN", "")
    s = str(text)
    return s.replace(t, "***REDACTED***") if t else s


def call(method, url, body=None, auth=True):
    headers = {"Authorization": "Bearer " + os.environ["ZENODO_TOKEN"]} if auth else {}
    payload = None
    if body is not None:
        payload = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=payload, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.loads(r.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        print(redact(f"FAILED {method} {url.split('?')[0]}: HTTP {e.code} {e.read().decode('utf-8', 'replace')[:1500]}"))
        sys.exit(1)
    except Exception as e:
        print(redact(f"FAILED {method} {url.split('?')[0]}: {type(e).__name__}: {e}"))
        sys.exit(1)


def locate(desc, old):
    """Return the exact substring of the HTML description that renders as `old` (raw, or with &#39;/&#x27; for ')."""
    for cand in (old, old.replace("'", "&#39;"), old.replace("'", "&#x27;"), html.escape(old, quote=True)):
        if desc.count(cand) == 1:
            return cand
    return None


def main():
    out, apply = sys.argv[1], "--apply" in sys.argv
    os.makedirs(out, exist_ok=True)
    load_token()
    plans = {}
    for rid, (old, new) in EDITS.items():
        _, dep = call("GET", f"{API}/deposit/depositions/{rid}")
        meta = dep["metadata"]; desc = meta.get("description", "")
        hit = locate(desc, old)
        if hit is None:
            print(f"{rid}: old sentence not found exactly once; stop"); sys.exit(1)
        new_html = new.replace("'", "&#39;") if "&#39;" in hit else new
        after = dict(meta); after["description"] = desc.replace(hit, new_html)
        json.dump(meta, open(os.path.join(out, f"{rid}-before.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        json.dump(after, open(os.path.join(out, f"{rid}-after-planned.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print(f"{rid}: state {dep.get('state')} submitted {dep.get('submitted')}; old sentence found once; description "
              f"{len(desc)} -> {len(after['description'])} chars; other metadata keys unchanged: {sorted(meta) == sorted(after)}")
        plans[rid] = after
    if not apply:
        print("dry run only (no --apply)"); return
    for rid, after in plans.items():
        call("POST", f"{API}/deposit/depositions/{rid}/actions/edit")
        call("PUT", f"{API}/deposit/depositions/{rid}", {"metadata": after})
        _, pub = call("POST", f"{API}/deposit/depositions/{rid}/actions/publish")
        _, rec = call("GET", f"{API}/records/{rid}", auth=False)
        d = html.unescape(rec["metadata"].get("description", ""))
        old, new = EDITS[rid]
        ok = new in d and old not in d
        json.dump(rec["metadata"], open(os.path.join(out, f"{rid}-after-published.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print(f"{rid}: published (state {pub.get('state')}); public record shows the new sentence and not the old: {ok}")
        if not ok: sys.exit(1)


if __name__ == "__main__":
    main()
