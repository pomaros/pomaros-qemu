# Product acceptance work

- Implement an explicit guest filesystem quiesce operation plus a host shutdown
  request/acknowledgement transport for QEMU. VZ uses VMSync and vsock; this
  backend has no provider. Do not treat QMP quit, process exit or host file flush
  as proof that guest FAT buffers were drained. Inspect whether a generic VM
  shutdown callback and guest power-off instruction can form the shared path.
- Build/package the full desktop from CORE.lock and qualify real HVF startup,
  GPU pixels, keyboard/pointer input, user-mode NAT and guest filesystem
  writes/readback across a controlled restart. Record exact input hashes and
  strict verdicts, with a QMP supervisor ready to stop/capture a failing guest.
- Test the explicit TCG lane separately; no silent fallback or HVF substitution.
- Plan an installed-QEMU-free package with dependency/source/license delivery,
  then Developer ID signing/notarization. The initial development app requires
  an installed QEMU 11 and is signed ad-hoc.
- Add profile export/offline upgrade while preserving personal disks.
- Design QEMU host clipboard/file integration before promising bridge parity.
