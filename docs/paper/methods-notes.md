# Methods notes (paper Section 8: platform and runs)

## Update 2026-10-26: WSL memory during the extended replay

Source: results/2026-10-21-extended-replay/platform-change-wsl-24gb.txt, run.log, and the per-config final table
results/2026-10-26-nanoda-version-matrix/extended-replay-227/corpus-227.tsv (column wsl_memory_at_outcome;
`python -I scripts/extended_final_table.py . results/2026-10-26-nanoda-version-matrix/extended-replay-227`).

- COMPUTED: the WSL VM memory changed twice during the extended replay of the 227 unreferenced configs.
  - **Until 2026-10-21 13:56:21:** the Windows default, half of the PC's 31.9 GB, which is 15,965 MB. There was no .wslconfig. platform-change-wsl-24gb.txt records that "the 189 ran at ~16 GB".
  - **2026-10-21 13:56:21 (Joe's choice after Catalan's memory stop):** `.wslconfig` `memory=24GB`, then a restart. Afterwards free reported 24,037 MB. The run.log line is "stopped by hand for the WSL memory change ... WSL restarted (24,037 MB)".
  - **2026-10-22 08:10:32:** set to 20 GB, because Windows, not WSL, was the binding limit. Afterwards free reported 20,005 MB. This stayed in force to the end of the replay. The current `.wslconfig` reads `memory=20GB`.
  - Kernel, clone (fd4aeeb, clean), binaries, sandbox, timeouts and guard limits did not change at either restart.
- COMPUTED: the WSL memory in force when each outcome was recorded.
  - **Under the 15,965 MB default:** 3 results, ElementaryPositivity, KaplanskyDirectFiniteness and ShortEgyptianFractions. Catalan was stopped by the guard under the default, at a 14.2 GB nanoda high-water mark.
  - **Under 24 GB:** 32 results, listed in summary-227.txt.
  - **Under 20 GB:** 177 results.
- INFERRED: memory size changes no verdict unless a run runs out of memory. A config that completed here with a peak above ~14 GB would not have completed on the 189's platform. Every config's peak is recorded in runs/<C>-nanoda.mem.json.
- The nanoda version matrix of 2026-10-26 ran under the 20 GB VM, with each nanoda run capped at 16G (RAM plus swap) in its own v1 memory cgroup. See wsl-comparator/140_matrix_run.sh.
  - systemd 255 does not enforce MemoryMax in this cgroup-hybrid WSL. That was tested 2026-10-26: a 600 MB allocation under MemoryMax=200M ran to the end.
  - So the cap is set on the unit's v1 cgroup directly.

## Update 2026-10-26: network restriction of the sandbox

Each comparator run executed as the unprivileged user checker in a systemd-run unit whose seccomp filter (RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET) denied creating IPv4, IPv6, Unix-domain, netlink and packet sockets. A test on 2026-10-26 confirmed that TCP and UDP over IPv4 and IPv6, and DNS lookups, failed inside such a unit. AF_VSOCK sockets, which reach the Windows host, were not denied, and a test connection to the host succeeded. We did not test whether vsock offers a route to the internet. The earlier wording 'all network sockets blocked' overstated the restriction.

The corpus, extended-replay and version-matrix builds used a pre-fetched clone of openai/math at fd4aeeb (the SiegelZeros runs of 2026-10-08/09 used one at adc7f12), and 11 export sizes from the version matrix match an independent run (nealmcb's results/nanoda-ab-let.jsonl) to the byte.

- The SiegelZeros comparator result cited in the paper is the 2026-10-08 14:00 run, wsl-comparator/29_comparator_nanoda.sh: results/2026-10-08-lean-comparator-nanoda-netblock.txt, where both kernels accept. That was the first run under the deny list above. The earlier 12:15 run (08_comparator.sh) used the comparator README's wrapper, RestrictAddressFamilies=~AF_UNIX, which denies only Unix-domain sockets, so it is not cited for that claim.
- Comparator's landrun (`--best-effort`, no network flags) adds no network restriction on this 5.15 kernel. Tested: TCP and DNS succeed under landrun alone.
- Test and inventory: results/2026-10-26-network-check/ (README.md, inventory.md).

## Update 2026-10-27 (appended; Joe's drafting decisions): the fd4aeeb reroute clone

Source: results/2026-10-27-reroute-fd4aeeb/SUMMARY.md, run.log, control-prebuild.log, reroute-prebuild.log (`bash wsl-comparator/150_reroute_fd4aeeb.sh results/2026-10-27-reroute-fd4aeeb`).

- **Artifacts wording (use this, not "fresh clone"):** "local clone of fd4aeeb; package directory reused read-only from the original clone; OAI closure built from scratch."
  - COMPUTED: lean/.lake/packages (Mathlib and the other pinned packages, prebuilt) was bind-mounted read-only from /home/checker/math, and a write test as checker was refused. The packages were not rebuilt.
  - INFERRED (from how the kernels receive declarations, docs/paper/independence.md (a)): this does not weaken the kernel check. Both kernels re-typecheck every declaration in the export, Mathlib's included, whatever produced the .olean files. What it limits is the independence of the build, so "fresh clone" alone would overstate it.
- **Prebuild times: put both in the table.** Wall times are the sandbox units' "Service runtime" lines.

  | run | prebuild | jobs | comparator |
  |---|---|---|---|
  | control | 11 min 20 s (11min 19.935s) | 9,243 | 842 s |
  | reroute | 1 min 39 s (1min 39.395s) | 9,245 | 659 s |

  - The reroute ran in the same clone, after the control. It added the two PaperLemma3 modules and patched one file.
  - INFERRED: lake reused the control's build outputs and rebuilt only the new modules, the patched module and what depends on it, so the short time is expected, not an anomaly. reroute-prebuild.log lists only modules that printed warnings (e.g. "Built OAI.NumberTheory.SiegelZeros.PaperLemma3.Lemma3 (12s)"), so the full list of rebuilt modules is not recorded.
- **Scope sentence (at the import level, which is what was measured):** "Three further configurations load modules from a separate copy of this code (namespace OAI.Erdos970), with its own multiplicity estimate. The reroute concerns the SiegelZeros chain only."
  - COMPUTED: results/2026-10-26-claims-ledger/jacobsthal-import-scan.txt (Jacobsthal, JacobsthalImproved, OstmannPrimes; import closure, not declaration closure); the copy's own uniform_rectangular_multiplicity is cited in ledger-v2.tsv.
  - Not run: a declaration-level scan of whether those three proofs use the copy's Corollary 4. Skip it unless a reader asks.
- **Never cite results/2026-10-08-lean-main-rerouted.txt in the paper.** It belongs to the superseded `#reroute` metaprogram (lean-checks/README.md). Older write-ups still cite it: docs/writeup.md:108, 110, 114 and docs/lean-paper-map.md:20, 41. If the paper draws on those passages, take the claims from the comparator route instead:
  - results/2026-10-09-lean-comparator-rerouted-nanoda.txt;
  - results/2026-10-27-reroute-fd4aeeb/;
  - results/2026-10-08-lean-main-closure-cor4-usage.txt, for "exists_absolute_real_zero_gap does not use Corollary 4". This is also shown by "matches []" in the 2026-10-27 scans.
- **Release:** push the repo now. Hold the tag and the Zenodo deposit until the paper's final version, so the archived state is the one the paper cites.
