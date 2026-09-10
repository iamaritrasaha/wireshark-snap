# Wireshark Snap packaging

Community-maintained preparation for a possible Wireshark Snap. This is not an
official Wireshark Foundation repository, and no Snap Store release exists
from this project.

The current preparation target is the official Wireshark `4.6.8` source
release. The source provenance, SHA-256, Qt 6/build requirements, core24 and
KDE neon 6 assessment, strict-confinement plan, `dumpcap` privilege boundary,
minimal interfaces, Store implications, planned utilities, and update policy
are recorded in [docs/PACKAGING.md](docs/PACKAGING.md).

Security and capture acceptance requirements are in
[docs/SECURITY.md](docs/SECURITY.md), and future Store workflow constraints
are in [docs/STORE.md](docs/STORE.md).

This preparation phase intentionally does not include:

- `snapcraft.yaml`;
- GitHub Actions;
- a local Wireshark build or installation; or
- Snap Store upload or publication.

Do not treat compilation, offline dissection, or a devmode run as proof that
strictly confined live packet capture works. The `dumpcap` boundary requires
separate implementation and runtime evidence.
