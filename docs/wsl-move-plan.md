# Plan: move the WSL distro to D:

Prepared 2026-10-11 for Joe to run. Claude prepared it but does not run it. Script: `scripts/wsl-move.ps1`. Run it in an elevated Windows PowerShell terminal, one confirmed step at a time.

**Status (2026-10-11): deferred.** Joe decided not to run the move yet. The headline batch runs on C: instead. Nothing in this plan has been run.

## Current state (computed 2026-10-11)

| Item | Value |
|---|---|
| WSL | 2.4.11.0, kernel 5.15.167.4-1, Windows 10.0.26200 |
| Distros | `Ubuntu-24.04` (the one to move) and `docker-desktop` (stopped; not touched) |
| Disk image | `C:\Users\Work\AppData\Local\wsl\{beda3264-2b75-4d2c-b8d2-931eeb830b69}\ext4.vhdx`, 43.1 GB, not sparse |
| Inside WSL | 41 GB used; `/home/checker/math` is the clone at adc7f12, with origin/main fd4aeeb fetched |
| Default user | root (registry DefaultUid 0). Our scripts always pass `-u root` and switch to `checker` with sudo. |
| `checker` | uid 1000, lingering enabled (`loginctl` Linger=yes), needed for `systemd-run --user` |
| `/etc/wsl.conf` | only `[boot]` with `systemd=true`. There is no `[user]` section, so nothing else needs to survive. |
| D: | NTFS, 298.1 GB, 230.7 GB free, Seagate FreeAgent Desktop over USB (external hard drive) |
| C: | 59.5 GB free |

Space on D: needs the moved image (43 GB) plus the replay at fd4aeeb (~115 GB, an estimate). That is ~158 GB, leaving ~70 GB of margin if the backup export goes to C:. With the backup on D: as well (~41 GB), the margin is only ~30 GB. The script therefore defaults to `C:\wsl-backup`. C: has room for the export, and gets the image's 43 GB back after the move.

Caveat (inferred): the external USB hard drive will be much slower than the internal SSD for builds. The drive must stay connected and awake while WSL runs. In Windows power settings, set "Turn off hard disk after" to Never and disable USB selective suspend for the duration.

## Steps

| Step | Command | Success looks like | Roll back |
|---|---|---|---|
| a | `wsl --version`; check that `wsl --help` lists `--move` | Version 2.4.11 and `--move` present. `--manage <distro> --move` arrived in the 2.3/2.4 releases; if `--help` does not list it, run `wsl --update` or use step f. | Nothing changed. |
| b | `wsl --shutdown` | `wsl -l -v` shows Ubuntu-24.04 Stopped | Start it again with `wsl -d Ubuntu-24.04`. |
| c | `wsl --export Ubuntu-24.04 C:\wsl-backup\Ubuntu-24.04-<date>.tar` | The command finishes without error | Delete the partial tar. The distro is unchanged. |
| d | Check the tar's size | Roughly 35-45 GB; the script stops below 20 GB | Re-export. |
| e | `wsl --manage Ubuntu-24.04 --move D:\WSL\Ubuntu-24.04` | `D:\WSL\Ubuntu-24.04\ext4.vhdx` exists at about 43 GB, the old C: image is gone, and the distro starts | If the move fails, the distro normally stays at its old location. If it is left broken: `wsl --unregister Ubuntu-24.04`, then `wsl --import Ubuntu-24.04 C:\Users\Work\AppData\Local\wsl\restore C:\wsl-backup\<tar>` (from the step-c backup). |
| f (fallback, only if e is unavailable) | `wsl --import Ubuntu-24.04-D D:\WSL\Ubuntu-24.04 <tar>`, run the checklist below against `Ubuntu-24.04-D`, then `wsl --unregister Ubuntu-24.04` | The imported distro passes the checklist. Its default user is root, matching today's DefaultUid 0, and `/etc/wsl.conf` comes with the tar, so systemd stays on. | Before the unregister: `wsl --unregister Ubuntu-24.04-D` removes the copy, and the original is untouched. **The unregister of the original is DESTRUCTIVE AND IRREVERSIBLE. It deletes the C: image. Only run it after the checklist passes on the copy.** Afterwards the only rollback is re-importing from the tar. |
| g | `wsl -d Ubuntu-24.04` (or `-D` after the fallback) | systemd is PID 1, `/home/checker` is present, `wsl -l -v` shows the distro, and the C: image path no longer exists | If the C: image is still there after a successful move, delete it only after the checklist passes. |

Keep the backup tar until the checklist below has passed and the first headline-batch build has run.

## Verification checklist for the session after the move (Claude runs this, Part D step 1)

1. Default user is root (`whoami` without `-u` prints root), and `checker` exists with uid 1000.
2. systemd is running: `ps -p 1 -o comm=` prints systemd, and `systemctl is-system-running` reports running (or degraded, with the failed units listed).
3. `systemd-run --user` works for checker, and `loginctl show-user checker -p Linger` shows yes.
4. The network-block wrapper still blocks TCP, UDP and Unix sockets: rerun `wsl-comparator/28_netblock_probe.sh` and compare with `28_netblock_probe.log`. Inside the wrapper, TCP 1.1.1.1:443, curl github.com, the UDP socket and the Unix socket must all fail.
5. The clone is at the expected commit with a clean status (`git -C /home/checker/math rev-parse HEAD`; `git status --short` is empty). The build outputs are present (4,254 OAI `.olean` files).
6. The image is on D: (`df` in WSL; `D:\WSL\Ubuntu-24.04\ext4.vhdx` exists), and the guards are switched: `wsl-comparator/72_corpus_guard_d.sh` (watches D: free, floor 25 GB) replaces `69_corpus_guard.sh`, and the Windows-side monitor checks D: instead of C:.
7. SiegelZeros still accepts from the existing build: `wsl-comparator/67_corpus_run.sh SiegelZeros /home/checker/corpus/configs/SiegelZeros-nanoda.json 7200 <log>`, which must show both kernels accepting, "Your solution is okay!" and exit 0.

## Guard changes to apply after the move (prepared, not applied)

- `wsl-comparator/72_corpus_guard_d.sh` replaces `69_corpus_guard.sh` in the batch driver. It stops the build if D: free space falls below 25 GB, in place of the fixed 42 GB WSL-usage cap that protected C:.
- The Windows-side monitor keeps its free-RAM check (3 GB). Its disk check moves from `df /c` to `df /d`.
- `66_disk_watchdog.sh` (42 GB cap) is not used after the move.

## Update 2026-10-26 (appended; earlier text unchanged): network block

Each comparator run executed as the unprivileged user checker in a systemd-run unit whose seccomp filter (RestrictAddressFamilies=~AF_UNIX AF_INET AF_INET6 AF_NETLINK AF_PACKET) denied creating IPv4, IPv6, Unix-domain, netlink and packet sockets. A test on 2026-10-26 confirmed that TCP and UDP over IPv4 and IPv6, and DNS lookups, failed inside such a unit. AF_VSOCK sockets, which reach the Windows host, were not denied, and a test connection to the host succeeded. We did not test whether vsock offers a route to the internet. The earlier wording 'all network sockets blocked' overstated the restriction.

Test and inventory: results/2026-10-26-network-check/ (README.md, inventory.md).
