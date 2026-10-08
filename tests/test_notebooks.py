"""Validate notebook structure and imports without executing exercise solutions."""
import ast
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parents[1]


class NotebookTests(unittest.TestCase):
    def test_structure_and_syntax(self):
        for path in (ROOT / "notebooks/lectures").glob("*.ipynb"):
            with self.subTest(notebook=path.name):
                notebook = nbformat.read(path, as_version=4)
                nbformat.validate(notebook)
                self.assertEqual(notebook.metadata.kernelspec.name, "python3")
                for cell in notebook.cells:
                    if cell.cell_type == "code":
                        ast.parse(cell.source)

    def test_imports_from_repository_and_notebook_directory(self):
        notebook = json.loads((ROOT / "notebooks/lectures/1_vacum_land.ipynb").read_text())
        source = "".join(notebook["cells"][2]["source"])
        for directory in (ROOT, ROOT / "notebooks/lectures"):
            with self.subTest(directory=directory):
                result = subprocess.run([sys.executable, "-c", source], cwd=directory,
                                        capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr)
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, "-c", source], cwd=directory,
                                    capture_output=True, text=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Open this notebook from inside the course repository", result.stderr)


if __name__ == "__main__":
    unittest.main()
