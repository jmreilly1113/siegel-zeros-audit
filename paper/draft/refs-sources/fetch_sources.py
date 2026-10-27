"""Read-only fetch of the metadata of every refs.bib source (2026-10-27). Writes one JSON extract per source next to this file.

Usage: python -I paper/draft/refs-sources/fetch_sources.py <out dir>
GitHub: `gh api` GET requests only. Others: plain HTTPS GET (arXiv abstract pages, Zenodo record API, Crossref works API).
Nothing is posted. Each extract keeps only the fields used to check a bibliography entry, plus the request and its time.
"""
import json, os, re, subprocess, sys, time, urllib.request, html

out = sys.argv[1]
now = time.strftime('%Y-%m-%dT%H:%M:%S%z')


def gh(path):
    r = subprocess.run(['gh', 'api', '-X', 'GET', path], capture_output=True, text=True, encoding='utf-8')
    return json.loads(r.stdout) if r.returncode == 0 else {'error': r.stderr.strip()[:300]}


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'curl/8 (read-only bibliography check)'})
    with urllib.request.urlopen(req, timeout=60) as f:
        return f.read().decode('utf-8', 'replace')


def save(name, req, data):
    with open(os.path.join(out, name + '.json'), 'x', encoding='utf-8', newline='\n') as o:
        json.dump({'request': req, 'fetched': now, 'data': data}, o, ensure_ascii=False, indent=1)


def pick(d, keys): return {k: d.get(k) for k in keys} if isinstance(d, dict) else d


A = 'adc7f1241b42e322a6451854ab7e4b4c146bf78a'; F = 'fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb'
for p in ('preprints/Uniform-exclusion-of-Landau-Siegel-zeros-October-1-2026/paper.pdf', 'preprints/The-Quasi-Riemann-Hypothesis-September-30-2026/paper.pdf'):
    q = f'repos/openai/math/contents/{p}?ref={F}'
    save('openai-math-' + p.split('/')[1][:24], 'gh api ' + q, pick(gh(q), ['path', 'sha', 'size', 'html_url']))
for c in (A, F):
    q = f'repos/openai/math/commits/{c}'
    d = gh(q); save('openai-math-commit-' + c[:7], 'gh api ' + q, {'sha': d.get('sha'), 'date': (d.get('commit') or {}).get('committer', {}).get('date'), 'html_url': d.get('html_url')})
for repo, c in (('leanprover/comparator', 'd03acab154d269c06e60e4de7e4cc85deebff94b'), ('leanprover/lean4export', '076e8e57707e813375e8f9da8bf989799ace9680'),
                ('ammkrn/nanoda_lib', '3a2407216ee84a75f9e1aead6803d0578be06ae7'), ('leanprover/lean4', '5045d0056413266e57c625dcd7c365b10e377c52'),
                ('leanprover-community/mathlib4', 'd13f23b723b8a846827a245b89c10fc7d3f11612'), ('nealmcb/openai-math-lean-tooling', '1ca7ff2a0280760783ee2b198c0d6f2a1cfeaba4')):
    r = gh(f'repos/{repo}'); d = gh(f'repos/{repo}/commits/{c}')
    save('repo-' + repo.replace('/', '_'), f'gh api repos/{repo}; gh api repos/{repo}/commits/{c}',
         {'full_name': r.get('full_name'), 'owner': (r.get('owner') or {}).get('login'), 'owner_type': (r.get('owner') or {}).get('type'), 'description': r.get('description'),
          'commit': d.get('sha'), 'commit_date': (d.get('commit') or {}).get('committer', {}).get('date'), 'error': d.get('error') or r.get('error')})
for u in ('ammkrn', 'nealmcb'):
    save('user-' + u, f'gh api users/{u}', pick(gh(f'users/{u}'), ['login', 'name', 'type']))
for org in ('leanprover', 'leanprover-community'):
    save('org-' + org, f'gh api orgs/{org}', pick(gh(f'orgs/{org}'), ['login', 'name', 'description']))
for repo, n in (('ammkrn/nanoda_lib', 55), ('ammkrn/nanoda_lib', 61), ('ammkrn/nanoda_lib', 62), ('grwtsk/openai-math', 29), ('grwtsk/openai-math', 40)):
    d = gh(f'repos/{repo}/issues/{n}')
    save(f'issue-{repo.replace("/", "_")}-{n}', f'gh api repos/{repo}/issues/{n}', {'title': d.get('title'), 'user': (d.get('user') or {}).get('login'), 'created_at': d.get('created_at'), 'html_url': d.get('html_url'), 'error': d.get('error')})
for repo, cid in (('ammkrn/nanoda_lib', 6402528075), ('grwtsk/openai-math', 6296359378), ('grwtsk/openai-math', 6087525965), ('grwtsk/openai-math', 6431288875)):
    d = gh(f'repos/{repo}/issues/comments/{cid}')
    save(f'comment-{repo.replace("/", "_")}-{cid}', f'gh api repos/{repo}/issues/comments/{cid}', {'user': (d.get('user') or {}).get('login'), 'created_at': d.get('created_at'), 'issue_url': d.get('issue_url'), 'html_url': d.get('html_url'), 'error': d.get('error')})
for f in ('CITATION.cff',):
    d = gh(f'repos/leanprover-community/mathlib4/contents/{f}?ref=d13f23b723b8a846827a245b89c10fc7d3f11612')
    save('mathlib4-citation-cff', f'gh api repos/leanprover-community/mathlib4/contents/{f}?ref=d13f23b...', pick(d, ['path', 'sha', 'download_url']) if 'path' in d else d)
for aid in ('2610.15483', '2610.08144'):
    t = get(f'https://arxiv.org/abs/{aid}v1')
    title = re.search(r'<h1 class="title mathjax">(.*?)</h1>', t, re.S); auth = re.search(r'<div class="authors">(.*?)</div>', t, re.S); dt = re.search(r'\[Submitted on ([^\]]*)\]', t)
    save('arxiv-' + aid, f'GET https://arxiv.org/abs/{aid}v1',
         {'title': html.unescape(re.sub('<.*?>', '', title.group(1))).strip() if title else None, 'authors': html.unescape(re.sub('<.*?>', '', auth.group(1))).strip() if auth else None,
          'submitted': dt.group(1) if dt else None})
for rid in ('23269528', '23499651', '23523697', '23505836', '23269527'):
    try:
        d = json.loads(get(f'https://zenodo.org/api/records/{rid}'))
        m = d.get('metadata', {})
        save('zenodo-' + rid, f'GET https://zenodo.org/api/records/{rid}', {'id': d.get('id'), 'doi': d.get('doi'), 'conceptdoi': d.get('conceptdoi'), 'title': m.get('title'), 'creators': [c.get('name') for c in m.get('creators', [])],
                                                                         'publication_date': m.get('publication_date'), 'version': m.get('version')})
    except Exception as e:
        save('zenodo-' + rid, f'GET https://zenodo.org/api/records/{rid}', {'error': str(e)[:200]})
d = json.loads(get('https://api.crossref.org/works/10.1112/S0010437X05001351'))['message']
save('crossref-fischler', 'GET https://api.crossref.org/works/10.1112/S0010437X05001351',
     {'title': d.get('title'), 'author': [(a.get('given'), a.get('family')) for a in d.get('author', [])], 'container': d.get('container-title'), 'volume': d.get('volume'),
      'issue': d.get('issue'), 'page': d.get('page'), 'issued': d.get('issued'), 'DOI': d.get('DOI')})
print('done', len(os.listdir(out)), 'files')
