#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 John Knipper
"""Package a PomAROS QEMU app using pinned shared guest tools and an installed QEMU."""
import argparse
import hashlib
import json
from pathlib import Path
import plistlib
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]

def lock(path):
    return dict(line.strip().split('=', 1) for line in path.read_text().splitlines()
                if line.strip() and not line.startswith('#'))

def validate_guest(manifest, startup):
    if not (manifest.get('backend') == 'qemu' and manifest.get('profile') == 'wanderer'
            and manifest.get('desktop_session') == 'desktop'
            and all(manifest.get(k) for k in ('work_volume', 'usb_desktop', 'virtio_gpu', 'network_stack'))):
        raise ValueError('requires a QEMU persistent USB/GPU/network desktop package')
    if any(manifest.get(k) for k in ('host_services', 'vsock_device', 'work_probe', 'shutdown_probe',
                                     'soak_probe', 'clipboard_probe', 'input_probe', 'network_probe')):
        raise ValueError('unsupported host services or qualification probes in product')
    if 'SYS:C/VMSync' in startup:
        raise ValueError('QEMU guest must not depend on the VZ host-service provider')

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--esp', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--tools', type=Path, default=ROOT.parent / 'pomaros-vm')
    p.add_argument('--qemu', type=Path, default=Path('/opt/homebrew/bin/qemu-system-aarch64'))
    p.add_argument('--firmware', type=Path, default=Path('/opt/homebrew/share/qemu/edk2-aarch64-code.fd'))
    a = p.parse_args()
    if a.output.exists() or a.output.suffix != '.app':
        p.error('output must be a new .app directory')
    if subprocess.check_output(['git', '-C', str(ROOT), 'status', '--porcelain'], text=True):
        p.error('commit product source before recording application provenance')
    tools_lock = lock(ROOT / 'TOOLS.lock')
    actual = subprocess.check_output(['git', '-C', str(a.tools), 'rev-parse', 'HEAD'], text=True).strip()
    expected = subprocess.check_output(['git', '-C', str(a.tools), 'rev-parse', tools_lock['TOOLS_REVISION']], text=True).strip()
    if actual != expected or subprocess.check_output(['git', '-C', str(a.tools), 'status', '--porcelain'], text=True):
        p.error('shared tools checkout must be clean at TOOLS.lock revision')
    guest = json.loads((a.esp / 'provenance.json').read_text())
    validate_guest(guest, (a.esp / 'Startup-Sequence').read_text())
    core = lock(ROOT / 'CORE.lock')
    if guest['source_revision'] != core['CORE_REVISION']:
        p.error('guest revision differs from CORE.lock')
    qemu_location = a.qemu.absolute()
    qemu = qemu_location.resolve(strict=True)
    version = subprocess.check_output([str(qemu), '--version'], text=True)
    if 'version 11.' not in version:
        p.error('this machine configuration requires QEMU 11')
    launcher = ROOT / 'build/pomaros-qemu'
    for path in (launcher, a.firmware):
        if not path.is_file():
            p.error('missing build input: ' + str(path))
    a.output.mkdir(parents=True)
    try:
        contents = a.output / 'Contents'; binary = contents / 'MacOS'; resources = contents / 'Resources'
        binary.mkdir(parents=True); resources.mkdir()
        shutil.copy2(launcher, binary / 'PomAROSQEMU')
        shutil.copy2(a.firmware, resources / 'edk2-aarch64-code.fd')
        subprocess.run(['python3', str(a.tools / 'tools/make-disk.py'), '--esp', str(a.esp),
                        '--work-volume', '--output', str(resources / 'System.img')], check=True)
        (resources / 'launch.json').write_text(json.dumps({'qemu': str(qemu_location),
            'firmware': 'edk2-aarch64-code.fd', 'machine': 'virt-11.0'}, indent=2) + '\n')
        info = {'CFBundleIdentifier': 'org.pomaros.qemu', 'CFBundleName': 'PomAROS QEMU',
                'CFBundleDisplayName': 'PomAROS QEMU', 'CFBundleExecutable': 'PomAROSQEMU',
                'CFBundlePackageType': 'APPL', 'CFBundleShortVersionString': '0.1.1',
                'CFBundleVersion': '2', 'LSMinimumSystemVersion': '13.0'}
        (contents / 'Info.plist').write_bytes(plistlib.dumps(info, sort_keys=True))
        shutil.copy2(ROOT / 'LICENSE', resources / 'HOST-LICENSE')
        # Firmware redistribution includes QEMU's firmware license inventory.
        firmware_share = a.firmware.resolve().parent
        licenses = list(firmware_share.glob('*LICENSE*')) + list(firmware_share.glob('*license*'))
        if not licenses:
            raise ValueError('firmware license inventory not found beside QEMU firmware')
        for path in licenses:
            if path.is_file():
                shutil.copy2(path, resources / path.name)
        source = Path(guest['configure_command'][0]).parent
        for name in ('LICENSE', 'LICENSE.GPL', 'LICENSE.LGPL', 'LICENSE.Author', 'LEGAL'):
            shutil.copy2(source / name, resources / ('AROS-' + name))
        subprocess.run(['python3', str(a.tools / 'tools/package-notices.py'), '--source', str(source),
                        '--output', str(resources / 'Licenses/libfdt'), '--build', guest['build']], check=True)
        hashes = {p.relative_to(resources).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in resources.rglob('*') if p.is_file()}
        (resources / 'provenance.json').write_text(json.dumps({'guest': guest, 'tools_revision': actual,
            'qemu_version': version, 'qemu_path': str(qemu), 'qemu_bundled': False,
            'launcher_sha256': hashlib.sha256(launcher.read_bytes()).hexdigest(),
            'qemu_sha256': hashlib.sha256(qemu.read_bytes()).hexdigest(),
            'source_revision': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
            'files': hashes}, indent=2) + '\n')
        subprocess.run(['codesign', '--force', '--sign', '-', '--entitlements', str(ROOT / 'entitlements.plist'), str(a.output)], check=True)
        subprocess.run(['codesign', '--verify', '--strict', str(a.output)], check=True)
    except BaseException:
        shutil.rmtree(a.output)
        raise
    print('package-app PASS:', a.output)

if __name__ == '__main__':
    main()
