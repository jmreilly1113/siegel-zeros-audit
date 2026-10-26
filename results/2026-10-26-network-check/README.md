# Network-block check of the comparator sandbox, 2026-10-26

**Date:** 2026-10-26, 15:55–16:05 EDT.

**Platform:**
- WSL 2.4.11.0, kernel 5.15.167.4-microsoft-standard-WSL2, WSLg 1.0.65, Windows 10.0.26200.9711.
- Ubuntu-24.04 with systemd 255 (255.4-1ubuntu8.18). The cgroup setup is hybrid: the memory controller is on v1.
- The tests ran as the unprivileged user checker (uid 1000), launched by root through sudo, exactly as the run scripts do.

**Unit properties tested:**
- `67_corpus_run.sh:23`, `75_sbx.sh:11`, `107_run.sh:27`, `29_comparator_nanoda.sh:14`, `48_comparator_rerouted_nanoda.sh:20` and the matrix runner 140 all use:
  `systemd-run --user --property="RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET" --wait --pipe --collect ...`
- The matrix runner 140 is a system unit that drops to checker with setpriv.
- The user unit shows `NoNewPrivs: 1` and `Seccomp: 2` (filter mode) in /proc/self/status (t22_net.out).
- The first SiegelZeros comparator run (`08_comparator.sh`, 2026-10-08 12:15) instead used the comparator README's wrapper, `RestrictAddressFamilies=~AF_UNIX`. That wrapper blocks Unix-domain sockets only. Its network control in `wsl-comparator/28_netblock_probe.log` (2026-10-08) shows TCP to 1.1.1.1:443 open and `curl https://github.com` returning 200.

## Files

Each script was run as root in WSL (`bash <script> > /tmp/<name>.out 2>&1`); the matching `.out` is its verbatim output.

| Script | What it tests |
|---|---|
| `t22_net.sh` → `t22_net.out` | probes inside the unit, plus a control as checker outside any unit |
| `t23_interop.sh` → `t23_interop.out` | WSL interop (Windows .exe) inside the unit |
| `landrun_probe.sh` → `landrun_probe.out` | comparator's landrun arguments alone, no systemd unit |
| `comparator_landrun_args.sh` → `comparator_landrun_args.out` | comparator d03acab `Main.lean` landrun arguments, and whether the kernel exposes an LSM list |
| `t24_none.sh` → `t24_none.out` | the proposed `RestrictAddressFamilies=none` (it uses `t24_probe_block.txt`, the probe from t22) |
| `t24_diagnose_none.sh` → `t24_diagnose_none.out` | the man page entry, and which property forms systemd-run accepts |

## Results (COMPUTED)

| probe | inside the unit (`~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET`) | control, outside any unit |
|---|---|---|
| TCP connect 1.1.1.1:443 (Python; bash /dev/tcp) | blocked, errno 97 | connected |
| TCP over IPv6; UDP socket | blocked, errno 97 | not run |
| DNS: getaddrinfo, getent hosts, curl https://github.com | fail (name resolution) | resolves; curl HTTP 200 |
| AF_UNIX, AF_NETLINK, AF_PACKET sockets | blocked, errno 97 | not run |
| AF_BLUETOOTH, AF_TIPC, AF_RDS, AF_CAN, AF_XDP | errno 97 (not built into this kernel) | not run |
| **AF_VSOCK socket; connect to the Windows host, CID 2 port 50000** | **allowed; connected** | allowed; connected |
| AF_ALG (kernel crypto API, not a network family) | allowed | not run |
| WSL interop (cmd.exe, Windows curl.exe) | fails: WSL's launcher needs AF_UNIX ("UtilConnectUnix: socket failed 97"); the .exe never ran | not run |
| comparator's landrun alone (`--best-effort --ro / --rw /dev -ldd -add-exec`) | not applicable | TCP to 1.1.1.1:443 allowed, DNS resolves: landrun adds no network restriction on this 5.15 kernel |

**Not tested, by decision:** whether vsock offers any route to the internet. No vsock-to-internet path was attempted.

## Proposed tightening: `RestrictAddressFamilies=none`

- COMPUTED (`t24_none.out`, `t24_diagnose_none.out`): systemd 255's man page documents "none" ("all address families will be denied").
- But `systemd-run` rejects it as a transient-unit property: "Failed to start transient service unit: Failed to set unit properties: Invalid argument". This happens for user and system units.
- No unit started and no command ran, so nothing executed under a weaker setting.
- Forms that systemd-run accepts: `~`, the empty string, `AF_UNIX`, `~AF_VSOCK`.
- No tool test (lake build, lean4export, nanoda) could run under "none".

## Update 2026-10-26 16:40: full deny list (Joe's option A)

**Family list (COMPUTED).** The source is this kernel's include/linux/socket.h:
- microsoft/WSL2-Linux-Kernel tag linux-msft-wsl-5.15.167.4, commit 6ac7abbd97a07d5b0bc4bbdb0f3b364f8eb2a22b, fetched read-only through the GitHub API.
- Copy: kernel-5.15.167.4-include-linux-socket.h, sha256 15c2039a7d95cb45e91f8c9fa69571ea65cba5fc4e2156b103369ad3d2f57dc6; it is GPL-2.0 WITH Linux-syscall-note.
- AF_MAX is 46. These are the 45 defined families, without the aliases AF_LOCAL = 1 and AF_ROUTE = AF_NETLINK, and without AF_UNSPEC = 0:

1 AF_UNIX, 2 AF_INET, 3 AF_AX25, 4 AF_IPX, 5 AF_APPLETALK, 6 AF_NETROM, 7 AF_BRIDGE, 8 AF_ATMPVC, 9 AF_X25, 10 AF_INET6, 11 AF_ROSE, 12 AF_DECnet, 13 AF_NETBEUI, 14 AF_SECURITY, 15 AF_KEY, 16 AF_NETLINK, 17 AF_PACKET, 18 AF_ASH, 19 AF_ECONET, 20 AF_ATMSVC, 21 AF_RDS, 22 AF_SNA, 23 AF_IRDA, 24 AF_PPPOX, 25 AF_WANPIPE, 26 AF_LLC, 27 AF_IB, 28 AF_MPLS, 29 AF_CAN, 30 AF_TIPC, 31 AF_BLUETOOTH, 32 AF_IUCV, 33 AF_RXRPC, 34 AF_ISDN, 35 AF_PHONET, 36 AF_IEEE802154, 37 AF_CAIF, 38 AF_ALG, 39 AF_NFC, 40 AF_VSOCK, 41 AF_KCM, 42 AF_QIPCRTR, 43 AF_SMC, 44 AF_XDP, 45 AF_MCTP

Ubuntu's glibc header agrees on PF_MAX 46 and PF_MCTP 45. systemd-run accepted each name, one at a time and as a single list.

**Old and new properties:**
- Old: `RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET`
- New: `RestrictAddressFamilies=~` followed by all 45 names above, in that order. It is used by wsl-comparator/75d_sbx.sh, 140d_matrix_run.sh, 142d_matrix_batch.sh and 143d_matrix_export.sh. Each is identical to its 75/140/142/143 original except for this string, or for calling the d variant. 143d also takes LEAN_NUM_THREADS and the export directory from the environment.
- NoNewPrivs 1 and Seccomp 2 hold under the new property, in user and system units alike.

**t25_allfamilies** (t25_allfamilies.sh → t25_allfamilies.out, t25_inside_user_unit.out, t25_inside_system_unit.out, t25_control.out):
- The probe calls socket(f, type, 0) for f = 1..46 and type in SOCK_STREAM, SOCK_DGRAM, SOCK_RAW.
- Inside a user unit (75d) and a system unit (140d style, setpriv to checker), all 138 calls failed with errno 97 (EAFNOSUPPORT). None succeeded, and none failed differently. PASS.
- Control (checker, outside any unit): at least one socket() succeeds for families 1 (UNIX), 2 (INET), 10 (INET6), 16 (NETLINK), 24 (PPPOX) and 40 (VSOCK).
- Old vs new (t25_old_vs_new.out):
  - Under the old property, families 24 (AF_PPPOX, all three types) and 40 (AF_VSOCK, STREAM) succeed. So does 38 (AF_ALG) with SOCK_SEQPACKET.
  - Under the new property all three fail with 97, and they succeed in the control.
  - So the old filter also left AF_PPPOX and AF_ALG creatable.

**t26_denyall** (t26_denyall.sh → t26_denyall.out, t26_MinUncut-B3.log): t22 and t23 rerun under the new property, plus the tool tests:
- **t22 probes**, in both unit types: TCP and UDP over IPv4 and IPv6, DNS, AF_UNIX, NETLINK, PACKET, VSOCK create and connect to the host, ALG, BLUETOOTH, TIPC, RDS, CAN and XDP all fail with errno 97, or with name resolution failure for DNS.
- **t23 interop:** fails, at both the Unix and vsock steps.
- **Small lake build:** a fresh one-file project builds ("Build completed successfully (3 jobs)", T24.olean written).
- **Lake build in the clone:** OAI.Analysis.Laughlin.Main is a no-op ("Build completed successfully (10181 jobs)").
- **lean4export:** Laughlin, 433,770,627 bytes, sha256 842b632a…8523. That is identical to the 14:37 export made under the old property.
- **nanoda:** B3 on MinUncut through 140d passes (exit 0, 44 s, 997,124 kB).
- PASS.
