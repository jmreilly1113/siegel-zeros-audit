# Inventory of network-block claims (2026-10-26)

Method:
- `git grep -n -i` for network, netblock and socket wording in the repo, excluding external/.
- The four published Zenodo records, read through https://zenodo.org/api/records/<id>, with their zip files downloaded and searched. Nothing was changed on Zenodo.
- Our comments on grwtsk/openai-math #40, read through `gh api repos/grwtsk/openai-math/issues/40/comments`. The brief said openai/math #40, but that issue does not exist (HTTP 404); our #40 comments are on grwtsk/openai-math (docs/issue40-facts.md line 1).
- Raw run logs and probe outputs (`INNER netblock ...` lines, `runs/*.log` "limits: ... network blocked") are measurement records, not prose claims. They are listed by class at the end and not edited.

## Which sandbox each set of runs used (COMPUTED from the scripts)

| runs | script(s) | property |
|---|---|---|
| first SiegelZeros comparator run, 2026-10-08 12:15 | wsl-comparator/08_comparator.sh | `RestrictAddressFamilies=~AF_UNIX`: comparator README's wrapper; Unix-domain sockets only |
| SiegelZeros + nanoda (2026-10-08 14:00), rerouted run (2026-10-09) | 29_comparator_nanoda.sh, 48_comparator_rerouted_nanoda.sh | `~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET` |
| corpus (189), pilot, discrepancy, post-fix, paper prep, extended replay (227) | 67_corpus_run.sh, 70, 73, 75_sbx.sh, 79, 98, 104, 105, 107_paperprep.sh / 107_run.sh, 108 | same as above |
| nanoda version matrix 2026-10-26 | 140_matrix_run.sh (system unit; setpriv to checker); exports through 75_sbx.sh | same as above |
| Lean/nanoda checks outside comparator, 2026-10-08/09 | 30, 32, 34, 36, 39, 49 | no systemd unit (not sandboxed; no network claim found for these) |

The 08 setup was checked: `wsl-comparator/28_netblock_probe.log` (2026-10-08) has its control. Under `~AF_UNIX` alone, TCP to 1.1.1.1:443 was OPEN, `curl https://github.com` gave 200, and a UDP socket was created. That wrapper did not block IP networking. The 29/48 setup uses the same property string as 67/75/107, so the 2026-10-26 test (README.md here) applies to it.

## Repo documents (an Update 2026-10-26 is appended to each, earlier text unchanged)

| file:line | exact sentence | setup described |
|---|---|---|
| README.md:22 | "The official Lean FRO comparator, rerun with nanoda as a second, independently written kernel and with network access blocked, accepts both challenge theorems with only the standard axioms (...). The shipped configuration is re-run at adc7f12 under the full network block, ..." | 29 / 107 |
| README-corpus-replay.md:15 | "**Platform:** x86_64 WSL2, with each run in a network-blocked systemd-run sandbox as an unprivileged user." | 67 |
| docs/packet-v3/README-draft.md:24 | same sentence as README.md:22 | 29 / 107 |
| docs/packet-v3/release-notes-v3.md:33-44 | "## (d) Network block" ... "The full block applies from the nanoda run onward (2026-10-08, `29_comparator_nanoda.sh`, ...)." ... "INFERRED: v1's first-run result does not depend on network access." | 08 vs 29 |
| docs/v2-release-notes.md:35-46 | same section (d) as v3 | 08 vs 29 |
| docs/reproduce.md:45 | "This extends the README's AF_UNIX block to all network sockets. It matters on kernels below 6.7, where Landlock cannot restrict network access; WSL's 5.15 kernel has Landlock ABI 1. `28_netblock_probe.sh` shows that the block works." | 29 |
| docs/reproduce.md:103 | "the same sandbox (`systemd-run --user`, all network sockets blocked);" | 107 |
| docs/writeup.md:88 | "The sandbox also blocked all network sockets (IPv4/IPv6/netlink/packet, via seccomp; the block was shown to work beforehand) (`results/2026-10-08-lean-comparator-nanoda-netblock.txt`)." | 29 |
| docs/writeup.md:120 | "With the unmodified challenge file, our config copy (only `enable_nanoda: true` changed) and the same sandbox and network block as 2.8, ..." | 48 |
| docs/tasks.md:47 | "(2026-10-08; ...; both kernels accept; network blocked by seccomp instead of a kernel update) 1+2. Comparator rerun with nanoda as a second kernel and a full sandbox" | 29 |
| docs/issue40-facts.md:23 | "Sandbox: `systemd-run --user` with `RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET`, as user `checker`. Source: ... (with the network-block probe)" | 29 / 48 (accurate as worded) |
| docs/paper/independence.md:50 | "landrun 811cfff (sandbox) and the systemd-run network block" | 67 |
| docs/wsl-move-plan.md:44 | "The network-block wrapper still blocks TCP, UDP and Unix sockets: rerun `wsl-comparator/28_netblock_probe.sh` ..." | 28/29 (accurate as worded) |
| docs/log.md:248, 339, 744 | "second kernel (nanoda) and network-blocked sandbox"; "same sandbox and network block as 29_comparator_nanoda.sh"; "The post-hoc SiegelZeros run shows uid 1000, no capabilities, network blocked, ACCEPT_BOTH." | 29 / 48 / 107 |
| results/2026-10-08-lean-comparator-nanoda-netblock.txt:1 | "# Official comparator with nanoda as a second kernel, network sockets blocked (plan steps 1+2)" | 29 |
| results/2026-10-11-corpus-pilot-summary.txt:2 | "... prebuilds each solution module with LEAN_NUM_THREADS=4 inside the same network-blocking systemd-run wrapper, ..." | 70 / 67 |
| results/2026-10-11-corpus-runas-findings.txt:36 | "Conclusion (COMPUTED for the probe, INFERRED for the pilot runs): the comparator runs as checker (uid 1000), unprivileged, no capabilities, no sudo, network-blocked." | 73 / 67 |
| results/2026-10-20-corpus-summary-final.md:20 | "Each comparator run ran as the unprivileged user `checker` inside a systemd-run unit with all network sockets blocked." | 67 |
| results/2026-10-20-nanoda-discrepancy/SUMMARY.txt:9 | "... exports and nanoda runs as the user checker in the corpus systemd-run sandbox, network blocked):" | 104 / 105 |
| results/2026-10-20-nanoda-postfix-f67473b/SUMMARY.txt:4 | "... each comparator run as the user checker in the same network-blocking systemd-run sandbox as the corpus runs" | 98 |
| results/2026-10-20-paper-prep/SUMMARY.txt:51 | "every run had the full network block, but the first comparator run (2026-10-08, script 08) blocked AF_UNIX only;" | 08 vs 29 / 107 |
| results/2026-10-20-paper-prep/task4-manifest-vs-v1.txt:33 | "v1: cannot restrict network access; WSL's 5.15 kernel has Landlock ABI 1. `28_netblock_probe.sh` shows that the block works." | 29 |
| results/2026-10-26-nanoda-version-matrix/MANIFEST.txt:33 | "... network blocked (RestrictAddressFamilies), timeout 1800 s, ..." | 140 |
| results/2026-10-26-nanoda-version-matrix/SUMMARY.md:12 | "Each nanoda run is direct (not through comparator), as checker, network-blocked, ..." | 140 |
| docs/paper/methods-notes.md | new paragraph added (item 6) | all |

Not network-block claims, so no update appended:
- docs/plan-remaining-gaps.md:28 ("The sandbox makes the filesystem read-only but does not block network or IPC"). This is accurate about landrun.
- docs/reviewer-packet.md:28 and docs/drafts/2026-10-20-issue40-corpus-comment.md:43 (they only cite the filename `-netblock.txt`).
- results/2026-10-08-lean-comparator-wsl.txt:3 (it states the `~AF_UNIX` command; no blocking claim).

JSON and YAML metadata in the repo (cannot take a prose appendix; to correct at the next deposit):
- `.zenodo.json` and `docs/zenodo-v3-metadata.json`: "... accepts the family's Lean statements with standard axioms only, under a full network block;"
- `CITATION.cff`: "... acceptance of the Lean formalization by the official comparator with two kernels (Lean and nanoda) under a network block;"
- `results/2026-10-20-corpus-zenodo/metadata.json`: "... on x86_64 WSL2 in a network-blocked systemd-run sandbox."
- `results/2026-10-20-paper-prep/manifest.json:65` and `results/2026-10-21-paper-prep-4/manifest-final.json:68`: "landlock": "kernel < 6.7: Landlock cannot restrict network (v1 reproduce.md); network blocked by seccomp instead".

## Published, for Joe to correct (nothing changed)

**Zenodo record descriptions** (API, read 2026-10-26):

| record | version | sentence |
|---|---|---|
| 10.5281/zenodo.23269528 | reviewer-packet-v1, 2026-10-09 | none in the description |
| 10.5281/zenodo.23499651 | reviewer-packet-v2-preliminary, 2026-10-20 | "It contains: the official Lean FRO comparator rerun with nanoda as a second kernel and the network blocked;" |
| 10.5281/zenodo.23523697 | reviewer-packet-v3, 2026-10-21 | "Contents: (1) the official Lean FRO comparator with nanoda as a second kernel accepts the family's Lean statements with standard axioms only, under a full network block;" |
| 10.5281/zenodo.23505836 | corpus-replay-2026-10-20 | "Toolchain: Lean 4.34.1, Mathlib d13f23b, lean4export 076e8e5, landrun 811cfff, nanoda_lib 3a24072, on x86_64 WSL2 in a network-blocked systemd-run sandbox." |

**Zenodo packet files** (zips downloaded and searched): the same sentences as the repo files above, as of each deposit.
- **v1 (12 hits):** README.md:7, docs/reproduce.md:45 and :103, docs/writeup.md:88 and :120, docs/tasks.md:47, docs/issue40-facts.md:23, docs/log.md:248 and :339, results/...nanoda-netblock.txt:1.
- **v2 (13 hits):** as v1, with README.md:15 and .zenodo.json.
- **v3 (34 hits):** every repo file in the table above that existed on 2026-10-21, plus .zenodo.json, CITATION.cff, docs/zenodo-v3-metadata.json and the corpus metadata.json.
- **Corpus zip (9 hits):** README.md:13 ("network-blocked systemd-run sandbox"), README-siegel-packet.md:11, docs/log.md:248 and :339, corpus-pilot-summary.txt:2, corpus-runas-findings.txt:36, corpus-summary-final.md:20, nanoda-discrepancy/SUMMARY.txt:9, nanoda-postfix-f67473b/SUMMARY.txt:4.

**grwtsk/openai-math #40, our comment 6087525965 (2026-10-09 19:10:40 UTC, not edited):**
- "It ran as an unprivileged user under `systemd-run --user` with `RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET`."
- "A probe in the same file shows TCP, UDP and Unix sockets all failing under that wrapper, including in a grandchild process as landrun runs it."
- Both sentences are accurate as worded; they name the families tested and do not claim "all". What is missing: AF_VSOCK was not denied.
- Our other #40 comments (6109694404, 6291050955, 6307033041) contain no network or sandbox sentence.

## Raw measurement records (not edited)

These are outputs of the probes they name. They are accurate for the families they tested and say nothing about vsock:
- `INNER netblock ...` lines in results/2026-10-20-paper-prep*/wsl/*.log, results/2026-10-21-extended-replay/phase1/*, manifest-diff*.txt and manifest-*.json "netblock" blocks.
- The `limits: ... network blocked` line printed by 140 in results/2026-10-26-nanoda-version-matrix/runs/*.log.
