# SPDX-License-Identifier: MIT
# Copyright (c) 2026 John Knipper
"""The supervisor ignores async QMP events and reports errors/disconnection."""
import importlib.util
import json
from pathlib import Path
import socket
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('qualify', ROOT / 'tools/qualify.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)

class Protocol(unittest.TestCase):
    def test_async_event_error_and_disconnect(self):
        with tempfile.TemporaryDirectory(prefix='pq-test-', dir='/tmp') as directory:
            endpoint = Path(directory) / 'qmp'
            server = socket.socket(socket.AF_UNIX); server.bind(str(endpoint)); server.listen(1)
            def serve():
                conn, _ = server.accept()
                with conn, conn.makefile('rwb') as stream:
                    stream.write(b'{"QMP":{"version":{}}}\n'); stream.flush()
                    request = json.loads(stream.readline())
                    self.assertEqual(request['execute'], 'qmp_capabilities')
                    stream.write(b'{"return":{}}\n'); stream.flush()
                    request = json.loads(stream.readline())
                    self.assertEqual(request['execute'], 'query-status')
                    stream.write(b'{"event":"STOP"}\n{"return":{"running":false}}\n'); stream.flush()
                    stream.readline(); stream.write(b'{"error":{"desc":"bad command"}}\n'); stream.flush()
                    stream.readline()
                server.close()
            thread = threading.Thread(target=serve, daemon=True); thread.start()
            client = module.QMP(endpoint)
            try:
                self.assertFalse(client.execute('query-status')['running'])
                with self.assertRaisesRegex(RuntimeError, 'bad command'):
                    client.execute('unknown')
                with self.assertRaisesRegex(RuntimeError, 'disconnected'):
                    client.execute('disconnect')
            finally:
                client.close(); thread.join(timeout=5)
            self.assertFalse(thread.is_alive())
