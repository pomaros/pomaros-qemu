#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 John Knipper
"""Compile runtime contract probes against one explicitly configured guest SDK."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
def identity(path):
    return {"path":str(path),"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"bytes":path.stat().st_size}
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build',type=Path,required=True)
    parser.add_argument('--toolchain',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    build=args.build.resolve(); toolchain=args.toolchain.resolve(); output=args.output.resolve()
    if (build/'DEVELOPMENT-DELTA.json').exists():
        parser.error('SDK contains an experimental module delta; select a fresh configured reference')
    binding=json.loads((build/'vm-build-environment.json').read_text())
    if binding['source_lock'].get('CORE_X18_POLICY')!='unrestricted' or binding['source_lock'].get('CORE_TARGET')!='apple-aarch64':
        parser.error('requires the common guest SDK target and register ABI')
    sdk=build/'bin/apple-aarch64'; dev=sdk/'AROS/Developer'; host=build/'bin/darwin-aarch64/tools'
    sources=[ROOT/'tests/probes/PthreadFirstUse.c',ROOT/'tests/probes/RenameReplace.c']
    inputs=[*sources,toolchain/'bin/clang',host/'collect-aros',dev/'lib/startup.o',
            dev/'lib/libpthread.a',dev/'lib/libstdcio.a',dev/'lib/libstdc.a',sdk/'gen/include/aros/config.h']
    for path in inputs:
        if not path.is_file():parser.error('missing input: '+str(path))
    frozen=[identity(path) for path in inputs]
    output.mkdir(parents=True,exist_ok=False)
    manifest={'result':'FAIL_BUILD','runtime':'UNTESTED','configured_build':binding,'inputs':frozen,'programs':[]}
    try:
        for source in sources:
            binary=output/source.stem
            cmd=[str(toolchain/'bin/clang'),'--target=aarch64-unknown-aros','-B'+str(host),
                 '-mcmodel=large','-fno-pic','-fno-pie','-O2','-Wall','-Wextra','-Werror',
                 '-Wno-missing-field-initializers','-isystem',str(dev/'include'),
                 '-isystem',str(sdk/'gen/include'),'-isystem',str(dev/'include/aros/stdc'),
                 '-nostartfiles','-nodefaultlibs','-L',str(dev/'lib'),'-L',str(toolchain/'lib/generic'),
                 str(dev/'lib/startup.o'),str(source),'-o',str(binary),'-Wl,--start-group',
                 '-lpthread','-lposixc','-lstdcio','-lstdc','-ldos','-lexec','-laros','-lautoinit',
                 '-llibinit','-lutility','-lamiga','-larossupport','-lclang_rt.builtins-aarch64','-Wl,--end-group']
            with (output/(source.stem+'.log')).open('x') as log:
                subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
            manifest['programs'].append({'command':cmd,'binary':identity(binary)})
        if frozen!=[identity(path) for path in inputs]:raise RuntimeError('input changed during build')
        manifest['result']='PASS_BUILD'
    finally:
        (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('runtime probes PASS_BUILD; execution untested; core='+binding['source_revision'])
if __name__=='__main__':main()
