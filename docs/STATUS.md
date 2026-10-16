# Qualification status

The PomAROS QEMU product is under preparation. The production macOS launcher
builds and has isolated profile/command/argument admission tests. It has no
vsock host service provider, host clipboard/file bridge or guest flush/quit
transport. The application requires an installed QEMU 11.

The product pins shared source candidate `b027ee4ecd` in `CORE.lock`; guest
package/desktop acceptance is pending that common build. Earlier VM audit failures (QuickPart UUID
header and ELF loader crash) are separate unresolved work. No full desktop,
network, persistent filesystem or shutdown stability is established by this
repository's host tests. Physical Apple/Raspberry Pi behavior is not tested.

Run artifacts belong in ignored `artifacts/`; test fixtures use temporary
profiles. Do not point tests at the default personal profile.

## 2026-10-16 preparation evidence

The Swift launcher builds and is ad-hoc signed. Six production-host tests
pass: disk preservation/path encoding, exclusive profile locks, symlink refusal,
explicit acceleration selection, protected diagnostic QMP endpoints and guest
packaging admission.

A two-second paused TCG construction run using the production command's whole
device set passes on QEMU 11.0.1. It executes no guest code and establishes only
machine/device option admission. Evidence is
`artifacts/construction-smoke/result.json`; real HVF guest acceptance is pending.
The test uses a private scratch disk, firmware and profile.


The private shared source and tooling pins are reachable in their private
origins. Their availability establishes reproducible preparation inputs rather
than a usable persistent-data release. Closing QEMU cannot be advertised as a
safe guest flush; the guest and host shutdown path is tracked in [TODO.md](../TODO.md).
