#!/usr/bin/env python3
"""
Objective Verification Gate for Loop
Exits 0 on success, non-zero on failure.
"""

import subprocess
import sys
import os

def check_diff_budget(max_lines):
    """Fails when the uncommitted git diff exceeds the surgical-change budget."""
    try:
        res = subprocess.run("git diff --shortstat", shell=True, capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            import re
            m_ins = re.search(r'(\d+)\s+insertions?\(\+\)', res.stdout)
            m_del = re.search(r'(\d+)\s+deletions?\(-\)', res.stdout)
            ins = int(m_ins.group(1)) if m_ins else 0
            dels = int(m_del.group(1)) if m_del else 0
            total = ins + dels
            if total > max_lines:
                print(f"[FAIL] Diff budget exceeded: {{total}} lines changed (max: {{max_lines}}). Keep changes surgical!")
                return False
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
