# SiegelZeros control and reroute at openai/math fd4aeeb, under the 45-family deny list (2026-10-26 22:18 – 23:00)

Driver: `bash wsl-comparator/150_reroute_fd4aeeb.sh results/2026-10-27-reroute-fd4aeeb`, run as root in WSL Ubuntu-24.04 (sha256 dfa716ee7a510aa6…). A precheck run (PRECHECK=1) came first, testing the clone, mount and unmount.

Runners:
- 75r_sbx.sh (88172beb8f0e08ce…): a systemd-run --user unit as checker, for prebuilds and scans.
- 67r_corpus_run_capped.sh (45d70e515dd7037e…): a system unit that sets its own v1 memory cgroup to 16G (RAM plus swap), then drops to checker with setpriv and no_new_privs. Used for the comparator runs.

Both runners are identical to 75d/67d except that they take the clone directory as a parameter. They use the property RestrictAddressFamilies=~AF_UNIX AF_INET AF_AX25 AF_IPX AF_APPLETALK AF_NETROM AF_BRIDGE AF_ATMPVC AF_X25 AF_INET6 AF_ROSE AF_DECnet AF_NETBEUI AF_SECURITY AF_KEY AF_NETLINK AF_PACKET AF_ASH AF_ECONET AF_ATMSVC AF_RDS AF_SNA AF_IRDA AF_PPPOX AF_WANPIPE AF_LLC AF_IB AF_MPLS AF_CAN AF_TIPC AF_BLUETOOTH AF_IUCV AF_RXRPC AF_ISDN AF_PHONET AF_IEEE802154 AF_CAIF AF_ALG AF_NFC AF_VSOCK AF_KCM AF_QIPCRTR AF_SMC AF_XDP AF_MCTP: the 45 families of kernel 5.15.167.4 (results/2026-10-26-network-check/README.md).

Guard: 69_corpus_guard.sh 95 1500 20 ran throughout. It made no stops.

**The clone.**
- /home/checker/math-r2 is a local `git clone` of the clean /home/checker/math, so no network was used. It was checked out at fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb with 0 tracked changes.
- lake-manifest.json, lean-toolchain and lakefile.lean are byte-identical to the original's.
- lean/.lake/packages is bind-mounted READ-ONLY from /home/checker/math/lean/.lake/packages: the same pinned, prebuilt packages, with no extra disk. A write test as checker was refused. The mount was removed at the end (run.log).
- The OAI closure was built from scratch in the clone.

**Toolchain:** Lean 4.34.1, Mathlib d13f23b, Comparator d03acab (/usr/local/bin/comparator sha256 afa65e57…), lean4export 076e8e5, and the official nanoda 3a24072 (/usr/local/bin/nanoda_bin sha256 897971d7…, STACK_SIZE 16 MiB), which comparator takes from PATH.

**Config:** wsl-comparator/SiegelZeros-nanoda.json, the shipped SiegelZeros config with `enable_nanoda: true` as on 2026-10-08/09.

## Results (COMPUTED)

| step | log | exit | key lines | wall | peak memory |
|---|---|---|---|---|---|
| 0. MemoryMax test | memorymax-test.sh → memorymax-test.out | 0 | MemoryMax=200M: a 600 MB allocation was "not killed" in both the user and the system unit; the v1-cgroup cap killed it (inner exit 137) | seconds | – |
| control prebuild (4 threads) | control-prebuild.log | SANDBOX 0 | Build completed successfully (9243 jobs) | 11 min 20 s | – (guard only) |
| control comparator | control-comparator.log | COMPARATOR 0 | "nanoda kernel accepts the solution", "Lean default kernel accepts the solution", "Your solution is okay!" | 842 s | max RSS 7,707,508 kB; cgroup max_usage 7,412,195,328 B; oom_kill 0 |
| control scan (ReroutedDeps.lean d646d9bd…) | control-deps.log | SANDBOX 0 | dirichletRealZeroBound_proof: 116314 constants, matches actual_biquadratic_rectangle_span, uniform_rectangular_multiplicity, source_rectangle_span_of_polynomial_zero_test; exists_absolute_real_zero_gap: 107760, matches []; both depend on [propext, Classical.choice, Quot.sound]. **The block is identical, line for line, to 2026-10-09 (adc7f12).** | ~1 min | – |
| install and patch | reroute-diff.txt | 0 | installed PaperLemma3/Lemma3.lean 1ce196f5… and Bridge.lean af401514… (checked before and after install); git apply of the 10-09 patch; numstat 1 file +2/−1; challenge file sha256 bedaac02… unchanged | – | – |
| reroute prebuild | reroute-prebuild.log | SANDBOX 0 | Build completed successfully (9245 jobs) | 1 min 39 s | – |
| reroute comparator | reroute-comparator.log | COMPARATOR 0 | "nanoda kernel accepts the solution", "Lean default kernel accepts the solution", "Your solution is okay!" | 659 s | max RSS 7,662,352 kB; cgroup max_usage 6,280,855,552 B; oom_kill 0 |
| reroute scan | reroute-deps.log | SANDBOX 0 | dirichletRealZeroBound_proof: 92658 constants, matches Lemma3.actual_biquadratic_rectangle_span_via_lemma3 and Lemma3.interpolation; exists_absolute_real_zero_gap: 107760, matches []; standard axioms. **Identical to 2026-10-09.** | ~30 s | – |

**No STOP condition was hit:** no hash mismatches, the diff check passed, no build failed, and no scan differed.

**Closed:** ledger gaps L050 (the reroute at fd4aeeb under the deny list) and L079 (a SiegelZeros comparator run under the deny list).
