# Qualification status

The PomAROS QEMU product is under preparation. The production macOS launcher
builds and has isolated profile/command/argument admission tests. It has no
vsock host service provider, host clipboard/file bridge or guest flush/quit
transport. The application requires an installed QEMU 11.

The product pins shared source candidate `b027ee4ecd` in `CORE.lock`; guest
full guest distribution builds and packages successfully; desktop acceptance is
tracked below. The former QuickPart UUID build failure is corrected. No full desktop,
network, persistent filesystem or shutdown stability is established by this
repository's host tests. Physical Apple/Raspberry Pi behavior is not tested.

Run artifacts belong in ignored `artifacts/`; test fixtures use temporary
profiles. Do not point tests at the default personal profile.

## 2026-10-16 preparation evidence

The Swift launcher builds and is ad-hoc signed. Seven production-host tests
pass: disk preservation/path encoding, exclusive profile locks, symlink refusal,
explicit acceleration selection, protected diagnostic QMP endpoints and guest
packaging admission. The QMP supervisor protocol also rejects errors and
disconnection while correctly handling asynchronous events.

A two-second paused TCG construction run using the production command's whole
device set passes on QEMU 11.0.1. It executes no guest code and establishes only
machine/device option admission. Evidence is
`artifacts/construction-smoke/result.json`; real HVF guest acceptance is pending.
The test uses a private scratch disk, firmware and profile.


The private shared source and tooling pins are reachable in their private
origins. Their availability establishes reproducible preparation inputs rather
than a usable persistent-data release. Closing QEMU cannot be advertised as a
safe guest flush; the guest and host shutdown path is tracked in [TODO.md](../TODO.md).


The shared candidate's headless core bundle has now passed real windowed
QEMU/HVF and Virtualization.framework core ABI/DOS/FDT/timer/IRQ checks. Their
bundle SHA-256 is identical (`6abba4b73af8c513404ff88b633498c39b2db630e3f9bbb207fb3aba734ca829`).
The QEMU run qualifies independent QMP register access before guest execution.
Evidence is retained in the VM tooling repository's ignored
`artifacts/common-core-regression.json`. This establishes the common guest core
on both engines. The fresh complete desktop application packages with 3863
runtime files, EFI, required firmware and license materials.

## Fresh desktop evidence

The first normal-window HVF run aborts QEMU 11.0.1 inside its MMIO handler at
`assert(isv)` after xHCI instantiation. A deliberate LLDB reproduction proves
paused QMP access before execution, then captures guest PC `0x538604f0` with
`hv_vcpu_get_reg` returning success on the CPU's owning thread. The final trace
is a read at VA/IPA `0x8000014004` with ISV=0. The exact guest instruction is
under source diagnosis; it is not inferred from the host assertion alone.
Crash report, exact binary hash, backtrace and MMIO trace are retained in
`artifacts/desktop-hvf/` and `artifacts/desktop-hvf-lldb/`.

One explicit TCG comparison reaches stable desktop, two USB bindings and GPU
IRQ completion. Its screenshot shows Wanderer, Shell and the existing debug
statistics window. The strict pixel heuristic rejects that geometry, so its
overall verdict is FAIL rather than accepted desktop functionality. Evidence:
`artifacts/desktop-tcg/`. No network or persistent shutdown acceptance follows
from these tests. All runs use private scratch profiles and normal windows.

The QMP supervisor's broken-pipe cleanup path has a regression test; a host
abort now yields a final failure verdict and cleans up the app's error dialog.
