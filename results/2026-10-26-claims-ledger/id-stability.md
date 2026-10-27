# Ledger id stability check (2026-10-27)

Inputs:
- ledger.tsv (v1, 90 rows);
- ledger-v2.tsv (98 rows);
- gaps.md.

The comparison is by claim text. The row-by-row map is id-map-v1-v2.tsv, produced by an inline Python comparison of the two TSVs (`csv.DictReader`, match on the claim column). It was read-only; neither ledger was changed.

## Result (COMPUTED)

**Ids changed meaning between v1 and v2.** build_ledger.py numbers rows sequentially, so v2 renumbered every row after the first removed one.

- **L001-L049: same meaning.**
  - L032 is the same claim. It was reworded and its value filled when the PENDING row was closed.
  - L041 is unchanged in text; only its status changed.
- **L050 changed meaning.**
  - v1: "The reroute has not been run at openai/math fd4aeeb or under the 45-family deny list" (MISSING).
  - v2: "The reroute patch applies cleanly at fd4aeeb", which was v1 L051.
  - The v1 gap is closed in v2 by L095, L096 and L097.
- **L051-L078 now mean v1's L052-L079.** The shift is −1.
- **L079 changed meaning.**
  - v1: "No SiegelZeros comparator run exists under the 45-family deny list" (MISSING).
  - v2: "WSL memory changed from 24 GB to 20 GB at 2026-10-22 08:10", which was v1 L081.
  - The v1 gap is closed in v2 by L093 and L094.
- **L078-L088 now mean v1's L080-L090.** The shift is −2.
- **L089-L098 are new in v2.** In v1, L089 and L090 meant the toolchain pins and the nanoda pins; in v2 they mean the Jacobsthal copy and the Jacobsthal import scan.

So 41 ids (L050-L090) mean different things in v1 and v2.

## Files that cite an affected id (L050-L090)

Found with `grep -rnoE "\bL0(5[0-9]|[6-8][0-9]|90)\b"` over .md, .tsv, .txt, .py and .tex files, excluding external/ and .git/.

| file | lines | ids cited | which ledger | ambiguous? |
|---|---|---|---|---|
| results/2026-10-26-claims-ledger/gaps.md | 7, 8 | L050, L079 | v1 (the 2026-10-26 table, written for ledger.tsv) | yes, read against v2 |
| results/2026-10-26-claims-ledger/gaps.md | 30, 31 | L050, L079 | v1, labelled "v1 gap" in the table | no |
| results/2026-10-26-claims-ledger/gaps.md | 34, 35, 42 | L089, L090 | v2 (the 23:10 update, which says the ids were renumbered) | yes, read against v1 |
| results/2026-10-26-claims-ledger/LEDGER.md | 56, 57, 58 | L063, L064, L065 (failure classes 1-3) | v1; these are L062-L064 in v2, and L065 in v2 is the nealmcb 416/416 row | yes |
| results/2026-10-27-reroute-fd4aeeb/SUMMARY.md | 38 | L050, L079 ("Closed: ledger gaps ...") | v1, not labelled | yes. In v2, L050 is the patch-apply check and L079 is the WSL 20 GB change |
| paper/outline.md | many | L050-L098 | v2 | no (v2 ids are kept in v3) |
| paper/claim-map.tsv | all rows | L001-L098 | v2 | no |

No file in docs/ cites an affected id. These files are listed only; none was edited.

## Rule from now on

Ids are append-only. Never renumber.
- ledger-v3.tsv keeps every v2 id, claim, value and source byte-for-byte. Its first 12 columns equal ledger-v2.tsv row for row.
- New rows take explicit ids from L099 on.
- A row that is no longer wanted keeps its id and gets a status or use change. It is not deleted.
- build_ledger_v3.py enforces this: it asserts that the v2 ids are L001-L098 and that the new ids are consecutive from L099, and it refuses to overwrite.
- ledger.tsv and ledger-v2.tsv are left in place, unchanged.

## L079 resolved against L078 and the earlier record (COMPUTED)

The question was whether L079 means 20 GB from 2026-10-22 08:10 or 24 GB from 2026-10-21 13:56. Both events happened, and the sources agree on each. There is no disagreement, so this is not a STOP.

- **v2 L078 (= v1 L080): 24 GB from 2026-10-21 13:56:21.**
  - results/2026-10-21-extended-replay/platform-change-wsl-24gb.txt:6-7: ".wslconfig ... memory=24GB; wsl --shutdown; restart"; "free -m total 24,037 MB".
  - results/2026-10-21-extended-replay/run.log:30: "2026-10-21 13:56:21 stopped by hand for the WSL memory change ... WSL restarted (24,037 MB)".
- **v2 L079 (= v1 L081): 20 GB from 2026-10-22 08:10.**
  - platform-change-wsl-24gb.txt:14: "Second change, 2026-10-22 08:10 ...: WSL memory 24 GB -> 20 GB"; line 21: "free -m total 20,005 MB".
  - run.log:185: "2026-10-22 08:10:32 ... WSL memory 20 GB".
- **v1 L079 (neither memory claim):** "No SiegelZeros comparator run exists under the 45-family deny list", a MISSING gap. It is closed by v2 L093 and L094 (results/2026-10-27-reroute-fd4aeeb/).

The same sequence is in docs/paper/methods-notes.md ("Update 2026-10-26: WSL memory during the extended replay"): 15,965 MB default, then 24 GB from 2026-10-21 13:56:21, then 20 GB from 2026-10-22 08:10:32 to the end of the replay.
