#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 John Knipper
"""Use the pinned shared signing/notarization recipe for the QEMU product."""
import argparse
from pathlib import Path
import subprocess
import sys

root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(add_help=False)
p.add_argument('--tools',type=Path,default=root.parent/'pomaros-vm')
a,arguments=p.parse_known_args()
lock=dict(line.split('=',1) for line in (root/'TOOLS.lock').read_text().splitlines() if line and not line.startswith('#'))
revision=subprocess.check_output(['git','-C',str(a.tools),'rev-parse','HEAD'],text=True).strip()
if revision!=lock['TOOLS_REVISION'] or subprocess.check_output(['git','-C',str(a.tools),'status','--porcelain'],text=True):
    raise SystemExit('shared distribution tools must be clean at TOOLS.lock')
raise SystemExit(subprocess.call([sys.executable,str(a.tools/'tools/distribute.py'),*arguments,'--product','qemu','--repo',str(root)]))
