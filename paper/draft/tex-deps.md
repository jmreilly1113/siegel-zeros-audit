# TeX dependencies not in the local TeX Live (2026-10-27)

- plainurl.bst: read-only fetch from CTAN, https://mirrors.ctan.org/biblio/bibtex/contrib/urlbst/plainurl.bst (served by ctan.math.illinois.edu), sha256 3fed7ca6a2db55121e4856952f5d89655500e47e8a35af18a88f63752812f183.
  It is part of urlbst 0.9.1 (Norman Gray; LPPL/GPL), a modification of plain.bst; see its header. Kept here so bibtex finds it in the build folder.
- lipics-v2021.cls: NOT available from CTAN. The CTAN package API has no "lipics", "lipics-v2021" or "dagstuhl" package (HTTP 200, "Not found"), and
  the CTAN file search for lipics-v2021.cls returns no file. Not fetched from elsewhere; the draft stays in the article class.
