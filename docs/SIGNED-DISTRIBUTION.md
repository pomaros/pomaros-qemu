# Signed internal distributions

Use `tools/distribute.py` to invoke the shared recipe pinned by `TOOLS.lock`.
See PomAROS VM's `docs/SIGNED-DISTRIBUTION.md` for the app ZIP → accepted ticket
→ stapled app → signed DMG → accepted ticket → stapled DMG sequence.

```sh
python3 tools/distribute.py prepare --app '/path/PomAROS QEMU.app' --output artifacts/signed-qemu
python3 tools/qualify.py --app 'artifacts/signed-qemu/PomAROS QEMU.app' --core-lock artifacts/signed-qemu/guest-source.lock --output artifacts/signed-qemu-qa --accel hvf --lldb
python3 tools/distribute.py zip --distribution artifacts/signed-qemu --output artifacts/PomAROS-QEMU-app.zip --acceptance artifacts/signed-qemu-qa/verdict.json
```

Reserve the project's VM/QEMU resources before the bounded **windowed** check.
The launcher is Developer ID signed with hardened runtime and no extra
entitlements. QEMU 11 remains separately installed, with its own signature and
HVF entitlements; its dependency tree is not copied into this package.

This remains an internal development distribution. Guest-quiesce/host-quit,
host clipboard/file services and full persistent-data acceptance are pending.
The DMG includes those limits, prerequisites, actual guest provenance and
license/source-access notices. No GitHub release upload is performed.
