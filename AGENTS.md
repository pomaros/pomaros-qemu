# Working on PomAROS QEMU

Private product repository. Push only to private pomaros/pomaros-qemu.
Keep the native repository empty/private. Public or upstream publication needs
John's explicit authorization. Original host/tools code is MIT, John Knipper.

OS source belongs in the shared ../aros-core-pomaros checkout and is pinned by
CORE.lock. Packaging tools are pinned from ../pomaros-vm by TOOLS.lock; do not
copy a kernel or duplicate the shared guest build tools here. VM guest x18 is
unrestricted; macOS host code follows the Apple ABI. No silent HVF/TCG fallback.

Use isolated profile disks, retain old profiles, and lock before starting QEMU.
Automated VM runs require the project's board reservation, are bounded, and
record exact inputs/results in ignored artifacts/. No M1 hardware runs here.
