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

    def test_creates_agents_md_and_skills_automatically(self):
        scaffold(self.dir, "--verifier", "pytest")
        agents_md = self.dir / "AGENTS.md"
        self.assertTrue(agents_md.exists())
        self.assertIn("Loop Engineering Protocol", agents_md.read_text())
        self.assertIn("pytest", agents_md.read_text())

        agent_skill = self.dir / ".agents" / "skills" / "loop-engineering" / "SKILL.md"
        claude_skill = self.dir / ".claude" / "skills" / "loop-engineering" / "SKILL.md"
        self.assertTrue(agent_skill.exists())
        self.assertTrue(claude_skill.exists())
        self.assertIn("name: loop-engineering", agent_skill.read_text())
        self.assertIn("pytest", agent_skill.read_text())

    def test_appends_protocol_to_existing_agents_md(self):
        existing_agents = self.dir / "AGENTS.md"
        existing_agents.write_text("# Existing Project Guidelines\n- Rule 1: Clean architecture\n")
        scaffold(self.dir, "--verifier", "cargo test")
        content = existing_agents.read_text()
        self.assertIn("Existing Project Guidelines", content)
        self.assertIn("Loop Engineering Protocol", content)
        self.assertIn("cargo test", content)

    def test_flags_can_skip_agents_md_and_skill(self):
        scaffold(self.dir, "--no-agents-md", "--no-skill")
        self.assertFalse((self.dir / "AGENTS.md").exists())
        self.assertFalse((self.dir / ".agents" / "skills" / "loop-engineering").exists())
        self.assertFalse((self.dir / ".claude" / "skills" / "loop-engineering").exists())


if __name__ == "__main__":
    unittest.main()
