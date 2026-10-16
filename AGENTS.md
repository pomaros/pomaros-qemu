# Working on PomAROS QEMU

Public product repository pomaros/pomaros-qemu. Pushes require the user's
authorization and coordinated review; upstream submissions are a separate action.
Keep the native repository empty/private. Original host/tools code is MIT, John Knipper.

OS source belongs in the shared ../aros-core checkout and is pinned by
CORE.lock. Packaging tools are pinned from ../pomaros-vm by TOOLS.lock; do not
copy a kernel or duplicate the shared guest build tools here. VM guest x18 is
unrestricted; macOS host code follows the Apple ABI. No silent HVF/TCG fallback.

Use isolated profile disks, retain old profiles, and lock before starting QEMU.
Automated VM runs require the project's board reservation, are bounded, and
record exact inputs/results in ignored artifacts/. No M1 hardware runs here.
