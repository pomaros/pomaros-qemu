# Signed preview distributions

Use `tools/distribute.py` to invoke the shared recipe pinned by `TOOLS.lock`.
See PomAROS VM's `docs/SIGNED-DISTRIBUTION.md` for the app ZIP → accepted ticket
→ stapled app → signed DMG → accepted ticket → stapled DMG sequence.

```sh
python3 tools/distribute.py prepare --app '/path/PomAROS QEMU.app' --output artifacts/signed-qemu --public-preview --release-tag v0.1.1-preview.1
python3 tools/qualify.py --app 'artifacts/signed-qemu/PomAROS QEMU.app' --core-lock artifacts/signed-qemu/guest-source.lock --output artifacts/signed-qemu-qa --accel hvf --lldb
python3 tools/distribute.py zip --distribution artifacts/signed-qemu --output artifacts/PomAROS-QEMU-app.zip --acceptance artifacts/signed-qemu-qa/verdict.json
```

Reserve the project's VM/QEMU resources before the bounded **windowed** check.
The launcher is Developer ID signed with hardened runtime and no extra
entitlements. QEMU 11 remains separately installed, with its own signature and
HVF entitlements; its dependency tree is not copied into this package.

This is a public development preview. Guest-quiesce/host-quit,
host clipboard/file services and full persistent-data acceptance are pending.
The DMG includes those limits, prerequisites, actual guest provenance and
license/source-access notices. The coordinator publishes reviewed source assets and binaries together; this tool performs no GitHub upload.

For a retained historical payload, `prepare --guest-source-lock PATH` requires
a lock containing its actual source URL, exact revision, branch and ABI. It
refuses to replace the current public pin with an old private commit silently.
Existing signed/notarized archives and their provenance are never modified by
source acquisition or pin updates.
