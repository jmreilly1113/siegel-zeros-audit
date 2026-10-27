# Erratum: ledger ids in results/2026-10-27-reroute-fd4aeeb/SUMMARY.md (2026-10-27)

SUMMARY.md is not edited. Its line 38 reads:

> **Closed:** ledger gaps L050 (the reroute at fd4aeeb under the deny list) and L079 (a SiegelZeros comparator run under the deny list).

Both ids there are **v1** ids (ledger.tsv). They were renumbered in v2 (id-stability.md). Mapped through id-map-v1-v2.tsv:

| SUMMARY.md:38 | meaning (v1) | v2 / v3 / v4 row of the same meaning | rows that close the gap (v2 = v3 = v4 ids) | what the same id means from v2 on |
|---|---|---|---|---|
| L050 | v1:L050, MISSING: the reroute has not been run at fd4aeeb or under the 45-family deny list | none (a gap row; removed when closed) | v2:L095 (reroute comparator, ACCEPT_BOTH, exit 0), v2:L096 (reroute scan, 92658), v2:L097 (installed files, +2/-1) | v2:L050 = the reroute patch applies cleanly at fd4aeeb (v1:L051) |
| L079 | v1:L079, MISSING: no SiegelZeros comparator run under the 45-family deny list | none (a gap row; removed when closed) | v2:L093 (control comparator, ACCEPT_BOTH, exit 0), v2:L094 (control scan, 116314) | v2:L079 = WSL memory 24 GB -> 20 GB at 2026-10-22 08:10 (v1:L081) |

Read SUMMARY.md:38 as: "Closed: ledger gaps v1:L050 and v1:L079 (now v2:L095-L097 and v2:L093-L094)."

From 2026-10-27, every ledger id cited outside a ledger TSV names its version (v1:, v2:, v3:, v4:). Ids are append-only from v3, so v2:L001-L098, v3:L001-L130 and v4:L001-L139 agree wherever the id exists. Only v1 differs, for L050-L090.
