"""Publication checks that never execute training or notebook cells."""

import ast
import importlib.util
import os
from pathlib import Path
import platform
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class HostMetadataTests(unittest.TestCase):
    def setUp(self):
        path = ROOT / "scripts/reproduce.py"
        tree = ast.parse(path.read_text())
        functions = [node for node in tree.body
                     if isinstance(node, ast.FunctionDef) and node.name == "host_info"]
        self.assertEqual(len(functions), 1)
        scope = {"os": os, "platform": platform}
        exec(compile(ast.Module(body=functions, type_ignores=[]), str(path), "exec"), scope)
        self.host_info = scope["host_info"]

    def test_serializable_inventory_not_peak_memory(self):
        import json
        record = self.host_info()
        json.dumps(record)
        self.assertEqual(record["system"], platform.system())
        self.assertIsNone(record["peak_memory_bytes"])
        if record["host_memory_bytes"] is not None:
            self.assertGreater(record["host_memory_bytes"], 0)

    def test_memory_query_unavailable(self):
        with patch.object(os, "sysconf", side_effect=ValueError, create=True):
            self.assertIsNone(self.host_info()["host_memory_bytes"])


@unittest.skipUnless(importlib.util.find_spec("pypdf"), "Install the publication extra")
class ArchivedFigureTests(unittest.TestCase):
    def test_only_one_legend_operator_changes(self):
        from pypdf import PdfReader
        from pypdf.generic import ContentStream
        spec = importlib.util.spec_from_file_location(
            "camera_ready_figures", ROOT / "scripts/prepare_camera_ready_figures.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        before_bytes = module.SOURCE.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "legend.pdf"
            module.correct_legend(target=target)
            before, after = PdfReader(module.SOURCE), PdfReader(target)
            self.assertEqual(len(before.pages), len(after.pages))
            changes = []
            for a, b in zip(before.pages, after.pages):
                self.assertEqual(a.mediabox, b.mediabox)
                ops_a = ContentStream(a.get_contents(), before).operations
                ops_b = ContentStream(b.get_contents(), after).operations
                self.assertEqual(len(ops_a), len(ops_b))
                changes.extend((x, y) for x, y in zip(ops_a, ops_b) if x != y)
            self.assertEqual(len(changes), 1)
            old, new = changes[0]
            self.assertEqual(old[1], b"TJ")
            self.assertEqual(new[1], b"TJ")
            self.assertEqual(list(new[0][0]), ["p=inf"])
        self.assertEqual(module.SOURCE.read_bytes(), before_bytes)


if __name__ == "__main__":
    unittest.main()
