# Packaging preparation

This repository contains preparation notes for a community-maintained Snap
package for Wireshark. It is not an official Wireshark Foundation repository.

The implementation is in `snap/snapcraft.yaml` and the cloud-only verification
pipeline is in `.github/workflows/snap.yml`. No Wireshark or generated Snap
artifact is built or installed on the development machine.

Research below was checked against official Wireshark and Snapcraft sources on
2026-09-10.

## Current upstream source

The initial packaging target is the official Wireshark 4.6.8 source release.
Wireshark announced 4.6.8 on 2026-08-12, and the Foundation's source index
lists the archive as a 54 MiB file last modified on that date.

| Field | Verified value |
| --- | --- |
| Release | `4.6.8` |
| Release announcement | [Wireshark 4.6.8 and 4.4.18 Released](https://www.wireshark.org/news/20260812.html) |
| Official archive | [`wireshark-4.6.8.tar.xz`](https://www.wireshark.org/download/src/wireshark-4.6.8.tar.xz) |
| Archive size in signed manifest | `56464692` bytes |
| Official checksum manifest | [`SIGNATURES-4.6.8.txt`](https://www.wireshark.org/download/SIGNATURES-4.6.8.txt) |
| Published verification key | [`gerald_at_wireshark_dot_org.gpg`](https://www.wireshark.org/download/gerald_at_wireshark_dot_org.gpg) |
| SHA-256 | `c0f1ccf217bc0d3b51a9c03ea178b0f7df682e475da26a2d21cd4a1bdd9579d0` |
| Upstream source repository | [`gitlab.com/wireshark/wireshark`](https://gitlab.com/wireshark/wireshark) |

The checksum above is transcribed from the Foundation-hosted, PGP-signed
manifest. The implementation must download the archive from the official
source URL, verify the manifest/signature using the published Wireshark public
key, and independently run `sha256sum` before the archive is accepted. The
local preparation phase did not download or build the archive; the cloud
workflow now obtains it only during the disposable Snapcraft build.

For a downstream release package, use the official source archive rather than
an arbitrary Git snapshot. The upstream Developer's Guide explicitly
recommends official source releases for downstream packaging.

## Build requirements

Upstream's Unix build requirements are:

- C and C++ compilers;
- Flex;
- Python 3;
- CMake;
- several required development libraries; and
- either Make or Ninja.

Documentation generation additionally needs Asciidoctor, Xsltproc, and
DocBook. Perl is used to generate some code and run some analysis checks.
Those documentation and analysis tools are not automatically required in the
runtime Snap and should not be staged unless the implementation deliberately
builds those artifacts.

The planned Snap build should use CMake with Ninja in an out-of-tree build.
The source tree ships a `ninja_ccache` CMake preset, but the first packaging
implementation should keep its configuration explicit and record any preset
decision in the implementation change.

The upstream Debian-family setup helper is useful as a dependency inventory:

```text
tools/debian-setup.sh --install-qt6-deps
```

It is reference material only here; it must not be run as part of this
documentation task or copied wholesale into Snap metadata.

For Snapcraft, keep the distinction clear:

- `build-packages` are compiler, CMake, Ninja, Flex, Python, headers, and
  other build-only inputs;
- `stage-packages` or a supported content snap provide runtime libraries; and
- source archives and their checksums are pinned inputs, not an implicit Git
  checkout.

The initial manifest derives its CMake switches from the 4.6.8 release and
keeps build-only inputs in `build-packages`. Runtime libraries are listed in
`stage-packages`; CI checks the resulting staged ELF/runtime layout and can
extend the closure when the cloud build exposes a real missing dependency.

## Qt 6 requirements

Wireshark must be built with Qt 6.2 or later. Upstream's Ubuntu example names
these packages as a starting point:

```text
qt6-tools-dev
qt6-tools-dev-tools
libqt6svg6-dev
qt6-multimedia-dev
```

Qt Multimedia is used for advanced RTP-player controls and may be optional for
the first GUI milestone; keep it enabled only if the build and runtime
requirements justify it. The final Snap build must also account for the
non-Qt libraries required by Wireshark, including GLib and libpcap, plus any
features intentionally enabled.

The manifest explicitly selects `USE_qt6=ON` and uses the `kde-neon-6`
extension for the Qt desktop runtime. The implementation must record the
resolved Qt version and confirm that the runtime libraries used by Wireshark
come from the selected Snap build/runtime inputs.

## Base and KDE neon 6 extension

`core24` plus the `kde-neon-6` extension is suitable as the initial design for
the Qt 6 desktop application:

- Snapcraft documents `kde-neon-6` as supported with `core24` and `core22`;
- the core24 variant supplies Qt 6 and KDE Frameworks 6 build/runtime
  content; and
- the extension is designed for C++ Qt/KDE applications and supplies the
  desktop integration environment.

The extension is attached to the GUI app and adds content connections and
application plugs for the desktop stack, including `desktop`,
`desktop-legacy`, `opengl`, `wayland`, `x11`, `audio-playback`, `unity7`,
`network`, and `network-bind`. The implementation must inspect
`snapcraft expand-extensions` output before adding any duplicate manual plugs.

This is a GUI/runtime suitability decision, not a packet-capture decision.
The extension does not grant raw network capture privileges, does not make
`dumpcap` root-capable, and does not justify classic confinement.

## Strict-confinement plan

The target is `confinement: strict`.

The GUI, TShark, and offline-analysis utilities must run as ordinary users.
The package must not launch Wireshark or TShark as root, must not request
classic confinement as a shortcut, and must not ship a fake or invented
`common-id` for command-line utilities. Use upstream's desktop metadata when
the desktop entry is implemented; the upstream desktop ID is
`org.wireshark.Wireshark`.

The implementation separates these acceptance levels:

1. GUI launch and offline capture-file analysis.
2. Command-line dissection and file utilities.
3. Live capture through `dumpcap` as an ordinary user.

Levels 1 and 2 must not be described as proving level 3. If strict live
capture cannot be made to work with a narrowly justified Snap interface, the
Snap must report capture as unavailable rather than silently running as root,
using host binaries, or claiming support. Any future host helper or daemon
would require a separate security design, an authenticated/mediated IPC
boundary, and explicit Store review; it is outside this preparation scope.

## `dumpcap` privilege model

Wireshark's own security model isolates raw adapter access in `dumpcap` so the
GUI and dissectors can run with normal user privileges. Upstream prefers Linux
file capabilities (`CAP_NET_ADMIN` and `CAP_NET_RAW`) over a setuid-root
`dumpcap` for conventional Linux packages.

That conventional package model cannot simply be copied into a strict Snap:

- a setuid-root executable inside the Snap is not an acceptable design;
- the Snapcraft forum records that file capabilities were not supported for a
  normal non-service Snap application; and
- the current public interface catalogue has no `network-monitoring`
  interface.

Therefore Qwen must not add a `dumpcap` app with a made-up `common-id`, must
not use `process-control` as a substitute for capture privileges, and must not
claim that the `network` interface captures packets. The implementation must
test the smallest viable strict interface set and document the exact observed
denial if live capture remains blocked.

## Minimal initial interfaces

Start from the interfaces automatically introduced by `kde-neon-6`, then add
only what a tested feature needs:

| Interface | Initial decision | Reason |
| --- | --- | --- |
| `desktop`, `desktop-legacy`, `wayland`, `x11`, `opengl` | Use the KDE neon 6 extension surface | GUI integration; avoid duplicate declarations until expansion is inspected |
| `network` | Use only for client network access actually used by the app | Auto-connected and does not provide raw capture |
| `home` | Requested by the GUI and file-oriented CLI apps | File access for normal user documents and capture files |
| `network-observe` | Do not add initially | Read-only network status is not packet capture and is not needed until a concrete feature proves it |
| `network-control` | Do not add initially; test only as a narrowly scoped capture hypothesis | Broad, privileged networking access; auto-connect is off and Store review may be required |
| `process-control`, `pstore`, `removable-media`, `raw-usb`, `system-observe` | Do not add initially | No current requirement in the preparation scope |

There is no `network-monitoring` interface in the current Snapcraft interface
catalogue. `network-control` enables broad configuration of networking and
network namespaces; it is not a Wireshark-specific capture permission. Any
request to connect it automatically must include evidence from a strict test,
the smallest affected app, and a Store-review justification.

## Planned commands and utilities

These are the commands exposed or used by the implementation and its cloud
verification workflow:

### Source and reproducibility

- `curl` or `wget` to retrieve the official archive and signed manifest;
- `gpg --verify` against the published Wireshark public key;
- `sha256sum` to verify the pinned SHA-256;
- `git ls-remote` only when comparing an upstream Git tag, never as a
  replacement for the signed release archive.

### Snapcraft

- `snapcraft extensions` to confirm available extension/base combinations;
- `snapcraft expand-extensions` to audit the generated interface/content
  surface;
- `snapcraft lint` and `snapcraft pack` in the cloud build;
- `sudo snap install <file>.snap --dangerous` only on a disposable CI runner;
- `snap connections <snap-name>` to record actual interface connections;
- `snappy-debug` or equivalent journal/AppArmor inspection to identify
  denials, without treating a devmode run as acceptance evidence.

### Wireshark build and runtime checks

- `cmake -G Ninja` or the reviewed CMake preset;
- `ninja`, `ninja test`, and selected `ninja` targets;
- `wireshark`, `tshark`, `dumpcap`, `capinfos`, `editcap`, `mergecap`, and
  `text2pcap` as separate, least-privileged entry points;
- `dumpcap -D` and `tshark -D` to enumerate capture devices;
- `readelf`, `ldd`, and `file` to audit staged binaries and runtime linkage;
- `getcap` and `stat` to prove that no unreviewed privilege bit or capability
  was smuggled into the package.

The workflow also generates a deterministic Ethernet/IPv4/UDP pcapng fixture,
checks `tshark` fields and dissector registration, exercises the file utility
commands, starts the GUI under Xvfb, records `snap connections`, and inspects
kernel AppArmor observations. Interface enumeration and a bounded loopback
capture are recorded as evidence; an unavailable capture path is reported as
a strict-CI limitation rather than converted into a privileged package.

Snap app commands other than the primary GUI are invoked as
`wireshark.tshark`, `wireshark.dumpcap`, `wireshark.capinfos`,
`wireshark.editcap`, `wireshark.mergecap`, `wireshark.text2pcap`, and
`wireshark.reordercap`. Unqualified aliases are intentionally not requested:
default aliases require Snap Store review and this project has not entered the
Store process.

## Current CI evidence

[GitHub Actions run 34490796508](https://github.com/iamaritrasaha/wireshark-snap/actions/runs/34490796508)
and [run 34500118063](https://github.com/iamaritrasaha/wireshark-snap/actions/runs/34500118063)
verified the signed upstream manifest, built the source successfully, uploaded
`wireshark_4.6.8_amd64.snap`, and installed and removed that exact artifact on
a fresh runner. The GUI `--version` check reported Wireshark 4.6.8 with Qt
6.11.1. Smoke testing then exposed CLI runtime linkage requirements: CLI apps
require a Snap-local `LD_LIBRARY_PATH` and `PATH`, directory environment variables
(`WIRESHARK_DATA_DIR`, `WIRESHARK_PLUGIN_DIR`, `WIRESHARK_EXTCAP_DIR`), and the
asynchronous DNS resolver library `libc-ares2` (linking `libcares.so.2`), which
CMake discovers from the SDK environment during compilation.

The manifest now gives each CLI app the required library search paths, stages
`libc-ares2` and `libnl-route-3-200`, and sets the Wireshark directory environment
variables across all apps. Full verification across dissectors, plugins,
offline capture-file parsing, and interface enumeration proceeds in cloud CI.

## Update strategy

Until reproducible packaging and acceptance tests exist, updates are manual:

1. Monitor the official Wireshark release/news and security information.
2. Select a specific official source archive, signed manifest, version, and
   checksum.
3. Review upstream release notes and dependency changes.
4. Update the pinned source metadata and build inputs together.
5. Re-run provenance, build, interface, offline-analysis, and live-capture
   checks before considering a revision.

Once a Store release exists, use the normal Snap risk levels: `edge` for
development revisions, `beta` for broader testing, `candidate` for release
verification, and `stable` for the supported user release. Promote a tested
revision rather than rebuilding the same source separately for each channel;
use progressive release for a first or high-risk stable update. Snapd then
refreshes installed Store snaps automatically according to the user's refresh
policy.

The current workflow does not contain Store credentials or publication
commands. It builds and uploads a CI artifact only; it does not register a
Store name, upload to the Store, or release any channel.

## Source references

- [Wireshark 4.6.8 release announcement](https://www.wireshark.org/news/20260812.html)
- [Wireshark source archive index](https://www.wireshark.org/download/src/)
- [Wireshark 4.6.8 signed checksums](https://www.wireshark.org/download/SIGNATURES-4.6.8.txt)
- [Wireshark Developer's Guide: Unix setup and build](https://www.wireshark.org/docs/wsdg_html_chunked/ChSetupUNIX.html)
- [Wireshark Developer's Guide: Qt](https://www.wireshark.org/docs/wsdg_html_chunked/ChLibsQt.html)
- [Wireshark Developer's Guide: binary packaging and privileges](https://www.wireshark.org/docs/wsdg_html_chunked/ChSrcBinary.html)
- [Snapcraft KDE neon extensions](https://documentation.ubuntu.com/snapcraft/stable/reference/extensions/kde-neon-extensions/)
- [Snapcraft source checksums](https://documentation.ubuntu.com/snapcraft/stable/reference/snapcraft-yaml/)
- [Snapcraft CMake plugin](https://documentation.ubuntu.com/snapcraft/en/latest/common/craft-parts/reference/plugins/cmake_plugin/)
- [Canonical Snapcraft build action](https://github.com/canonical/action-build)
- [Snap strict-confinement security policies](https://snapcraft.io/docs/explanation/security/security-policies/)
- [Snap interfaces reference](https://snapcraft.io/docs/reference/interfaces/)
- [Snap network interface](https://snapcraft.io/docs/reference/interfaces/network-interface/)
- [Snap network-observe interface](https://snapcraft.io/docs/reference/interfaces/network-observe-interface/)
- [Snap network-control interface](https://snapcraft.io/docs/reference/interfaces/network-control-interface/)
- [Snapcraft discussion: Wireshark and setcap](https://forum.snapcraft.io/t/wireshark-and-setcap/9629)
- [Snap channels and tracks](https://snapcraft.io/docs/explanation/how-snaps-work/channels-and-tracks/)
