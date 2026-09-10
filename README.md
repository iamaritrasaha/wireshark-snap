# Wireshark Snap packaging

Community-maintained packaging for a Wireshark Snap. This is not an official
Wireshark Foundation repository, and no Snap Store release exists from this
project.

The current package target is the official Wireshark `4.6.8` source release.
The source provenance, SHA-256, Qt 6/build requirements, core24 and KDE neon 6
assessment, strict-confinement plan, `dumpcap` privilege boundary, interfaces,
Store implications, utilities, CI evidence, and update policy are recorded in
[docs/PACKAGING.md](docs/PACKAGING.md).

Security and capture acceptance requirements are in
[docs/SECURITY.md](docs/SECURITY.md), and future Store workflow constraints
are in [docs/STORE.md](docs/STORE.md).

The implementation is in [`snap/snapcraft.yaml`](snap/snapcraft.yaml), with
the cloud-only build and smoke-test pipeline in
[`.github/workflows/snap.yml`](.github/workflows/snap.yml). Local development
does not build, install, or run Wireshark; generated Snap artifacts remain in
GitHub Actions only.

The package uses strict confinement and does not run Wireshark or TShark as
root. Offline dissection is a separate acceptance level from live capture:
the CI workflow records `dumpcap` interface/capture results and does not add
broad interfaces merely to make a capture probe pass.
