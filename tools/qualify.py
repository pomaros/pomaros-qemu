#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 John Knipper
"""Bounded windowed QEMU desktop proof with an independent QMP supervisor."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
MARKERS = ('[KI] alive window open', '[KI] desktop stable', '[VM] desktop two HID bindings PASS',
           '[VM] virtio graphics IRQ completion PASS')

class QMP:
    def __init__(self, endpoint):
        self.sock = socket.socket(socket.AF_UNIX); self.sock.settimeout(4)
        self.sock.connect(str(endpoint)); self.stream = self.sock.makefile('rwb')
        self.greeting = self.read(); self.execute('qmp_capabilities')
    def read(self):
        line = self.stream.readline()
        if not line: raise RuntimeError('QMP disconnected')
        return json.loads(line)
    def execute(self, name, arguments=None):
        self.stream.write(json.dumps({'execute': name, 'arguments': arguments or {}}).encode() + b'\n')
        self.stream.flush()
        while True:
            reply = self.read()
            if 'error' in reply: raise RuntimeError(str(reply['error']))
            if 'return' in reply: return reply['return']
    def close(self):
        try:
            self.stream.close()
        except OSError:
            # A failed flush can leave buffered bytes after the QEMU peer aborts.
            pass
        finally:
            self.sock.close()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--app', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--tools', type=Path, default=ROOT.parent / 'pomaros-vm')
    p.add_argument('--accel', choices=('hvf', 'tcg'), default='hvf')
    p.add_argument('--timeout', type=float, default=60)
    p.add_argument('--lldb', action='store_true', help='attach an assertion debugger before the paused guest runs')
    a = p.parse_args(); a.output = a.output.resolve(); a.app = a.app.resolve()
    if a.output.exists() or not 5 <= a.timeout <= 180:
        p.error('output must be new and timeout must be 5..180 seconds')
    resources = a.app / 'Contents/Resources'
    tools_lock = dict(line.split('=', 1) for line in (ROOT / 'TOOLS.lock').read_text().splitlines()
                      if line and not line.startswith('#'))
    tools_revision = subprocess.check_output(['git', '-C', str(a.tools), 'rev-parse', 'HEAD'], text=True).strip()
    if tools_revision != tools_lock['TOOLS_REVISION']:
        p.error('pixel gate checkout differs from TOOLS.lock')
    manifest = json.loads((resources / 'provenance.json').read_text())
    guest = manifest['guest']
    lock = dict(line.split('=', 1) for line in (ROOT / 'CORE.lock').read_text().splitlines()
                if line and not line.startswith('#'))
    if guest['source_revision'] != lock['CORE_REVISION']:
        p.error('application core differs from CORE.lock')
    a.output.mkdir(parents=True)
    profile = a.output / 'profile'
    seed = resources / 'System.img'
    verdict = {'result': 'FAIL', 'reason': 'not-started', 'backend': a.accel,
               'source_revision': guest['source_revision'], 'tools_revision': tools_revision, 'markers': {},
               'launcher_sha256': hashlib.sha256((a.app / 'Contents/MacOS/PomAROSQEMU').read_bytes()).hexdigest(),
               'seed_sha256': hashlib.sha256(seed.read_bytes()).hexdigest(),
               'scope': 'windowed desktop/GPU/USB bindings; network, file persistence and safe shutdown not qualified',
               'supervisor_ready_before_guest': False}
    process = None; qmp = None; debugger = None; debugger_log = None; started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix='pq-', dir='/tmp') as scratch:
        endpoint = Path(scratch) / 'qmp.sock'
        command = [str(a.app / 'Contents/MacOS/PomAROSQEMU'), '--resources', str(resources),
                   '--profile', str(profile), '--accel', a.accel, '--qmp', str(endpoint), '--start-paused']
        (a.output / 'command.json').write_text(json.dumps(command, indent=2) + '\n')
        environment = dict(os.environ); environment.pop('POMAROS_QEMU_STATE_DIRECTORY', None)
        try:
            with (a.output / 'launcher.log').open('w') as output:
                process = subprocess.Popen(command, stdout=output, stderr=subprocess.STDOUT,
                                           start_new_session=True, env=environment)
                deadline = time.monotonic() + 10
                while time.monotonic() < deadline and not endpoint.exists():
                    if process.poll() is not None: raise RuntimeError('launcher exited before QMP')
                    time.sleep(.1)
                qmp = QMP(endpoint)
                initial = qmp.execute('query-status')
                if initial['running']: raise RuntimeError('guest ran before independent supervisor readiness')
                initial_registers = qmp.execute('human-monitor-command', {'command-line': 'info registers'})
                if 'PC=' not in initial_registers: raise RuntimeError('QMP register read did not return CPU state')
                (a.output / 'initial-registers.txt').write_text(initial_registers)
                verdict['supervisor_ready_before_guest'] = True
                if a.accel == 'hvf':
                    for event in ('hvf_data_abort', 'hvf_insn_abort'):
                        qmp.execute('trace-event-set-state', {'name': event, 'enable': True})
                    verdict['hvf_abort_trace_enabled_before_guest'] = True
                if a.lldb:
                    rows = subprocess.check_output(['ps', '-axo', 'pid=,ppid=,comm='], text=True).splitlines()
                    children = [int(fields[0]) for row in rows if len(fields := row.split(None, 2)) == 3
                                and int(fields[1]) == process.pid and fields[2].endswith('/qemu-system-aarch64')]
                    if len(children) != 1: raise RuntimeError('cannot identify unique owned QEMU child for LLDB')
                    commands = ['process handle SIGUSR2 -n false -p true -s false',
                                'breakpoint set -n __assert_rtn', 'breakpoint command add 1',
                                'thread backtrace', 'register read', 'memory read -f s -c 1 $x0',
                                'memory read -f s -c 1 $x1', 'memory read -f s -c 1 $x3',
                                'expr unsigned long long $guestregs[32] = {0}',
                                'expr unsigned int $guestregresults[32] = {0}',
                                'expr for(unsigned i=0;i<32;++i) { $guestregresults[i]=((unsigned int(*)(unsigned long long,unsigned int,unsigned long long*))hv_vcpu_get_reg)(0,i,&$guestregs[i]); }',
                                'memory read -f x -s 4 -c 32 `&$guestregresults`',
                                'memory read -f x -s 8 -c 32 `&$guestregs`',
                                'expr unsigned long long $guestpc = $guestregs[31]',
                                'expr -f hex -- $guestpc', 'expr unsigned char $guestopcode[64] = {0}',
                                'expr ((void(*)(unsigned long long,void*,unsigned long long))cpu_physical_memory_read)($guestpc-16,&$guestopcode,64)',
                                'memory read -f x -s 4 -c 16 `&$guestopcode`',
                                'disassemble -s `&$guestopcode` -c 16', 'DONE',
                                'script print("POMAROS_DEBUGGER_READY", flush=True)', 'continue', 'process kill', 'quit']
                    command_file = a.output / 'debugger.commands'
                    command_file.write_text('\n'.join(commands) + '\n')
                    debugger_log = (a.output / 'debugger.log').open('w')
                    debugger = subprocess.Popen(['lldb', '-b', '-p', str(children[0]), '-s', str(command_file)],
                                                stdout=debugger_log, stderr=subprocess.STDOUT, start_new_session=True)
                    limit = time.monotonic() + 30
                    while time.monotonic() < limit:
                        debug_text = (a.output / 'debugger.log').read_text(errors='replace')
                        if 'POMAROS_DEBUGGER_READY\n' in debug_text: break
                        if debugger.poll() is not None: raise RuntimeError('LLDB attach failed before guest execution')
                        time.sleep(.1)
                    else: raise RuntimeError('LLDB readiness timeout before guest execution')
                    verdict['lldb_ready_before_guest'] = True
                qmp.execute('cont')
                deadline = time.monotonic() + a.timeout
                stable_since = None
                while time.monotonic() < deadline:
                    serial = profile / 'serial.log'
                    text = serial.read_text(errors='replace') if serial.exists() else ''
                    if any(f in text for f in ('FAIL:', '[B2Q] FAIL', 'Synchronous Exception')):
                        raise RuntimeError('guest-failure')
                    if process.poll() is not None: raise RuntimeError('early-exit')
                    host_log = profile / 'qemu.log'
                    host_text = host_log.read_text(errors='replace') if host_log.exists() else ''
                    if 'Assertion failed:' in host_text: raise RuntimeError('host-qemu-assertion')
                    if a.lldb and debugger.poll() is not None:
                        raise RuntimeError('host-debugger-stopped-target; inspect debugger.log')
                    if all(marker in text for marker in MARKERS):
                        stable_since = stable_since or time.monotonic()
                        if time.monotonic() - stable_since >= 3: break
                    time.sleep(.1)
                else: raise RuntimeError('desktop-proof-timeout')
                qmp.execute('screendump', {'filename': str(a.output / 'desktop.png'), 'format': 'png', 'device': 'gpu', 'head': 0})
                wallpaper_path='Prefs/Presets/Wallpapers/2007-comp-entries/02-d980_aros-rose.jpg'
                wallpaper=a.output/'configured-wallpaper.jpg'
                wallpaper_hash=guest['distribution_files'][wallpaper_path]['sha256']
                mtools_environment=dict(os.environ); mtools_environment.pop('MTOOLS_SKIP_CHECK',None)
                subprocess.run(['mcopy','-i',str(seed)+'@@67108864','::System/'+wallpaper_path,str(wallpaper)],check=True,env=mtools_environment)
                verdict['wallpaper_reference_sha256']=wallpaper_hash
                result = subprocess.run(['python3', str(a.tools / 'tests/check-aros-render-frame.py'),
                                         '--profile', 'wanderer-wallpaper', '--wallpaper', str(wallpaper), '--wallpaper-sha256',wallpaper_hash,
                                         '--serial-log', str(profile / 'serial.log'), str(a.output / 'desktop.png')],
                                        capture_output=True, text=True)
                (a.output / 'pixels.log').write_text(result.stdout + result.stderr)
                if result.returncode: raise RuntimeError('desktop-pixel-gate-failed')
                rows = subprocess.check_output(['ps', '-axo', 'pid=,ppid=,comm='], text=True).splitlines()
                children = [int(fields[0]) for row in rows if len(fields := row.split(None, 2)) == 3
                            and int(fields[1]) == process.pid and fields[2].endswith('/qemu-system-aarch64')]
                if len(children) != 1: raise RuntimeError('cannot identify owned QEMU window process')
                capture = subprocess.run(['swift', str(a.tools / 'tools/capture-window.swift'), str(children[0]),
                                          str(a.output / 'desktop-window.png')], capture_output=True, text=True, timeout=30)
                (a.output / 'window-capture.log').write_text(capture.stdout + capture.stderr)
                verdict['host_window_capture']=capture.returncode==0
                verdict['guest_viewport_capture']=True
                verdict.update(result='PASS', reason='desktop-gpu-pixels-and-two-usb-bindings')
        except Exception as error:
            verdict['reason'] = str(error)
        finally:
            if qmp is not None:
                try:
                    qmp.execute('stop')
                    for filename, instruction in [('registers.txt', 'info registers'), ('instructions.txt', 'x /24i $pc'), ('stack.txt', 'x /64gx $sp')]:
                        (a.output / filename).write_text(qmp.execute('human-monitor-command', {'command-line': instruction}))
                    qmp.execute('screendump', {'filename': str(a.output / 'stopped-desktop.png'), 'format': 'png', 'device': 'gpu', 'head': 0})
                except Exception as error:
                    (a.output / 'capture-error.txt').write_text(str(error))
                try: qmp.execute('quit')
                except Exception: pass
                qmp.close()
            if process is not None:
                try: process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    verdict['forced_cleanup'] = True
                    try: os.killpg(process.pid, signal.SIGTERM)
                    except ProcessLookupError: pass
                    try: process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        try: os.killpg(process.pid, signal.SIGKILL)
                        except ProcessLookupError: pass
                        process.wait(timeout=3)
                verdict['host_exit'] = process.returncode
            if debugger is not None:
                try: debugger.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(debugger.pid, signal.SIGTERM); debugger.wait(timeout=5)
            if debugger_log is not None: debugger_log.close()
            serial = profile / 'serial.log'
            text = serial.read_text(errors='replace') if serial.exists() else ''
            verdict['markers'] = {marker: text.count(marker) for marker in MARKERS}
            verdict['seconds'] = round(time.monotonic() - started, 2)
            verdict['seed_unchanged'] = hashlib.sha256(seed.read_bytes()).hexdigest() == verdict['seed_sha256']
            if not verdict['seed_unchanged']: verdict.update(result='FAIL', reason='seed-mutated')
            (a.output / 'verdict.json').write_text(json.dumps(verdict, indent=2) + '\n')
    print(json.dumps(verdict))
    raise SystemExit(verdict['result'] != 'PASS')

if __name__ == '__main__':
    main()
