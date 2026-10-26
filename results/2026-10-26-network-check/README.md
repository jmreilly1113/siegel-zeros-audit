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
