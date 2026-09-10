# Security plan

This is a community-maintained packaging project, not an official Wireshark
Foundation repository. The security plan is intentionally conservative because
packet capture can expose all traffic visible to a network interface.

## Security boundaries

- Target strict confinement.
- Keep the GUI and dissectors unprivileged.
- Keep `dumpcap` as the only Wireshark component that could require raw
  network privileges.
- Never run Wireshark or TShark as root.
- Never use classic confinement merely to bypass a missing interface.
- Never bundle or invoke an untracked host `dumpcap`, `tshark`, or Wireshark
  binary.
- Treat a devmode run as diagnostic evidence only, never as release evidence.

Wireshark upstream states that functions requiring elevated privileges belong
in `dumpcap`. It documents Linux capabilities as preferable to setuid for
traditional packages, but a strict Snap must not assume that a traditional
file-capability or setuid installation recipe remains valid inside the Snap
sandbox.

## Capture security decision

The first implementation must prove live capture as a separate acceptance
level. It must record:

- which app requested the capture;
- which interface is connected;
- the effective UID/GID and capabilities of `dumpcap`;
- the AppArmor/seccomp result;
- the exact capture-device enumeration result; and
- a real, user-initiated capture with generated traffic.

If the strict interface model cannot provide capture, the package must retain a
truthful "offline analysis available; live capture unavailable" state. Do not
weaken confinement or add a broad interface without evidence and review.

A future helper/daemon is not pre-approved by this document. It would need a
small, authenticated IPC protocol, strict input validation, clear ownership of
the capture file/socket, controlled privilege dropping, lifecycle cleanup, and
an explicit Snap Store review record.

## Interface least privilege

The initial interface set is documented in [PACKAGING.md](PACKAGING.md). In
particular:

- the KDE neon 6 extension supplies the expected Qt desktop integration;
- `network` is ordinary outbound client access, not raw packet capture;
- `home` is only for normal non-hidden user files when open/save requires it;
- `network-observe` is not a capture permission;
- `network-control` is broad privileged networking access and is not an
  initial default;
- `process-control`, `pstore`, `raw-usb`, `removable-media`, and system
  observation interfaces are not justified by this application baseline.

Avoid top-level plugs that apply sensitive permissions to every app. Apply a
permission to only the app that needs it, and request automatic connection
only when the feature and Store policy justify it.

## Data handling

Packet captures can contain credentials, personal data, and contents of
private communications. The implementation should:

- write temporary and generated capture data under Snap-writable per-user
  locations unless the user explicitly chooses another permitted location;
- avoid telemetry and network upload by default;
- avoid copying captures into logs or crash reports;
- make file permissions and retention behavior explicit; and
- ensure command-line utilities do not print packet payloads unless the user
  asked for them.

The package must not put credentials or secrets in environment variables,
Snap metadata, source URLs, or build logs.

## Supply-chain controls

For every upstream update:

1. Obtain the source archive and signed manifest from Wireshark's official
   download service.
2. Verify the PGP signature using the public key published by Wireshark.
3. Verify the exact SHA-256 recorded in the manifest.
4. Review the upstream release notes and relevant security advisories.
5. Keep build-only and runtime dependencies distinct.
6. Inspect the staged file list and ELF dependencies before packaging.

The GitHub Actions workflow uses the official source URL and Snapcraft source
checksum during the cloud build. It does not store credentials, download an
unreviewed third-party binary, or publish to the Snap Store.

## Required future verification

The current cloud smoke workflow produces evidence for:

- source archive provenance and checksum;
- `snapcraft lint` with no unexplained errors;
- strict confinement and actual interface connections;
- absence of setuid bits and unexpected file capabilities;
- GUI launch without root;
- offline opening, filtering, and exporting of a capture file;
- command-line dissection without root;
- real `dumpcap` behavior, including the honest failure path if capture is not
  possible; and
- no orphaned helper or capture processes after exit.

The package is not security-accepted merely because it compiles or because a
synthetic capture-file test passes.

## References

- [Wireshark packet-capture architecture](https://www.wireshark.org/docs/wsdg_html_chunked/ChWorksCapturePackets.html)
- [Wireshark binary packaging and privilege options](https://www.wireshark.org/docs/wsdg_html_chunked/ChSrcBinary.html)
- [Snap confinement](https://snapcraft.io/docs/explanation/security/snap-confinement/)
- [Snap security policies](https://snapcraft.io/docs/explanation/security/security-policies/)
- [Snap interfaces](https://snapcraft.io/docs/reference/interfaces/)
- [Snap super-privileged interfaces](https://snapcraft.io/docs/explanation/interfaces/super-privileged-interfaces/)
- [Snapcraft discussion: Wireshark and setcap](https://forum.snapcraft.io/t/wireshark-and-setcap/9629)
