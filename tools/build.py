#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 John Knipper
"""Build the QEMU product using the pinned common kernel and shared packaging tools."""
import argparse
import json
from pathlib import Path
import subprocess
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('package', ROOT / 'tools/package-app.py')
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)

def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args], text=True).strip()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, default=ROOT.parent / 'aros-core-pomaros')
    p.add_argument('--tools', type=Path, default=ROOT.parent / 'pomaros-vm')
    p.add_argument('--build', type=Path, default=ROOT.parent / 'Build/pomaros-qemu/clean-core')
    p.add_argument('--output', type=Path, default=ROOT / 'artifacts/distribution')
    p.add_argument('--jobs', type=int, default=6)
    a = p.parse_args()
    for name in ('source', 'tools', 'build', 'output'):
        setattr(a, name, getattr(a, name).resolve())
    if not 1 <= a.jobs <= 32:
        p.error('jobs must be 1..32')
    core = package.lock(ROOT / 'CORE.lock'); tools = package.lock(ROOT / 'TOOLS.lock')
    for path, revision in ((a.source, core['CORE_REVISION']), (a.tools, tools['TOOLS_REVISION'])):
        expected = git(path, 'rev-parse', revision)
        if git(path, 'rev-parse', 'HEAD') != expected or git(path, 'status', '--porcelain'):
            p.error(str(path) + ' must be clean at its pinned revision')
    def run(*args):
        subprocess.run([str(x) for x in args], check=True, cwd=ROOT)
    if not a.build.exists():
        run('python3', a.tools / 'tools/configure-core.py', '--source', a.source, '--output', a.build)
    build_identity = json.loads((a.build / 'vm-build-environment.json').read_text())
    if build_identity['source_revision'] != core['CORE_REVISION']:
        p.error('configured build has a different core revision; use a new build directory')
    # Share the maintained dependency graph: no second list of AROS modules here.
    run('make', '-C', a.build, '-j' + str(a.jobs), 'apple-wanderer-payloads')
    run('python3', a.tools / 'tools/distribution.py', 'build', '--build', a.build, '--jobs', a.jobs)
    run('make', '-C', a.tools / 'boot/arosboot', 'AROS_CORE_SOURCE=' + str(a.source))
    run('python3', a.tools / 'tools/distribution.py', 'package', '--backend', 'qemu',
        '--build', a.build, '--efi', a.tools / 'build/uefi/BOOTAA64.EFI', '--output', a.output)
    run('make')
    run('python3', ROOT / 'tools/package-app.py', '--tools', a.tools, '--esp', a.output / 'esp',
        '--output', a.output / 'PomAROS QEMU.app')

if __name__ == '__main__':
    main()
