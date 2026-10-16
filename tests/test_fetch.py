# SPDX-License-Identifier: MIT
# Copyright (c) 2026 John Knipper
"""Exercise the real two-repository bootstrap without network or guest execution."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]

class Fetch(unittest.TestCase):
    def test_exact_tools_then_shared_core_and_no_overwrite(self):
        with tempfile.TemporaryDirectory(prefix='pomaros acquisition ') as directory:
            root=Path(directory)
            def repository(name,files):
                path=root/name;path.mkdir()
                def git(*args):
                    return subprocess.check_output(['git','-C',str(path),*args],text=True).strip()
                git('init','-q','-b','main')
                for relative,data in files.items():
                    p=path/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
                git('add','.');git('-c','user.name=Fetch Test','-c','user.email=fetch@example.invalid','commit','-qm','fixture')
                return path,git('rev-parse','HEAD')
            core,core_revision=repository('core-origin',{'source':b'guest source\n'})
            tools,tools_revision=repository('tools-origin',{'tools/fetch-core.py':
                (ROOT.parent/'pomaros-vm/tools/fetch-core.py').read_bytes()})
            product=root/'product';(product/'tools').mkdir(parents=True)
            shutil.copyfile(ROOT/'tools/fetch-sources.py',product/'tools/fetch-sources.py')
            (product/'TOOLS.lock').write_text(f'TOOLS_URL={tools}\nTOOLS_REVISION={tools_revision}\n')
            (product/'CORE.lock').write_text(f'CORE_URL={core}\nCORE_REVISION={core_revision}\n')
            selected_tools=root/'selected tools';selected_core=root/'selected core'
            command=['python3',str(product/'tools/fetch-sources.py'),'--tools',str(selected_tools),'--source',str(selected_core)]
            first=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(first.returncode,0,first.stdout+first.stderr)
            for path,revision in ((selected_tools,tools_revision),(selected_core,core_revision)):
                self.assertEqual(subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip(),revision)
            (selected_tools/'personal').write_text('keep this\n')
            second=subprocess.run(command,capture_output=True,text=True)
            self.assertNotEqual(second.returncode,0)
            self.assertEqual((selected_tools/'personal').read_text(),'keep this\n')
            self.assertEqual((selected_core/'source').read_text(),'guest source\n')
