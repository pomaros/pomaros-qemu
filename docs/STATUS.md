# Qualification status

## Current common-core reference

`CORE.lock` selects common core `63de2673bec7b6c1c4226a7909ec9614d5cc4a91`;
`TOOLS.lock` selects shared VM tooling `70d2a5622afdfac4e4e822ad0097616a3a0f836c`.
The complete product passes the windowed HVF desktop gate in21.49 seconds,
with QMP and LLDB ready before guest execution, strict wallpaper/widget pixels,
two USB HID bindings and graphics IRQ completion. The seed is unchanged.
Evidence: `artifacts/consolidation-reference-hvf/verdict.json`.
The same core separately passes the shared two-CPU TCG Exec/x18/FPSIMD/timer/
wake/teardown scenario in29.02s. Network, file persistence, safe shutdown, real
input events, application GPU acceleration and physical Apple behaviour are
not established by the QEMU product gate.

## Shared guest build tools

TOOLS.lock selects `70d2a5622afdfac4e4e822ad0097616a3a0f836c`. The shared source-bound build driver and distribution
builder require GNU make 4 and preserve it across nested named make calls.
Actual response-file generation passes with a misleading old make earlier in
PATH; old/missing overrides and cleanup failures are covered. Eight backend
packaging tests and the source-pin test pass. The previous direct generated-file
build helper is removed in favor of the verified driver.
The shared runner also supports guest LLDB before execution, short QMP socket
paths and package-declared USB hardware, and refuses incompatible ESP/WORK
profiles. Its bounded two-core TCG Exec gate passes in 27.58 seconds in the
shared product's `artifacts/consolidation-shared-smp-handoff/`. This does not
relabel retained QEMU images, promote CORE.lock or qualify Apple hardware.

## Aligned common-core qualification

The preceding reference selected common main `afc0dbeefa12d65030ec0db8cd152a5518531913`.
The complete local product build and corrected default distribution pass.
The default distribution requires fd.library; its absence previously allowed
a desktop boot while native sockets refused with ENOSYS.

The corrected image passes the independent QMP/LLDB desktop gate in 20.71
seconds: unique valid UP CPU samples, GPU completion, two USB HID bindings,
strict wallpaper/widget pixels, unchanged seed and normal launcher exit.
Evidence: `artifacts/consolidation-descriptor-desktop/verdict.json`.
The same image passes the common Rust poll probe's six cases in 18.2 seconds
under TCG with a guest debugger attached before execution. That covers UDP,
invalid descriptors, real deadlines, stream hangup, pending-error preservation
and explicit refusal for pipe polling. It does not qualify general pipe
readiness, physical GPU hardware, applications or safe persistent shutdown.

The retained image used shared packaging implementation c37e211. Its later
verifier cohort was 525ae470c534a2c8fdf28381b6706c476b7de3b7, which corrects the VZ
production CPU-widget readiness check and requires a captured nonblank guest
viewport. Its desktop-contract tests pass. These VZ verifier changes do not
replace QEMU's pixel-exact desktop oracle or constitute another QEMU run.
The retained QEMU product and verdict keep their exact builder/source identities.

## Pre-export consolidation qualification

The complete fc028f product build/package passes. Its first independent QMP/LLDB
windowed run reaches accepted desktop, graphics completion and two HID bindings,
but remains FAIL: an obsolete kernel-widget marker is absent and CPUWidget
samples are unavailable. VM tools 6495dec correct the accounting clock origin
and introduce a separate strict user-space-widget oracle, passing offline
against the actual retained frame and eleven negative controls. A freshly
packaged runtime must confirm live sample readiness; no old run is relabeled.

The source pin selects the consolidated shared core at
`fc028f515e0d8b530b1da58ac036187c5ff133ed`; packaging tools select the reviewed
VM capacity merge at `dead213`. Fresh configuration passes using the existing
cross toolchain and the project build environment. The earlier attempt without
PyYAML failed and is retained. Complete compilation and guest runtime checks
are pending; the archived public-preview results below do not qualify this pin.

## Public preview preparation

Version 0.1.1 (`v0.1.1-preview.1`) packages the qualified public core below. Its declared macOS minimum is 26.0, matching the tested external Homebrew QEMU 11.0.1 executable; the launcher itself has a 13.0 deployment target. New signed runtime, Apple tickets and corresponding-source asset inventories are prepared separately; earlier 0.1.0 DMGs remain unchanged. Optional TrueType families outside the reviewed OFL/Apache/Bitstream set are excluded, with their selectors. Public publication follows the release coordinator’s final checks.

## Public-source qualification

`CORE.lock` pins public `pomaros/aros-core` revision `89db046157d415e98c05ca18316ca7ae63b07023`, shared with Hosted and VM. `TOOLS.lock` pins the reviewed VM tooling at `9bdd8d268bbb01e476542e4c8e835c340c90b5ad`. The final source was actually configured and rebuilt with frozen LLVM 20.1.0, UTC and retained release epoch `1792178266`. Boot, Wanderer and the full canonical distribution graph pass; all 44 required files exist. The package excludes VZ-only host-service commands and all eight physical Apple peripheral modules.

The actual windowed HVF desktop run passes in 20.21 seconds. QMP register/status access, the LLDB assertion supervisor and HVF abort tracing are ready before the guest runs. Desktop stability, two HID bindings and GPU completion markers pass. Its first unaltered capture passes all 352 configured-wallpaper blocks and the strict public monitor geometry/glyph/palette/blank-row contract. Negative controls reject alerts inside and outside the widget, over its removed and retained labels, generic requesters, software alerts and missing wallpaper. The seed is unchanged and QEMU exits normally; guest flushing is not established.

The accepted screenshot SHA-256 is `11e083af953d92ef2b8556f83d0de95dfccc85deec1d372b0642414fa0e48dfe`; it is copied unchanged into the README. It shows both project URLs and the limited public UP monitor. Clock accuracy, sensor values, actual input-event delivery, outbound networking and persistent safe shutdown remain unqualified. Evidence: `artifacts/desktop-hvf-public-up-final-89db/`.

The preceding runtime keeps its original FAIL verdict in `artifacts/desktop-hvf-public-89db/`: its pixel gate expected the removed native keyboard-backlight row. An independently reviewed profile replaces that expectation with a strict background row and retains the exact CORES/CPU masks; offline positive and negative controls passed on all three retained frames before the single new runtime. No core code or old verdict was changed to obtain the new result.

The final VM and QEMU packages have byte-identical kernel ELF, Exec library and raw bootstrap; only their backend startup ramdisks differ. The kernel ELF SHA-256 is `22fed8070a01bf5b52da8eb9240c309587747283ea0f81fee5fd00a418189d19`. Proof: the VM repository's local `artifacts/public-core-89db046/shared-kernel-proof.json`.

The tested app retains actual product revision `e9035fb`, packaging-tool revision `5896047` and guest revision `89db046`. The runtime verdict separately records the reviewed checker/tool revision `9bdd8d2`; documentation commits do not rewrite app provenance. These fresh development applications have ad-hoc signatures. Earlier notarized DMGs below remain sealed and unchanged.

## Archived image and earlier evidence

The earlier PomAROS QEMU development image builds and starts its full AROS desktop in a normal macOS Cocoa window using QEMU 11/HVF. The archived qualification below used core pin `9f346ab00d644bd40e0f53e2624c3f625d28f182` and the pinned VM tooling; the public-source migration is recorded separately. QEMU remains an external installation. Ordinary development builds use ad-hoc signing; the separately prepared internal DMG uses Developer ID signing and Apple notarization.

## Archived development qualification

The complete fresh guest SDK distribution graph passes, with all required files present. The QEMU package contains 3863 runtime files, its EFI loader, guest disk, firmware and license notices. It uses frozen LLVM 20.1.0 and release epoch `1792169063`/UTC. Actual guest objects were built at `48e445615380448d74ec02c9958a71201ce4904c`; later common changes add a hosted-only loader correction, extract the unchanged monitor renderer and add a Darwin-only monitor utility. Standalone loader tokens and the entire guest coldstart translation unit retain identical preprocessed code. Qualified artifacts and runs retain their original `3c382bc` source metadata; this pin update does not relabel those runs or rebuild unchanged guest objects.

Nine host tests pass, covering disk preservation, unusual paths, profile locking, symlink rejection, explicit acceleration, QMP endpoints, missing dependencies and desktop admission. A paused construction test admits the full device set under TCG; it executes no guest code and does not qualify a TCG desktop.

The actual final windowed HVF run passes in 33.49 seconds. Independent QMP status/register access, an owned-process LLDB assertion supervisor and HVF abort tracing are ready before guest execution. Guest markers establish desktop stability, two USB HID bindings and graphics IRQ completion. The unmodified guest framebuffer passes the strict production classifier: 352 blocks match the configured wallpaper extracted from the immutable package, and the monitor matches its frame, static glyphs and blank rows. Negative controls reject black/blue alerts inside and outside the monitor, alerts over its labels, generic requesters, software alerts and a missing wallpaper.

The accepted first candidate has SHA-256 `198ef072f943b815c47539c95fc3eabf8d5d7e2a8e1297aa694852915e006cea`. That earlier capture remains in its local run artifacts; the README displays the separately qualified public-source capture above. The image is the actual guest viewport from a windowed Cocoa run, without simulated macOS chrome. Both project URLs are visible. Local evidence: `artifacts/desktop-hvf-final-3c-accepted/`. Earlier failed runs and incomplete redraw candidates retain their original verdicts and pixels.

Guest logs also show a DHCP lease applied to vn0, with QEMU's NAT gateway and DNS configuration. Outbound DNS/TCP connectivity is not qualified by this desktop test. QEMU exits normally through the supervisor and the immutable seed remains unchanged; this does not establish guest filesystem flushing.

The final source pin also maps macOS EPERM to AROS write protection in the Unix hosted filesystem handler, with a production-code read-only fixture and a negative control. This hosted-only correction changes no standalone guest code. Source equivalence was rechecked; the sealed guest distributions below keep their original 3c/48e provenance and were not rebuilt or re-signed for it.

## Shared kernel

Actual final VZ and QEMU bundle payloads are independently parsed and hash-checked. Their `kernel.resource` and `exec.library` ELF files and raw stage2 bootstrap are byte-identical. Only the `SYS` ramdisk differs, reflecting backend startup and host-service settings. The kernel ELF SHA-256 is `646c209ca0cc241d7286522df40f7cafbbcf334a20c8d6574e8d45d7463438a7`. Proof is retained in the VM tooling repository's local `artifacts/pomaros-migration/final-3c-shared-kernel-proof.json`.

The macOS launcher uses Apple's ABI; the guest leaves x18 unrestricted. Only hosted AROS reserves it. Native Apple and future Raspberry Pi use the ordinary register policy and common source; their hardware is not tested here.

## Remaining limits

There is no guest-quiesce/host-quit transport for this backend. A QMP quit, normal process exit or window close can interrupt cached guest writes. This is a development package, not a release qualified for personal persistent data. The required shutdown path is tracked in [TODO.md](../TODO.md).

Host clipboard/file services are unavailable. Actual keyboard/pointer event delivery, outbound networking, persistent write/readback across controlled restarts, audio, long-term stability and production SMP remain unqualified. There is no claim of host-bridge parity with PomAROS VM or Hosted. Tests use isolated profiles and never open a personal disk. Product repositories and the curated [AROS core](https://github.com/pomaros/aros-core) are public. Historical archived binaries still reference the private lineage; the native repository remains empty and private.

## Signed internal distribution

The exact Developer ID signed launcher passes a separate 106.77-second supervised windowed HVF qualification, including strict wallpaper/widget checks and negative controls. The immutable seed is unchanged. Normal QEMU exit still does not establish guest filesystem flushing.

`PomAROS-QEMU-0.1.0-development-arm64.dmg` is signed by Developer ID Application: John Knipper (C43N3NG7Z5), with hardened runtime and a secure timestamp. Apple accepted the application ZIP (`aecd9255-9b27-4b99-857b-dfa714a16d17`) and final DMG (`b5b4e979-d210-49ff-9630-4f2df181a321`). The app was stapled before building the DMG; the final image is also stapled. Both signatures, Apple tickets and Gatekeeper checks pass.

Final post-staple DMG SHA-256: `b8b6efc15ce2fbf4ec97a850ddb5e599e34447d25bd71d903f144cb12a89b21c`. Local runtime and submission evidence lives under `artifacts/release-20261016-*` and `artifacts/notary-20261016-*`. See [SIGNED-DISTRIBUTION.md](SIGNED-DISTRIBUTION.md) for the reproducible signing and verification procedure.

These are internal development artifacts for John. No public binary download or GitHub Release was uploaded. The new public curated source does not contain the historical private source commits identified by these archived binaries. Recipients of those binaries still need their exact corresponding APL/GPL/LGPL and other component sources before redistribution. A future public-source build must be qualified separately; no archived binary was relabeled.

## Public-source migration

Builds acquire the curated official-history `pomaros/aros-core` fork through `CORE.lock` into the separate `../aros-core` checkout. The VM boot manifests exclude physical Apple PMGR, DART, RTKit, SPMI, SMC, PCIe, NVMe and SPI-HID drivers. `appleboot.device` remains because it supplies the VM RAM-backed system volume. The source acquisition and native-module admission checks do not establish a successful new guest build or boot. The archived runtime evidence above belongs to the unchanged earlier artifacts.

The build entry point delegates payloads to the shared source-bound build driver
and selects the shared GNU make4 helper for UEFI and host builds. It no longer
invokes macOS's unqualified named make for guest or loader targets. A matching
existing SDK may be consumed; source/tool pins remain mandatory and old binaries
keep their original provenance. The current full product qualification is recorded above.
