# Qualification status

PomAROS QEMU builds and starts its full AROS desktop in a normal macOS Cocoa window using QEMU 11/HVF. It shares core pin `3c382bcf39373ac50630f5df6e961a3afb05a64b` and the pinned VM tooling with PomAROS VM. QEMU remains an external installation; the application is signed ad-hoc.

## Verified on 2026-10-16

The complete fresh guest SDK distribution graph passes, with all required files present. The QEMU package contains 3863 runtime files, its EFI loader, guest disk, firmware and license notices. It uses frozen LLVM 20.1.0 and release epoch `1792169063`/UTC. Actual guest objects were built at `48e445615380448d74ec02c9958a71201ce4904c`; the final common pin adds a hosted-only loader correction. Standalone preprocessed loader tokens match exactly and retained source-amendment metadata records the unchanged guest artifacts.

Nine host tests pass, covering disk preservation, unusual paths, profile locking, symlink rejection, explicit acceleration, QMP endpoints, missing dependencies and desktop admission. A paused construction test admits the full device set under TCG; it executes no guest code and does not qualify a TCG desktop.

The actual final windowed HVF run passes in 33.49 seconds. Independent QMP status/register access, an owned-process LLDB assertion supervisor and HVF abort tracing are ready before guest execution. Guest markers establish desktop stability, two USB HID bindings and graphics IRQ completion. The unmodified guest framebuffer passes the strict production classifier: 352 blocks match the configured wallpaper extracted from the immutable package, and the monitor matches its frame, static glyphs and blank rows. Negative controls reject black/blue alerts inside and outside the monitor, alerts over its labels, generic requesters, software alerts and a missing wallpaper.

The accepted first candidate has SHA-256 `198ef072f943b815c47539c95fc3eabf8d5d7e2a8e1297aa694852915e006cea`. It is copied unchanged to `docs/images/pomaros-qemu.png` and embedded in the README. The image is the actual guest viewport from a windowed Cocoa run, without simulated macOS chrome. Both project URLs are visible. Local evidence: `artifacts/desktop-hvf-final-3c-accepted/`. Earlier failed runs and incomplete redraw candidates retain their original verdicts and pixels.

Guest logs also show a DHCP lease applied to vn0, with QEMU's NAT gateway and DNS configuration. Outbound DNS/TCP connectivity is not qualified by this desktop test. QEMU exits normally through the supervisor and the immutable seed remains unchanged; this does not establish guest filesystem flushing.

## Shared kernel

Actual final VZ and QEMU bundle payloads are independently parsed and hash-checked. Their `kernel.resource` and `exec.library` ELF files and raw stage2 bootstrap are byte-identical. Only the `SYS` ramdisk differs, reflecting backend startup and host-service settings. The kernel ELF SHA-256 is `646c209ca0cc241d7286522df40f7cafbbcf334a20c8d6574e8d45d7463438a7`. Proof is retained in the VM tooling repository's local `artifacts/pomaros-migration/final-3c-shared-kernel-proof.json`.

The macOS launcher uses Apple's ABI; the guest leaves x18 unrestricted. Only hosted AROS reserves it. Native Apple and future Raspberry Pi use the ordinary register policy and common source; their hardware is not tested here.

## Remaining limits

There is no guest-quiesce/host-quit transport for this backend. A QMP quit, normal process exit or window close can interrupt cached guest writes. This is a development package, not a release qualified for personal persistent data. The required shutdown path is tracked in [TODO.md](../TODO.md).

Host clipboard/file services are unavailable. Actual keyboard/pointer event delivery, outbound networking, persistent write/readback across controlled restarts, audio, long-term stability and production SMP remain unqualified. There is no claim of host-bridge parity with PomAROS VM or Hosted. Tests use isolated profiles and never open a personal disk. No public upstream publication or visibility change was performed; the native repository remains empty and private.
