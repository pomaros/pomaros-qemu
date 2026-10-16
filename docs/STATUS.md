# Qualification status

PomAROS QEMU builds and starts its full AROS desktop in a normal macOS Cocoa window using QEMU 11/HVF. It shares core pin `9f346ab00d644bd40e0f53e2624c3f625d28f182` and the pinned VM tooling with PomAROS VM. QEMU remains an external installation. Ordinary development builds use ad-hoc signing; the separately prepared internal DMG uses Developer ID signing and Apple notarization.

## Verified on 2026-10-16

The complete fresh guest SDK distribution graph passes, with all required files present. The QEMU package contains 3863 runtime files, its EFI loader, guest disk, firmware and license notices. It uses frozen LLVM 20.1.0 and release epoch `1792169063`/UTC. Actual guest objects were built at `48e445615380448d74ec02c9958a71201ce4904c`; later common changes add a hosted-only loader correction, extract the unchanged monitor renderer and add a Darwin-only monitor utility. Standalone loader tokens and the entire guest coldstart translation unit retain identical preprocessed code. Qualified artifacts and runs retain their original `3c382bc` source metadata; this pin update does not relabel those runs or rebuild unchanged guest objects.

Nine host tests pass, covering disk preservation, unusual paths, profile locking, symlink rejection, explicit acceleration, QMP endpoints, missing dependencies and desktop admission. A paused construction test admits the full device set under TCG; it executes no guest code and does not qualify a TCG desktop.

The actual final windowed HVF run passes in 33.49 seconds. Independent QMP status/register access, an owned-process LLDB assertion supervisor and HVF abort tracing are ready before guest execution. Guest markers establish desktop stability, two USB HID bindings and graphics IRQ completion. The unmodified guest framebuffer passes the strict production classifier: 352 blocks match the configured wallpaper extracted from the immutable package, and the monitor matches its frame, static glyphs and blank rows. Negative controls reject black/blue alerts inside and outside the monitor, alerts over its labels, generic requesters, software alerts and a missing wallpaper.

The accepted first candidate has SHA-256 `198ef072f943b815c47539c95fc3eabf8d5d7e2a8e1297aa694852915e006cea`. It is copied unchanged to `docs/images/pomaros-qemu.png` and embedded in the README. The image is the actual guest viewport from a windowed Cocoa run, without simulated macOS chrome. Both project URLs are visible. Local evidence: `artifacts/desktop-hvf-final-3c-accepted/`. Earlier failed runs and incomplete redraw candidates retain their original verdicts and pixels.

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

Future builds acquire the curated official-history `pomaros/aros-core` fork through `CORE.lock` into the separate `../aros-core` checkout. The VM boot manifests exclude physical Apple PMGR, DART, RTKit, SPMI, SMC, PCIe, NVMe and SPI-HID drivers. `appleboot.device` remains because it supplies the VM RAM-backed system volume. The source acquisition and native-module admission checks do not establish a successful new guest build or boot. The runtime evidence above belongs to the unchanged archived artifacts.
