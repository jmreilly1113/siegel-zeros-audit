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
