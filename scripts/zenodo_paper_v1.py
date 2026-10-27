"""Publish the paper-v1 version of Zenodo concept record 10.5281/zenodo.23269527 (2026-10-27; Joe: "If all is good, push and
publish the Zenodo version").

Usage: python -I scripts/zenodo_paper_v1.py <out dir> [--apply]
  Without --apply: read-only. GET the latest version's deposition (23523697, reviewer-packet-v3), report its state, files and
  metadata keys, and write <out dir>/metadata-planned.json (docs/zenodo-paper-v1-metadata.json "metadata" plus publication_date).
  With --apply: POST actions/newversion; on the new draft delete the files inherited from v3; PUT the PDF and the zip into the
  draft's bucket and check each md5 against the local file; PUT the metadata; POST actions/publish; GET the public record and
  check its version, title, concept DOI and files.
Files: D:\\siegel-audit-offload\\zenodo-paper-v1\\ (built by results/2026-10-27-final-packaging/final/build_from_tag.sh).
Token: read from C:\\Users\\Work\\zenodo-token.txt into this process only; never printed, logged or written (redact()).
Stops at the first failure.
"""
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://zenodo.org/api"
TOKEN_FILE = r"C:\Users\Work\zenodo-token.txt"
LATEST = 23523697
CONCEPT_DOI = "10.5281/zenodo.23269527"
FILES_DIR = r"D:\siegel-audit-offload\zenodo-paper-v1"
FILES = ["siegel-zeros-audit-paper-v1.pdf", "siegel-zeros-audit-paper-v1.zip"]
META = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "zenodo-paper-v1-metadata.json")
PUBLICATION_DATE = "2026-10-27"


def load_token():
    with open(TOKEN_FILE, encoding="utf-8") as f:
        os.environ["ZENODO_TOKEN"] = f.read().strip()


def redact(text):
    t = os.environ.get("ZENODO_TOKEN", "")
    s = str(text)
    return s.replace(t, "***REDACTED***") if t else s


def call(method, url, body=None, auth=True, raw=None):
    headers = {"Authorization": "Bearer " + os.environ["ZENODO_TOKEN"]} if auth else {}
    payload = None
    if body is not None:
        payload = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if raw is not None:
        payload = raw
        headers["Content-Type"] = "application/octet-stream"
    req = urllib.request.Request(url, data=payload, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            data = r.read().decode("utf-8")
            return r.status, (json.loads(data) if data.strip() else {})
    except urllib.error.HTTPError as e:
        print(redact(f"FAILED {method} {url.split('?')[0]}: HTTP {e.code} {e.read().decode('utf-8', 'replace')[:1500]}"))
        sys.exit(1)
    except Exception as e:
        print(redact(f"FAILED {method} {url.split('?')[0]}: {type(e).__name__}: {e}"))
        sys.exit(1)


def planned_metadata():
    m = json.load(open(META, encoding="utf-8"))["metadata"]
    m = {k: v for k, v in m.items() if not k.startswith("_")}
    m["related_identifiers"] = [{k: v for k, v in r.items() if not k.startswith("_")} for r in m["related_identifiers"]]
    m["publication_date"] = PUBLICATION_DATE
    return m


def main():
    out, apply = sys.argv[1], "--apply" in sys.argv
    os.makedirs(out, exist_ok=True)
    load_token()
    meta = planned_metadata()
    local = {}
    for n in FILES:
        b = open(os.path.join(FILES_DIR, n), "rb").read()
        local[n] = (len(b), hashlib.md5(b).hexdigest(), hashlib.sha256(b).hexdigest())
        print(f"local {n}: {local[n][0]} bytes, md5 {local[n][1]}, sha256 {local[n][2]}")
    _, dep = call("GET", f"{API}/deposit/depositions/{LATEST}")
    print(f"{LATEST}: state {dep.get('state')}, submitted {dep.get('submitted')}, version {dep['metadata'].get('version')}, "
          f"conceptdoi {dep.get('conceptdoi')}, files {[f['filename'] for f in dep.get('files', [])]}")
    print(f"{LATEST} metadata keys: {sorted(dep['metadata'])}")
    if dep.get("conceptdoi") != CONCEPT_DOI:
        print("concept DOI differs; stop"); sys.exit(1)
    json.dump(meta, open(os.path.join(out, "metadata-planned.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    if not apply:
        print("dry run only (no --apply)"); return

    _, nv = call("POST", f"{API}/deposit/depositions/{LATEST}/actions/newversion")
    draft_url = nv["links"]["latest_draft"]
    _, draft = call("GET", draft_url)
    did = draft["id"]
    print(f"new version draft {did}: state {draft.get('state')}, inherited files {[f['filename'] for f in draft.get('files', [])]}")
    for f in draft.get("files", []):
        call("DELETE", f"{API}/deposit/depositions/{did}/files/{f['id']}")
    bucket = draft["links"]["bucket"]
    for n in FILES:
        _, up = call("PUT", f"{bucket}/{n}", raw=open(os.path.join(FILES_DIR, n), "rb").read())
        ok = up.get("checksum") == "md5:" + local[n][1] and up.get("size") == local[n][0]
        print(f"uploaded {n}: size {up.get('size')}, checksum {up.get('checksum')}; matches local: {ok}")
        if not ok: sys.exit(1)
    _, put = call("PUT", f"{API}/deposit/depositions/{did}", {"metadata": meta})
    _, chk = call("GET", f"{API}/deposit/depositions/{did}")
    names = sorted(f["filename"] for f in chk.get("files", []))
    print(f"draft {did} files {names}; version {chk['metadata'].get('version')}; doi to be {chk['metadata'].get('prereserve_doi', {}).get('doi')}")
    if names != sorted(FILES): print("draft files differ from the two planned files; stop"); sys.exit(1)
    _, pub = call("POST", f"{API}/deposit/depositions/{did}/actions/publish")
    print(f"published {did}: state {pub.get('state')}, doi {pub.get('doi')}, conceptdoi {pub.get('conceptdoi')}")
    _, rec = call("GET", f"{API}/records/{did}", auth=False)
    rm = rec.get("metadata", {})
    rfiles = sorted((f.get("key"), f.get("checksum"), f.get("size")) for f in rec.get("files", []))
    checks = {"version": rm.get("version") == "paper-v1", "title": rm.get("title") == meta["title"],
              "conceptdoi": rec.get("conceptdoi") == CONCEPT_DOI,
              "files": rfiles == sorted((n, "md5:" + local[n][1], local[n][0]) for n in FILES)}
    json.dump({"doi": rec.get("doi"), "conceptdoi": rec.get("conceptdoi"), "id": rec.get("id"), "links": rec.get("links", {}).get("self_html") or rec.get("links", {}).get("html"),
               "metadata": rm, "files": rfiles}, open(os.path.join(out, f"{did}-published.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"public record {did}: {checks}")
    if not all(checks.values()): sys.exit(1)


if __name__ == "__main__":
    main()
