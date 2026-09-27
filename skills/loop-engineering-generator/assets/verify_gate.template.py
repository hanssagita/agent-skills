#!/usr/bin/env python3
"""
Objective Verification Gate for Loop
Exits 0 on success, non-zero on failure.
"""

import subprocess
import sys
import os
from pathlib import Path

# Anchor execution to project root directory
os.chdir(Path(__file__).resolve().parent.parent)


def check_diff_budget(max_lines):
    """Fails when uncommitted, staged, or untracked changes exceed the surgical-change budget."""
    try:
        # Check diff against HEAD scoped to current directory (captures staged & unstaged changes)
        res = subprocess.run("git diff HEAD --shortstat .", shell=True, capture_output=True, text=True)
        if res.returncode != 0:
            # Fallback if HEAD does not exist yet (e.g. freshly initialized repo before initial commit)
            res = subprocess.run("git diff --shortstat .", shell=True, capture_output=True, text=True)

        ins = 0
        dels = 0
        if res.returncode == 0 and res.stdout.strip():
            import re
            m_ins = re.search(r'(\d+)\s+insertions?\(\+\)', res.stdout)
            m_del = re.search(r'(\d+)\s+deletions?\(-\)', res.stdout)
            ins = int(m_ins.group(1)) if m_ins else 0
            dels = int(m_del.group(1)) if m_del else 0

        # Also inspect untracked files (excluding loop harness and context scaffolding)
        untracked_lines = 0
        res_untracked = subprocess.run("git status --porcelain -u .", shell=True, capture_output=True, text=True)
        if res_untracked.returncode == 0 and res_untracked.stdout.strip():
            harness_prefixes = ("LOOP.md", "AGENTS.md", "loop_state.json", ".ai-context/", ".agents/", ".claude/", "scripts/")
            for line in res_untracked.stdout.strip().splitlines():
                if line.startswith("?? "):
                    rel_path = line[3:].strip().strip('"')
                    norm_path = rel_path.lstrip("./")
                    if any(norm_path == p or norm_path.startswith(p) for p in harness_prefixes):
                        continue
                    if os.path.isfile(rel_path):
                        try:
                            with open(rel_path, "r", encoding="utf-8", errors="ignore") as f:
                                untracked_lines += sum(1 for _ in f)
                        except Exception:
                            pass

        total = ins + dels + untracked_lines
        if total > max_lines:
            detail = f"{{total}} lines changed ({{ins}}+{{dels}} diff, {{untracked_lines}} untracked)" if untracked_lines > 0 else f"{{total}} lines changed"
            print(f"[FAIL] Diff budget exceeded: {{detail}} (max: {{max_lines}}). Keep changes surgical!")
            return False
        if total > 0:
            print(f"[PASS] Diff budget check: {{total}}/{{max_lines}} lines changed.")
    except Exception as e:
        print(f"[WARN] Diff budget check skipped: {{e}}")
    return True

def run_check(cmd, description):
    print(f"[*] Checking: {{description}}...")
    if not cmd or "TODO: Configure your verification command" in cmd:
        print("[FAIL] No verification command configured! Please set a valid test command in scripts/verify_gate.py.")
        return False

    if "verify_gate.py" in cmd:
        print("[FAIL] Self-referential command detected! verify_gate.py cannot invoke itself.")
        return False

    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[FAIL] {{description}} failed!")
        if res.stdout:
            print(res.stdout)
        if res.stderr:
            print(res.stderr)
        return False
    print(f"[PASS] {{description}} passed.")
    return True

def main():
    # Verification checks tailored to project standards:
    checks = [
        ({verifier_cmd_repr}, "Primary Verification Gate"),
    ]

    for cmd, desc in checks:
        if not run_check(cmd, desc):
            sys.exit(1)

    if not check_diff_budget(max_lines={max_diff_lines}):
        sys.exit(1)

    print("\n[SUCCESS] All verification gates passed. Loop stop condition met.")
    sys.exit(0)

if __name__ == "__main__":
    main()
