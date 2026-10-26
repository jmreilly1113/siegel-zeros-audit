# Draft corrections for the published records (2026-10-26). NOT POSTED; nothing external was edited.

The old sentences were read from https://zenodo.org/api/records/<id> on 2026-10-26 (description field, HTML stripped). The replacement wording follows the repo edit of the same day: "IP and Unix-domain sockets blocked by a seccomp filter; see the 2026-10-26 network note."

The "network note" would be results/2026-10-26-network-check/README.md at a pushed commit. Replace `<NOTE-URL>` with that link.

## 10.5281/zenodo.23499651 (reviewer-packet-v2-preliminary)

- Old: "It contains: the official Lean FRO comparator rerun with nanoda as a second kernel and the network blocked;"
- New: "It contains: the official Lean FRO comparator rerun with nanoda as a second kernel, with IP and Unix-domain sockets blocked by a seccomp filter (see the 2026-10-26 network note, <NOTE-URL>);"

## 10.5281/zenodo.23523697 (reviewer-packet-v3)

- Old: "Contents: (1) the official Lean FRO comparator with nanoda as a second kernel accepts the family's Lean statements with standard axioms only, under a full network block;"
- New: "Contents: (1) the official Lean FRO comparator with nanoda as a second kernel accepts the family's Lean statements with standard axioms only (IP and Unix-domain sockets blocked by a seccomp filter; see the 2026-10-26 network note, <NOTE-URL>);"
- This is the same wording now in the repo's .zenodo.json and docs/zenodo-v3-metadata.json.

## 10.5281/zenodo.23505836 (corpus-replay-2026-10-20)

- Old: "Toolchain: Lean 4.34.1, Mathlib d13f23b, lean4export 076e8e5, landrun 811cfff, nanoda_lib 3a24072, on x86_64 WSL2 in a network-blocked systemd-run sandbox."
- New: "Toolchain: Lean 4.34.1, Mathlib d13f23b, lean4export 076e8e5, landrun 811cfff, nanoda_lib 3a24072, on x86_64 WSL2 in a systemd-run sandbox with IP and Unix-domain sockets blocked by a seccomp filter (see the 2026-10-26 network note, <NOTE-URL>)."

## 10.5281/zenodo.23269528 (reviewer-packet-v1)

The description has no network sentence. The packet files inside it do: README.md:7, docs/reproduce.md:45 and :103, and others (inventory.md). Zenodo does not allow a published file to change, so those can only be corrected in a new version.

## Optional sentence for each description, if a fuller statement is wanted

"A test on 2026-10-26 found that AF_VSOCK sockets, which reach the Windows host, were not denied by that filter; the deny list has since been extended to every address family of the kernel (<NOTE-URL>)."

## grwtsk/openai-math #40: one-line follow-up to our comment 6087525965 (draft)

> Follow-up to the sandbox line above: the `RestrictAddressFamilies` filter did not cover AF_VSOCK, which reaches the Windows host under WSL2 (a test connection succeeded; no route to the internet was tested). Details: <NOTE-URL>.
