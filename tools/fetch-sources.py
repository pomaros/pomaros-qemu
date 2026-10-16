#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 John Knipper
"""Acquire pinned public VM tooling, then the same shared core as PomAROS VM."""
import argparse
import importlib.util
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--source', type=Path, default=ROOT.parent/'aros-core')
p.add_argument('--tools', type=Path, default=ROOT.parent/'pomaros-vm')
a = p.parse_args()
lock = dict(line.strip().split('=', 1) for line in (ROOT/'TOOLS.lock').read_text().splitlines()
            if line.strip() and not line.startswith('#'))
revision = lock['TOOLS_REVISION']; tools = a.tools.absolute()
if not re.fullmatch(r'[0-9a-f]{40}', revision) or tools.is_symlink():
    p.error('requires an exact tools pin and a non-symlink checkout')
try:
    # Bootstrap the shared recipe before importing it. Existing directories are
    # read-only to this command; Git refuses occupied clone destinations.
    if not tools.exists():
        tools.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['git', 'clone', '--filter=blob:none', '--no-checkout', '--', lock['TOOLS_URL'], str(tools)], check=True)
        subprocess.run(['git', '-C', str(tools), 'checkout', '--detach', revision], check=True)
    def git(*args):
        return subprocess.check_output(['git', '-C', str(tools), *args], text=True).strip()
    if Path(git('rev-parse', '--show-toplevel')).resolve() != tools.resolve():
        p.error('tools must name the Git worktree root')
    if git('rev-parse', 'HEAD') != revision or git('status', '--porcelain'):
        p.error('tools must already be clean at TOOLS.lock; choose a NEW --tools path')
    spec = importlib.util.spec_from_file_location('fetch_core', tools/'tools/fetch-core.py')
    shared = importlib.util.module_from_spec(spec); spec.loader.exec_module(shared)
    shared.acquire(shared.read_lock(ROOT/'CORE.lock'), 'CORE', a.source)
except (OSError, ValueError, subprocess.CalledProcessError) as error:
    p.error(str(error))
