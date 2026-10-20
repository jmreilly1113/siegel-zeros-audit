"""Create the corpus-replay Zenodo record through the REST API (not the GitHub integration).

Usage:
  python -I scripts/zenodo_corpus_deposit.py create  <zip> <metadata.json> <state.json>
      a. create a new deposition (a new record, not a new version), b. upload the zip to its bucket and compare
      Zenodo's md5 with ours, c. set the metadata (with a pre-reserved DOI). Does NOT publish.
  python -I scripts/zenodo_corpus_deposit.py publish <state.json>
      publish the draft recorded in state.json (only after Joe's approval).

Token: read from C:\\Users\\Work\\zenodo-token.txt into an environment variable inside this process; never printed,
logged or written. Every printed string passes through redact(). Stops at the first failed call.
"""
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://zenodo.org/api"
TOKEN_FILE = r"C:\Users\Work\zenodo-token.txt"


def load_token():
    with open(TOKEN_FILE, encoding="utf-8") as f:
        os.environ["ZENODO_TOKEN"] = f.read().strip()


def redact(text):
    t = os.environ.get("ZENODO_TOKEN", "")
    s = str(text)
    return s.replace(t, "***REDACTED***") if t else s


def call(method, url, body=None, data=None, ctype="application/json"):
    headers = {"Authorization": "Bearer " + os.environ["ZENODO_TOKEN"]}
    payload = None
    if body is not None:
        payload = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = ctype
    elif data is not None:
        payload = data
        headers["Content-Type"] = "application/octet-stream"
    req = urllib.request.Request(url, data=payload, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return r.status, json.loads(r.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", "replace")
        print(redact(f"FAILED {method} {url.split('?')[0]}: HTTP {e.code} {msg[:2000]}"))
        sys.exit(1)
    except Exception as e:  # network etc.
        print(redact(f"FAILED {method} {url.split('?')[0]}: {type(e).__name__}: {e}"))
        sys.exit(1)


def create(zip_path, meta_path, state_path):
    data = open(zip_path, "rb").read()
    md5 = hashlib.md5(data).hexdigest()
    sha = hashlib.sha256(data).hexdigest()
    meta = json.load(open(meta_path, encoding="utf-8"))
    # a. new deposition
    st, dep = call("POST", f"{API}/deposit/depositions", body={})
    print(redact(f"a. created deposition id={dep.get('id')} status={st} state={dep.get('state')} submitted={dep.get('submitted')}"))
    did = dep["id"]
    bucket = dep["links"]["bucket"]
    state = {"id": did, "bucket": bucket, "html": dep["links"].get("html"), "zip_sha256": sha, "zip_md5": md5}
    json.dump(state, open(state_path, "w", encoding="utf-8"), indent=1)
    # b. upload
    name = os.path.basename(zip_path)
    st, f = call("PUT", f"{bucket}/{name}", data=data)
    zmd5 = str(f.get("checksum", "")).replace("md5:", "")
    print(redact(f"b. uploaded {name}: status={st} size={f.get('size')} zenodo md5={zmd5} ours={md5} match={zmd5 == md5}"))
    if zmd5 != md5:
        print("STOP: checksum mismatch")
        sys.exit(1)
    # c. metadata
    st, dep2 = call("PUT", f"{API}/deposit/depositions/{did}", body={"metadata": meta})
    m = dep2.get("metadata", {})
    doi = (m.get("prereserve_doi") or {}).get("doi")
    print(redact(f"c. metadata set: status={st} title={m.get('title')!r} upload_type={m.get('upload_type')} license={m.get('license')}"))
    print(redact(f"   reserved DOI={doi} conceptrecid={dep2.get('conceptrecid')} state={dep2.get('state')} submitted={dep2.get('submitted')}"))
    print(redact(f"   related_identifiers={m.get('related_identifiers')}"))
    state.update({"doi": doi, "conceptrecid": dep2.get("conceptrecid"), "html": dep2["links"].get("html"),
                  "zenodo_md5": zmd5, "file": name})
    json.dump(state, open(state_path, "w", encoding="utf-8"), indent=1)
    print(redact(f"d. STOP (not published). Draft: {state['html']}"))


def publish(state_path):
    state = json.load(open(state_path, encoding="utf-8"))
    st, dep = call("POST", f"{API}/deposit/depositions/{state['id']}/actions/publish", body={})
    print(redact(f"published: status={st} doi={dep.get('doi')} record={dep.get('links', {}).get('record_html') or dep.get('links', {}).get('html')}"))
    state.update({"published_doi": dep.get("doi"), "record": dep.get("links", {}).get("record_html")})
    json.dump(state, open(state_path, "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    load_token()
    if sys.argv[1] == "create":
        create(sys.argv[2], sys.argv[3], sys.argv[4])
    elif sys.argv[1] == "publish":
        publish(sys.argv[2])
