# SPDX-License-Identifier: MIT
# Copyright (c) 2026 John Knipper
"""Exercise production profile preservation/locking without running a VM."""
import fcntl
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class Launcher(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='pomaros qemu,')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.resources = self.root / 'resources'; self.resources.mkdir()
        self.profile = self.root / 'profile, one'
        self.qemu = self.root / 'qemu'
        self.qemu.write_text('#!/bin/sh\nif [ "$1" = --version ]; then echo "QEMU emulator version 11.0.1"; exit 0; fi\nexit 99\n')
        self.qemu.chmod(0o755)
        (self.resources / 'launch.json').write_text(json.dumps({'qemu': str(self.qemu), 'firmware': 'firmware.fd', 'machine': 'virt-11.0'}))
        (self.resources / 'firmware.fd').write_bytes(b'firmware')
        (self.resources / 'System.img').write_bytes(b'personal disk seed')

    def run_launcher(self, *extra):
        return subprocess.run([str(ROOT / 'build/pomaros-qemu'), '--resources', str(self.resources),
            '--profile', str(self.profile), '--inspect', *extra], capture_output=True, text=True, timeout=10)

    def test_preserves_disk_and_quotes_paths(self):
        (self.resources / 'System.img').chmod(0o400)
        first = self.run_launcher()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual((self.profile / 'system.img').stat().st_mode & 0o777, 0o600)
        command = json.loads(first.stdout)
        block = json.loads(command['arguments'][command['arguments'].index('-blockdev') + 1])
        self.assertEqual(block['file']['filename'], str(self.profile / 'system.img'))
        (self.profile / 'system.img').write_bytes(b'personal data')
        (self.resources / 'System.img').chmod(0o600)
        (self.resources / 'System.img').write_bytes(b'new seed')
        self.assertEqual(self.run_launcher().returncode, 0)
        self.assertEqual((self.profile / 'system.img').read_bytes(), b'personal data')
        self.assertIn('virt-11.0,acpi=on,gic-version=3,msi=gicv2m', command['arguments'])
        self.assertIn('hvf', command['arguments'])
        self.assertIn('cocoa,full-screen=off', command['arguments'])

    def test_profile_lock_is_exclusive(self):
        self.profile.mkdir()
        with (self.profile / 'profile.lock').open('w') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            result = self.run_launcher()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('already running', result.stderr)
            self.assertFalse((self.profile / 'system.img').exists())

    def test_symlink_disk_and_directory_refused(self):
        outside = self.root / 'outside'; outside.write_bytes(b'untouched')
        self.profile.mkdir()
        (self.profile / 'system.img').symlink_to(outside)
        self.assertNotEqual(self.run_launcher().returncode, 0)
        self.assertEqual(outside.read_bytes(), b'untouched')
        (self.profile / 'system.img').unlink()
        # A separate profile symlink may never receive personal data.
        other = self.root / 'other'; other.mkdir()
        link = self.root / 'link'; link.symlink_to(other)
        self.profile = link
        self.assertNotEqual(self.run_launcher().returncode, 0)
        self.assertEqual(list(other.iterdir()), [])

    def test_optional_qmp_endpoint_does_not_replace_files(self):
        import uuid
        endpoint = '/tmp/pomaros-qmp-' + uuid.uuid4().hex
        result = self.run_launcher('--qmp', endpoint)
        self.assertEqual(result.returncode, 0, result.stderr)
        arguments = json.loads(result.stdout)['arguments']
        self.assertIn('unix:' + endpoint + ',server=on,wait=off', arguments)
        self.assertFalse(Path(endpoint).exists())
        self.assertNotEqual(self.run_launcher('--qmp', str(self.qemu)).returncode, 0)
        self.assertTrue(self.qemu.is_file())

    def test_no_silent_acceleration_fallback(self):
        tcg = self.run_launcher('--accel', 'tcg')
        self.assertEqual(tcg.returncode, 0, tcg.stderr)
        self.assertIn('cortex-a72', json.loads(tcg.stdout)['arguments'])
        self.assertNotEqual(self.run_launcher('--accel', 'auto').returncode, 0)

class Packaging(unittest.TestCase):
    def test_rejects_host_bridge_and_probes(self):
        spec = importlib.util.spec_from_file_location('package_app', ROOT / 'tools/package-app.py')
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        valid = dict(backend='qemu', profile='wanderer', desktop_session='desktop',
                     work_volume=True, usb_desktop=True, virtio_gpu=True, network_stack=True)
        module.validate_guest(valid, 'SYS:VMUSB\n')
        with self.assertRaises(ValueError):
            module.validate_guest(dict(valid, desktop_session='forever'), 'SYS:VMUSB\n')
        for key in ('host_services', 'vsock_device', 'shutdown_probe', 'input_probe'):
            with self.assertRaises(ValueError):
                module.validate_guest(dict(valid, **{key: True}), 'SYS:VMUSB\n')
        with self.assertRaises(ValueError):
            module.validate_guest(valid, 'Run >NIL: SYS:C/VMSync\n')
