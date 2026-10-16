# Product acceptance work

- Implement an explicit guest filesystem quiesce operation plus a host shutdown
  request/acknowledgement transport for QEMU. VZ uses VMSync and vsock; this
  backend has no provider. Do not treat QMP quit, process exit or host file flush
  as proof that guest FAT buffers were drained. Inspect whether a generic VM
  shutdown callback and guest power-off instruction can form the shared path.
- Extend the accepted full desktop HVF/GPU/USB-binding checks to actual
  keyboard/pointer events, outbound DNS/TCP and guest filesystem writes/readback
  across a controlled restart once guest quiesce exists. DHCP lease application
  is observed, but does not establish full network connectivity. Retain exact
  input hashes and independent QMP/debugger failure capture.
- Test the explicit TCG lane separately; no silent fallback or HVF substitution.
- Plan an installed-QEMU-free package with dependency/source/license delivery,
  then Developer ID signing/notarization. The initial development app requires
  an installed QEMU 11 and is signed ad-hoc.
- Add profile export/offline upgrade while preserving personal disks.
- Design QEMU host clipboard/file integration before promising bridge parity.
