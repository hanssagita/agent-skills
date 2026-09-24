"""Regression tests for skills/loop-engineering-generator/scripts/scaffold_loop.py.

Run: python3 -m unittest discover tests
"""

import ast
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "skills/loop-engineering-generator/scripts/scaffold_loop.py"


def scaffold(cwd, *args):
    return subprocess.run([sys.executable, str(SCRIPT), "--output", ".", *args],
                          cwd=cwd, capture_output=True, text=True, check=True)


def run(cwd, *cmd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=30)


class ScaffoldLoopTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_empty_dir_verifier_fails_fast_without_recursion(self):
        scaffold(self.dir)
        res = run(self.dir, sys.executable, "scripts/verify_gate.py")
        self.assertEqual(res.returncode, 1)
        self.assertIn("No verification command configured", res.stdout)

    def test_quoted_verifier_generates_valid_scripts(self):
        scaffold(self.dir, "--verifier", """echo "a b" && echo 'c'""")
        ast.parse((self.dir / "scripts/verify_gate.py").read_text())
        self.assertEqual(run(self.dir, "bash", "-n", "scripts/run_loop.sh").returncode, 0)
        self.assertEqual(run(self.dir, sys.executable, "scripts/verify_gate.py").returncode, 0)
        self.assertEqual(run(self.dir, "bash", "scripts/run_loop.sh").returncode, 0)

    def test_rerun_does_not_overwrite_without_force(self):
        scaffold(self.dir)
        (self.dir / "LOOP.md").write_text("EDITED")
        scaffold(self.dir)
        self.assertEqual((self.dir / "LOOP.md").read_text(), "EDITED")
        scaffold(self.dir, "--force")
        self.assertNotEqual((self.dir / "LOOP.md").read_text(), "EDITED")

    def test_mixed_stack_detection(self):
        (self.dir / "package.json").write_text(json.dumps({"scripts": {"test": "vitest"}}))
        (self.dir / "pnpm-lock.yaml").touch()
        (self.dir / "pyproject.toml").touch()
        scaffold(self.dir)
        loop_md = (self.dir / "LOOP.md").read_text()
        self.assertIn("pnpm", loop_md)
        self.assertIn("Python", loop_md)
        self.assertIn('"pnpm test"', (self.dir / "scripts/verify_gate.py").read_text())

    def test_diff_budget_blocks_oversized_diff(self):
        for cmd in (["git", "init", "-q"], ["git", "config", "user.email", "t@t"], ["git", "config", "user.name", "t"]):
            run(self.dir, *cmd)
        target = self.dir / "big.txt"
        target.write_text("")
        run(self.dir, "git", "add", ".")
        run(self.dir, "git", "commit", "-qm", "init")
        target.write_text("\n".join(str(i) for i in range(60)) + "\n")
        scaffold(self.dir, "--verifier", "true")
        res = run(self.dir, sys.executable, "scripts/verify_gate.py")
        self.assertEqual(res.returncode, 1)
        self.assertIn("Diff budget exceeded", res.stdout)


if __name__ == "__main__":
    unittest.main()
