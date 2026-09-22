#!/usr/bin/env python3
"""
scaffold_loop.py — Universal Loop Engineering Contract & Scaffolding Generator

Principles:
  - Do not loop on confidence. Loop on evidence.
  - Surface assumptions. Minimal code. Surgical edits.
  - Maker-Checker split: maker builds, checker validates against objective gates.
  - Respect existing repository standards (package.json, pyproject.toml, Cargo.toml, etc.).
  - LLM-agnostic & IDE-agnostic.
"""

import argparse
import json
import os
import sys
from pathlib import Path

TEMPLATES = {
    "code-tdd": {
        "title": "TDD Implementation & Bugfix Loop",
        "description": "Closed-loop code development with automated test verification and diff bounding.",
        "trigger": "Failing test, bug report, or new feature specification.",
        "goal": "Make target test suite pass with zero regressions and no superfluous code changes.",
        "action_policy": "Edit only source code and test files directly related to the issue. Max 50 lines changed per iteration. No refactoring unrelated code.",
        "verifier": "Native test suite exit code == 0 && git diff line count within budget.",
        "max_iterations": 4,
        "maker_checker": "Maker edits code and runs targeted tests. Checker independently runs full test suite and diff check.",
    },
    "refactor": {
        "title": "Surgical Code Simplification Loop",
        "description": "Simplify code complexity while keeping all existing behavior and tests strictly passing.",
        "trigger": "Complex file, cyclomatic complexity warning, or abstraction cleanup request.",
        "goal": "Reduce cyclomatic complexity / lines of code while 100% of existing regression tests pass.",
        "action_policy": "Surgically touch target functions only. Do not alter external APIs or behavior.",
        "verifier": "Existing test suite passes 100% && complexity score decreases.",
        "max_iterations": 3,
        "maker_checker": "Maker performs atomic refactorings. Checker runs regression test suite and checks for API drift.",
    },
    "research-doc": {
        "title": "Evidence-Grounded Research & Synthesis Loop",
        "description": "Iterative document or PRD generation grounded in cited primary sources and verifiable rubrics.",
        "trigger": "Research brief, technical RFC requirement, or quantitative evaluation request.",
        "goal": "Generate document satisfying rubric score >= 8/10 on clarity, factual citations, and technical feasibility.",
        "action_policy": "Synthesize verified claims only. Every non-trivial assertion must cite an existing source or benchmark.",
        "verifier": "Citation resolver passes (100% links/sources valid) && rubric checker gives >= 8/10 across all categories.",
        "max_iterations": 3,
        "maker_checker": "Maker synthesizes content. Checker validates citation integrity and scores rubric independently.",
    },
    "general": {
        "title": "Closed Autonomous Engineering Loop",
        "description": "General purpose closed-loop workflow with bounded iterations and verifiable success criteria.",
        "trigger": "Specific task requiring iterative refinement.",
        "goal": "Achieve objective success criteria with verifiable evidence.",
        "action_policy": "Make minimal necessary modifications. Log progress after each iteration.",
        "verifier": "Objective verification script or schema check exits with 0.",
        "max_iterations": 3,
        "maker_checker": "Maker implements solution. Checker runs verification gates.",
    }
}

LOOP_MD_TEMPLATE = """# LOOP CONTRACT: {title}

> **Core Axiom:** Do not loop on confidence. Loop on evidence.
> **Comprehension Debt Warning:** Keep diffs surgical. If the loop cannot verify progress automatically, stop and ask the human.

---

## 1. Loop Profile

| Dimension | Specification |
| :--- | :--- |
| **Archetype** | `{archetype}` |
| **Goal** | {goal} |
| **Trigger** | {trigger} |
| **Max Iterations** | {max_iterations} (hard stop) |
| **Detected Standards** | {detected_standards} |
| **Estimated Cost Gate** | Stop if tokens exceed allocated budget or 3 consecutive iterations fail same gate |

---

## 2. The 6 Building Blocks

### 1. Automation (Heartbeat)
- Initiated by: `{trigger}`
- Cadence: Discrete step execution.
- LLM / IDE: Agnostic (Compatible with Claude Code, Cursor, Antigravity, OpenCode, Windsurf, Cline, CLI).

### 2. Context (Hot & Warm State)
- Read contract: `LOOP.md`
- Repository standards: Follow rules in `README.md`, `package.json`, `pyproject.toml`, `AGENTS.md` (if present).
- Target files: Inspect specific workspace files before making changes.
- Ground rules: Think before coding, surgical edits, simplicity first.

### 3. Action Policy (Boundaries)
- {action_policy}
- Forbidden: Unprompted refactoring, editing lock files without reason, ignoring test failures.

### 4. Verification Gate (Checker)
- **Primary Verifier:** `{verifier}`
- Verification command:
  ```bash
  {verifier_cmd}
  ```
- Pass condition: Clean exit code (0), zero regressions, zero unverified assumptions.

### 5. State Persistence
- Progress tracked in `loop_state.json` or git commit history.
- Schema: `[iteration_number, changes_made, verifier_output, outcome]`

### 6. Stop Conditions
- **SUCCESS STOP:** Primary verifier passes with zero warnings.
- **FAILURE STOP:** `{max_iterations}` iterations reached without passing verifier.
- **ESCALATION STOP:** Unrecoverable environment/harness error or contradictory requirements detected.

---

## 3. Maker-Checker Execution Protocol

```
           ┌─────────────────────────────────────────┐
           │        1. PLAN (State Next Step)         │
           └────────────────────┬────────────────────┘
                                │
                   ┌────────────┴────────────┐
                   │    2. DO (Maker Phase)   │
                   │ (Minimal Surgical Edit) │
                   └────────────┬────────────┘
                                │
                   ┌────────────┴────────────┐
                   │  3. VERIFY (Checker)    │
                   │ (Run Objective Gate)    │
                   └────────────┬────────────┘
                                │
                   ┌────────────┴────────────┐
                   │   4. DECIDE (Stop/Iter) │
                   │ Passed? -> STOP         │
                   │ Failed? -> Log & Loop   │
                   └─────────────────────────┘
```

1. **PLAN:** Explicitly state the single next step and what hypothesis it tests.
2. **DO:** Maker applies surgical modification adhering to detected repository standards.
3. **VERIFY:** Checker executes the objective verification command:
   ```bash
   {verifier_cmd}
   ```
4. **DECIDE:**
   - If verifier succeeds: Mark complete, summarize verified diff, STOP.
   - If verifier fails: Feed error back into context, increment iteration count, repeat until `{max_iterations}`.

---

## 4. Production Checklist (Before Launching Loop)

- [ ] Has the repository stack been detected or grilled (language, test runner, package manager)?
- [ ] Is "done" completely objective? (No subjective "looks good")
- [ ] Can the agent run the verifier autonomously without human typing?
- [ ] Is the failure stop condition strictly bounded (<= {max_iterations} iterations)?
- [ ] Is the action surface restricted to only the necessary files?
"""

VERIFIER_SCRIPT_TEMPLATE = """#!/usr/bin/env python3
\"\"\"
Objective Verification Gate for Loop
Exits 0 on success, non-zero on failure.
\"\"\"

import subprocess
import sys

def run_check(cmd, description):
    print(f"[*] Checking: {{description}}...")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[FAIL] {{description}} failed!")
        print(res.stdout)
        print(res.stderr)
        return False
    print(f"[PASS] {{description}} passed.")
    return True

def main():
    # Verification checks tailored to project standards:
    checks = [
        ("{verifier_cmd}", "Primary Verification Gate"),
    ]

    for cmd, desc in checks:
        if not run_check(cmd, desc):
            sys.exit(1)

    print("\\n[SUCCESS] All verification gates passed. Loop stop condition met.")
    sys.exit(0)

if __name__ == "__main__":
    main()
"""

RUNNER_SCRIPT_TEMPLATE = """#!/usr/bin/env bash
set -euo pipefail

# Closed Loop Execution Harness
MAX_ITER={max_iterations}
ITER=1

echo "=================================================="
echo " Starting Closed Loop: {title}"
echo " Max Iterations: $MAX_ITER"
echo "=================================================="

while [ "$ITER" -le "$MAX_ITER" ]; do
    echo ""
    echo ">>> Iteration $ITER of $MAX_ITER..."

    # Check if verifier passes
    if {verifier_cmd}; then
        echo ""
        echo "[SUCCESS] Verifier passed on iteration $ITER! Exiting loop."
        exit 0
    fi

    echo "[INFO] Verifier failed on iteration $ITER."
    if [ "$ITER" -eq "$MAX_ITER" ]; then
        echo "[STOP] Reached maximum iterations ($MAX_ITER) without passing verifier."
        echo "[ACTION] Escalate to human operator. Do not continue blind looping."
        exit 1
    fi

    ITER=$((ITER + 1))
done
"""

def detect_repository_standards(target_dir: Path) -> dict:
    """Inspects workspace to detect language, package manager, and test runner."""
    standards = {
        "stack": "unknown",
        "default_test_cmd": "python3 scripts/verify_gate.py",
        "configs_found": []
    }

    # JavaScript / TypeScript
    pkg_json = target_dir / "package.json"
    if pkg_json.exists():
        standards["configs_found"].append("package.json")
        try:
            with open(pkg_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            scripts = data.get("scripts", {})
            if "test" in scripts:
                if (target_dir / "pnpm-lock.yaml").exists():
                    standards["stack"] = "TypeScript/Node (pnpm)"
                    standards["default_test_cmd"] = "pnpm test"
                elif (target_dir / "yarn.lock").exists():
                    standards["stack"] = "TypeScript/Node (yarn)"
                    standards["default_test_cmd"] = "yarn test"
                else:
                    standards["stack"] = "JavaScript/Node (npm)"
                    standards["default_test_cmd"] = "npm test"
        except Exception:
            pass

    # Python
    pyproject = target_dir / "pyproject.toml"
    pytest_ini = target_dir / "pytest.ini"
    reqs = target_dir / "requirements.txt"
    if pyproject.exists() or pytest_ini.exists() or reqs.exists():
        standards["stack"] = "Python"
        standards["default_test_cmd"] = "pytest"
        if pyproject.exists():
            standards["configs_found"].append("pyproject.toml")
        if pytest_ini.exists():
            standards["configs_found"].append("pytest.ini")

    # Rust
    cargo = target_dir / "Cargo.toml"
    if cargo.exists():
        standards["stack"] = "Rust (cargo)"
        standards["default_test_cmd"] = "cargo test"
        standards["configs_found"].append("Cargo.toml")

    # Go
    gomod = target_dir / "go.mod"
    if gomod.exists():
        standards["stack"] = "Go"
        standards["default_test_cmd"] = "go test ./..."
        standards["configs_found"].append("go.mod")

    # Java / Maven / Gradle
    if (target_dir / "pom.xml").exists():
        standards["stack"] = "Java (Maven)"
        standards["default_test_cmd"] = "mvn test"
        standards["configs_found"].append("pom.xml")
    elif (target_dir / "build.gradle").exists() or (target_dir / "build.gradle.kts").exists():
        standards["stack"] = "Java/Kotlin (Gradle)"
        standards["default_test_cmd"] = "./gradlew test"
        standards["configs_found"].append("build.gradle")

    # Agent / Project Guides
    for guide in ["README.md", "AGENTS.md", "CLAUDE.md", ".cursorrules"]:
        if (target_dir / guide).exists():
            standards["configs_found"].append(guide)

    return standards

def scaffold(output_dir: Path, archetype: str, goal: str = None, verifier_cmd: str = None):
    output_dir.mkdir(parents=True, exist_ok=True)
    spec = TEMPLATES.get(archetype, TEMPLATES["general"])

    # Detect existing repo standards
    detected = detect_repository_standards(output_dir)
    if not detected["configs_found"] and output_dir.resolve() != Path.cwd().resolve():
        detected = detect_repository_standards(Path.cwd())

    actual_goal = goal if goal else spec["goal"]
    
    if verifier_cmd:
        actual_verifier_cmd = verifier_cmd
    elif detected["stack"] != "unknown":
        actual_verifier_cmd = detected["default_test_cmd"]
    else:
        actual_verifier_cmd = "python3 scripts/verify_gate.py"

    detected_summary = f"{detected['stack']} (found: {', '.join(detected['configs_found']) if detected['configs_found'] else 'none'})"

    loop_md = LOOP_MD_TEMPLATE.format(
        archetype=archetype,
        title=spec["title"],
        goal=actual_goal,
        trigger=spec["trigger"],
        max_iterations=spec["max_iterations"],
        action_policy=spec["action_policy"],
        verifier=spec["verifier"],
        verifier_cmd=actual_verifier_cmd,
        detected_standards=detected_summary
    )

    loop_md_path = output_dir / "LOOP.md"
    loop_md_path.write_text(loop_md, encoding="utf-8")
    print(f"  + Created {loop_md_path} (Detected: {detected_summary})")

    scripts_dir = output_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    verifier_path = scripts_dir / "verify_gate.py"
    verifier_content = VERIFIER_SCRIPT_TEMPLATE.format(verifier_cmd=actual_verifier_cmd)
    verifier_path.write_text(verifier_content, encoding="utf-8")
    verifier_path.chmod(0o755)
    print(f"  + Created {verifier_path}")

    runner_path = scripts_dir / "run_loop.sh"
    runner_content = RUNNER_SCRIPT_TEMPLATE.format(
        title=spec["title"],
        max_iterations=spec["max_iterations"],
        verifier_cmd=actual_verifier_cmd
    )
    runner_path.write_text(runner_content, encoding="utf-8")
    runner_path.chmod(0o755)
    print(f"  + Created {runner_path}")

    print("\n[OK] Loop contract and execution scaffolding successfully created.")
    print(f"Review your contract: {loop_md_path}")

def main():
    parser = argparse.ArgumentParser(description="Scaffold an autonomous closed loop contract adhering to project standards.")
    parser.add_argument("--type", choices=list(TEMPLATES.keys()), default="general", help="Loop archetype")
    parser.add_argument("--goal", type=str, help="Specific goal statement")
    parser.add_argument("--verifier", type=str, help="Verification command (e.g. 'pytest', 'pnpm test')")
    parser.add_argument("--output", type=str, default=".", help="Directory where files will be created")

    args = parser.parse_args()
    scaffold(
        output_dir=Path(args.output),
        archetype=args.type,
        goal=args.goal,
        verifier_cmd=args.verifier
    )

if __name__ == "__main__":
    main()
