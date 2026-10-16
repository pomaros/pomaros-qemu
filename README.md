# PomAROS QEMU

AROS ARM64 on Apple Silicon Macs using QEMU and hardware acceleration (HVF).
This product shares the common PomAROS source revision with hosted and Apple
Virtualization.framework products. VM guest x18 remains unrestricted. Native
Apple/Raspberry Pi target work belongs to that shared kernel source; this
repository contains the Mac launcher and packaging only.

The product is being prepared; a host build alone is not guest qualification.
See [status and evidence](docs/STATUS.md).

## Run

Install QEMU 11 (`brew install qemu`) and open `PomAROS QEMU.app`. The packaged
application includes its guest image and EFI firmware; QEMU is an external
installation in this first package. The app records its exact QEMU path and
refuses a different major version. A fully bundled/notarized installer is a
subsequent distribution step.

The application starts in a normal Cocoa window with fullscreen explicitly off.
The user can choose fullscreen afterward. The window provides the AROS display,
keyboard and pointer. The default
profile is `~/Library/Application Support/PomAROS QEMU/Default/`. Its system disk
is seeded once and remains writable; updates never overwrite that disk.
Profiles are locked for the whole QEMU process lifetime. Two profiles can be
selected explicitly with the command-line launcher:

```sh
build/pomaros-qemu --resources '/path/PomAROS QEMU.app/Contents/Resources' \
  --profile "$HOME/Library/Application Support/PomAROS QEMU/Test"
```

`POMAROS_QEMU_STATE_DIRECTORY` overrides the profile. Add `--accel tcg` to select
software emulation explicitly; the default HVF never falls back silently.
Save personal files on `WORK:`. In full distributions the system lives on
`WORK:System` and its preferences persist too.

**This is a development package; integrated safe shutdown is pending.** This
backend has no VZ host service provider or guest filesystem quiesce/host quit
transport. The platform's `C:Shutdown` power-off path has not been established.
Closing the QEMU window, QMP quit or terminating QEMU can interrupt cached guest
writes. Save work and keep backups of closed profiles; this package does not
claim safe persistence across an ordinary window close. A guest-quiesce command
and host shutdown transport are tracked in [TODO.md](TODO.md).

Host clipboard and file exchange are unavailable. Networking uses QEMU
user-mode NAT and virtio-net; audio is not configured. These are explicit
limits, not claims of parity with the VM or hosted product's host bridge.

Logs and the exact QEMU command are in the selected profile. Changing a system
image creates a new package; existing profiles require a separate offline
upgrade. Keep the original profile for rollback.

## Build

Requirements: Apple Silicon macOS, Xcode command-line tools, Python 3, GNU make
4 first on PATH, Homebrew QEMU 11, LLVM/lld, dtc and mtools, and the shared AROS
cross toolchain in `../aros-crosstools`.

`CORE.lock` pins the common AROS source and `TOOLS.lock` pins the shared build
and packaging implementation from `pomaros-vm`. Fetch those private repositories
into sibling checkouts and select the exact revisions before building. AROS
source uses APL; our launcher/tool code uses MIT. QEMU is installed separately;
firmware and guest license notices accompany the application.

```sh
make test
python3 tools/build.py
```

The build uses its own `../Build/pomaros-qemu/clean-core` directory so simultaneous
VM and QEMU product builds cannot race a shared mutable build tree. It creates
an isolated VM configuration, builds the common AROS runtime,
packages the QEMU backend and signs a local app. It stops on missing modules or
wrong source identities. Build or guest failures are retained as failures.

To package an already qualified QEMU ESP:

```sh
make package ESP=/absolute/qemu-esp OUTPUT='/absolute/new/PomAROS QEMU.app'
```

The launcher uses the versioned `virt-11.0` machine, GICv3 with GICv2m,
virtio GPU/block/network, xHCI USB input and an EFI/virtio early console.
Machine availability is verified locally; complete desktop behavior needs
separate guest acceptance. `--headless --timeout 20` is an explicit bounded
diagnostic invocation. Add `--qmp /tmp/new-short-socket` to allow an independent
QMP supervisor to stop/inspect a diagnostic guest; the socket must be new.
`--inspect` records the command and prepares an isolated
profile without starting a VM.

A bounded WINDOWED desktop gate is available after packaging:

```sh
python3 tools/qualify.py --app '/absolute/PomAROS QEMU.app' \
  --output /absolute/new-run --accel hvf
```

It starts the guest paused, proves QMP register access before execution, then
checks desktop/GPU/USB bindings and the pinned Wanderer pixel gate. It saves
CPU registers, instructions, stack and a screenshot before ending a failed run.
Its verdict excludes network, guest filesystem persistence and safe shutdown;
those require separate acceptance. All runs use disposable profile copies.
