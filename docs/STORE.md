# Snap Store preparation

No revision has been uploaded or published. This repository is community
maintained and does not represent the Wireshark Foundation.

## Store position

| Item | Current position |
| --- | --- |
| Store publication | Not started |
| Confinement target | Strict |
| Base design | `core24` with `kde-neon-6`, subject to build validation |
| Initial upstream target | Wireshark `4.6.8` |
| Snap Store name | Not registered or assumed here |
| Store credentials | Not added to the repository |
| GitHub Actions | Not created |

The Store name is globally unique and must be registered separately when
publication is authorized. Do not imply that the repository name guarantees
the Store name or that a Store listing already exists.

## Strict confinement and review

Strict confinement remains the release requirement. Snap Store review will
consider the requested plugs, their scope, and whether the application could
use a narrower interface. Classic confinement is not a fallback for this
project: it requires prior review, an explicit `--classic` install, publisher
vetting, and is not installable on Ubuntu Core.

The review narrative must be explicit about the packet-capture boundary:

- the GUI and dissectors run as ordinary users;
- upstream's privileged capture component is `dumpcap`;
- the package does not claim setuid or file-capability support inside the Snap;
- there is no current `network-monitoring` interface in the public interface
  catalogue; and
- any request for `network-control` must be based on observed strict-mode
  behavior, limited to the affected app, and accompanied by a reason why the
  feature cannot work with less access.

The KDE neon 6 extension automatically introduces the Qt desktop runtime and
its normal desktop plugs. The implementation must attach the expanded
metadata and explain any manual plug that is not already supplied by the
extension.

`network` and `network-bind` are auto-connected standard interfaces. A
`home` plug is appropriate only if the GUI must access non-hidden files in the
user's home directory. Sensitive or non-auto-connected interfaces should not
be requested for convenience.

## Pre-submission checklist

- [ ] `snapcraft.yaml` is created in a later, explicitly authorized change.
- [ ] The source archive, signed manifest, version, and SHA-256 are pinned.
- [ ] Upstream Wireshark and third-party licenses are preserved and reviewed.
- [ ] The upstream desktop entry and icons are used without inventing an
      application ID.
- [ ] Build-only dependencies are not shipped in the runtime payload.
- [ ] `snapcraft expand-extensions` output is reviewed.
- [ ] `snapcraft lint` is clean or every warning is explained.
- [ ] Strict GUI and offline-analysis tests pass as an ordinary user.
- [ ] `dumpcap` privilege behavior is tested and documented honestly.
- [ ] No unreviewed setuid bit, file capability, host binary, or arbitrary
      filesystem access is present.
- [ ] Store metadata does not claim official Wireshark authorship or support.
- [ ] A reviewer can reproduce the source and checksum decisions.

## Publication sequence for later use

Publication is intentionally out of scope now. When authorized, the planned
sequence is:

1. Register or confirm the Snap Store name and publisher identity.
2. Upload a tested revision without immediately promoting it to stable when
   additional testing is needed.
3. Use `edge` for implementation testing, `beta` for broader testing, and
   `candidate` for release verification.
4. Request only the Store capabilities and auto-connections justified by the
   final tested metadata.
5. Promote the same tested revision to `stable`, using a progressive release
   for a high-risk first release or privilege change.
6. Test installation from the Store on a host other than the build host.

Do not upload, release, request Store approval, or publish while this
preparation-only phase is in effect.

## Update policy

The update source is the official Wireshark release archive and signed
manifest, not an arbitrary branch or an unreviewed mirror. Each update must
include:

- the upstream version and release date;
- the signed-manifest URL and SHA-256;
- release-note and security-review notes;
- dependency/interface changes;
- offline and live-capture test results; and
- the proposed Snap risk channel.

After publication, Store revisions receive Snap's normal automatic refresh
behavior for the channel being tracked. Use channel promotion and progressive
release to control rollout; do not create a separate unofficial update
mechanism inside the application.

## Metadata rules

- Describe the package as community-maintained Snap packaging.
- Credit Wireshark Foundation and upstream contributors.
- Use the upstream license and preserve notices for bundled components.
- Keep the summary within Snapcraft's metadata limits.
- Do not invent download counts, support promises, publisher verification,
  release dates, fees, or official affiliation.
- Do not add command-line aliases or desktop associations until they are
  backed by the staged upstream metadata and tested behavior.

## References

- [Snapcraft publish a snap](https://snapcraft.io/docs/releasing-your-app/)
- [Snapcraft manage revisions and releases](https://documentation.ubuntu.com/snapcraft/latest/how-to/publishing/manage-revisions-and-releases/)
- [Snap channels and tracks](https://snapcraft.io/docs/explanation/how-snaps-work/channels-and-tracks/)
- [Snap Store review of classic confinement](https://snapcraft.io/docs/reference/administration/reviewing-classic-confinement-snaps/)
- [Snap super-privileged interfaces](https://snapcraft.io/docs/explanation/interfaces/super-privileged-interfaces/)
- [Snap interfaces reference](https://snapcraft.io/docs/reference/interfaces/)
- [KDE neon 6 extension](https://documentation.ubuntu.com/snapcraft/stable/reference/extensions/kde-neon-extensions/)
- [Wireshark source releases](https://www.wireshark.org/docs/wsdg_html_chunked/ChSrcObtain.html)
